"""
intercepts.utils
~~~~~~~~~~~~~~~~

A collection of utilities for patching python code.
"""

import types
import uuid

from typing import cast, Any, Optional, Tuple, Union


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


def get_handler_id(
    obj: Union[types.FunctionType, types.MethodType]
) -> Optional[uuid.UUID]:
    if isinstance(obj, types.FunctionType):
        consts = obj.__code__.co_consts
        if len(consts) < 2 or consts[-2] != "~intercept~":
            return None
        return consts[-1]
    elif isinstance(obj, types.MethodType):
        if hasattr(obj, "handler_id"):
            return cast(Any, obj).handler_id
        return None
    else:
        raise TypeError("Unsupported handler type: %s" % type(obj))
