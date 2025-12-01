"""Simple parallel map helper using ThreadPoolExecutor."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, Any


def parallel_map(fn: Callable[[Any], Any], items: Iterable[Any], max_workers: int = 4) -> List[Any]:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(fn, it): it for it in items}
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception:
                results.append(None)
    return results


__all__ = ['parallel_map']
