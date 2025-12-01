"""Very small in-memory cache helper (dict wrapper)."""
from typing import Any, Optional


class SimpleCache:
    def __init__(self):
        self._d = {}

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._d.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._d[key] = value

    def clear(self) -> None:
        self._d.clear()


__all__ = ['SimpleCache']
