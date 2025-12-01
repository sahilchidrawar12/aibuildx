"""Accessibility checker stub: verifies key dimensions and ramp slopes."""
from typing import Dict, Any


def check_accessibility(payload: Dict[str, Any]) -> Dict[str, Any]:
    ramp_slope = float(payload.get('ramp_slope', 0.05))
    door_clear_width = float(payload.get('door_clear_width_mm', 900))
    issues = []
    if ramp_slope > 0.08:
        issues.append('Ramp slope exceeds typical limit')
    if door_clear_width < 800:
        issues.append('Door clear width may be insufficient for accessibility')
    return {'status': 'ok', 'issues': issues}


class AccessibilityChecker:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return check_accessibility(payload)


__all__ = ['check_accessibility', 'AccessibilityChecker']
