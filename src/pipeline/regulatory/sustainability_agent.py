"""Sustainability agent: combines embodied carbon and simple reuse scoring into a single metric."""
from typing import Dict, Any


def assess(payload: Dict[str, Any]) -> Dict[str, Any]:
    carbon = float(payload.get('kgCO2e', 0.0))
    reuse_score = float(payload.get('reuse_score', 0.5))
    # simple normalized score: lower is better for carbon, higher is better for reuse
    score = max(0.0, min(1.0, (1.0 - min(carbon / 10000.0, 1.0)) * 0.6 + reuse_score * 0.4))
    return {'status': 'ok', 'sustainability_score': score}


class SustainabilityAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return assess(payload)


__all__ = ['assess', 'SustainabilityAgent']
