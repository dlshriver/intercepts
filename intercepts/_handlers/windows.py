from __future__ import annotations

import ctypes
import ctypes.util
import mmap
import typing

from .base import PyObject_Call_address

INSTR_TEMPLATE = bytes.fromhex("48b9aaaaaaaaaaaaaaaa48b8bbbbbbbbbbbbbbbb48ffe0")
_i = INSTR_TEMPLATE.index(b"\xbb" * 8)
INSTR_TEMPLATE = INSTR_TEMPLATE[:_i] + PyObject_Call_address + INSTR_TEMPLATE[_i + 8 :]

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

PAGESIZE = mmap.PAGESIZE
MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_EXECUTE_READ = 0x20
PAGE_READWRITE = 0x04


def malloc(size: int) -> typing.Tuple[int, ctypes.Array[ctypes.c_char]]:
    page_aligned_addr = KERNEL32.VirtualAlloc(
        None, PAGESIZE, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
    )
    page = (ctypes.c_char * PAGESIZE).from_address(page_aligned_addr)
    return page_aligned_addr, page


def mprotect(addr, size):
    dummy = ctypes.create_string_buffer(ctypes.sizeof(ctypes.c_size_t))
    _result = KERNEL32.VirtualProtect(
        addr, size, PAGE_EXECUTE_READ, ctypes.addressof(dummy)
    )
    if not _result:  # pragma: no cover
        # TODO(dlshriver): can we return more information?
        raise Exception("VirtualProtect failed")


__all__ = ["malloc", "mprotect", "INSTR_TEMPLATE"]
