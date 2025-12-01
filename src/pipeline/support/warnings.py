"""Lightweight warnings utilities used across pipeline."""
from typing import Callable


def warn_once(message: str, _cache={'seen': set()}):
    if message not in _cache['seen']:
        print(f"[WARNING] {message}")
        _cache['seen'].add(message)


__all__ = ['warn_once']
