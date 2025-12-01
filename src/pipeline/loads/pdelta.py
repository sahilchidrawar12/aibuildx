"""P-Delta (second-order) analysis for columns and frames.

Calculates second-order effects of gravity loads on lateral deflections.
Includes P-delta moments, effective length factors, and stability checks
for columns under combined axial and bending loads.

Classes:
    PDeltaAnalyzer: Main P-Delta effect calculation class
"""

import math
from typing import Dict, Tuple, Optional


class PDeltaAnalyzer:
    """Analyzes P-Delta (second-order geometric) effects.
    
    Handles:
    - P-Delta amplification factors
    - Second-order moments
    - Effective length factor adjustment
    - Stability coefficient calculations (IBC/AISC)
    - Combined axial and flexural design checks
    """
    
    def __init__(self, first_order_drift: float = 0.0):
        """Initialize P-Delta analyzer.
        
        Args:
            first_order_drift (float): Initial first-order story drift (in)
        """
        self.first_order_drift = first_order_drift
        self.stability_index = 0.0
    
    def p_delta_moment(self, axial_load: float, deflection: float) -> float:
        """Calculate P-Delta moment (second-order effect).
        
        M_pd = P * Delta
        
        Args:
            axial_load (float): Axial load (lbs, positive compression)
            deflection (float): Lateral deflection (in)
        
        Returns:
            float: P-Delta moment (in-lbs)
        
        Example:
            >>> analyzer = PDeltaAnalyzer()
            >>> m_pd = analyzer.p_delta_moment(axial_load=500000, deflection=0.5)
            >>> round(m_pd / 1000, 1)
            250.0
        """
        m_pd = abs(axial_load * deflection)
        return m_pd
    
    def amplification_factor(self, first_order_moment: float, 
                            second_order_moment: float) -> float:
        """Calculate moment amplification factor.
        
        B_2 = M_2 / M_1 (typically 1.0 to 1.5)
        
        Args:
            first_order_moment (float): Primary moment (in-lbs)
            second_order_moment (float): P-Delta moment (in-lbs)
        
        Returns:
            float: Amplification factor B_2
        """
        if abs(first_order_moment) < 1e-6:
            return 1.0
        
        b_2 = 1.0 + (second_order_moment / first_order_moment)
        return max(b_2, 1.0)  # Always >= 1.0
    
    def stability_coefficient(self, total_gravity: float, story_height: float,
                             first_order_shear: float, 
                             first_order_drift: Optional[float] = None) -> float:
        """Calculate story stability coefficient (Theta).
        
        Theta = (P_total * Delta) / (V * h)
        
        Stability check: Theta <= 0.10 (typically)
        
        Args:
            total_gravity (float): Total gravity load for story (lbs)
            story_height (float): Story height (in)
            first_order_shear (float): Story shear (lbs)
            first_order_drift (float): Story drift (in)
        
        Returns:
            float: Stability coefficient Theta
        
        Example:
            >>> analyzer = PDeltaAnalyzer()
            >>> theta = analyzer.stability_coefficient(
            ...     total_gravity=2000000,
            ...     story_height=12*12,  # 12 ft
            ...     first_order_shear=150000,
            ...     first_order_drift=1.0
            ... )
            >>> round(theta, 3)
            0.111
        """
        if first_order_drift is None:
            first_order_drift = self.first_order_drift
        
        if first_order_shear == 0 or story_height == 0:
            return 0.0
        
        theta = (total_gravity * first_order_drift) / (first_order_shear * story_height)
        return theta
    
    def p_delta_amplification(self, theta: float, num_stories: int = 1) -> float:
        """Calculate P-Delta amplification for frame system.
        
        B_d = 1 / (1 - Theta)
        Applicable when Theta <= 0.10 (approximately)
        
        Args:
            theta (float): Stability coefficient
            num_stories (int): Number of stories (for cumulative effects)
        
        Returns:
            float: P-Delta amplification factor B_d
        
        Raises:
            ValueError: If theta >= 1.0 (instability)
        """
        cumulative_theta = theta * num_stories
        
        if cumulative_theta >= 1.0:
            raise ValueError(f"System is unstable: cumulative Theta = {cumulative_theta}")
        
        b_d = 1.0 / (1.0 - cumulative_theta)
        return b_d
    
    def effective_length_factor(self, k_initial: float, theta: float) -> float:
        """Adjust effective length factor for P-Delta effects.
        
        k_effective = k * sqrt(B_d)
        
        Args:
            k_initial (float): Initial effective length factor (typically 1.0-2.0)
            theta (float): Stability coefficient
        
        Returns:
            float: Adjusted effective length factor
        """
        try:
            b_d = self.p_delta_amplification(theta)
            k_eff = k_initial * math.sqrt(b_d)
            return k_eff
        except ValueError:
            return float('inf')  # Unstable
    
    def second_order_analysis(self, first_order_moments: Dict[str, float],
                             p_delta_moments: Dict[str, float]) -> Dict[str, float]:
        """Combine first and second-order moments.
        
        Args:
            first_order_moments (dict): {'story_1': M1, 'story_2': M2, ...}
            p_delta_moments (dict): {'story_1': M_pd1, 'story_2': M_pd2, ...}
        
        Returns:
            dict: Second-order moments {'story_1': M_total, ...}
        """
        second_order = {}
        for key in first_order_moments.keys():
            m1 = first_order_moments.get(key, 0)
            m_pd = p_delta_moments.get(key, 0)
            second_order[key] = m1 + m_pd
        
        return second_order
    
    def column_check(self, axial_force: float, moment: float,
                    bending_capacity: float, axial_capacity: float) -> Tuple[bool, float]:
        """Check column adequacy under combined loading.
        
        Uses AISC 360 interaction equation (simplified):
        P/Pc + M/Mc <= 1.0
        
        Args:
            axial_force (float): Axial force (lbs)
            moment (float): Total moment including P-Delta (in-lbs)
            bending_capacity (float): Moment capacity (in-lbs)
            axial_capacity (float): Axial capacity (lbs)
        
        Returns:
            tuple: (passes, utilization_ratio)
        """
        if axial_capacity == 0 or bending_capacity == 0:
            return False, 1.0
        
        p_ratio = axial_force / axial_capacity
        m_ratio = moment / bending_capacity
        
        # AISC interaction (simplified)
        utilization = p_ratio + m_ratio
        
        return utilization <= 1.0, utilization
    
    def sway_check(self, theta: float, threshold: float = 0.1) -> Tuple[bool, str]:
        """Check if story sway is acceptable.
        
        Args:
            theta (float): Stability coefficient
            threshold (float): Maximum acceptable Theta (default 0.1)
        
        Returns:
            tuple: (acceptable, message)
        """
        if theta <= threshold:
            return True, f"Sway check OK: Theta = {theta:.4f}"
        else:
            return False, f"Sway CRITICAL: Theta = {theta:.4f} > {threshold}"
    
    def drift_amplification(self, first_order_drift: float, theta: float) -> float:
        """Calculate amplified drift including P-Delta effects.
        
        Delta_amplified = Delta_1 * B_d
        
        Args:
            first_order_drift (float): First-order drift (in)
            theta (float): Stability coefficient
        
        Returns:
            float: Amplified drift (in)
        """
        try:
            b_d = self.p_delta_amplification(theta)
            amplified_drift = first_order_drift * b_d
            return amplified_drift
        except ValueError:
            return float('inf')
    
    def summary(self, theta: float, m1: float, m_pd: float) -> str:
        """Generate P-Delta analysis summary.
        
        Args:
            theta (float): Stability coefficient
            m1 (float): First-order moment (in-lbs)
            m_pd (float): P-Delta moment (in-lbs)
        
        Returns:
            str: Formatted summary text
        """
        try:
            b_d = self.p_delta_amplification(theta)
            sway_ok, sway_msg = self.sway_check(theta)
        except ValueError:
            b_d = float('inf')
            sway_ok = False
            sway_msg = "System UNSTABLE"
        
        m_total = m1 + m_pd
        summary = f"\n{'='*70}\n"
        summary += f"P-Delta Analysis Summary\n"
        summary += f"{'='*70}\n"
        summary += f"Stability Coefficient (Theta): {theta:.4f}\n"
        summary += f"Amplification Factor (B_d): {b_d:.4f}\n"
        summary += f"First-Order Moment: {m1:.0f} in-lbs\n"
        summary += f"P-Delta Moment: {m_pd:.0f} in-lbs\n"
        summary += f"Total Second-Order Moment: {m_total:.0f} in-lbs\n"
        summary += f"Sway Status: {sway_msg}\n"
        summary += f"{'='*70}\n"
        
        return summary
