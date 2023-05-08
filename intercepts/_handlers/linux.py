from __future__ import annotations

import ctypes
import os
import typing
import platform

from .base import PyObject_Call_address

if platform.machine() == "aarch64" :
    INSTR_TEMPLATE = bytes.fromhex("c30000586000005860001fd61f2003d5aaaaaaaaaaaaaaaabbbbbbbbbbbbbbbb")
else :
    INSTR_TEMPLATE = bytes.fromhex("48bfaaaaaaaaaaaaaaaa48b8bbbbbbbbbbbbbbbbffe0")
_i = INSTR_TEMPLATE.index(b"\xbb" * 8)
INSTR_TEMPLATE = INSTR_TEMPLATE[:_i] + PyObject_Call_address + INSTR_TEMPLATE[_i + 8 :]

CDLL = ctypes.CDLL(ctypes.util.find_library("c"))
PAGESIZE = os.sysconf("SC_PAGE_SIZE")


def malloc(size: int) -> typing.Tuple[int, ctypes.Array[ctypes.c_char]]:
    pages = ctypes.create_string_buffer(PAGESIZE + size)
    page_aligned_addr = (ctypes.addressof(pages) + PAGESIZE - 1) & ~(PAGESIZE - 1)
    return page_aligned_addr, pages


def mprotect(addr, size):
    mprotect_result = CDLL.mprotect(
        ctypes.c_void_p(addr),
        ctypes.c_size_t(size),
        ctypes.c_int(0x01 | 0x02 | 0x04),
    )
    if mprotect_result:  # pragma: no cover
        # TODO(dlshriver): can we return more information?
        raise Exception("mprotect failed")


__all__ = ["malloc", "mprotect", "INSTR_TEMPLATE"]
