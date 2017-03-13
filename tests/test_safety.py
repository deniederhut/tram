#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pytest
import random
import threading
import time

from tram import List

def test_list_safety():
    shared = List([])
    def funk():
        time.sleep(random.random() / 1e6)
        shared.append(0)
    thread_list = [threading.Thread(target=funk) for _ in range(100)]
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    assert len(shared) == 100
