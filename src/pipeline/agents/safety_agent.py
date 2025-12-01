"""Safety agent: computes simple safety index and recommendations."""
from typing import Dict, Any


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    load = float(payload.get('load', 1.0))
    capacity = float(payload.get('capacity', 1.0))
    margin = capacity - load
    safety_index = max(0.0, min(1.0, margin / (capacity if capacity else 1e-6)))
    recommendation = 'OK' if safety_index >= 0.2 else 'Review'
    return {'status': 'ok', 'safety_index': safety_index, 'recommendation': recommendation}


class SafetyAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
