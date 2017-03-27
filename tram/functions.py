#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from tram.objects import Action, HasTram


def transfer_value(from_instance, to_instance, amount):
    """
    """
    def fun(instance_list, read_list):
        for instance, value in zip(instance_list, read_list):
            if instance is to_instance:
                yield instance, value + amount
            else:
                yield instance, value - amount
    do = Action()
    do.transaction(from_instance, to_instance, write_action=fun)


def transfer_item(from_instance, to_instance, index):
    """
    """
    def fun(instance_list, read_list):
        for instance, value in zip(instance_list, read_list):
            if instance is from_instance:
                result = value.pop(index)
                yield instance, value
            else:
                try:
                    value.update({index : result})
                except AttributeError:
                    value.insert(index, result)
                yield instance, value
    do = Action()
    do.transaction(from_instance, to_instance, write_action=fun)
