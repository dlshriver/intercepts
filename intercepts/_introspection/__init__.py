import sys

if sys.platform.startswith("linux"):
    from .linux import get_addr, replace_cfunction, WORD_SIZE
else:  # pragma: no cover
    raise ImportError(f"Unfortunately {sys.platform} is not supported.")

__all__ = ["get_addr", "replace_cfunction", "WORD_SIZE"]
