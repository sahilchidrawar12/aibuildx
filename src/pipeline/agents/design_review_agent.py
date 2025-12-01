"""Design review agent: runs a few heuristic checks and returns remarks."""
from typing import Dict, Any, List


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[str] = []
    section = payload.get('section', {})
    material = payload.get('material', {})
    if section.get('area', 0) <= 0:
        checks.append('Invalid section area')
    if material.get('yield', 0) < 200:
        checks.append('Low yield material for this design')
    if payload.get('deflection_ratio', 0) > 0.02:
        checks.append('Deflection exceeds limit')
    if not checks:
        checks.append('Design checks passed')
    return {'status': 'ok', 'remarks': checks}


class DesignReviewAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
