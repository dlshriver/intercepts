from __future__ import annotations

import dis
import sys
import types
import typing

_PYTHON_VERSION = sys.version_info[:2]


def replace_load_global(code: types.CodeType, name: str, value: typing.Any):
    if name not in code.co_names:
        return code
    _co_code = code.co_code
    if value not in code.co_consts:
        _co_consts = code.co_consts + (value,)
    _const_index = _co_consts.index(value)
    _name_index = code.co_names.index(name)
    load_const = [dis.opmap["LOAD_CONST"], _const_index]
    if _PYTHON_VERSION < (3, 11):
        _co_code = _co_code.replace(
            bytes([dis.opmap["LOAD_GLOBAL"], _name_index]),
            bytes(load_const),
        )
    else:
        # CPython 3.11 has 5 CACHE ops after LOAD_GLOBAL
        # CPython 3.12 has 4 CACHE ops after LOAD_GLOBAL
        _cache_len = 5 if _PYTHON_VERSION <= (3, 11) else 4
        _co_code = _co_code.replace(
            bytes(
                [
                    dis.opmap["LOAD_GLOBAL"],
                    (_name_index << 1),
                    *([dis.opmap["CACHE"], 0] * _cache_len),
                ]
            ),
            # Need the NOPs to prevent segfaults with coveragepy and pytest
            bytes(load_const + [dis.opmap["NOP"], 0] * _cache_len),
        ).replace(
            bytes(
                [
                    dis.opmap["LOAD_GLOBAL"],
                    (_name_index << 1) + 1,
                    *([dis.opmap["CACHE"], 0] * _cache_len),
                ]
            ),
            # Need the NOPs to prevent segfaults with coveragepy and pytest
            bytes(
                [dis.opmap["PUSH_NULL"], 0]
                + load_const
                + [dis.opmap["NOP"], 0] * (_cache_len - 1)
            ),
        )
    if _PYTHON_VERSION < (3, 8):
        return types.CodeType(
            code.co_argcount,
            code.co_kwonlyargcount,
            code.co_nlocals,
            code.co_stacksize,
            code.co_flags,
            _co_code,
            _co_consts,
            code.co_names,
            code.co_varnames,
            code.co_filename,
            code.co_name,
            code.co_firstlineno,
            code.co_lnotab,
            code.co_freevars,
            code.co_cellvars,
        )
    return code.replace(co_code=_co_code, co_consts=_co_consts)
