'''
intercepts
~~~~~~~~~~

This module implements the intercepts api
'''

import sys
import types
import uuid
from collections import defaultdict
from functools import partial

FUNC_HANDLERS = {}
METHOD_HANDLERS = {}


def _clone_code(code, argcount=None, kwonlyargcount=None,
                nlocals=None, stacksize=None, flags=None,
                codestring=None, consts=None, names=None,
                varnames=None, filename=None, name=None,
                firstlineno=None, lnotab=None, freevars=None,
                cellvars=None):
    return types.CodeType(
        argcount or code.co_argcount,  # argcount: integer
        kwonlyargcount or code.co_kwonlyargcount,  # kwonlyargcount: integer
        nlocals or code.co_nlocals,  # nlocals: integer
        stacksize or code.co_stacksize,  # stacksize: integer
        flags or code.co_flags,  # flags: integer
        codestring or code.co_code,  # codestring: bytes
        consts or code.co_consts,  # consts: tuple
        names or code.co_names,  # names: tuple
        varnames or code.co_varnames,  # varnames: tuple
        filename or code.co_filename,  # filename: string
        name or code.co_name,  # name: string
        firstlineno or code.co_firstlineno,  # firstlineno: integer
        lnotab or code.co_lnotab,  # lnotab: bytes
        freevars or code.co_freevars,  # freevars: tuple
        cellvars or code.co_cellvars  # cellvars: tuple
    )


def _get_func_handler(func, handler):
    def intercept_handler(*args, **kwargs):
        import sys
        import intercepts
        code = sys._getframe(0).f_code
        _handler_id = code.co_consts[-1]
        _handler, _func, _, _ = intercepts.FUNC_HANDLERS[_handler_id]
        result = _handler(_func, *args, **kwargs)
        return result
    handler_id = uuid.uuid4()
    orig_func = types.FunctionType(
        func.__code__,
        sys.modules[func.__module__].__dict__,
        argdefs=func.__defaults__,
        closure=func.__closure__)
    new_handler_code = _clone_code(intercept_handler.__code__,
                                   consts=(intercept_handler.__code__
                                           .co_consts + (handler_id,)),
                                   filename=func.__code__.co_filename,
                                   name=func.__code__.co_name)
    FUNC_HANDLERS[handler_id] = (handler, orig_func,
                                 func, new_handler_code)
    return new_handler_code


def _get_method_handler(method, handler):
    def intercept_handler(*args, **kwargs):
        import sys
        import intercepts
        code = sys._getframe(0).f_code
        _handler_id = code.co_consts[-1]
        _handler, _func, _, _ = intercepts.METHOD_HANDLERS[_handler_id]
        result = _handler(_func, *args, **kwargs)
        return result
    handler_id = uuid.uuid4()
    orig_func = types.FunctionType(
        method.__func__.__code__,
        sys.modules[method.__module__].__dict__,
        argdefs=method.__defaults__,
        closure=method.__closure__)
    new_handler_code = _clone_code(intercept_handler.__code__,
                                   consts=(intercept_handler.__code__
                                           .co_consts + (handler_id,)),
                                   filename=method.__code__.co_filename,
                                   name=method.__code__.co_name)
    new_func = types.FunctionType(
        new_handler_code,
        sys.modules[method.__module__].__dict__,
        argdefs=method.__defaults__,
        closure=method.__closure__)
    new_method = types.MethodType(
        new_func,
        method.__self__
    )
    METHOD_HANDLERS[handler_id] = (handler, orig_func,
                                   types.MethodType(
                                       orig_func,
                                       method.__self__
                                   ), new_handler_code)
    return new_method


def register(obj, handler):
    r'''Registers an intercept handler.

    :param obj: The callable to intercept.
    :param handler: A function to handle the intercept.
    :return: None

    Usage::

        >>> import intercepts
        >>> increment = lambda x: x + 1
        >>> handler = lambda func, arg: arg - (func(arg) - arg)
        >>> intercepts.register(increment, handler)
        >>> increment(43)
        42
    '''
    if not callable(obj):
        raise TypeError('Cannot intercept non-callable objects')
    if obj == handler:
        raise ValueError('A function cannot handle itself')
    if isinstance(obj, types.FunctionType):
        obj.__code__ = _get_func_handler(obj, handler)
        return
    if isinstance(obj, types.MethodType):
        setattr(obj.__self__, obj.__func__.__name__,
                _get_method_handler(obj, handler))
        return
    raise NotImplementedError('Unsupported type: {}'
                              .format(repr(type(obj))))


def unregister(obj, depth=-1):
    r'''Unregisters the handlers for an object.

    :param obj: The callable for which unregister handlers.
    :param depth: (optional) The maximum number of handlers to unregister. Defaults to -1.
    :return: None
    '''
    if not callable(obj):
        raise TypeError('Cannot intercept non-callable objects')
    if isinstance(obj, types.FunctionType):
        num_handlers = len(FUNC_HANDLERS) + 1
        while len(FUNC_HANDLERS) < num_handlers and depth != 0:
            num_handlers = len(FUNC_HANDLERS)
            for handler_id, func_handler in list(FUNC_HANDLERS.items()):
                _, orig_func, handled_func, handler_code = func_handler
                if obj.__code__ == handler_code:
                    handled_func.__code__ = orig_func.__code__
                    del FUNC_HANDLERS[handler_id]
                    depth -= 1
                    break
        return
    if isinstance(obj, types.MethodType):
        num_handlers = len(METHOD_HANDLERS) + 1
        while len(METHOD_HANDLERS) < num_handlers and depth != 0:
            num_handlers = len(METHOD_HANDLERS)
            for handler_id, method_handler in list(METHOD_HANDLERS.items()):
                _, _, orig_method, handler_code = method_handler
                if obj.__func__.__code__ == handler_code:
                    obj.__func__.__code__ = orig_method.__func__.__code__
                    del METHOD_HANDLERS[handler_id]
                    depth -= 1
                    break
        return
    raise NotImplementedError('Unsupported type: {}'
                              .format(repr(type(obj))))


def unregister_all():
    r'''Unregisters all handlers.
    '''
    for _, _, func, _ in list(FUNC_HANDLERS.values()):
        unregister(func)
    for _, _, method, _ in list(METHOD_HANDLERS.values()):
        unregister(getattr(method.__self__,
                           method.__func__.__name__))
