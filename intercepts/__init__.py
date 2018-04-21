import sys
import types
import uuid
from collections import defaultdict
from functools import partial

FUNC_HANDLERS = {}


def register_func_handler(func, handler):
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
    handler_code = intercept_handler.__code__
    new_handler_code = types.CodeType(
        handler_code.co_argcount,  # argcount: integer
        handler_code.co_kwonlyargcount,  # kwonlyargcount: integer
        handler_code.co_nlocals,  # nlocals: integer
        handler_code.co_stacksize,  # stacksize: integer
        handler_code.co_flags,  # flags: integer
        handler_code.co_code,  # codestring: bytes
        handler_code.co_consts + (handler_id,),  # consts: tuple
        handler_code.co_names,  # names: tuple
        handler_code.co_varnames,  # varnames: tuple
        func.__code__.co_filename,  # filename: string
        func.__code__.co_name,  # name: string
        handler_code.co_firstlineno,  # firstlineno: integer
        handler_code.co_lnotab,  # lnotab: bytes
        handler_code.co_freevars,  # freevars: tuple
        handler_code.co_cellvars  # cellvars: tuple
    )
    FUNC_HANDLERS[handler_id] = (handler, orig_func,
                                 func, new_handler_code)
    return new_handler_code


def register(obj, handler):
    if not callable(obj):
        raise TypeError('Cannot intercept non-callable objects')
    if isinstance(obj, types.FunctionType):
        if obj == handler:
            raise ValueError('A function cannot handle itself')
        obj.__code__ = register_func_handler(obj, handler)
        return
    raise NotImplementedError('Unsupported type: {}'
                              .format(repr(type(obj))))


def unregister(func, depth=-1):
    num_handlers = len(FUNC_HANDLERS) + 1
    while len(FUNC_HANDLERS) < num_handlers and depth != 0:
        num_handlers = len(FUNC_HANDLERS)
        for handler_id, func_handler in list(FUNC_HANDLERS.items()):
            _, orig_func, handled_func, handler_code = func_handler
            if func.__code__ == handler_code:
                handled_func.__code__ = orig_func.__code__
                del FUNC_HANDLERS[handler_id]
                depth -= 1
                break


def unregister_all():
    for _, _, func, _ in list(FUNC_HANDLERS.values()):
        unregister(func)
