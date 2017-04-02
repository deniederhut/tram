#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from collections import namedtuple
import threading
import time
import sys

from tram.decorators import atomic

Record = namedtuple('Record', 'instance value version'.split())

class ValidationError(Exception):
    """Raised when a log fails to validate"""
    pass


class SuccessError(Exception):
    """Raised to exit transaction loop"""
    pass


class Action:
    """Object which implements TL2 algorithm
    """

    def __init__(self, retries=100, sleep=0):
        self.retries = retries
        self.sleep = sleep

    def __enter__(self):
        """initialize local logs"""
        self.read_log = []
        self.write_log = []

    def __exit__(self, exc_type, exc_value, traceback):
        """send logs to the garbage collector"""
        del self.read_log
        del self.write_log

    def validate(self):
        """Raise exception if any instance reads are no longer valid
        """
        for record in self.read_log:
            if record.instance.version > record.version:
                raise ValidationError("Read log is stale")

    def read(self, instance_list):
        """Non-blocking read of attribute data"""
        result = []
        for instance in instance_list:
            # Try to find last write value in log
            try:
                __, data, version = next(filter(lambda x: x.instance is instance, reversed(self.write_log)))
            # If it doesn't exist, grab shared value
            except StopIteration:
                data, version = instance.data, instance.version
            self.read_log.append(Record(instance, data, version))
            result.append(data)
        return result

    @staticmethod
    def sequence_lock(instance_list):
        """Lock all instances

        This method locks instances in order of their memory id to avoid deadlocking
        """
        for instance in sorted(instance_list, key=id):
            instance.__enter__()

    @staticmethod
    def sequence_unlock(instance_list):
        """Unlock all instances

        This method unlocks instances in order of their memory id to avoid race condition
        """
        for instance in sorted(instance_list, key=id, reverse=True):
            instance.__exit__(None, None, None)

    def transaction(self, *instance_list, write_action, read_action=None):
        """Conduct threadsafe operation"""
        if read_action is None:
            read_action = self.read
        retries = self.retries
        time.sleep(self.sleep) # these are here for testing in threaded envs
        while retries:
            with self:
                read_list = read_action(instance_list)
                self.write(write_action(instance_list, read_list))
                self.sequence_lock(instance_list)
                time.sleep(self.sleep) # for testing
                try:
                    self.validate()
                    time.sleep(self.sleep) # for testing
                    self.commit()
                except ValidationError:
                    pass
                except SuccessError:
                    break
                finally:
                    self.sequence_unlock(instance_list)
            retries -= 1

    def commit(self):
        """Commit write log to memory"""
        for record in self.write_log:
            record.instance.data = record.value
            record.instance.version = record.version
        raise SuccessError

    def write(self, pair_list):
        """Write instance-value pairs to write log"""
        for instance, value in pair_list:
            self.write_log.append(Record(instance, value, time.time()))


class HasTram:
    """An Tobject with version and lock attributes"""

    def __init__(self, data=None):
        self.data = data
        self._locked = False
        self._version = time.time()

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.data))

    def __lt__(self, other):
        return self.data <  self._cast(other)

    def __le__(self, other):
        return self.data <= self._cast(other)

    def __eq__(self, other):
        return self.data == self._cast(other)

    def __gt__(self, other):
        return self.data >  self._cast(other)

    def __ge__(self, other):
        return self.data >= self._cast(other)

    def _cast(self, other):
        return other.data if isinstance(other, HasTram) else other

    def __contains__(self, item):
        return item in self.data

    def __len__(self):
        return len(self.data)

    def __add__(self, other):
        return self.__class__(self.data + self._cast(other))

    def __iadd__(self, other):
        @atomic
        def fun(data, *args, **kwargs):
            return data + other
        do = Action()
        do.transaction(self, write_action=fun)
        return self

    def __radd__(self, other):
        return self._cast(other) + self.data

    def __mul__(self, other):
        return self.__class__(self.data * self._cast(other))

    def __imul__(self, other):
        @atomic
        def fun(data, *args, **kwargs):
            return data * other
        do = Action()
        do.transaction(self, write_action=fun)
        return self

    def __rmul__(self, other):
        return self._cast(other) * self.data

    def __iter__(self):
        raise NotImplementedError(
        "iteration is not supported in instances of type {}".format(self.__class__.__name__)
        )

    def __getitem__(self, index):
        return self.data[index]

    def __enter__(self):
        wait_time = 1e-7
        while self._locked:
            time.sleep(wait_time)
            wait_time *= 2
        self._locked = True

    def __exit__(self, exc_type, exc_value, traceback):
        self._locked = False

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if value < self.version: # versions are clocks
            raise ValueError("Can't overwrite clock {} with older value: {}".format(self.version, value))
        else:
            self._version = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, item):
        self._data = item

    def clear(self):
        """Sets instance data to be cls()

        This is typically a falsey value, like 0 or []
        """
        @atomic
        def fun(*args, **kwargs):
            return type(self.data)()
        do = Action()
        do.transaction(self, write_action=fun)

    def copy(self):
        return self.__class__(self.data)


