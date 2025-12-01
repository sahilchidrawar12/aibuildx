"""Cost agent: simple cost estimate aggregator."""
from typing import Dict, Any, List


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = payload.get('items', [])
    total_cost = 0.0
    for it in items:
        unit = float(it.get('unit_cost', 0.0))
        qty = float(it.get('qty', 1.0))
        total_cost += unit * qty
    return {'status': 'ok', 'total_cost': total_cost}


class CostAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
