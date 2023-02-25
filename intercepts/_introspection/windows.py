from __future__ import annotations

import ctypes
import ctypes.util
import mmap
import os
import struct
import sys

# TODO(dlshriver) ensure that the system is what we expect it to be

INSTRUCTIONS = bytes.fromhex("48b9aaaaaaaaaaaaaaaa48b8bbbbbbbbbbbbbbbb48ffe0")

(PyObject_Call_address,) = struct.unpack(
    "N", ctypes.string_at(ctypes.addressof(ctypes.pythonapi.PyObject_Call), 8)
)
PAGESIZE = mmap.PAGESIZE
PTR_SIZE = ctypes.sizeof(ctypes.c_size_t)
MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_READWRITE = 0x04
KERNEL32 = ctypes.cdll.kernel32
KERNEL32.VirtualAlloc.argtypes = [
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_uint32,
    ctypes.c_uint32,
]
KERNEL32.VirtualAlloc.restype = ctypes.c_void_p
KERNEL32.VirtualProtect.argtypes = [
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_uint32,
    ctypes.c_void_p,
]
KERNEL32.VirtualProtect.restype = ctypes.c_bool

_id_bytes = ctypes.string_at(id(id), 8 * PTR_SIZE)
_id = ctypes.cast(
    _id_bytes,
    ctypes.py_object,
).value


def get_addr(obj):
    return _id(obj)


def replace_cfunction(obj, handler):
    instr_len = len(INSTRUCTIONS)
    obj_addr = _id(obj)
    (obj_method_def_addr,) = struct.unpack(
        "N",
        ctypes.string_at(obj_addr + 2 * PTR_SIZE, 1 * PTR_SIZE),
    )

    # build function byte string
    instr = INSTRUCTIONS
    instr = (
        instr[: instr.index(b"\xaa" * 8)]
        + struct.pack("N", id(handler))
        + instr[instr.index(b"\xaa" * 8) + 8 :]
    )
    instr = (
        instr[: instr.index(b"\xbb" * 8)]
        + struct.pack("N", PyObject_Call_address)
        + instr[instr.index(b"\xbb" * 8) + 8 :]
    )

    # allocate pages
    page_aligned_addr = KERNEL32.VirtualAlloc(
        None, PAGESIZE, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
    )
    ctypes.memmove(page_aligned_addr, instr, len(instr))

    # change memory protection
    dummy = ctypes.create_string_buffer(PTR_SIZE)
    _result = KERNEL32.VirtualProtect(
        page_aligned_addr, instr_len, PAGE_EXECUTE_READ, ctypes.addressof(dummy)
    )
    if not _result:  # pragma: no cover
        # TODO(dlshriver): can we return more information?
        raise Exception("VirtualProtect failed")

    # create replacement MethodDef
    obj_method_def = ctypes.string_at(obj_method_def_addr, 4 * PTR_SIZE)
    method_def_words = list(struct.unpack("NNNN", obj_method_def))
    method_def_words[1] = page_aligned_addr
    method_def_words[2] = 3
    handler_method_def = struct.pack("NNNN", *method_def_words)
    handler_method_def_addr = struct.pack("N", _id(handler_method_def) + 4 * PTR_SIZE)

    # set method def
    ctypes.memmove(obj_addr + 2 * PTR_SIZE, handler_method_def_addr, PTR_SIZE)
    # set vector call
    ctypes.memset(obj_addr + 6 * PTR_SIZE, 0, PTR_SIZE)

    return instr, handler_method_def