class Number(HasTram):

    def __len__(self):
        raise NotImplementedError(
        "length is not supported in instances of type {}".format(self.__class__.__name__)
        )

    def __contains__(self, item):
        raise NotImplementedError(
        "containment is not supported in instances of type {}".format(self.__class__.__name__)
        )

    def __sub__(self, other):
        return self.__class__(self.data - self._cast(other))

    def __isub__(self, other):
        @atomic
        def fun(data):
            return data - other
        do = Action()
        do.transaction(self, write_action=fun)
        return self

    def __rsub__(self, other):
        return self._cast(other) - self.data

    def __truediv__(self, other):
        return Float(self.data / self._cast(other))

    def __itruediv__(self, other):
        @atomic
        def fun(data):
            return data / other
        do = Action()
        do.transaction(self, write_action=fun)
        return self

    def __rtruediv__(self, other):
        return self._cast(other) / self.data

    def __floordiv__(self, other):
        return Int(self.data // self._cast(other))

    def __ifloordiv__(self, other):
        @atomic
        def fun(data):
            return data // other
        do = Action()
        do.transaction(self, write_action=fun)
        return self

    def __rfloordiv__(self, other):
        return self._cast(other) // self.data

    def __mod__(self, other):
        return Int(self.data % self._cast(other))

    def __pow__(self, other):
        return self.__class__(self.data ** self._cast(other))

    def __ipow__(self, other):
        @atomic
        def fun(data):
            return data ** other
        do = Action()
        do.transaction(self, write_action=fun)
        return self

    def __rpow__(self, other):
        return self._cast(other) ** self.data


class Int(Number):

    def __init__(self, data=0):
        data = int(data)
        super().__init__(data)


class Float(Number):

    def __init__(self, data=0.):
        data = float(data)
        super().__init__(data)


class List(HasTram):

    def __init__(self, data=None):
        super().__init__()
        self.data = data

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data.copy())

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.data + other.data)
        return self.__class__(self.data + list(other))

    def __radd__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(other.data + self.data)
        return self.__class__(list(other) + self.data)

    def __mul__(self, n):
        return self.__class__(self.data*n)

    __rmul__ = __mul__

    def __setitem__(self, index, item):
        @atomic
        def fun(data, *args, **kwargs):
            return data[ :index] + [item] + data[index+1: ]
        do = Action()
        do.transaction(self, write_action=fun)

    def __delitem__(self, index):
        @atomic
        def fun(data):
            return data[ :index] + data[index+1: ]
        do = Action()
        do.transaction(self, write_action=fun)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, item):
        if item:
            self._data = list(item)
        else:
            self._data = []

    def append(self, item):
        self.__iadd__([item])

    def extend(self, other):
        self.__iadd__(other)

    def count(self, item):
        return self.data.count(item)

    def ifilter(self, function):
        @atomic
        def fun(data):
            return filter(function, data)
        do = Action()
        do.transaction(self.data, write_action=fun)

    def imap(self, function, *args, **kwargs):
        @atomic
        def fun(data):
            nonlocal args, kwargs
            return function(data, *args, **kwargs)
        do = Action()
        do.transaction(*self.data, write_action=fun)

    def index(self, item, *args):
        return self.data.index(item, *args)

    def insert(self, item, index):
        @atomic
        def fun(data):
            nonlocal index, item
            if index < 0:
                index = len(data) + index
            return data[ :index] + [item] + data[index: ]
        do = Action()
        do.transaction(self, write_action=fun)

    def pop(self, index=-1):
        result = []
        @atomic
        def fun(data, *args, **kwargs):
            nonlocal index, result
            if index < 0:
                index = len(data) + index
            result.append(data[index])
            return data[ :index] + data[index+1: ]
        do = Action()
        do.transaction(self, write_action=fun)
        if len(result) == 1:
            return result[0]
        else:
            return result

    def remove(self, item):
        @atomic
        def fun(data):
            nonlocal item
            index = data.index(item)
            return data[ :index] + data[index+1: ]
        do = Action()
        do.transaction(self, write_action=fun)

    def reverse(self, *args, **kwargs):
        @atomic
        def fun(data):
            nonlocal args, kwargs
            return reversed(data, *args, **kwargs)
        do = Action()
        do.transaction(self, write_action=fun)

    def sort(self, *args, **kwargs):
        @atomic
        def fun(data):
            nonlocal args, kwargs
            return sorted(data, *args, **kwargs)
        do = Action()
        do.transaction(self, write_action=fun)


class Dict(HasTram):

    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__(data={})
        if args:
            self.data.update(args[0])
        elif kwargs:
            self.data.update(kwargs)

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise KeyError(key)

    def __setitem__(self, key, item):
        @atomic
        def fun(data):
            result = data.copy()
            result.update({key : item})
            return result
        do = Action()
        do.transaction(self, write_action=fun)

    def __delitem__(self, key):
        @atomic
        def fun(data):
            result = data.copy()
            result.pop(key)
            return result
        do = Action()
        do.transaction(self, write_action=fun)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, item):
        if item:
            self._data = dict(item)
        else:
            self._data = {}

    @classmethod
    def fromkeys(cls, iterable, value=None):
        data = dict()
        for key in iterable:
            data[key] = value
        return cls(data)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def items(self):
        return list(self.data.items())

    def keys(self):
        return list(self.data.keys())

    def update(self, mapping):
        @atomic
        def fun(data):
            result = data.copy()
            result.update(mapping)
            return result
        do = Action()
        do.transaction(self, write_action=fun)

    def values(self):
        return list(self.data.values())
