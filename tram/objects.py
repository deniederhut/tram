#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from collections import namedtuple
import threading
import time
import sys

Record = namedtuple('Record', 'instance value version'.split())

class ValidationError(Exception):
    """Raised when a log fails to validate"""
    pass


class SuccessError(Exception):
    """Raised to exit transaction loop"""
    pass


class Action:
    """An class whose public methods are transactions

    The public methods of this class expect to see sequences of tuples, where
    the objects in those tuples either implement the Atomic interface or are
    themselves immutable.

    - self.set implements overwrites
    - self.update does in-place addition
    - self.transfer moves values from one instance to another

    This class implements the STM TL2 algorithm (the logic is mostly contained
    in cls.transaction). Primary differences between other threadsafe
    algorithms include non-locking reads and dynamically available writes.
    """

    sleep = 0

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

    @staticmethod
    def nada(instance_list, read_list):
        """Convenience method to return data unchanged"""
        return (
            (instance, data)
            for instance, data in zip(instance_list, read_list)
        )

    def transaction(self, *instance_list, read_action=None, write_action=nada, retries=100):
        """Conduct threadsafe operation"""
        if read_action is None:
            read_action = self.read
        time.sleep(self.sleep) # these are here for testing in threaded envs
        while retries:
            with self:
                read_list = read_action(instance_list)
                self.write(write_action(instance_list, read_list))
                self.sequence_lock(instance_list)
                time.sleep(self.sleep)
                try:
                    self.validate()
                    time.sleep(self.sleep)
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

    def __init__(self):
        self._locked = False
        self._version = time.time()

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.data))

    def __lt__(self, other):
        return self.data <  self.__cast(other)

    def __le__(self, other):
        return self.data <= self.__cast(other)

    def __eq__(self, other):
        return self.data == self.__cast(other)

    def __gt__(self, other):
        return self.data >  self.__cast(other)

    def __ge__(self, other):
        return self.data >= self.__cast(other)

    def __cast(self, other):
        return other.data if isinstance(other, self.__class__) else other

    def __contains__(self, item):
        return item in self.data

    def __len__(self):
        return len(self.data)

    def __iadd__(self, other):
        def funk(instance_list, read_list):
            return (
                (instance, data+other)
                for instance, data in zip(instance_list, read_list)
            )
        do = Action()
        do.transaction(self, write_action=funk)

    def __imul__(self, other):
        def funk(instance_list, read_list):
            return (
                (instance, data*other)
                for instance, data in zip(instance_list, read_list)
            )
        do = Action()
        do.transaction(self, write_action=funk)

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
        raise NotImplementedError("{} is meant to be subclassed".format(self.__class__.__name__))

    @data.setter
    def data(self, item):
        raise NotImplementedError("{} is meant to be subclassed".format(self.__class__.__name__))


class List(HasTram):

    def __init__(self, data=None):
        super().__init__()
        self.data = data

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
        def funk(instance_list, read_list):
                return (
                    (instance, data[ :index] + [item] + data[index+1: ])
                    for instance, data in zip(instance_list, read_list)
                )
        do = Action()
        do.transaction(self, write_action=funk)

    def __delitem__(self, index):
        def funk(instance_list, read_list):
            return (
                (instance, data[ :index] + data[index+1: ])
                for instance, data in zip(instance_list, read_list)
            )
        do = Action()
        do.transaction(self, write_action=funk)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, item):
        if item:
            self._data = list(item)
        else:
            self._data = []

    def index(self, item, *args):
        return self.data.index(item, *args)

    def append(self, item):
        self.__iadd__([item])

    def insert(self, item, index):
        if index < 0:
            index = len(self.data) + index
        def funk(instance_list, read_list):
            return (
                (instance, data[:index] + [item] + data[index:])
                for instance, data in zip(instance_list, read_list)
            )
        do = Action()
        do.transaction(self, write_action=funk)

    def pop(self, index=-1):
        result = []
        if index < 0:
            index = len(self.data) + index
        def funk(instance_list, read_list):
            nonlocal result
            for instance, data in zip(instance_list, read_list):
                result.append(data[index])
                yield (instance, data[ :index] + data[index+1: ])
        do = Action()
        do.transaction(self, write_action=funk)
        if len(result) == 1:
            return result[0]
        else:
            return result

    def remove(self, item):
        def funk(instance_list, read_list):
            index = self.index(item)
            return (
                (instance, data[ :index] + data[index+1: ])
                for instance, data in zip(instance_list, read_list)
            )
        do = Action()
        do.transaction(self, write_action=funk)

    def sort(self, *args, **kwargs):
        def funk(instance_list, read_list):
            return (
                (instance, sorted(data, *args, **kwargs))
                for instance, data in zip(instance_list, read_list)
            )
        do = Action()
        do.transaction(self, write_action=funk)

    def extend(self, other):
        self.__iadd__(other)


class Dict(HasTram):
    pass
