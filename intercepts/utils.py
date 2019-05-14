"""
intercepts.utils
~~~~~~~~~~~~~~~~

A collection of utilities for patching python code.
"""
import atexit
import ctypes
import types

from typing import Optional, Tuple
from intercepts.builtinutils import addr, getattr_replacement, setattr_replacement


def create_code_like(
    code: types.CodeType,
    argcount: Optional[int] = None,
    kwonlyargcount: Optional[int] = None,
    nlocals: Optional[int] = None,
    stacksize: Optional[int] = None,
    flags: Optional[int] = None,
    codestring: Optional[bytes] = None,
    consts: Optional[Tuple] = None,
    names: Optional[Tuple[str]] = None,
    varnames: Optional[Tuple[str]] = None,
    filename: Optional[str] = None,
    name: Optional[str] = None,
    firstlineno: Optional[int] = None,
    lnotab: Optional[bytes] = None,
    freevars: Optional[Tuple] = None,
    cellvars: Optional[Tuple] = None,
) -> types.CodeType:
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
        cellvars or code.co_cellvars,  # cellvars: tuple
    )


def copy_builtin(dst, src):
    ctypes.memmove(dst, src, 48)


def replace_builtin(dst, src):
    ctypes.memmove(dst + 16, src + 16, 32)


def copy_function(dst, src):
    ctypes.memmove(dst, src, 14 * 8)


def replace_function(dst, src):
    for i in range(15):
        if i in [2, 3, 4, 5]:
            ctypes.memmove(dst + 8 * i, src + 8 * i, 8)


replace_builtin(addr(getattr_replacement), addr(getattr))
replace_builtin(addr(setattr_replacement), addr(setattr))

WRAPPER_ASSIGNMENTS = (
    "__module__",
    "__name__",
    "__qualname__",
    "__doc__",
    "__annotations__",
)
WRAPPER_UPDATES = ("__dict__",)


def update_wrapper(
    wrapper, wrapped, assigned=WRAPPER_ASSIGNMENTS, updated=WRAPPER_UPDATES
):
    """Update a wrapper function to look like the wrapped function
       wrapper is the function to be updated
       wrapped is the original function
       assigned is a tuple naming the attributes assigned directly
       from the wrapped function to the wrapper function (defaults to
       functools.WRAPPER_ASSIGNMENTS)
       updated is a tuple naming the attributes of the wrapper that
       are updated with the corresponding attribute from the wrapped
       function (defaults to functools.WRAPPER_UPDATES)
    """
    # this is copied from https://github.com/python/cpython/blob/master/Lib/functools.py
    # and modified to use our getattr and setattr copies
    import sys

    for attr in assigned:
        try:
            value = getattr_replacement(wrapped, attr)
        except AttributeError:
            pass
        else:
            setattr_replacement(wrapper, attr, value)
    for attr in updated:
        getattr_replacement(wrapper, attr).update(
            getattr_replacement(wrapped, attr, {})
        )
    wrapper.__wrapped__ = wrapped
    return wrapper


@atexit.register
def cleanup():
    pass
