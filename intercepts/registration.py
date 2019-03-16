"""
intercepts.registration
~~~~~~~~~~~~~~~~~~~~~~~

This module implements the intercepts registration api.
"""

import sys
import types
import uuid
from typing import Callable, Dict, Tuple, Union

from .utils import create_code_like, get_handler_id

MethodOrFunction = Union[types.FunctionType, types.MethodType]

_INTERCEPTORS = (
    {}
)  # type: Dict[uuid.UUID, Tuple[MethodOrFunction, Callable, MethodOrFunction]]


class _MethodInterceptor:
    def __init__(self, method, handler, handler_id):
        self.method = method
        self.handler = handler
        self.handler_id = handler_id

    @property
    def interceptor(self):
        def method_interceptor(*args, **kwargs):
            _method, _handler, _ = globals()["_INTERCEPTORS"][self.handler_id]
            _method = types.FunctionType(
                _method.__func__.__code__,
                sys.modules[_method.__module__].__dict__,
                argdefs=_method.__defaults__,
                closure=_method.__closure__,
            )
            result = _handler(_method, *args, **kwargs)
            return result

        method_interceptor.handler_id = self.handler_id
        method_interceptor.__name__ = self.method.__func__.__name__
        return method_interceptor


def _intercept_handler(*args, **kwargs):
    sys = globals()["sys"]
    code = sys._getframe(0).f_code
    _handler_id = code.co_consts[-1]
    _func, _handler, _ = globals()["~INTERCEPTORS"][_handler_id]
    result = _handler(_func, *args, **kwargs)
    return result


def register_function(func: types.FunctionType, handler: Callable) -> None:
    r"""Registers an intercept handler for a function.

    :param func: The function to intercept.
    :param handler: A function to handle the intercept.
    """
    handler_id = uuid.uuid4()

    global_dict = func.__globals__
    global_dict["~INTERCEPTORS"] = _INTERCEPTORS
    if "sys" not in global_dict:
        global_dict["sys"] = sys.modules["sys"]
    orig_func = types.FunctionType(
        func.__code__, global_dict, func.__name__, func.__defaults__, func.__closure__
    )

    handler_code = create_code_like(
        _intercept_handler.__code__,
        consts=(_intercept_handler.__code__.co_consts + ("~intercept~", handler_id)),
        filename=func.__code__.co_filename,
        name=func.__code__.co_name,
        freevars=func.__code__.co_freevars,
    )
    func.__code__ = handler_code

    _INTERCEPTORS[handler_id] = (orig_func, handler, func)


def register_method(method: types.MethodType, handler: Callable) -> None:
    r"""Registers an intercept handler for a method.

    :param method: The method to intercept.
    :param handler: A function to handle the intercept.
    """
    handler_id = uuid.uuid4()

    intercepted_method = types.MethodType(
        _MethodInterceptor(method, handler, handler_id).interceptor, method.__self__
    )
    setattr(method.__self__, method.__func__.__name__, intercepted_method)
    _INTERCEPTORS[handler_id] = (method, handler, intercepted_method)


def register(obj: MethodOrFunction, handler: Callable) -> None:
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
    if not callable(obj):
        raise TypeError("Cannot intercept non-callable objects")
    elif obj == handler:
        raise ValueError("A function cannot handle itself")
    elif isinstance(obj, types.FunctionType):
        register_function(obj, handler)
    elif isinstance(obj, types.MethodType):
        register_method(obj, handler)
    else:
        raise NotImplementedError("Unsupported type: {}".format(repr(type(obj))))


def unregister(obj: MethodOrFunction, depth: int = -1) -> None:
    r"""Unregisters the handlers for an object.

    :param obj: The callable for which to unregister handlers.
    :param depth: (optional) The maximum number of handlers to unregister. Defaults to all.
    """
    if not callable(obj):
        raise TypeError("Cannot intercept non-callable objects")
    elif not isinstance(obj, types.FunctionType) and not isinstance(
        obj, types.MethodType
    ):
        raise NotImplementedError("Unsupported type: {}".format(repr(type(obj))))

    handler_id = get_handler_id(obj)
    while handler_id in _INTERCEPTORS and depth != 0:
        orig, _, _ = _INTERCEPTORS[handler_id]
        if isinstance(obj, types.FunctionType):
            assert isinstance(orig, types.FunctionType)
            obj.__code__ = orig.__code__
        elif isinstance(obj, types.MethodType):
            assert isinstance(orig, types.MethodType)
            setattr(orig.__self__, orig.__func__.__name__, orig)
        else:
            raise ValueError("Unexpected type %s" % type(obj))
        del _INTERCEPTORS[handler_id]
        handler_id = get_handler_id(orig)
        depth -= 1


def unregister_all() -> None:
    r"""Unregisters all handlers.
    """
    for _, _, obj in list(_INTERCEPTORS.values()):
        unregister(obj)
    assert len(_INTERCEPTORS) == 0

