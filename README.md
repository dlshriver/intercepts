Intercepts
==========

Intercepts allows you to intercept any function call in `python` and handle it in any manner you choose. For example, you can pre-process the inputs to a function, or apply post-processing on its output. Intercepts also allows you to completely replace a function with a custom implementation.

```python
>>> increment(41)
42
>>> intercepts.register(increment, handler)
>>> increment(41)
40
>>> intercepts.unregister(increment)
>>> intercepts.register(increment, handler2)
>>> increment(41)
'The answer is: 42'
>>> intercepts.unregister_all()
```

Handler functions receive the intercepted function as their first argument, as well as all of the arguments to the intercepted function.

```python
>>> def handler(func, num):
...  result = func(num)
...  return num - (result - num)
>>> def handler2(func, *args, **kwargs):
...  return 'The answer is: ' + func(*args, **kwargs)
```

Installation
------------

Intercepts can be installed using `pip`.

    $ pip install intercepts

Documentation
-------------

Sorry, we are in the very early stages of development so documentation is limited.

***This software is in early stages of development and may be unstable.***
