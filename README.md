[![Build Status](https://travis-ci.org/deniederhut/tram.svg?branch=master)](https://travis-ci.org/deniederhut/tram)

# TraM

TraM is a collection of threadsafe objects and function calls, created with software transactional memory, transactional locking II (STM-TL2; see [10.1007/11864219_14](https:link.springer.com/chapter/10.1007/11864219_14)).

## When do I need this?

Only when you have separate threads of control accessing shared memory, which is hard to do in Python, even on purpose. The basic problem solved by STM-TL2 is the risk of one thread changing a mutable object when another is using it. In STM-TL2, proposed changes are written to a journal, which is then validated, and finally committed (much like in database management system). Objects do get locked, but only for the duration of the commit, which is only changing pointer references.

## How do I install it?

`pip install git+https://github.com/deniederhut/tram.git`

## How do I use it?

TraM objects are like other Python objects, except that their methods are threadsafe:

```python
from tram import List
my_list = List([1, 2, 3])
my_list.insert(1, 1)

my_list
```

```python
List([1, 1, 2, 3])
```

TraM also includes a handful of functions which implement common use-cases for transactional objects

```python
from tram import Dict, transfer_item

right = Dict({'back' : 'scratcher'})
left = Dict({'mic' : 'test'})
transfer_item(left, right, 'mic')

right, left
```

```python
Dict({'mic': 'test', 'back': 'scratcher'}), Dict({})
```
