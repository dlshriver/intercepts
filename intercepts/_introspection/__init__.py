import sys

if sys.platform.startswith("linux"):
    from .linux import PTR_SIZE, get_addr, replace_cfunction
elif sys.platform.startswith("win32"):
    from .windows import PTR_SIZE, get_addr, replace_cfunction
else:  # pragma: no cover
    raise ImportError(f"Unfortunately {sys.platform} is not supported.")

__all__ = ["get_addr", "replace_cfunction", "PTR_SIZE"]
