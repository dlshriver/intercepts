from __future__ import annotations

import ctypes
import ctypes.util
import mmap
import typing

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

KERNEL32.VirtualFree.argtypes = [
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_uint32,
]
KERNEL32.VirtualFree.restype = ctypes.c_bool

PAGESIZE = mmap.PAGESIZE
MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
MEM_RELEASE = 0x00008000
PAGE_EXECUTE_READ = 0x20
PAGE_READWRITE = 0x04


def malloc(size: int) -> typing.Tuple[int, typing.Callable[[], int]]:
    page_aligned_addr = KERNEL32.VirtualAlloc(
        None, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
    )
    dealloc = lambda _addr=page_aligned_addr: KERNEL32.VirtualFree(
        _addr, 0, MEM_RELEASE
    )
    return page_aligned_addr, dealloc


def mprotect(addr: int, size: int) -> None:
    dummy = ctypes.create_string_buffer(ctypes.sizeof(ctypes.c_size_t))
    _result = KERNEL32.VirtualProtect(
        addr, size, PAGE_EXECUTE_READ, ctypes.addressof(dummy)
    )
    if not _result:  # pragma: no cover
        # TODO(dlshriver): can we return more information?
        raise Exception("VirtualProtect failed")


__all__ = ["malloc", "mprotect"]
