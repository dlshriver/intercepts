import sys

if sys.platform.startswith("linux"):
    from .linux import WORD_SIZE, get_addr, replace_cfunction
else:  # pragma: no cover
    raise ImportError(f"Unfortunately {sys.platform} is not supported.")

__all__ = ["get_addr", "replace_cfunction", "WORD_SIZE"]
