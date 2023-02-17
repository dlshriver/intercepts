Intercepts
==========

[![CI Status](https://github.com/dlshriver/intercepts/actions/workflows/ci.yml/badge.svg)](https://github.com/dlshriver/intercepts/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/dlshriver/intercepts/branch/main/graph/badge.svg?token=zsQBFINrdo)](https://codecov.io/gh/dlshriver/intercepts)
[![CodeFactor](https://www.codefactor.io/repository/github/dlshriver/intercepts/badge)](https://www.codefactor.io/repository/github/dlshriver/intercepts)
[![PyPI](https://img.shields.io/pypi/v/intercepts.svg)](https://pypi.org/project/intercepts/)
[![License](https://img.shields.io/github/license/dlshriver/intercepts.svg)](https://github.com/dlshriver/intercepts/blob/master/LICENSE)

Intercepts allows you to intercept function calls in Python and handle them in 
any manner you choose. For example, you can pre-process the inputs to a 
function, or apply post-processing on its output. Intercepts also allows you 
to completely replace a function with a custom implementation.

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

Handler functions receive all paramters to the intercepted function call and 
can access the intercepted function through the variable `_`.

```python
>>> def handler(num):
...   result = _(num)
...   return num - (result - num)
>>> def handler2(*args, **kwargs):
...   result = _(*args, **kwargs)
...   return f"The answer is: {result}"
```

The intercepts module also allows intercepting python built-in functions, such 
as `print` and `sorted`. For best results, the intercepts module should be the 
first module imported.

```python
>>> def print_handler(message):
...     return _(''.join(reversed(message)))
>>> print("Hello world")
Hello world
>>> intercepts.register(print, print_handler)
>>> print("Hello world")
dlrow olleH
```

Installation
------------

Intercepts requires Python 3.7+ on Linux or Windows and can be installed using `pip`.

    $ pip install intercepts

Or, use `pip` to install the latest version from the github source.

    $ pip install -U git+https://github.com/dlshriver/intercepts.git@main

Documentation
-------------

Some documentation is available [here](https://intercepts.readthedocs.io/en/latest/).
