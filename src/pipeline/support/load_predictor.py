"""Simple load predictor stub — estimates loads from geometry/usage heuristics."""
from typing import Dict, Any


def predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    area = float(payload.get('area', 1.0))
    use_factor = float(payload.get('use_factor', 1.0))
    basic_load = area * 2.5
    est = basic_load * use_factor
    return {'estimated_load': est}


__all__ = ['predict']
