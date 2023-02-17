.. _quickstart:

.. module:: intercepts
    :noindex:

Quickstart
==========

Ready to get started? This page provides an introduction on getting started
with intercepts.

First, make sure that intercepts is :ref:`installed <install>`.

Then, let's start with some simple examples.


Register an Intercept
---------------------

Intercepting calls with intercepts is very simple.

Begin by importing the intercepts module.

.. code-block:: python

    >>> import intercepts

Now lets define an intercept handler, like so:

.. code-block:: python

   def handler(*args, **kwargs):
        return _(*args, **kwargs) * 2

This intercept handler simply doubles the output of the original call.
In general, an intercept handler is a function that will be called in
place of the original call. The handler will receive the original
all of the parameters passed to the original call. It also has access 
to a special variable ``_``, which is a reference to the intercepted method.

Now that we have defined a handler, we can register it to intercept a call with :func:`register`.

.. code-block:: python

    >>> intercepts.register(sum, handler)

That's it. Now any call to sum, in any module will be intercepted by
``handler``, and its result will be doubled.

.. code-block:: python

    >>> sum([1, 2, 3, 4, 5, 6])
    42

Stacking Intercepts
-------------------

Multiple intercept handlers can be registered for a Python call.
For example, we can define pre and post processing handlers, such as:

.. code-block:: python

    def pre_handler(*args, **kwargs):
        print("Executing function:", _.__name__)
        return _(*args, **kwargs)

    def post_handler(*args, **kwargs):
        result = _(*args, **kwargs)
        print("Executed function:", _.__name__)
        return result

Registering these handlers for a function will print a message before and
after that methods execution.

.. code-block:: python

    >>> intercepts.register(sum, pre_handler)
    >>> intercepts.register(sum, post_handler)
    >>> sum([1, 2, 3, 4, 5, 6])
    Executing function: sum
    Executed function: sum
    42

The same handler can even be applied multiple times.

.. code-block:: python

    >>> intercepts.register(sum, handler)
    >>> intercepts.register(sum, handler)
    >>> sum([1, 2, 3, 4, 5, 6])
    84

Intercept handlers are stored as a stack, meaning that the last
handler registered will be the first one that is executed. For example:

.. code-block:: python

    def handler_0(*args, **kwargs):
        print("handler 0")
        return _(*args, **kwargs)

    def handler_1(*args, **kwargs):
        print("handler 1")
        return _(*args, **kwargs)

    intercepts.register(abs, handler_0)
    intercepts.register(abs, handler_1)

In this example, a call to ``abs`` will print ``handler 1`` and then
``handler_0``.

.. code-block:: python

    >>> abs(-42)
    handler 1
    handler 0
    42

Unregister an Intercept
-----------------------

To unregister the intercept handlers for a function, use the :func:`unregister` function.

.. code-block:: python

    >>> intercepts.unregister(sum)

This will remove all handlers from the ``sum`` function.

An integer value, ``depth`` can also be passed to :func:`unregister` to remove 
the last ``depth`` handlers from the function.

.. code-block:: python

    >>> intercepts.unregister(sum, depth=1)

Finally, you can unregister all intercept handlers with :func:`unregister_all`.

.. code-block:: python

    >>> intercepts.unregister_all()
