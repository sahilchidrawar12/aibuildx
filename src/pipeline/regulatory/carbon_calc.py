"""Embodied carbon estimator (very small stub).
Estimates kgCO2e based on steel mass and concrete volume heuristics.
"""
from typing import Dict, Any


def estimate_embodied_carbon(payload: Dict[str, Any]) -> Dict[str, Any]:
    steel_mass = float(payload.get('steel_mass_kg', 0.0))
    conc_vol = float(payload.get('concrete_m3', 0.0))
    steel_factor = 1.85  # kgCO2e per kg steel (stub)
    conc_factor = 300.0  # kgCO2e per m3 concrete (stub)
    total = steel_mass * steel_factor + conc_vol * conc_factor
    return {'status': 'ok', 'kgCO2e': total}


class CarbonCalculator:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return estimate_embodied_carbon(payload)


__all__ = ['estimate_embodied_carbon', 'CarbonCalculator']
