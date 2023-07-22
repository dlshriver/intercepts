from __future__ import annotations

import ctypes
import os
import typing

CDLL = ctypes.CDLL(ctypes.util.find_library("c"))
PAGESIZE = os.sysconf("SC_PAGE_SIZE")


def malloc(size: int) -> typing.Tuple[int, ctypes.Array[ctypes.c_char]]:
    pages = ctypes.create_string_buffer(PAGESIZE + size)
    page_aligned_addr = (ctypes.addressof(pages) + PAGESIZE - 1) & ~(PAGESIZE - 1)
    return page_aligned_addr, pages


def mprotect(addr: int, size: int) -> None:
    mprotect_result = CDLL.mprotect(
        ctypes.c_void_p(addr),
        ctypes.c_size_t(size),
        ctypes.c_int(0x01 | 0x02 | 0x04),
    )
    if mprotect_result:  # pragma: no cover
        # TODO(dlshriver): can we return more information?
        raise Exception(f"mprotect failed: {mprotect_result}")


__all__ = ["malloc", "mprotect"]
