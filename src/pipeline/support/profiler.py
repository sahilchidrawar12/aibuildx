"""Tiny profiler context manager for quick timing measurements."""
import time
from contextlib import contextmanager


def timeit(label: str):
    class _Timer:
        def __enter__(self):
            self._t = time.perf_counter()
            return self
        def __exit__(self, exc_type, exc, tb):
            elapsed = time.perf_counter() - self._t
            print(f"[PROFILE] {label}: {elapsed:.6f}s")
    return _Timer()


__all__ = ['timeit']
