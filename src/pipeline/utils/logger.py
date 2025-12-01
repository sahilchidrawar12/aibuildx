"""Tiny logger helper that remains import-light for demos/tests."""
from typing import Callable, Any


def get_logger(prefix: str = 'pipeline') -> Callable[[str], None]:
    def _log(msg: str, /) -> None:
        print(f"[{prefix}] {msg}")
    return _log


__all__ = ['get_logger']
