"""Small optimizer stub that picks a connection from candidates minimizing cost while meeting capacity."""
from typing import Dict, List, Any


def pick_best(candidates: List[Dict[str, Any]], demand: float) -> Dict[str, Any]:
    best = None
    for c in candidates:
        cap = float(c.get('capacity', 0))
        cost = float(c.get('cost', 1e9))
        if cap >= demand:
            if best is None or cost < best.get('cost', 1e9):
                best = c
    return best or {'status': 'none'}


__all__ = ['pick_best']
