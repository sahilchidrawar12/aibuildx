"""Material selection helpers for structural members.

Provides a small MaterialSelector that uses the material database to choose
appropriate steel grades based on target yield, ductility, and fabrication
requirements.

Class:
    MaterialSelector: Choose suitable material grades for sections
"""
from typing import Dict, List, Optional, Tuple

from src.pipeline.materials.databases import MATERIAL_DATABASE


class MaterialSelector:
    """Selects materials from `MATERIAL_DATABASE` based on simple criteria.

    Example:
        selector = MaterialSelector()
        choices = selector.select_by_min_yield(min_fy=50)
        best = selector.select_best_tradeoff(max_price_per_kg=1.2)
    """

    def __init__(self, material_db: Dict[str, Dict] = None):
        self.material_db = material_db or MATERIAL_DATABASE

    def select_by_min_yield(self, min_fy: float) -> List[Tuple[str, Dict]]:
        """Return list of materials with yield >= `min_fy` (ksi).

        Args:
            min_fy: Minimum yield strength in ksi

        Returns:
            List of tuples (grade_name, properties)
        """
        results = []
        for name, props in self.material_db.items():
            if props.get('fy', 0) >= min_fy:
                results.append((name, props))
        return sorted(results, key=lambda x: x[1].get('fy', 0))

    def select_best_tradeoff(self, max_price_per_kg: float = 2.0,
                             prefer_high_ductility: bool = False) -> Optional[Tuple[str, Dict]]:
        """Pick a material with price <= max and best ductility/yield tradeoff.

        Returns the single best grade or None if none match.
        """
        candidates = []
        for name, props in self.material_db.items():
            price = props.get('price_per_kg', float('inf'))
            if price <= max_price_per_kg:
                score = props.get('fy', 0)
                if prefer_high_ductility:
                    score *= props.get('ductility', 1.0)
                candidates.append((score, name, props))

        if not candidates:
            return None

        # choose highest score
        candidates.sort(reverse=True)
        _, name, props = candidates[0]
        return name, props

    def get_material(self, grade_name: str) -> Optional[Dict]:
        """Return properties for a material grade or None if not found."""
        return self.material_db.get(grade_name)

    def recommend_material_for_section(self, section_area_in2: float,
                                       required_fy: float = 50.0,
                                       max_price_per_kg: float = 2.0) -> Optional[Dict]:
        """Recommend a material grade for a section based on area and requirements.

        Heuristic: prefer grades that meet yield, within price, and with higher
        ductility for slender sections.
        """
        candidates = []
        for name, props in self.material_db.items():
            if props.get('fy', 0) < required_fy:
                continue
            price = props.get('price_per_kg', float('inf'))
            if price > max_price_per_kg:
                continue
            duct = props.get('ductility', 1.0)
            # small sections benefit from higher ductility
            score = props.get('fy', 0) * (1.0 + 0.5 * (duct - 1.0))
            candidates.append((score, name, props))

        if not candidates:
            return None
        candidates.sort(reverse=True)
        return {'grade': candidates[0][1], **candidates[0][2]}
