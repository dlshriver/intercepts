"""
intercepts
~~~~~~~~~~

A library for intercepting any call in Python.

Usage:

    >>> import intercepts
    >>> def print_handler(print_func, message):
    ...     return print_func(''.join(reversed(message)))
    >>> print("Hello world")
    Hello world
    >>> intercepts.register(print, print_handler)
    >>> print("Hello world")
    dlrow olleH

:copyright: (c) 2019 by David Shriver.
"""
# import intercepts._builtins

from .registration import register, unregister, unregister_all
from .__version__ import __version__

__all__ = ["register", "unregister", "unregister_all"]
