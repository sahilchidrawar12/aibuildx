"""Section selector: choose a section by simple criteria from a catalog-like list."""
from typing import List, Dict, Any, Optional


def select_by_min_area(sections: List[Dict[str, Any]], min_area: float) -> Optional[Dict[str, Any]]:
    candidates = [s for s in sections if s.get('area', 0) >= min_area]
    if not candidates:
        return None
    return min(candidates, key=lambda s: s.get('area', float('inf')))


def select_by_min_weight(sections: List[Dict[str, Any]], max_weight: float) -> List[Dict[str, Any]]:
    return [s for s in sections if s.get('weight', float('inf')) <= max_weight]


__all__ = ['select_by_min_area', 'select_by_min_weight']
