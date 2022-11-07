from __future__ import annotations

import ctypes
import ctypes.util
import os
import struct
import sys

from ..utils import WORD_SIZE

# TODO(dlshriver) clean this up so we're not littering the module's name space

with open(sys.executable, "rb") as f:
    python_exe_bytes = f.read()
if python_exe_bytes[:0x04] != b"\x7fELF":  # pragma: no cover
    raise ValueError("python is not an ELF")
if python_exe_bytes[0x04] != 0x02:  # pragma: no cover
    raise NotImplementedError("We only support 64-bit for now.")
if [None, "little", "big"][python_exe_bytes[0x05]] != sys.byteorder:  # pragma: no cover
    # TODO(dlshriver): can we deal with this?
    raise ValueError("System and executable endianness do not match.")
if python_exe_bytes[0x05] != 1:  # pragma: no cover
    raise NotImplementedError("We only little endianness for now.")
if python_exe_bytes[0x12:0x14] == b"\x3E\x00":
    # TODO(dlshriver): automate instruction generation to avoid having to update by hand
    INSTRUCTIONS = b"\xf3\x0f\x1e\xfa\x48\x83\xec\x38\x48\x89\x7c\x24\x18\x48\x89\x74\x24\x10\x48\x89\x54\x24\x08\x48\x8b\x54\x24\x08\x48\x8b\x44\x24\x10\x48\x89\xc6\x48\xbf\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xb8\xbb\xbb\xbb\xbb\xff\xd0\x48\x89\x44\x24\x28\x48\x8b\x44\x24\x28\x48\x83\xc4\x38\xc3"
else:  # pragma: no cover
    raise NotImplementedError("We only support AMD x86-64 for now.")

section_header_table_offset = struct.unpack("L", python_exe_bytes[0x28:0x30])[0]
num_sections = struct.unpack("H", python_exe_bytes[0x3C:0x3E])[0]

PyObject_Call_address: str | None = None
for section_index in range(num_sections):
    section_type = struct.unpack(
        "I",
        python_exe_bytes[
            section_header_table_offset
            + 0x40 * section_index
            + 0x4 : section_header_table_offset
            + 0x40 * section_index
            + 0x4
            + 4
        ],
    )[0]
    if section_type == 0xB:
        section_link_index = struct.unpack(
            "I",
            python_exe_bytes[
                section_header_table_offset
                + 0x40 * section_index
                + 0x28 : section_header_table_offset
                + 0x40 * section_index
                + 0x28
                + 4
            ],
        )[0]
        section_link_type = struct.unpack(
            "I",
            python_exe_bytes[
                section_header_table_offset
                + 0x40 * section_link_index
                + 0x4 : section_header_table_offset
                + 0x40 * section_link_index
                + 0x4
                + 4
            ],
        )[0]
        if section_link_type != 0x3:  # pragma: no cover
            continue

        section_offset = struct.unpack(
            "L",
            python_exe_bytes[
                section_header_table_offset
                + 0x40 * section_index
                + 0x18 : section_header_table_offset
                + 0x40 * section_index
                + 0x18
                + 8
            ],
        )[0]
        section_size = struct.unpack(
            "L",
            python_exe_bytes[
                section_header_table_offset
                + 0x40 * section_index
                + 0x20 : section_header_table_offset
                + 0x40 * section_index
                + 0x20
                + 8
            ],
        )[0]
        section_link_offset = struct.unpack(
            "L",
            python_exe_bytes[
                section_header_table_offset
                + 0x40 * section_link_index
                + 0x18 : section_header_table_offset
                + 0x40 * section_link_index
                + 0x18
                + 8
            ],
        )[0]
        section_link_size = struct.unpack(
            "L",
            python_exe_bytes[
                section_header_table_offset
                + 0x40 * section_link_index
                + 0x20 : section_header_table_offset
                + 0x40 * section_link_index
                + 0x20
                + 8
            ],
        )[0]

        string_table = python_exe_bytes[
            section_link_offset : section_link_offset + section_link_size
        ]
        # TODO(dlshriver): use a variable instead of constant 24
        for i in range(section_size // 24):
            name_offset = struct.unpack(
                "I",
                python_exe_bytes[section_offset + i * 24 : section_offset + i * 24 + 4],
            )[0]
            name = string_table[
                name_offset : name_offset + string_table[name_offset:].index(b"\x00")
            ]
            PyObject_Call_address = struct.unpack(
                "L",
                python_exe_bytes[
                    section_offset + i * 24 + 8 : section_offset + i * 24 + 16
                ],
            )[0]
            if name == b"PyObject_Call":
                break
if PyObject_Call_address is None:  # pragma: no cover
    raise ValueError("Could not find symbol 'PyObject_Call'.")

CDLL = ctypes.CDLL(ctypes.util.find_library("c"))
pagesize = os.sysconf("SC_PAGE_SIZE")

_id_bytes = ctypes.string_at(id(id), 8 * WORD_SIZE)
_id = ctypes.cast(
    _id_bytes,
    ctypes.py_object,
).value


def get_addr(obj):
    return _id(obj)


def replace_cfunction(obj, handler):
    instr_len = len(INSTRUCTIONS)
    instr_addr = _id(INSTRUCTIONS) + 4 * WORD_SIZE
    obj_addr = _id(obj)
    obj_method_def_addr = struct.unpack(
        "L" * 1,
        ctypes.string_at(obj_addr + 2 * WORD_SIZE, 1 * WORD_SIZE),
    )[0]

    # allocate pages
    pages = ctypes.create_string_buffer(pagesize * 2)
    page_aligned_addr = (ctypes.addressof(pages) + pagesize - 1) & ~(pagesize - 1)
    ctypes.memmove(page_aligned_addr, instr_addr, instr_len)
    handler_addr_bytes = struct.pack("L", _id(handler))
    ctypes.memmove(
        page_aligned_addr + INSTRUCTIONS.index(b"\xaa" * 8),
        _id(handler_addr_bytes) + 4 * WORD_SIZE,
        WORD_SIZE,
    )
    addr = page_aligned_addr + INSTRUCTIONS.index(b"\xbb" * 4)
    addr_bytes = struct.pack("I", PyObject_Call_address)
    ctypes.memmove(addr, addr_bytes, 4)
    mprotect_result = CDLL.mprotect(
        ctypes.c_void_p(page_aligned_addr),
        ctypes.c_size_t(pagesize),
        ctypes.c_int(0x01 | 0x02 | 0x04),
    )
    if mprotect_result:  # pragma: no cover
        # TODO(dlshriver): can we return more information?
        raise Exception("mprotect failed")

    # create replacement MethodDef
    obj_method_def = ctypes.string_at(obj_method_def_addr, 4 * WORD_SIZE)
    method_def_words = list(struct.unpack("L" * 4, obj_method_def))
    method_def_words[1] = page_aligned_addr
    method_def_words[2] = 3
    handler_method_def = struct.pack("L" * 4, *method_def_words)
    handler_method_def_addr = struct.pack("L", _id(handler_method_def) + 4 * WORD_SIZE)

    # set method def
    ctypes.memmove(
        obj_addr + 2 * WORD_SIZE + 0 * WORD_SIZE, handler_method_def_addr, WORD_SIZE
    )
    # set vector call
    ctypes.memset(obj_addr + 2 * WORD_SIZE + 4 * WORD_SIZE, 0, WORD_SIZE)

    return pages, handler_method_def
