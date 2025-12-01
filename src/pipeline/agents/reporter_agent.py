"""Reporter agent: collect simple stats and produce a small report dict."""
from typing import Dict, Any, List


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Accept the standardized pipeline output (full model) or simple items list
    items: List[Dict[str, Any]] = []
    if payload.get('items') is not None:
        items = payload.get('items')
    elif payload.get('members') is not None:
        items = payload.get('members')
    elif isinstance(payload.get('data'), dict) and payload['data'].get('members'):
        items = payload['data']['members']

    total = len(items)
    bom = []
    totals = {'weight_kg': 0.0, 'count': total}
    for it in items:
        sel = it.get('selection', {})
        weight = float(sel.get('weight_kg', 0.0) or 0.0)
        totals['weight_kg'] += weight
        bom.append({'id': it.get('id'), 'section': sel.get('section_name'), 'weight_kg': weight})

    return {'status': 'ok', 'bom': bom, 'totals': totals, 'members': items}


class ReporterAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
