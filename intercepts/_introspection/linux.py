from __future__ import annotations

import ctypes
import ctypes.util
import os
import struct
import sys

# TODO(dlshriver) clean this up so we're not littering the module's name space

with open(sys.executable, "rb") as f:
    _python_exe_bytes = f.read()
if _python_exe_bytes[:0x04] != b"\x7fELF":  # pragma: no cover
    raise ValueError("python is not an ELF")
if _python_exe_bytes[0x04] != 0x02:  # pragma: no cover
    raise NotImplementedError("We only support 64-bit for now.")
if [None, "little", "big"][
    _python_exe_bytes[0x05]
] != sys.byteorder:  # pragma: no cover
    # TODO(dlshriver): can we deal with this?
    raise ValueError("System and executable endianness do not match.")
if _python_exe_bytes[0x12:0x14] == b"\x3E\x00":
    # TODO(dlshriver): automate instruction generation to avoid having to update by hand
    INSTRUCTIONS = b"\x48\x83\xec\x38\x48\x89\x7c\x24\x18\x48\x89\x74\x24\x10\x48\x89\x54\x24\x08\x48\x8b\x54\x24\x08\x48\x8b\x44\x24\x10\x48\xb9\xbb\xbb\xbb\xbb\xbb\xbb\xbb\xbb\x48\x89\xc6\x48\xbf\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xff\xd1\x48\x89\x44\x24\x28\x48\x8b\x44\x24\x28\x48\x83\xc4\x38\xc3"
else:  # pragma: no cover
    raise NotImplementedError("We only support AMD x86-64 for now.")

(PyObject_Call_address,) = struct.unpack(
    "N", ctypes.string_at(ctypes.addressof(ctypes.pythonapi.PyObject_Call), 8)
)
CDLL = ctypes.CDLL(ctypes.util.find_library("c"))
PAGESIZE = os.sysconf("SC_PAGE_SIZE")
PTR_SIZE = ctypes.sizeof(ctypes.c_size_t)

_id_bytes = ctypes.string_at(id(id), 8 * PTR_SIZE)
_id = ctypes.cast(
    _id_bytes,
    ctypes.py_object,
).value


def get_addr(obj):
    return _id(obj)


def replace_cfunction(obj, handler):
    instr_len = len(INSTRUCTIONS)
    instr_addr = _id(INSTRUCTIONS) + 4 * PTR_SIZE
    obj_addr = _id(obj)
    (obj_method_def_addr,) = struct.unpack(
        "N",
        ctypes.string_at(obj_addr + 2 * PTR_SIZE, 1 * PTR_SIZE),
    )

    # allocate pages
    pages = ctypes.create_string_buffer(PAGESIZE * 2)
    page_aligned_addr = (ctypes.addressof(pages) + PAGESIZE - 1) & ~(PAGESIZE - 1)
    ctypes.memmove(page_aligned_addr, instr_addr, instr_len)
    handler_addr = ctypes.create_string_buffer(struct.pack("N", _id(handler)))
    ctypes.memmove(
        page_aligned_addr + INSTRUCTIONS.index(b"\xaa" * PTR_SIZE),
        handler_addr,
        PTR_SIZE,
    )
    addr = page_aligned_addr + INSTRUCTIONS.index(b"\xbb" * PTR_SIZE)
    addr_bytes = struct.pack("N", PyObject_Call_address)
    ctypes.memmove(addr, addr_bytes, PTR_SIZE)

    # change memory protection
    mprotect_result = CDLL.mprotect(
        ctypes.c_void_p(page_aligned_addr),
        ctypes.c_size_t(PAGESIZE),
        ctypes.c_int(0x01 | 0x02 | 0x04),
    )
    if mprotect_result:  # pragma: no cover
        # TODO(dlshriver): can we return more information?
        raise Exception("mprotect failed")

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

    return pages, handler_method_def
