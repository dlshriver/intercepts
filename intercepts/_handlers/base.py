from __future__ import annotations

import ctypes
import ctypes.util
import struct
import types
import typing

PTR_SIZE = ctypes.sizeof(ctypes.c_size_t)
PyObject_Call_address = ctypes.string_at(
    ctypes.addressof(ctypes.pythonapi.PyObject_Call), 8
)

_id_bytes = ctypes.string_at(id(id), 8 * PTR_SIZE)
_id = ctypes.cast(
    typing.cast(ctypes._SimpleCData, _id_bytes),
    ctypes.py_object,
).value


def get_addr(obj):
    return _id(obj)


def replace_cfunction_base(
    obj: types.BuiltinFunctionType,
    handler: typing.Callable,
    instr_template: bytes,
    malloc: typing.Callable[[int], typing.Tuple[int, ctypes.Array[ctypes.c_char]]],
    mprotect: typing.Callable[[int, int], int],
) -> typing.Tuple[typing.Any, bytes]:
    instr_len = len(instr_template)
    obj_addr = _id(obj)
    (obj_method_def_addr,) = struct.unpack(
        "N",
        ctypes.string_at(obj_addr + 2 * PTR_SIZE, 1 * PTR_SIZE),
    )

    # build function byte string
    i = instr_template.index(b"\xaa" * 8)
    instr = instr_template[:i] + struct.pack("N", id(handler)) + instr_template[i + 8 :]

    # allocate memory
    addr, mem = malloc(instr_len)
    # write memory
    ctypes.memmove(addr, instr, instr_len)
    # change memory protection
    mprotect(addr, instr_len)

    # create replacement MethodDef
    obj_method_def = ctypes.string_at(obj_method_def_addr, 4 * PTR_SIZE)
    method_def_words = list(struct.unpack("NNNN", obj_method_def))
    method_def_words[1] = addr
    method_def_words[2] = 3
    handler_method_def = struct.pack("NNNN", *method_def_words)
    handler_method_def_addr = struct.pack("N", _id(handler_method_def) + 4 * PTR_SIZE)

    # set method def
    ctypes.memmove(obj_addr + 2 * PTR_SIZE, handler_method_def_addr, PTR_SIZE)
    # set vector call
    ctypes.memset(obj_addr + 6 * PTR_SIZE, 0, PTR_SIZE)

    return mem, handler_method_def


__all__ = ["get_addr", "replace_cfunction", "PTR_SIZE"]
