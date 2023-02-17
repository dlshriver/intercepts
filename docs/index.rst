.. intercepts documentation master file, created by
   sphinx-quickstart on Thu Feb 16 18:53:05 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Intercepts
==========

.. image:: https://img.shields.io/github/license/dlshriver/intercepts.svg
   :target: https://github.com/dlshriver/intercepts/blob/master/LICENSE
   :alt: License

.. image:: https://img.shields.io/pypi/v/intercepts.svg
   :target: https://pypi.org/project/intercepts/
   :alt: Version

.. image:: https://github.com/dlshriver/intercepts/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/dlshriver/intercepts/actions/workflows/ci.yml
   :alt: Build Status

.. image:: https://codecov.io/gh/dlshriver/intercepts/branch/main/graph/badge.svg?token=zsQBFINrdo
   :target: https://codecov.io/gh/dlshriver/intercepts
   :alt: Codecov.io
   
.. image:: https://www.codefactor.io/repository/github/dlshriver/intercepts/badge
   :target: https://www.codefactor.io/repository/github/dlshriver/intercepts
   :alt: CodeFactor


Intercepts allows you to intercept function calls in Python and handle them in 
any manner you choose. For example, you can pre-process the inputs to a 
function, or apply post-processing on its output. Intercepts also allows you 
to completely replace a function with a custom implementation.

.. code-block:: python

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


Handler functions receive all paramters to the intercepted function call and 
can access the intercepted function through the variable ``_``.

.. code-block:: python

   >>> def handler(num):
   ...   result = _(num)
   ...   return num - (result - num)
   >>> def handler2(*args, **kwargs):
   ...   result = _(*args, **kwargs)
   ...   return f"The answer is: {result}"


The intercepts module also allows intercepting python built-in functions, such 
as ``print`` and ``sorted``. For best results, the intercepts module should be the 
first module imported.

.. code-block:: python

   >>> def print_handler(message):
   ...     return _(''.join(reversed(message)))
   >>> print("Hello world")
   Hello world
   >>> intercepts.register(print, print_handler)
   >>> print("Hello world")
   dlrow olleH


Further Reading
---------------

.. toctree::
   :maxdepth: 1
   :caption: Getting Started
   :glob:

   getting_started/install
   getting_started/quickstart

.. toctree::
   :maxdepth: 1
   :caption: Reference
   :glob:

   api
