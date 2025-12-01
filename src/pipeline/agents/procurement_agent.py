"""Procurement agent: shortlist suppliers and simple ETA aggregation."""
from typing import Dict, Any, List


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    suppliers: List[Dict[str, Any]] = payload.get('suppliers', [])
    item = payload.get('item')
    # naive ranking by price + lead_time
    ranked = sorted(suppliers, key=lambda s: (s.get('price', 1e9), s.get('lead_days', 9999)))
    shortlist = ranked[:3]
    avg_lead = None
    if suppliers:
        avg_lead = sum(s.get('lead_days', 0) for s in suppliers) / len(suppliers)
    return {'status': 'ok', 'item': item, 'shortlist': shortlist, 'avg_lead_days': avg_lead}


class ProcurementAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
