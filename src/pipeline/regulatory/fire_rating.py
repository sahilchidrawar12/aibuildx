"""Fire rating estimator stub — estimates required fire resistance based on occupancy/function."""
from typing import Dict, Any


def estimate_fire_rating(payload: Dict[str, Any]) -> Dict[str, Any]:
    occupancy = payload.get('occupancy', 'A')
    construction_type = payload.get('construction_type', 'II')
    # naive mapping
    base = 1  # hours
    if occupancy in ('A','E'):
        base = 2
    if construction_type in ('I', 'II'):
        base += 1
    return {'status': 'ok', 'required_fire_hours': base}


class FireRatingAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return estimate_fire_rating(payload)


__all__ = ['estimate_fire_rating', 'FireRatingAgent']
