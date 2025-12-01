"""Compliance module for design code checking.

Provides design code verification and compliance checking for structural
members and connections according to AISC standards.

Classes:
    AISC360Checker: AISC 360 (General Structural Steel) compliance
    AISC341SeismicChecker: AISC 341 (Seismic Provisions) compliance

Import Examples:
    from src.pipeline.compliance import AISC360Checker
    from src.pipeline.compliance import AISC341SeismicChecker
    
    # General structural design
    checker = AISC360Checker(fy=50, fu=65)
    p_y, p_r = checker.tensile_capacity(10)  # Tensile capacity
    pc = checker.compression_capacity(20, 100)  # Column capacity
    
    # Seismic design
    seismic = AISC341SeismicChecker('D', 'SMRF')
    m_cap = seismic.capacity_design_moment(100)
    meets_scwb, ratio = seismic.beam_column_moment_ratio(250, 200)
"""

from .aisc360 import AISC360Checker
from .aisc341 import AISC341SeismicChecker

__all__ = [
    'AISC360Checker',
    'AISC341SeismicChecker',
]
