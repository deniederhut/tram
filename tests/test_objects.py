#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
import pytest

import tram.objects as m


#################
# The Int object
#################

def test_int_init():
    i = m.Int(1.4)
    assert i.data == 1

def test_int_add():
    i = m.Int(1)
    assert i + 1 == 2
    assert -1 + i == 0
    _id = id(i)
    i += 1
    assert i == 2
    assert _id == id(i)

def test_int_sub():
    i = m.Int(1)
    assert i - 1 == 0
    assert 0 - i == -1
    _id = id(i)
    i -= 1
    assert i == 0
    assert _id == id(i)

def test_int_mul():
    i = m.Int(1)
    assert i * 2 == 2
    assert 2 * i == 2
    _id = id(i)
    i *= 2
    assert i == 2
    assert _id == id(i)

def test_int_truediv():
    i = m.Int(5)
    assert i / 2 == 2.5
    assert 2 / i == 0.4
    _id = id(i)
    i /= 2
    assert i == 2.5
    assert _id == id(i)

def test_int_floordiv():
    i = m.Int(5)
    assert i // 2 == 2
    assert 2 // i == 0
    _id = id(i)
    i //= 2
    assert i == 2
    assert _id == id(i)

def test_int_pow():
    i = m.Int(2)
    assert i ** 3 == 8
    assert 3 ** i == 9
    _id = id(i)
    i **= 3
    assert i == 8
    assert _id == id(i)

def test_int_clear():
    i = m.Int(2)
    _id = id(i)
    i.clear()
    assert i == 0
    assert _id == id(i)

def test_int_contains():
    i = m.Int()
    with pytest.raises(NotImplementedError):
        4 in i

def test_int_len():
    i = m.Int()
    with pytest.raises(NotImplementedError):
        len(i)

#################
# The Float object
#################

def test_float_init():
    i = m.Float(1.4)
    assert i.data == 1.4

def test_float_add():
    i = m.Float(1)
    assert i + 1 == 2
    assert -1 + i == 0
    _id = id(i)
    i += 1
    assert i == 2
    assert _id == id(i)

def test_float_sub():
    i = m.Float(1)
    assert i - 1 == 0
    assert 0 - i == -1
    _id = id(i)
    i -= 1
    assert i == 0
    assert _id == id(i)

def test_float_mul():
    i = m.Float(1)
    assert i * 2 == 2
    assert 2 * i == 2
    _id = id(i)
    i *= 2
    assert i == 2
    assert _id == id(i)

def test_float_truediv():
    i = m.Float(5)
    assert i / 2 == 2.5
    assert 2 / i == 0.4
    _id = id(i)
    i /= 2
    assert i == 2.5
    assert _id == id(i)

def test_float_floordiv():
    i = m.Float(5)
    assert i // 2 == 2
    assert 2 // i == 0
    _id = id(i)
    i //= 2
    assert i == 2
    assert _id == id(i)

def test_float_pow():
    i = m.Float(2)
    assert i ** 3 == 8
    assert 3 ** i == 9
    _id = id(i)
    i **= 3
    assert i == 8
    assert _id == id(i)

def test_float_clear():
    i = m.Float(2)
    _id = id(i)
    i.clear()
    assert i == 0.0
    assert _id == id(i)

def test_float_contains():
    i = m.Float()
    with pytest.raises(NotImplementedError):
        4 in i

def test_float_len():
    i = m.Float()
    with pytest.raises(NotImplementedError):
        len(i)

#################
# The List object
#################

def test_list_init():
    l = m.List(None)
    assert l._data == []
    l = m.List([])
    assert l._data == []
    data = [1, 2, 3]
    l = m.List(data)
    assert l._data == data
    assert l._data is not data
    assert l._locked == False
    assert l.version < time.time()

def test_list_add():
    left = m.List([-1])
    right = m.List()
    assert left + right == left
    assert [0] + left == m.List([0, -1])
    assert left + [1] == m.List([-1, 1])
    instance_id = id(left)
    data_id = id(left.data)
    left += [0]
    assert left == [-1, 0]
    assert id(left) == instance_id
    assert id(left.data) != data_id

def test_list_mul():
    left = m.List([-1])
    assert 3 * left == m.List([-1, -1, -1])
    assert len(left * 3) == 3

