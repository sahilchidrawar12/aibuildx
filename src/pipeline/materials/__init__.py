"""Materials module: databases and helper selectors.

Exports:
    MATERIAL_DATABASE (databases.py)
    MaterialSelector (material_selector.py)
    CoatingSpecifier (coating.py)
"""
from .databases import MATERIAL_DATABASE, BOLT_SPECIFICATIONS, BOLT_STRENGTH
from .material_selector import MaterialSelector
from .coating import CoatingSpecifier

__all__ = [
    'MATERIAL_DATABASE',
    'BOLT_SPECIFICATIONS',
    'BOLT_STRENGTH',
    'MaterialSelector',
    'CoatingSpecifier',
]
