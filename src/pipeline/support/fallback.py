"""Fallback helpers to attempt operations and supply defaults."""
from typing import Callable, Any


def fallback(default: Any, fn: Callable[..., Any], *args, **kwargs) -> Any:
    try:
        return fn(*args, **kwargs)
    except Exception:
        return default


__all__ = ['fallback']
