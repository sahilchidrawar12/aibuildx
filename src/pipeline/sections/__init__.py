"""
Sections module init - provides access to all advanced section calculation classes.
Includes compound sections, web openings, torsional properties, and plastic analysis.
"""

from .compound_section import CompoundSectionBuilder
from .web_opening import WebOpeningHandler
from .torsional import TorsionalPropertyCalculator
from .plastic_analysis import PlasticAnalysisProperties

__all__ = [
    'CompoundSectionBuilder',
    'WebOpeningHandler',
    'TorsionalPropertyCalculator',
    'PlasticAnalysisProperties',
]
