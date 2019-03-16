Intercepts
==========

[![Build Status](https://travis-ci.org/dlshriver/intercepts.svg?branch=master)](https://travis-ci.org/dlshriver/intercepts)
[![PyPI](https://img.shields.io/pypi/v/intercepts.svg)](https://pypi.org/project/intercepts/)
[![license](https://img.shields.io/github/license/dlshriver/intercepts.svg)](https://github.com/dlshriver/intercepts/blob/master/LICENSE)

Intercepts allows you to intercept any function call in Python and handle it in any manner you choose. For example, you can pre-process the inputs to a function, or apply post-processing on its output. Intercepts also allows you to completely replace a function with a custom implementation.

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
...  return "The answer is: %s" % func(*args, **kwargs)
```

The intercepts module also allows intercepting python built-in functions, such as `print` and `sorted`. For best results, the intercepts module should be the first module imported.

```python
>>> def print_handler(print_func, message):
...     return print_func(''.join(reversed(message)))
>>> print("Hello world")
Hello world
>>> intercepts.register(print, print_handler)
>>> print("Hello world")
dlrow olleH
```

Requirements
------------

Intercepts requires python 3.3+. There are currently no additional dependencies.

Installation
------------

Intercepts can be installed using `pip`.

    $ pip install intercepts

Or, use `pip` to install the latest version from the github source.

    $ pip install -U git+https://github.com/dlshriver/intercepts.git@master

Documentation
-------------

Sorry, we are in the very early stages of development so documentation is limited. There is some documentation in the [`docs`](https://github.com/dlshriver/intercepts/tree/master/docs) directory, but for the most up-to-date documentation, use `pydoc`.

    $ pydoc intercepts

***This software is in early stages of development and may be unstable.***
