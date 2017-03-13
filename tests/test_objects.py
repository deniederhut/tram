#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
import pytest

import tram.objects as m

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
