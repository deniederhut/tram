#!/usr/bin/env python
# -*- encoding: utf-8 -*-


def atomic(fun, *args, **kwargs):
    """Decorator that wraps a function literal for modifying data inside of
    generators acting on the instance-data pairs used by the transaction
    """
    def new_fun(instance_list, read_list):
        return (
            (instance, fun(data, *args, **kwargs))
            for instance, data in zip(instance_list, read_list)
        )
    return new_fun
