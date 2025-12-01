"""Simplified IBC checker stub.
Provides lightweight checks such as story height, occupancy, and basic load category checks.
"""
from typing import Dict, Any


def check_building(payload: Dict[str, Any]) -> Dict[str, Any]:
    stories = int(payload.get('stories', 1))
    occupancy = payload.get('occupancy', 'R')
    height = float(payload.get('height_m', stories * 3.0))
    issues = []
    if height > 75 and occupancy == 'R':
        issues.append('High-rise residential requires special provisions')
    if stories > 5 and occupancy in ('H', 'I'):
        issues.append('Provide additional egress for high occupancy')
    return {'status': 'ok', 'stories': stories, 'height_m': height, 'issues': issues}


class IBCChecker:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return check_building(payload)


__all__ = ['check_building', 'IBCChecker']
