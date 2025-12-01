"""Very small spatial index for 2D points (grid bucketing).
Used for simple proximity queries in clash detection or spatial lookups.
"""
from typing import Tuple, List, Dict
from collections import defaultdict


class GridIndex:
    def __init__(self, cell_size: float = 1.0):
        self.cell_size = cell_size
        self._cells = defaultdict(list)

    def _cell_key(self, pt: Tuple[float, float]) -> Tuple[int, int]:
        return (int(pt[0] // self.cell_size), int(pt[1] // self.cell_size))

    def insert(self, id: str, pt: Tuple[float, float]):
        self._cells[self._cell_key(pt)].append((id, pt))

    def query_radius(self, pt: Tuple[float, float], radius: float) -> List[Tuple[str, Tuple[float, float]]]:
        kx, ky = self._cell_key(pt)
        r_cells = int(radius // self.cell_size) + 1
        out = []
        for dx in range(-r_cells, r_cells + 1):
            for dy in range(-r_cells, r_cells + 1):
                for item in self._cells.get((kx + dx, ky + dy), []):
                    out.append(item)
        return out


__all__ = ['GridIndex']
