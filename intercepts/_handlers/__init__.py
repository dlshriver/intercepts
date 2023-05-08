from __future__ import annotations

import platform
import sys
import types
import typing

from .base import PTR_SIZE, get_addr, replace_cfunction_base

if platform.machine() not in {"x86_64", "AMD64", "aarch64"}:  # pragma: no cover
    raise ImportError(f"Unfortunately {platform.machine()} is not currently supported.")
if sys.byteorder != "little":  # pragma: no cover
    raise ImportError(
        f"Unfortunately {sys.byteorder} endianness is not currently supported."
    )

if sys.platform.startswith("linux"):
    from .linux import *
elif sys.platform.startswith("win32"):
    from .windows import INSTR_TEMPLATE, malloc, mprotect
else:  # pragma: no cover
    raise ImportError(f"Unfortunately {sys.platform} is not currently supported.")


def replace_cfunction(
    obj: types.BuiltinFunctionType, handler: typing.Callable
) -> typing.Tuple[bytes, bytes]:
    return replace_cfunction_base(obj, handler, INSTR_TEMPLATE, malloc, mprotect)


__all__ = ["get_addr", "replace_cfunction", "PTR_SIZE"]
