"""Coating recommendations for corrosion protection and durability.

Provides a simple CoatingSpecifier to recommend paint or galvanizing systems
based on environment exposure, desired service life, and maintenance plan.
"""
from typing import Dict, Optional

COATING_DATABASE = {
    'galvanized': {
        'description': 'Hot-dip galvanized (HDG) coating',
        'expected_life_years': 25,
        'suitable_for': ['outdoor', 'marine', 'industrial', 'rural'],
        'cost_multiplier': 1.3,
    },
    'zinc_rich_primer': {
        'description': 'Zinc-rich primer with topcoat',
        'expected_life_years': 15,
        'suitable_for': ['outdoor', 'industrial', 'urban'],
        'cost_multiplier': 1.1,
    },
    'epoxy_mastic': {
        'description': 'Epoxy mastic system',
        'expected_life_years': 20,
        'suitable_for': ['marine', 'industrial'],
        'cost_multiplier': 1.4,
    },
    'alkyd_topcoat': {
        'description': 'Alkyd topcoat (decorative)',
        'expected_life_years': 8,
        'suitable_for': ['indoor', 'urban'],
        'cost_multiplier': 1.0,
    },
}


class CoatingSpecifier:
    """Recommend coatings based on environment and desired service life."""

    def __init__(self, coating_db: Dict[str, Dict] = None):
        self.coating_db = coating_db or COATING_DATABASE

    def recommend(self, environment: str = 'outdoor', desired_years: int = 20,
                  allow_galvanizing: bool = True) -> Optional[Dict]:
        """Return the best matching coating spec or None.

        Args:
            environment: One of 'outdoor', 'indoor', 'marine', 'industrial', 'urban', 'rural'
            desired_years: Desired service life (years)
            allow_galvanizing: Whether HDG is acceptable
        """
        candidates = []
        for name, props in self.coating_db.items():
            if environment not in props.get('suitable_for', []):
                continue
            if name == 'galvanized' and not allow_galvanizing:
                continue
            score = props.get('expected_life_years', 0) - abs(props.get('expected_life_years', 0) - desired_years)
            candidates.append((score, name, props))

        if not candidates:
            return None
        candidates.sort(reverse=True)
        chosen = candidates[0]
        return {'name': chosen[1], **chosen[2]}

    def list_options(self) -> Dict[str, Dict]:
        """Return available coating options."""
        return self.coating_db

    def cost_estimate(self, area_sqft: float, coating_name: str) -> float:
        """Simple cost estimate in arbitrary units.

        Formula: base_rate ($/ft^2) * area * cost_multiplier
        """
        base_rate = 0.5  # $/ft^2 baseline
        spec = self.coating_db.get(coating_name)
        if not spec:
            raise ValueError('Unknown coating')
        return base_rate * area_sqft * spec.get('cost_multiplier', 1.0)
