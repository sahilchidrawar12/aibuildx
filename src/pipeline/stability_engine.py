"""Stability and buckling checks (Euler, KL/r, P-Delta approximations)."""
from typing import Dict,Any
import math

def euler_buckling_capacity(E: float, I: float, K: float, L: float) -> float:
    # E in MPa, I in mm^4, L in mm; returns N
    if L<=0 or I<=0 or E<=0:
        return 0.0
    # convert E MPa to N/mm^2 implicitly
    return (math.pi**2 * E * I) / ((K*L)**2)

def klr(radius_gyration: float, L: float) -> float:
    if radius_gyration<=0:
        return float('inf')
    return L / radius_gyration

def p_delta_amplification(Mu: float, P: float, L: float, EI: float) -> float:
    # crude estimate of moment amplification factor 1/(1 - P/Pcr)
    Pcr = (math.pi**2 * EI) / (L**2)
    if Pcr<=0 or P >= Pcr:
        return float('inf')
    return 1.0 / (1.0 - (P / Pcr))
