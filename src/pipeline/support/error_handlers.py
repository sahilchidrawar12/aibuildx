"""Basic error handling helpers for pipeline modules."""
from typing import Callable, Any, Tuple


def safe_call(fn: Callable[..., Any], *args, default: Any = None, **kwargs) -> Tuple[bool, Any]:
    try:
        return True, fn(*args, **kwargs)
    except Exception as e:
        return False, default


def raise_if_none(value: Any, msg: str = 'Unexpected None') -> Any:
    if value is None:
        raise ValueError(msg)
    return value


__all__ = ['safe_call', 'raise_if_none']
