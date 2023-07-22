from __future__ import annotations

import ctypes
import ctypes.util
import platform
import struct
import types
import typing

PTR_SIZE = ctypes.sizeof(ctypes.c_size_t)
PyObject_Call_address: typing.Final[bytes] = ctypes.string_at(
    ctypes.addressof(ctypes.pythonapi.PyObject_Call), 8
)

_INSTRS_aarch64: typing.Final[bytes] = bytes.fromhex(
    "0800009009000090001140f9230d40f960001fd61f2003d5bbbbbbbbbbbbbbbbaaaaaaaaaaaaaaaa"
)
_INSTR_x86_64: typing.Final[bytes] = bytes.fromhex(
    "488b0509000000488b3d0a000000ffe0bbbbbbbbbbbbbbbbaaaaaaaaaaaaaaaa"
)
INSTR_TEMPLATES: typing.Final[typing.Dict[str, bytes]] = {
    "aarch64": _INSTRS_aarch64,
    "x86_64": _INSTR_x86_64,
    "amd64": _INSTR_x86_64,
}
_instr_template = INSTR_TEMPLATES[platform.machine().lower()]
_i = _instr_template.index(b"\xbb" * 8)
INSTR_TEMPLATE: typing.Final[bytes] = (
    _instr_template[:_i] + PyObject_Call_address + _instr_template[_i + 8 :]
)

_id_bytes = ctypes.string_at(id(id), 8 * PTR_SIZE)
get_addr: typing.Callable[[object], int] = ctypes.cast(
    typing.cast(ctypes._SimpleCData, _id_bytes),
    ctypes.py_object,
).value


def replace_cfunction_base(
    obj: types.BuiltinFunctionType,
    handler: typing.Callable,
    malloc: typing.Callable[[int], typing.Tuple[int, ctypes.Array[ctypes.c_char]]],
    mprotect: typing.Callable[[int, int], None],
    instr_template: bytes = INSTR_TEMPLATE,
) -> typing.Tuple[typing.Any, bytes]:
    instr_len = len(instr_template)
    obj_addr = get_addr(obj)
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
    handler_method_def_addr = struct.pack(
        "N", get_addr(handler_method_def) + 4 * PTR_SIZE
    )

    # set method def
    ctypes.memmove(obj_addr + 2 * PTR_SIZE, handler_method_def_addr, PTR_SIZE)
    # set vector call
    ctypes.memset(obj_addr + 6 * PTR_SIZE, 0, PTR_SIZE)

    return mem, handler_method_def


__all__ = [
    "get_addr",
    "replace_cfunction",
    "INSTR_TEMPLATE",
    "INSTR_TEMPLATES",
    "PTR_SIZE",
]
