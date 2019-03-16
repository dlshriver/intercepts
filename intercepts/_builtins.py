"""
intercepts.builtins
"""
import builtins
import sys
import types

from functools import update_wrapper, wraps

TRUE_BUILTINS = globals()["__builtins__"].copy()
BUILTIN_DICT = globals()["__builtins__"]


def wrap_builtin(function):
    BUILTIN_DICT[function.__name__] = function
    update_wrapper(function, TRUE_BUILTINS[function.__name__])
    return function


@wrap_builtin
def globals():
    return sys.modules[sys._getframe(1).f_globals["__name__"]].__dict__


@wrap_builtin
def locals():
    return sys._getframe(1).f_locals


@wrap_builtin
def __import__(name, globals=None, locals=None, fromlist=(), level=0):
    return TRUE_BUILTINS["__import__"](name, globals, locals, fromlist, level)


def _replace_builtins():
    """Replaces all built-ins with interceptable functions.
    """
    builtins = globals()["__builtins__"]
    for name, builtin in sorted(builtins.items()):
        if isinstance(builtin, (types.BuiltinFunctionType, types.BuiltinMethodType)):

            def replace(name, builtin):
                @wraps(builtin)
                def builtin_replacement(*args, **kwargs):
                    return builtin(*args, **kwargs)

                return builtin_replacement

            builtins[name] = replace(name, builtin)


_replace_builtins()


__all__ = ["globals"]
