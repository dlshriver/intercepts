.. _quickstart:

Quickstart
==========

.. module:: intercepts

Ready to get started? This page provides an introduction on getting started
with intercepts.

First, make sure that intercepts is :ref:`installed <install>`.

Then, let's start with some simple examples.


Register an Intercept
---------------------

Intercepting calls with intercepts is very simple.

Begin by importing the intercepts module::

    >>> import intercepts

Now lets define an intercept handler, like so::

   def handler(func, *args, **kwargs):
        return func(*args, **kwargs) * 2

This intercept handler simply doubles the output of the original call.
In general, an intercept handler is a function that will be called in
place of the original call. The handler will receive the original
function as its first argument, as well as all of the parameters passed
to the original call. In this case, ``func`` will be a reference to the
original function, and ``args`` and ``kwargs`` will be the parameters
passed to the original call.

Now that we have defined a handler, we can register it to intercept a call.

    >>> intercepts.register(sum, handler)

That's it. Now any call to sum, in any module will be intercepted by
``handler``, and its result will be doubled.

    >>> sum([1, 2, 3, 4, 5, 6])
    42

Stacking Intercepts
-------------------

Multiple intercept handlers can be registered for a Python call.
For example, we can define pre and post processing handlers, such as::

    def pre_handler(func, *args, **kwargs):
        print("Executing function:", func.__name__)
        return func(*args, **kwargs)

    def post_handler(func, *args, **kwargs):
        result = func(*args, **kwargs)
        print("Executed function:", func.__name__)
        return result

Registering these handlers for a function will print a message before and
after that methods execution.

    >>> intercepts.register(sum, pre_handler)
    >>> intercepts.register(sum, post_handler)
    >>> sum([1, 2, 3, 4, 5, 6])
    Executing function: sum
    Executed function: sum
    42

The same handler can even be applied multiple times.

    >>> intercepts.register(sum, handler)
    >>> intercepts.register(sum, handler)
    >>> sum([1, 2, 3, 4, 5, 6])
    84

Intercept handlers are stored as a stack, meaning that the last
handler registered will be the first one that is executed. For example::

    def handler_0(func, *args, **kwargs):
        print("handler 0")
        return func(*args, **kwargs)

    def handler_1(func, *args, **kwargs):
        print("handler 1")
        return func(*args, **kwargs)

    intercepts.register(abs, handler_0)
    intercepts.register(abs, handler_1)

In this example, a call to ``abs`` will print ``handler 1`` and then
``handler_0``.

    >>> abs(-42)
    handler 1
    handler 0
    42

Unregister an Intercept
-----------------------

To unregister the intercept handlers for a function, use the ``unregister`` function::

    >>> intercepts.unregister(sum)

This will remove all handlers from the ``sum`` function.

A value can also be passed to ``unregister`` to remove the top ``depth``
handlers from the stack of intercept handlers for a function::

    >>> intercepts.unregister(sum, depth=1)

Finally, you can unregister all intercept handlers with::

    >>> intercepts.unregister_all()