def test_list_setitem():
    left = m.List([-1, 0, 1])
    left[1] = 100
    assert left == m.List([-1, 100, 1])

def test_list_delitem():
    left = m.List([-1, 0, 1])
    del left[1]
    assert left == m.List([-1, 1])

def test_list_append():
    left = m.List([-1])
    _id = id(left.data)
    left.append(0)
    assert left == m.List([-1, 0])
    assert id(left.data) != _id

def test_list_insert():
    left = m.List([1])
    _id = id(left.data)
    left.insert(-1, -1)
    assert left == m.List([-1, 1])
    assert id(left.data) != _id

def test_list_pop():
    left = m.List([-1, 0, 1])
    _id = id(left.data)
    result = left.pop()
    assert result == 1
    assert left == m.List([-1, 0])
    assert id(left.data) != _id

def test_list_remove():
    left = m.List([-1, 0, 1])
    _id = id(left.data)
    left.remove(0)
    assert left == m.List([-1, 1])
    assert id(left.data) != _id

def test_list_sort():
    left = m.List([1, 0, -1])
    _id = id(left.data)
    left.sort()
    assert left == m.List([-1, 0, 1])
    assert id(left.data) != _id
    left.sort(reverse=True)
    assert left == m.List([1, 0, -1])

def test_list_extend():
    left = m.List([-1, 0])
    right = [1]
    _id = id(left.data)
    left.extend(right)
    assert left == m.List([-1, 0, 1])
    assert id(left.data) != _id

def test_list_copy():
    left = m.List([-1])
    right = left.copy()
    assert left == right
    assert left is not right
    assert left.data is not right.data

def test_list_clear():
    l = m.List([1])
    instance_id = id(l)
    data_id = id(l.data)
    l.clear()
    assert id(l) == instance_id
    assert id(l.data) != data_id

def test_list_imap():
    left = m.List([m.HasTram(-1), m.HasTram(0)])
    left.imap(lambda x: x + 1)
    assert left == [0, 1]

#######################
# The dictionary object
#######################

def test_dict_init():
    d = m.Dict()
    assert d.data == {}
    d = m.Dict({})
    assert d.data == {}
    d = m.Dict(one=1, two=2, three=3)
    data = {'one' : 1, 'two' : 2, 'three' : 3}
    assert d.data == data
    assert d._data is not data
    assert d._locked == False
    assert d.version < time.time()

def test_dict_getitem():
    left = m.Dict({})
    with pytest.raises(KeyError):
        result = left['two']
    left = m.Dict({'one' : 1})
    assert left['one'] == 1

def test_dict_setitem():
    left = m.Dict(one=1)
    _id = id(left.data)
    left['two'] = 2
    assert left == m.Dict(one=1, two=2)
    assert id(left.data) != _id

def test_dict_clear():
    d = m.Dict({1 : 1})
    instance_id = id(d)
    data_id = id(d.data)
    d.clear()
    assert d == {}
    assert id(d) == instance_id
    assert id(d.data)!= data_id

def test_dict_copy():
    left = m.Dict({1 : 1})
    right = left.copy()
    assert right == left
    assert right is not left
    assert right.data is not left.data

def test_dict_delitem():
    left = m.Dict(one=1, two=2, three=3)
    _id = id(left.data)
    del left['one']
    assert left == m.Dict(two=2, three=3)
    assert id(left.data) != _id

def test_dict_fromkeys():
    left = m.Dict.fromkeys([1, 2], value=None)
    assert left.data == {1 : None, 2 : None}

def test_dict_get():
    left = m.Dict({'one' : 1})
    assert left.get('one') == 1
    assert left.get('two', 'dinosaur') == 'dinosaur'

def test_dict_items():
    left = m.Dict(one=1, two=2)
    assert sorted(left.items()) == sorted([('one', 1), ('two', 2)])

def test_dict_keys():
    left = m.Dict(one=1, two=2)
    assert sorted(left.keys()) == sorted(['one', 'two'])

def test_dict_update():
    left = m.Dict()
    _id = id(left.data)
    left.update({'one' : 1})
    assert left == {'one' : 1}
    assert id(left.data) != _id

def test_dict_values():
    left = m.Dict(one=1, two=2)
    assert sorted(left.values()) == sorted([1, 2])
