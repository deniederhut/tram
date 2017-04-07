#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import tram as m

def test_transfer_value():
    left = m.Float(1)
    left_obj_id = id(left)
    left_data_id = id(left.data)
    right = m.Float(-1)
    right_obj_id = id(right)
    right_data_id = id(right.data)
    m.transfer_value(left, right, 2)
    assert left == -1
    assert right == 1
    assert left_obj_id == id(left)
    assert left_data_id != id(left.data)
    assert right_obj_id == id(right)
    assert right_data_id != id(right.data)

def test_transfer_item_list():
    left = m.List([1])
    left_obj_id = id(left)
    left_data_id = id(left.data)
    right = m.List([-1])
    right_obj_id = id(right)
    right_data_id = id(right.data)
    m.transfer_item(left, right, 0)
    assert left == []
    assert right == [1, -1]
    assert left_obj_id == id(left)
    assert left_data_id != id(left.data)
    assert right_obj_id == id(right)
    assert right_data_id != id(right.data)

def test_transfer_item_dict():
    left = m.Dict({'one' : 1})
    left_obj_id = id(left)
    left_data_id = id(left.data)
    right = m.Dict({'two' : 2})
    right_obj_id = id(right)
    right_data_id = id(right.data)
    m.transfer_item(left, right, 'one')
    assert left == {}
    assert right == {'one' : 1, 'two' : 2}
    assert left_obj_id == id(left)
    assert left_data_id != id(left.data)
    assert right_obj_id == id(right)
    assert right_data_id != id(right.data)
