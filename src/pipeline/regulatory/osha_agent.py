"""OSHA compliance stub: basic checks for fall protection and PPE requirements."""
from typing import Dict, Any


def check_osha(payload: Dict[str, Any]) -> Dict[str, Any]:
    work_at_height = float(payload.get('work_at_height_m', 0.0))
    requires_fall_protection = work_at_height >= 1.8
    ppe_needed = []
    if requires_fall_protection:
        ppe_needed.append('fall_harness')
    if payload.get('hot_work'):
        ppe_needed.append('welding_shield')
    return {'status': 'ok', 'requires_fall_protection': requires_fall_protection, 'ppe': ppe_needed}


class OSHAAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return check_osha(payload)


__all__ = ['check_osha', 'OSHAAgent']
