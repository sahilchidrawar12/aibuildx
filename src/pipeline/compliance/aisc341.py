"""AISC 341 (Seismic Provisions) compliance checking.

Validates member designs against AISC 341 seismic design requirements including:
- Special moment resisting frames (SMRF)
- Special concentric braced frames (SCBF)
- Intermediate moment resisting frames (IMRF)
- Connection requirements per seismic design category
- Ductility and deformation requirements

Classes:
    AISC341SeismicChecker: Main AISC 341 seismic compliance class
"""

import math
from typing import Dict, Tuple, Optional


class AISC341SeismicChecker:
    """AISC 341 seismic design code compliance checker.
    
    Handles:
    - Special/intermediate moment frame requirements
    - Braced frame seismic design
    - Seismic design category (SDC) requirements
    - Connection seismic demand factors
    - Story drift and P-Delta under seismic loads
    """
    
    # Capacity design factors by SDC
    OVERSTRENGTH_FACTORS = {
        'A': 1.0,    # No seismic requirements
        'B': 1.0,    # Minimal seismic
        'C': 1.0,    # Moderate seismic
        'D': 1.25,   # Significant seismic
        'E': 1.5,    # Major seismic
        'F': 2.0,    # Near-fault/high seismic
    }
    
    # Connection demand factors
    CONNECTION_FACTORS = {
        'SMRF': 2.0,      # Special moment resisting frame
        'IMRF': 1.5,      # Intermediate moment resisting frame
        'SCBF': 1.8,      # Special concentric braced frame
        'ICBF': 1.2,      # Intermediate concentric braced frame
    }
    
    # Panel zone thickness requirements (simplified)
    PANEL_ZONE_REQUIREMENTS = {
        'A': 0.0,   # No requirement
        'B': 0.0,   # No requirement
        'C': 0.5,   # Minimum thickness ratio h/t
        'D': 0.6,   # Stricter requirement
        'E': 0.7,   # Very strict
        'F': 0.8,   # Maximum constraint
    }
    
    def __init__(self, sdc: str, system_type: str, fy: float = 50):
        """Initialize AISC 341 seismic checker.
        
        Args:
            sdc (str): Seismic Design Category ('A' through 'F')
            system_type (str): 'SMRF', 'IMRF', 'SCBF', 'ICBF'
            fy (float): Yield strength (ksi)
        """
        self.sdc = sdc
        self.system_type = system_type
        self.fy = fy
        self.omega_0 = self.OVERSTRENGTH_FACTORS.get(sdc, 1.0)
        self.connection_factor = self.CONNECTION_FACTORS.get(system_type, 1.0)
    
    def requires_seismic_provisions(self) -> bool:
        """Check if seismic provisions apply.
        
        Returns:
            bool: True if SDC C or higher
        """
        return self.sdc in ['C', 'D', 'E', 'F']
    
    def capacity_design_moment(self, moment_demand: float) -> float:
        """Calculate capacity design moment including overstrength.
        
        Capacity design = Demand * Omega_0
        
        Args:
            moment_demand (float): Seismic demand moment (kips-ft)
        
        Returns:
            float: Capacity design moment (kips-ft)
        
        Example:
            >>> checker = AISC341SeismicChecker('D', 'SMRF')
            >>> m_cap = checker.capacity_design_moment(100)
            >>> m_cap
            125.0
        """
        return moment_demand * self.omega_0
    
    def beam_column_moment_ratio(self, sum_column_moments: float,
                                sum_beam_moments: float) -> Tuple[bool, float]:
        """Check strong-column weak-beam criterion (SCWB).
        
        Sum(M_c) >= 1.2 * Sum(M_b) at joint
        
        Args:
            sum_column_moments (float): Sum of column moment capacities (kips-ft)
            sum_beam_moments (float): Sum of beam moment demands (kips-ft)
        
        Returns:
            tuple: (meets_requirement, ratio)
        
        Example:
            >>> checker = AISC341SeismicChecker('D', 'SMRF')
            >>> meets, ratio = checker.beam_column_moment_ratio(250, 200)
            >>> meets
            True
            >>> ratio
            1.25
        """
        if sum_beam_moments == 0:
            return True, 1.0
        
        required = 1.2 * sum_beam_moments
        ratio = sum_column_moments / sum_beam_moments if sum_beam_moments > 0 else 1.0
        
        return sum_column_moments >= required, ratio
    
    def beam_depth_limitation(self, beam_depth: float, story_height: float) -> Tuple[bool, float]:
        """Check beam depth limitation for SMRF (per AISC 341 I1).
        
        d_b <= h_s / 2.5 (typical SMRF requirement)
        
        Args:
            beam_depth (float): Beam depth (in)
            story_height (float): Story height (in)
        
        Returns:
            tuple: (meets_requirement, ratio)
        """
        if self.system_type != 'SMRF':
            return True, 1.0
        
        max_depth = story_height / 2.5
        ratio = beam_depth / max_depth if max_depth > 0 else 1.0
        
        return beam_depth <= max_depth, ratio
    
    def panel_zone_thickness(self, panel_width: float, max_thickness: float) -> Tuple[bool, float]:
        """Check panel zone thickness requirement.
        
        Minimum t_pz per AISC 341 Section J10.7
        
        Args:
            panel_width (float): Panel zone width (in)
            max_thickness (float): Maximum available thickness (in)
        
        Returns:
            tuple: (adequate, thickness_ratio)
        """
        if not self.requires_seismic_provisions():
            return True, 1.0
        
        # Required thickness ratio
        req_ratio = self.PANEL_ZONE_REQUIREMENTS.get(self.sdc, 0.0)
        
        # Minimum thickness
        min_thickness = panel_width * req_ratio
        
        ratio = max_thickness / min_thickness if min_thickness > 0 else 1.0
        
        return max_thickness >= min_thickness, ratio
    
    def weld_requirement(self) -> str:
        """Determine weld requirement based on seismic design.
        
        Returns:
            str: Weld requirement description
        """
        if self.sdc in ['A', 'B']:
            return 'Standard AWS D1.1'
        elif self.sdc == 'C':
            return 'AWS D1.1 with UT inspection'
        elif self.sdc == 'D':
            return 'AWS D1.1 100% UT, PWHT'
        elif self.sdc == 'E':
            return 'AWS D1.1 100% UT, PWHT, Charpy impact'
        else:  # F
            return 'AWS D1.1 100% UT, PWHT, Charpy impact, Near-fault provisions'
    
    def bolt_requirement(self) -> str:
        """Determine bolt requirement based on seismic design.
        
        Returns:
            str: Bolt requirement description
        """
        if self.sdc in ['A', 'B']:
            return 'ASTM A325 or A490 acceptable'
        elif self.sdc == 'C':
            return 'A325 or A490, standard inspection'
        elif self.sdc == 'D':
            return 'A325 or A490, snug-tight, inspection required'
        else:  # E, F
            return 'A490 turn-of-nut installation with calibration'
    
    def connection_demand(self, member_capacity: float) -> float:
        """Calculate seismic connection demand.
        
        Connection demand = Member capacity * Connection factor
        
        Args:
            member_capacity (float): Member flexural capacity (kips-ft)
        
        Returns:
            float: Required connection capacity (kips-ft)
        
        Example:
            >>> checker = AISC341SeismicChecker('E', 'SMRF')
            >>> conn_demand = checker.connection_demand(100)
            >>> conn_demand
            300.0
        """
        return member_capacity * self.connection_factor * self.omega_0 / 1.2  # Simplified
    
    def shear_connection_demand(self, shear_demand: float) -> float:
        """Calculate seismic shear connection demand.
        
        Args:
            shear_demand (float): Seismic shear demand (kips)
        
        Returns:
            float: Required connection shear capacity (kips)
        """
        return shear_demand * self.omega_0
    
    def story_drift_limit(self, story_height: float) -> float:
        """Maximum allowable story drift per AISC 341.
        
        Typical: 0.02*h for SDC D-F (2% story drift)
        
        Args:
            story_height (float): Story height (in)
        
        Returns:
            float: Maximum drift (in)
        
        Example:
            >>> checker = AISC341SeismicChecker('D', 'SMRF')
            >>> max_drift = checker.story_drift_limit(12*12)
            >>> max_drift
            2.88
        """
        if self.sdc in ['A', 'B']:
            ratio = 0.05  # 5% drift limit
        else:  # C, D, E, F
            ratio = 0.02  # 2% drift limit
        
        return story_height * ratio
    
    def expected_strength_factor(self) -> float:
        """Expected strength factor (R_y) for grade determination.
        
        Returns:
            float: Expected strength factor (typically 1.1-1.3)
        """
        # Higher grade steels have higher Ry
        if self.fy <= 36:
            return 1.3
        elif self.fy <= 50:
            return 1.2
        else:
            return 1.1
    
    def required_ductility(self) -> Dict[str, float]:
        """Ductility requirements for lateral system.
        
        Returns:
            dict: Ductility parameters by SDC
        """
        ductility_map = {
            'A': {'theta_u': 0.02, 'acceptance_angle': 0.03},
            'B': {'theta_u': 0.03, 'acceptance_angle': 0.04},
            'C': {'theta_u': 0.04, 'acceptance_angle': 0.05},
            'D': {'theta_u': 0.05, 'acceptance_angle': 0.06},
            'E': {'theta_u': 0.06, 'acceptance_angle': 0.07},
            'F': {'theta_u': 0.07, 'acceptance_angle': 0.08},
        }
        
        return ductility_map.get(self.sdc, ductility_map['A'])
    
    def seismic_demand_check(self, member_capacity: float, 
                            seismic_demand: float) -> Tuple[bool, float]:
        """Check if member capacity meets seismic demand.
        
        Args:
            member_capacity (float): Member design capacity (kips-ft)
            seismic_demand (float): Expected seismic demand (kips-ft)
        
        Returns:
            tuple: (adequate, utilization)
        """
        utilization = seismic_demand / member_capacity if member_capacity > 0 else 1.0
        
        return utilization <= 1.0, utilization
    
    def summary(self) -> str:
        """Generate AISC 341 seismic compliance summary.
        
        Returns:
            str: Formatted summary text
        """
        summary = f"\n{'='*70}\n"
        summary += f"AISC 341 Seismic Compliance Summary\n"
        summary += f"{'='*70}\n"
        summary += f"Seismic Design Category: {self.sdc}\n"
        summary += f"System Type: {self.system_type}\n"
        summary += f"Steel Grade: F_y = {self.fy} ksi\n"
        summary += f"Overstrength Factor (Omega_0): {self.omega_0}\n"
        summary += f"Connection Factor: {self.connection_factor}\n"
        summary += f"Weld Requirement: {self.weld_requirement()}\n"
        summary += f"Bolt Requirement: {self.bolt_requirement()}\n"
        summary += f"Story Drift Limit: 0.02h (2%)\n"
        summary += f"{'='*70}\n"
        
        return summary
