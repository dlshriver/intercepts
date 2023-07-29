from __future__ import annotations

import ctypes
import os
import typing

CDLL = ctypes.CDLL(ctypes.util.find_library("c"))
PAGESIZE = os.sysconf("SC_PAGE_SIZE")

CDLL.mmap.argtypes = [
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
]
CDLL.mmap.restype = ctypes.c_void_p

CDLL.munmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
CDLL.munmap.restype = ctypes.c_int

# From mman.h
PROT_READ = 0x01  # Page can be read.
PROT_WRITE = 0x02  # Page can be written.
PROT_EXEC = 0x04  # Page can be executed.

MAP_SHARED = 0x01  # Share changes.
MAP_ANONYMOUS = 0x20  # Not backed by a file.


def malloc(
    size: int,
) -> typing.Tuple[int, typing.Callable[[], int]]:
    page_aligned_addr = CDLL.mmap(
        None,
        size,
        PROT_READ | PROT_WRITE,
        MAP_SHARED | MAP_ANONYMOUS,
        0,
        0,
    )
    dealloc = lambda _addr=page_aligned_addr, _size=size: CDLL.munmap(_addr, _size)
    return page_aligned_addr, dealloc


def mprotect(addr: int, size: int) -> None:
    mprotect_result = CDLL.mprotect(
        ctypes.c_void_p(addr),
        ctypes.c_size_t(size),
        ctypes.c_int(PROT_READ | PROT_WRITE | PROT_EXEC),
    )
    if mprotect_result:  # pragma: no cover
        # TODO(dlshriver): can we return more information?
        raise Exception(f"mprotect failed: {mprotect_result}")


__all__ = ["malloc", "mprotect"]
