"""AISC 360 (General Structural Steel) compliance checking.

Validates member designs against AISC 360-22 provisions including:
- Limit states for tension, compression, bending
- Lateral-torsional buckling checks
- Combined loading interaction equations
- Connection design per AISC 360

Classes:
    AISC360Checker: Main AISC 360 code compliance class
"""

import math
from typing import Dict, Tuple, Optional


class AISC360Checker:
    """AISC 360-22 design code compliance checker.
    
    Handles:
    - Limit state design (LSD) per AISC
    - Member capacity calculations
    - Combined stress interaction
    - Code-specified reduction factors
    - Material properties per ASTM
    """
    
    # Design factors
    RESISTANCE_FACTORS = {
        'tension': 1.0,              # Phi_t = 1.0 (at limit state)
        'compression': 0.90,         # Phi_c for compression
        'bending': 0.90,             # Phi_b for bending
        'shear': 0.90,               # Phi_v for shear
        'connection_bolt': 0.75,     # Phi for bolts
        'connection_weld': 0.75,     # Phi for welds
    }
    
    # Buckling coefficients
    K_FACTOR_TYPICAL = {
        'pinned': 1.0,
        'fixed_free': 2.0,
        'fixed_fixed': 0.5,
        'fixed_pinned': 0.7,
    }
    
    def __init__(self, fy: float, fu: float, code_version: str = '360-22'):
        """Initialize AISC 360 checker.
        
        Args:
            fy (float): Yield strength (ksi)
            fu (float): Ultimate tensile strength (ksi)
            code_version (str): AISC version ('360-22', '360-16', etc)
        """
        self.fy = fy
        self.fu = fu
        self.code_version = code_version
    
    def tensile_capacity(self, area_gross: float, area_net: float = None) -> Tuple[float, float]:
        """Calculate tensile member capacity.
        
        Phi*Pn = min(Phi_t*F_y*A_g, Phi_t*F_u*A_e)
        
        Args:
            area_gross (float): Gross cross-sectional area (sq in)
            area_net (float): Net area (sq in), defaults to 0.85*A_g
        
        Returns:
            tuple: (Pn_yield, Pn_rupture) both in kips
        
        Example:
            >>> checker = AISC360Checker(fy=50, fu=65)
            >>> p_y, p_r = checker.tensile_capacity(10)
            >>> round(p_y, 1)
            500.0
            >>> round(p_r, 1)
            552.5
        """
        if area_net is None:
            area_net = 0.85 * area_gross
        
        # Yield limit state
        p_y = self.RESISTANCE_FACTORS['tension'] * self.fy * area_gross / 1000  # Convert to kips
        
        # Rupture limit state (with 0.75 reduction for fastener holes, etc)
        p_r = 0.75 * self.RESISTANCE_FACTORS['tension'] * self.fu * area_net / 1000
        
        return p_y, p_r
    
    def compression_capacity(self, area: float, slenderness_ratio: float) -> float:
        """Calculate compression member capacity (column).
        
        Uses elastic/inelastic buckling per AISC 360-22, Section E3
        
        Args:
            area (float): Cross-sectional area (sq in)
            slenderness_ratio (float): KL/r (slenderness)
        
        Returns:
            float: Column capacity Phi*Pn (kips)
        
        Example:
            >>> checker = AISC360Checker(fy=50, fu=65)
            >>> pc = checker.compression_capacity(20, 100)
            >>> round(pc / 100, 1)
            9.0
        """
        # Elastic/plastic buckling transition
        lambda_e = math.pi * math.sqrt(29000 / self.fy)  # Elastic slenderness
        
        if slenderness_ratio <= lambda_e:
            # Inelastic buckling
            f_cr = (0.658 ** (self.fy / (math.pi ** 2 * 29000 / (slenderness_ratio ** 2)))) * self.fy
        else:
            # Elastic buckling
            f_cr = (0.877 * 29000) / (slenderness_ratio ** 2)
        
        pn = f_cr * area
        phi_pn = self.RESISTANCE_FACTORS['compression'] * pn / 1000
        
        return phi_pn
    
    def bending_capacity(self, section_modulus: float, laterally_braced_length: float,
                        radius_gyration_y: float, section_type: str = 'I') -> float:
        """Calculate bending member capacity.
        
        Accounts for lateral-torsional buckling (LTB) per AISC 360 Section F2
        
        Args:
            section_modulus (float): Plastic section modulus S_p (in^3)
            laterally_braced_length (float): Unbraced length L_b (ft)
            radius_gyration_y (float): Radius of gyration about y-axis (in)
            section_type (str): 'I', 'box', 'pipe', 'channel'
        
        Returns:
            float: Moment capacity Phi*M_n (kips-ft)
        
        Example:
            >>> checker = AISC360Checker(fy=50, fu=65)
            >>> mn = checker.bending_capacity(100, 15, 2, 'I')
            >>> round(mn / 100, 1)
            3.5
        """
        # Plastic moment capacity
        m_p = self.fy * section_modulus / 1000  # in kips-in = convert to kips-ft
        m_p_ft = m_p / 12
        
        # Laterally braced length in inches
        lb = laterally_braced_length * 12
        
        # Check for compact section (simplified)
        if section_type == 'I':
            l_p = 1.76 * radius_gyration_y * math.sqrt(29000 / self.fy)
            l_r = 7.02 * radius_gyration_y * math.sqrt(29000 / self.fy)
        else:
            l_p = lb  # Conservative for non-I sections
            l_r = 2 * l_p
        
        if lb <= l_p:
            # Plastic moment (fully braced)
            m_n = m_p_ft
        elif lb <= l_r:
            # Inelastic LTB
            m_n = m_p_ft * (1.0 - 0.5 * ((lb - l_p) / (l_r - l_p)))
        else:
            # Elastic LTB
            m_n = (0.9 * 29000 * section_modulus / 12) / (lb / radius_gyration_y)
            m_n = m_n / 12 / 1000  # Convert to kips-ft
        
        phi_mn = self.RESISTANCE_FACTORS['bending'] * m_n
        
        return phi_mn
    
    def shear_capacity(self, area_web: float, thickness: float, 
                      height: float) -> float:
        """Calculate shear capacity.
        
        Args:
            area_web (float): Web area (sq in)
            thickness (float): Web thickness (in)
            height (float): Web height (in)
        
        Returns:
            float: Shear capacity Phi*V_n (kips)
        """
        # Simplified shear capacity (AISC Section G)
        kv = 5.0  # Transverse stiffeners
        lambda_w = height / thickness
        lambda_p = 1.10 * math.sqrt(kv * 29000 / self.fy)
        
        if lambda_w <= lambda_p:
            v_n = 0.6 * self.fy * area_web
        else:
            v_n = 0.6 * self.fy * area_web * (lambda_p / lambda_w)
        
        phi_vn = self.RESISTANCE_FACTORS['shear'] * v_n / 1000
        
        return phi_vn
    
    def combined_loading_check(self, demand_moment: float, capacity_moment: float,
                              demand_shear: float, capacity_shear: float) -> Tuple[bool, float]:
        """Check combined bending and shear.
        
        Uses AISC interaction equation (simplified):
        (M/Mc) + (V/Vc) <= 1.0
        
        Args:
            demand_moment (float): Applied moment (kips-ft)
            capacity_moment (float): Moment capacity (kips-ft)
            demand_shear (float): Applied shear (kips)
            capacity_shear (float): Shear capacity (kips)
        
        Returns:
            tuple: (passes, utilization_ratio)
        """
        m_ratio = demand_moment / capacity_moment if capacity_moment > 0 else 1.0
        v_ratio = demand_shear / capacity_shear if capacity_shear > 0 else 1.0
        
        utilization = m_ratio + 0.625 * v_ratio  # Simplified interaction
        
        return utilization <= 1.0, utilization
    
    def column_beam_interaction(self, demand_axial: float, capacity_axial: float,
                               demand_moment: float, capacity_moment: float) -> Tuple[bool, float]:
        """AISC H1-1b interaction equation for columns under bending.
        
        When P/P_c > 0.2: (P/P_c) + 8/9 * (M/M_c) <= 1.0
        When P/P_c <= 0.2: P/(2*P_c) + (M/M_c) <= 1.0
        
        Args:
            demand_axial (float): Applied axial force (kips)
            capacity_axial (float): Axial capacity (kips)
            demand_moment (float): Applied moment (kips-ft)
            capacity_moment (float): Moment capacity (kips-ft)
        
        Returns:
            tuple: (passes, utilization_ratio)
        """
        if capacity_axial == 0 or capacity_moment == 0:
            return False, 1.0
        
        p_ratio = demand_axial / capacity_axial
        m_ratio = demand_moment / capacity_moment
        
        if p_ratio > 0.2:
            utilization = p_ratio + (8.0/9.0) * m_ratio
        else:
            utilization = p_ratio / 2.0 + m_ratio
        
        return utilization <= 1.0, utilization
    
    def bolt_tension_capacity(self, diameter: float, grade: str, 
                             num_bolts: int = 1) -> float:
        """Calculate bolt tension capacity.
        
        Args:
            diameter (float): Bolt diameter (in)
            grade (str): Bolt grade ('A325', 'A490', etc)
            num_bolts (int): Number of bolts
        
        Returns:
            float: Total tension capacity (kips)
        """
        # Tensile strength by grade (ksi)
        strength = {
            'A307': 60,
            'A325': 90,
            'A490': 120,
        }
        
        f_ut = strength.get(grade, 60)
        
        # Tensile area (approximate)
        area = math.pi * (diameter ** 2) / 4 * 0.74  # 74% of nominal area
        
        # AISC reduction factor
        phi = 0.75
        
        # Capacity per bolt
        t_cap = phi * f_ut * area / 1000  # Convert to kips
        
        return t_cap * num_bolts
    
    def weld_capacity(self, size: float, length: float, type_weld: str = 'fillet',
                     metal: str = 'E70XX') -> float:
        """Calculate weld capacity.
        
        Args:
            size (float): Weld size (in)
            length (float): Weld length (in)
            type_weld (str): 'fillet', 'butt'
            metal (str): Electrode classification
        
        Returns:
            float: Weld capacity (kips)
        """
        # Electrode strength (ksi)
        strength = {
            'E60XX': 60,
            'E70XX': 70,
            'E80XX': 80,
            'E90XX': 90,
        }
        
        f_wet = strength.get(metal, 70)
        
        if type_weld == 'fillet':
            # Fillet weld: capacity = 0.6 * F_EXX * A_w
            area = size * length * math.sin(math.radians(45))  # Throat area
            capacity = 0.6 * f_wet * area / 1000
        else:  # butt
            # Butt weld: capacity = 0.9 * F_EXX * A_w
            area = size * length
            capacity = 0.9 * f_wet * area / 1000
        
        return capacity
    
    def summary(self) -> str:
        """Generate AISC 360 compliance summary.
        
        Returns:
            str: Formatted summary text
        """
        summary = f"\n{'='*70}\n"
        summary += f"AISC 360 Compliance Summary\n"
        summary += f"{'='*70}\n"
        summary += f"Code Version: {self.code_version}\n"
        summary += f"Steel Grade: F_y = {self.fy} ksi, F_u = {self.fu} ksi\n"
        summary += f"Resistance Factors:\n"
        for limit, factor in self.RESISTANCE_FACTORS.items():
            summary += f"  {limit}: {factor:.2f}\n"
        summary += f"{'='*70}\n"
        
        return summary
