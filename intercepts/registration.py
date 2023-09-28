"""
intercepts.registration
~~~~~~~~~~~~~~~~~~~~~~~

This module implements the intercepts registration api.
"""
from __future__ import annotations

import atexit
import ctypes
import struct
import sys
import types
from collections import defaultdict
from typing import Any, Callable, Type, TypeVar, cast

from ._handlers import PTR_SIZE, get_addr, replace_cfunction
from ._utils import replace_load_global

T = TypeVar("T")
_HANDLERS: dict[tuple[int, Type], list[tuple[Any, ...]]] = defaultdict(list)


def _check_intercept(obj, handler):
    if not isinstance(handler, types.FunctionType):
        raise ValueError("Argument `handler` must be a function.")
    if obj == handler:
        raise ValueError("A function cannot handle itself")


def register(obj: T, handler: Callable) -> T:
    r"""Registers an intercept handler.

    :param obj: The callable to intercept.
    :param handler: A function to handle the intercept.
    :returns: The intercepted callable.

    Usage::

        >>> import intercepts
        >>> increment = lambda x: x + 1
        >>> handler = lambda func, arg: arg - (func(arg) - arg)
        >>> intercepts.register(increment, handler)
        >>> increment(43)
        42
    """
    _register: dict[Type, Callable[[Any, types.FunctionType], Any]] = {
        types.BuiltinFunctionType: _register_builtin,
        types.FunctionType: _register_function,
        types.MethodType: _register_method,
    }
    obj_type = type(obj)
    if obj_type not in _register:
        raise NotImplementedError(f"Unsupported type: {obj_type}")
    _check_intercept(obj, handler)
    assert isinstance(handler, types.FunctionType)
    return _register[obj_type](obj, handler)


def _register_builtin(
    obj: types.BuiltinFunctionType, handler: types.FunctionType
) -> types.BuiltinFunctionType:
    obj_addr = get_addr(obj)
    _obj_bytes = ctypes.string_at(obj_addr, sys.getsizeof(obj))
    _obj = ctypes.cast(
        cast(ctypes._SimpleCData, _obj_bytes),
        ctypes.py_object,
    ).value

    globals_dict = handler.__globals__
    _code = replace_load_global(handler.__code__, "_", _obj)
    _handler = types.FunctionType(
        code=_code,
        globals=handler.__globals__,
        name=handler.__name__,
        argdefs=handler.__defaults__,
        closure=handler.__closure__,
    )

    refs = replace_cfunction(obj, _handler)
    _HANDLERS[obj_addr, type(obj)].append(
        (refs, (_handler, obj, _obj, handler, globals_dict), _obj_bytes)
    )

    # Need to increment reference count of _obj_bytes to avoid segfaults
    ctypes.memmove(
        get_addr(_obj_bytes),
        struct.pack(
            "N",
            struct.unpack("N", ctypes.string_at(get_addr(_obj_bytes), PTR_SIZE))[0] + 1,
        ),
        PTR_SIZE,
    )

    return obj


def _register_function(
    obj: types.FunctionType, handler: types.FunctionType
) -> types.FunctionType:
    _obj = types.FunctionType(
        code=obj.__code__,
        globals=obj.__globals__,
        name=obj.__name__,
        argdefs=obj.__defaults__,
        closure=obj.__closure__,
    )
    obj.__code__ = replace_load_global(handler.__code__, "_", _obj)

    _HANDLERS[get_addr(obj), type(obj)].append((obj, _obj))
    return obj


def _register_method(
    obj: types.MethodType, handler: types.FunctionType
) -> types.MethodType:
    _register_function(obj.__func__, handler)
    return obj


def unregister(obj: T, depth: int | None = None) -> T:
    r"""Unregisters the handlers for an object.

    :param obj: The callable for which to unregister handlers.
    :param depth: (optional) The maximum number of handlers to unregister. Defaults to all.
    :returns: The previously intercepted callable.
    """
    obj_type = type(obj)
    _unregister: dict[Type, Callable] = {
        types.BuiltinFunctionType: _unregister_builtin,
        types.FunctionType: _unregister_function,
        types.MethodType: _unregister_method,
    }
    if obj_type not in _unregister:
        raise NotImplementedError(f"Unsupported type: {obj_type}")
    _unregister[obj_type](obj, depth=depth)
    return obj


def _unregister_builtin_addr(addr: int, depth: int | None = None):
    handlers = _HANDLERS[addr, types.BuiltinFunctionType]
    if depth is None:
        depth = handlers.__len__()
    while handlers.__len__() and depth > 0:
        depth -= 1
        (_, dealloc), *_, _obj_bytes = handlers.pop()
        ctypes.memmove(
            addr + 2 * PTR_SIZE,
            _obj_bytes[2 * PTR_SIZE :],
            _obj_bytes.__len__() - 2 * PTR_SIZE,
        )
        dealloc()


def _unregister_builtin(obj: types.BuiltinFunctionType, depth: int | None = None):
    _unregister_builtin_addr(get_addr(obj), depth=depth)


def _unregister_function_addr(addr: int, depth: int | None = None):
    handlers = _HANDLERS[addr, types.FunctionType]
    if depth is None:
        depth = handlers.__len__()
    while handlers.__len__() and depth > 0:
        depth -= 1
        obj, _obj, *_ = handlers.pop()
        obj.__code__ = _obj.__code__


def _unregister_function(obj: types.FunctionType, depth: int | None = None):
    _unregister_function_addr(get_addr(obj), depth=depth)


def _unregister_method(obj: types.MethodType, depth: int | None = None):
    _unregister_function(obj.__func__, depth=depth)


@atexit.register
def unregister_all() -> None:
    r"""Unregisters all handlers."""
    _unregister: dict[Type, Callable] = {
        types.BuiltinFunctionType: _unregister_builtin_addr,
        types.FunctionType: _unregister_function_addr,
    }
    for addr, callable_type in _HANDLERS:
        _unregister[callable_type](addr)
    _HANDLERS.clear()
