"""Assembly agent: basic sequencing and manpower estimate."""
from typing import Dict, Any, List


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = payload.get('steps', [])
    total_hours = 0.0
    for s in steps:
        total_hours += float(s.get('hours', 0.0))
    crew_size = int(payload.get('crew_size', 2))
    days = total_hours / (8.0 * crew_size) if crew_size else None
    return {'status': 'ok', 'total_hours': total_hours, 'crew_size': crew_size, 'est_days': days}


class AssemblyAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
