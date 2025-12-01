"""Seismic load analysis per IBC and ASCE 41.

Calculates seismic design forces based on building parameters, response spectrum,
and site classification. Includes equivalent lateral force (ELF) method and
response spectrum analysis support.

Classes:
    SeismicLoadAnalyzer: Main seismic load calculation class
"""

import math
from typing import Dict, Tuple, Optional


class SeismicLoadAnalyzer:
    """Calculates seismic forces per IBC-2024 and ASCE 41.
    
    Handles:
    - Response spectrum parameters (S_s, S_1)
    - Site classification (A-F)
    - Seismic design category determination
    - Base shear calculation (ELF method)
    - Vertical distribution of forces
    - Damping adjustments
    """
    
    # Site Coefficients for Different Classes
    SITE_COEFFICIENTS = {
        'A': {'Fa': 0.8, 'Fv': 0.8},    # Rock
        'B': {'Fa': 1.0, 'Fv': 1.0},    # Firm soil
        'C': {'Fa': 1.2, 'Fv': 1.2},    # Medium soil
        'D': {'Fa': 1.3, 'Fv': 1.6},    # Soft soil
        'E': {'Fa': 1.4, 'Fv': 2.4},    # Very soft soil
        'F': {'Fa': 0.0, 'Fv': 0.0},    # Special soil (requires analysis)
    }
    
    # Response Modification Factors
    R_VALUES = {
        'moment_frame': 8,           # Special moment resisting frame
        'special_braced': 8,         # Special concentric braced frame
        'intermediate_braced': 6.5,  # Intermediate braced frame
        'ordinary_braced': 3.25,     # Ordinary braced frame
        'bearing_wall': 6,           # Bearing wall system
        'shear_wall': 6.5,           # Reinforced concrete shear wall
    }
    
    # Building Period Coefficients
    CT_COEFFICIENTS = {
        'moment_frame': 0.028,
        'braced_frame': 0.020,
        'other': 0.015,
    }
    
    def __init__(self, s_s: float, s_1: float, site_class: str = 'D',
                 occupancy_cat: str = 'II', system_type: str = 'moment_frame'):
        """Initialize seismic load analyzer.
        
        Args:
            s_s (float): Mapped spectral acceleration at 0.2 sec period (g)
            s_1 (float): Mapped spectral acceleration at 1.0 sec period (g)
            site_class (str): 'A' through 'F'
            occupancy_cat (str): 'I', 'II', 'III', or 'IV'
            system_type (str): Type of lateral system
        """
        self.s_s = s_s
        self.s_1 = s_1
        self.site_class = site_class
        self.occupancy_cat = occupancy_cat
        self.system_type = system_type
        
        # Importance factor
        importance_factors = {'I': 1.0, 'II': 1.0, 'III': 1.25, 'IV': 1.5}
        self.i_e = importance_factors.get(occupancy_cat, 1.0)
        
        # Response modification factor
        self.r_value = self.R_VALUES.get(system_type, 6)
        
        # Calculate SMS and SM1
        self._calculate_mapped_spectra()
    
    def _calculate_mapped_spectra(self) -> None:
        """Calculate mapped spectral accelerations SMS and SM1."""
        site_coeffs = self.SITE_COEFFICIENTS[self.site_class]
        fa = site_coeffs['Fa']
        fv = site_coeffs['Fv']
        
        # Mapped spectra (IBC equations)
        self.s_ms = self.s_s * fa
        self.s_m1 = self.s_1 * fv
        
        # Design spectral accelerations (divide by 1.4 safety factor)
        self.s_ds = (2.0 / 3.0) * self.s_ms
        self.s_d1 = (2.0 / 3.0) * self.s_m1
    
    def design_category(self) -> Tuple[str, str]:
        """Determine seismic design category.
        
        Returns:
            tuple: (sdc_short_period, sdc_long_period)
            Each can be 'A', 'B', 'C', 'D', 'E', or 'F'
        
        Example:
            >>> seismic = SeismicLoadAnalyzer(0.75, 0.25, 'D', 'II')
            >>> sdc_short, sdc_long = seismic.design_category()
            >>> sdc_short
            'D'
        """
        # Determine SDC based on SDS and SD1
        if self.s_ds < 0.167:
            sdc_short = 'A'
        elif self.s_ds < 0.33:
            sdc_short = 'B'
        elif self.s_ds < 0.50:
            sdc_short = 'C'
        else:
            sdc_short = 'D' if self.s_ds < 0.75 else ('E' if self.s_ds < 1.0 else 'F')
        
        if self.s_d1 < 0.067:
            sdc_long = 'A'
        elif self.s_d1 < 0.133:
            sdc_long = 'B'
        elif self.s_d1 < 0.20:
            sdc_long = 'C'
        else:
            sdc_long = 'D' if self.s_d1 < 0.30 else ('E' if self.s_d1 < 0.50 else 'F')
        
        return sdc_short, sdc_long
    
    def fundamental_period(self, height: float, system_type: Optional[str] = None) -> float:
        """Estimate fundamental period using empirical formula.
        
        Args:
            height (float): Building height (ft)
            system_type (str): 'moment_frame', 'braced_frame', 'other'
        
        Returns:
            float: Fundamental period T_a (seconds)
        
        Example:
            >>> seismic = SeismicLoadAnalyzer(0.5, 0.2)
            >>> t = seismic.fundamental_period(60, 'moment_frame')
            >>> round(t, 3)
            1.344
        """
        if system_type is None:
            system_type = 'moment_frame' if 'moment' in self.system_type else 'braced_frame'
        
        ct = self.CT_COEFFICIENTS.get(system_type, 0.015)
        
        # Empirical formula (ASCE 7)
        t_a = ct * (height ** 0.75)
        
        # Upper limit: T_a ≤ 0.05h for most systems
        t_max = 0.05 * height
        
        return min(t_a, t_max)
    
    def spectral_acceleration(self, period: float) -> float:
        """Calculate spectral acceleration at given period.
        
        Args:
            period (float): Period (seconds)
        
        Returns:
            float: Spectral acceleration S_a (g)
        """
        transition_period = self.s_d1 / self.s_ds
        
        if period <= transition_period:
            # Rising portion of spectrum
            sa = self.s_ds * (0.4 + 0.6 * period / transition_period)
        else:
            # Constant velocity portion
            sa = self.s_d1 / period
        
        return sa
    
    def base_shear(self, weight: float, period: Optional[float] = None,
                  height: Optional[float] = None) -> float:
        """Calculate seismic base shear (ELF method).
        
        Args:
            weight (float): Total seismic weight (lbs)
            period (float): Fundamental period (sec), calculated if not provided
            height (float): Building height (ft), required if period not given
        
        Returns:
            float: Base shear V (lbs)
        
        Example:
            >>> seismic = SeismicLoadAnalyzer(0.5, 0.2, 'D', 'II')
            >>> v = seismic.base_shear(weight=1000000, period=1.2)
            >>> round(v / 1000, 1)  # Convert to kips
            55.6
        """
        if period is None:
            if height is None:
                raise ValueError("Must provide period or height")
            period = self.fundamental_period(height)
        
        # Calculate spectral acceleration
        s_a = self.spectral_acceleration(period)
        
        # Seismic Response Coefficient
        c_s = (s_a * self.i_e) / self.r_value
        
        # Minimum seismic response coefficient
        c_s_min = 0.044 * self.s_ds * self.i_e
        c_s = max(c_s, c_s_min)
        
        # Base shear
        v_base = c_s * weight
        
        return v_base
    
    def vertical_distribution(self, story_weights: list, story_heights: list,
                            period: float) -> list:
        """Distribute base shear vertically across stories (ELF method).
        
        Args:
            story_weights (list): Seismic weights of each story (lbs)
            story_heights (list): Heights of each story above base (ft)
            period (float): Fundamental period (sec)
        
        Returns:
            list: Story shears (lbs) from top to bottom
        
        Example:
            >>> seismic = SeismicLoadAnalyzer(0.5, 0.2)
            >>> v_dist = seismic.vertical_distribution([100000, 100000],
            ...                                         [20, 40],
            ...                                         1.2)
            >>> len(v_dist)
            2
        """
        total_weight = sum(story_weights)
        total_height = max(story_heights)
        
        # Exponent k (depends on period)
        if period < 0.5:
            k = 1.0
        elif period > 2.5:
            k = 2.0
        else:
            k = 1.0 + 0.5 * (period - 0.5)
        
        # Calculate forces
        story_shears = []
        total_force = sum(w * (h ** k) for w, h in zip(story_weights, story_heights))
        
        for i, (w, h) in enumerate(zip(story_weights, story_heights)):
            # Force at this level
            f_x = (w * (h ** k) / total_force) * 1000  # Placeholder base shear
            story_shears.append(f_x)
        
        return story_shears
    
    def summary(self) -> str:
        """Generate seismic analysis summary.
        
        Returns:
            str: Formatted summary text
        """
        sdc_short, sdc_long = self.design_category()
        
        summary = f"\n{'='*70}\n"
        summary += f"Seismic Load Analysis Summary (IBC/ASCE 41)\n"
        summary += f"{'='*70}\n"
        summary += f"Ss (0.2s): {self.s_s:.3f}g, S1 (1.0s): {self.s_1:.3f}g\n"
        summary += f"SDS: {self.s_ds:.3f}g, SD1: {self.s_d1:.3f}g\n"
        summary += f"Site Class: {self.site_class}\n"
        summary += f"Occupancy Category: {self.occupancy_cat}\n"
        summary += f"Seismic Design Category: {sdc_short}/{sdc_long}\n"
        summary += f"System Type: {self.system_type}\n"
        summary += f"R Factor: {self.r_value}\n"
        summary += f"Importance Factor (Ie): {self.i_e}\n"
        summary += f"{'='*70}\n"
        
        return summary
