"""
intercepts.registration
~~~~~~~~~~~~~~~~~~~~~~~

This module implements the intercepts registration api.
"""

import atexit
import sys
import types

from functools import partial  # , update_wrapper
from typing import Callable, Dict, List, Union

import intercepts.builtinhandler as builtinhandler

from .functypes import PyCFunctionObject
from .utils import (
    addr,
    create_code_like,
    copy_builtin,
    replace_builtin,
    copy_function,
    replace_function,
    update_wrapper,
)

MethodOrFunction = Union[types.FunctionType, types.MethodType]


_HANDLERS = {}  # type: Dict[int, List[Callable]]


def _intercept_handler(*args, **kwargs):
    consts = sys._getframe(0).f_code.co_consts
    func_id = consts[-1]
    _func = _HANDLERS[func_id][0]
    handler = _func
    for _handler in _HANDLERS[func_id][2:]:
        handler = update_wrapper(partial(_handler, handler), _func)
    result = handler(*args, **kwargs)
    return result


def register_builtin(func, handler):
    func_addr = addr(func)
    if func_addr not in _HANDLERS:
        func_copy = PyCFunctionObject()
        copy_builtin(addr(func_copy), func_addr)
        _handler = builtinhandler.get_handler(func_addr)
        _HANDLERS[func_addr] = [func_copy, _handler]
        replace_builtin(func_addr, addr(_handler))
    _HANDLERS[func_addr].append(handler)
    return func


def register_function(
    func: types.FunctionType, handler: types.FunctionType
) -> types.FunctionType:
    r"""Registers an intercept handler for a function.

    :param func: The function to intercept.
    :param handler: A function to handle the intercept.
    """
    func_addr = addr(func)
    if func_addr not in _HANDLERS:
        handler_code = create_code_like(
            _intercept_handler.__code__,
            consts=(_intercept_handler.__code__.co_consts + (func_addr,)),
            name=func.__name__,
        )
        global_dict = _intercept_handler.__globals__
        _handler = types.FunctionType(
            handler_code,
            global_dict,
            func.__name__,
            func.__defaults__,
            func.__closure__,
        )
        _handler.__code__ = handler_code

        handler_addr = addr(_handler)

        def func_copy(*args, **kwargs):
            pass

        copy_function(addr(func_copy), func_addr)

        _HANDLERS[func_addr] = [func_copy, _handler]
        replace_function(func_addr, handler_addr)
    _HANDLERS[func_addr].append(handler)
    return func


def register_method(
    method: types.MethodType, handler: types.FunctionType
) -> types.MethodType:
    r"""Registers an intercept handler for a method.

    :param method: The method to intercept.
    :param handler: A function to handle the intercept.
    """
    register_function(method.__func__, handler)
    return method


def register(obj: MethodOrFunction, handler: types.FunctionType) -> MethodOrFunction:
    r"""Registers an intercept handler.

    :param obj: The callable to intercept.
    :param handler: A function to handle the intercept.

    Usage::

        >>> import intercepts
        >>> increment = lambda x: x + 1
        >>> handler = lambda func, arg: arg - (func(arg) - arg)
        >>> intercepts.register(increment, handler)
        >>> increment(43)
        42
    """
    if not isinstance(handler, types.FunctionType):
        raise ValueError("Argument `handler` must be a function.")
    if not callable(obj):
        raise TypeError("Cannot intercept non-callable objects")
    if obj == handler:
        raise ValueError("A function cannot handle itself")

    if isinstance(obj, types.BuiltinFunctionType):
        return register_builtin(obj, handler)
    elif isinstance(obj, types.FunctionType):
        return register_function(obj, handler)
    elif isinstance(obj, types.MethodType):
        return register_method(obj, handler)
    else:
        raise NotImplementedError("Unsupported type: {}".format(repr(type(obj))))


def unregister(obj: MethodOrFunction, depth: int = -1) -> MethodOrFunction:
    r"""Unregisters the handlers for an object.

    :param obj: The callable for which to unregister handlers.
    :param depth: (optional) The maximum number of handlers to unregister. Defaults to all.
    """
    # TODO : use an isinstance replacement
    if isinstance(obj, (types.BuiltinFunctionType, types.FunctionType)):
        func_addr = addr(obj)
    else:
        func_addr = addr(obj.__func__)
    handlers = _HANDLERS[func_addr]
    if depth < 0 or len(handlers) - depth <= 2:
        orig_func = handlers[0]
        if isinstance(orig_func, types.BuiltinFunctionType):
            replace_builtin(func_addr, addr(orig_func))
        elif isinstance(orig_func, types.FunctionType):
            replace_function(func_addr, addr(orig_func))
        else:
            raise ValueError("Unknown type of handled function: %s" % type(orig_func))
        del _HANDLERS[func_addr]
        assert func_addr not in _HANDLERS
    else:
        _HANDLERS[func_addr] = handlers[:-depth]
    return obj


@atexit.register
def unregister_all() -> None:
    r"""Unregisters all handlers.
    """
    global _HANDLERS
    for func_addr, handlers in _HANDLERS.items():
        orig_func = handlers[0]
        if isinstance(orig_func, types.BuiltinFunctionType):
            replace_builtin(func_addr, addr(orig_func))
        elif isinstance(orig_func, types.FunctionType):
            replace_function(func_addr, addr(orig_func))
        else:
            raise ValueError("Unknown type of handled function: %s" % type(orig_func))
    _HANDLERS = {}

