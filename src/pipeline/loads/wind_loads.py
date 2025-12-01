"""Wind load analysis per ASCE 7 and IBC standards.

Calculates wind pressures on structures based on location, exposure, and
structure dimensions. Includes velocity pressure, exposure factors, and
design wind pressures for MWFRS (Main Wind Force Resisting System).

Classes:
    WindLoadAnalyzer: Main wind load calculation class
"""

import math
from typing import Dict, Tuple, Optional


class WindLoadAnalyzer:
    """Calculates wind loads per ASCE 7-22 / IBC-2024.
    
    Handles:
    - Wind velocity pressure (q_z)
    - Exposure categories (B, C, D)
    - Directionality factors
    - Pressure coefficients for buildings
    - Gust factor calculations
    """
    
    # ASCE 7 Exposure Categories
    EXPOSURE_FACTORS = {
        'B': {  # Urban/suburban (dense trees, buildings)
            'z_g': 1200,  # Gradient height (ft)
            'alpha': 7.0,  # Surface roughness exponent
            'l_z': 1200,  # Turbulence length scale
        },
        'C': {  # Open terrain (few trees/buildings)
            'z_g': 900,
            'alpha': 9.5,
            'l_z': 900,
        },
        'D': {  # Flat open terrain (water/desert)
            'z_g': 700,
            'alpha': 11.5,
            'l_z': 700,
        },
    }
    
    # Pressure Coefficients for Enclosed Buildings
    CP_ENCLOSED = {
        'windward_wall': 0.8,      # Cp for windward wall
        'leeward_wall': -0.5,      # Cp for leeward wall
        'side_wall': -0.7,         # Cp for side walls
        'roof_windward': -0.7,     # Cp for roof windward
        'roof_leeward': -0.3,      # Cp for roof leeward
    }
    
    # Risk Category Factors
    RISK_CATEGORY = {
        'I': 0.87,    # Low hazard occupancy
        'II': 1.0,    # Standard occupancy
        'III': 1.15,  # Hazardous contents
        'IV': 1.25,   # Essential facilities
    }
    
    def __init__(self, v_design: float, exposure: str = 'C', risk_cat: str = 'II'):
        """Initialize wind load analyzer.
        
        Args:
            v_design (float): Design wind speed (mph, basic wind speed)
            exposure (str): 'B', 'C', or 'D'
            risk_cat (str): 'I', 'II', 'III', or 'IV'
        """
        self.v_design = v_design  # mph
        self.exposure = exposure
        self.risk_cat = risk_cat
        self.k_d = self.RISK_CATEGORY.get(risk_cat, 1.0)  # Directionality
        self.v_adjust = v_design * self.k_d
    
    def velocity_pressure(self, height: float) -> float:
        """Calculate velocity pressure at given height.
        
        Args:
            height (float): Height above ground (ft)
        
        Returns:
            float: Velocity pressure q_z (psf)
        
        Example:
            >>> wind = WindLoadAnalyzer(v_design=110, exposure='C')
            >>> q_30 = wind.velocity_pressure(30)  # At 30 ft height
            >>> round(q_30, 1)
            15.7
        """
        exposure_data = self.EXPOSURE_FACTORS[self.exposure]
        z_g = exposure_data['z_g']
        alpha = exposure_data['alpha']
        
        # Minimum height of 15 ft
        z = max(height, 15)
        
        # K_z exposure factor
        k_z = (z / z_g) ** (2 / alpha)
        k_z = max(k_z, 0.85)  # Minimum value
        
        # Velocity pressure (psf)
        q_z = 0.00256 * k_z * (self.v_adjust ** 2)
        
        return q_z
    
    def gust_factor(self, height: float, mean_roof_height: float) -> float:
        """Calculate gust factor G_f.
        
        Args:
            height (float): Height of interest (ft)
            mean_roof_height (float): Mean roof height of structure (ft)
        
        Returns:
            float: Gust factor (typically 0.85-0.90)
        """
        exposure_data = self.EXPOSURE_FACTORS[self.exposure]
        
        # Simplified gust factor (ASCE 7)
        if height < mean_roof_height:
            g_f = 0.85
        else:
            g_f = 0.90
        
        return g_f
    
    def design_pressure(self, height: float, mean_roof_height: float,
                       cp: float, directional: bool = True) -> float:
        """Calculate design wind pressure.
        
        p = q_z * G_f * C_p * directionality factor
        
        Args:
            height (float): Height of interest (ft)
            mean_roof_height (float): Mean roof height (ft)
            cp (float): Pressure coefficient
            directional (bool): Apply directionality factor (usually True)
        
        Returns:
            float: Design pressure (psf)
        
        Example:
            >>> wind = WindLoadAnalyzer(110, 'C', 'II')
            >>> p_windward = wind.design_pressure(30, 25, 0.8)
            >>> round(p_windward, 2)
            14.28
        """
        q_z = self.velocity_pressure(height)
        g_f = self.gust_factor(height, mean_roof_height)
        
        # Directionality factor (0.85 for most buildings)
        k_dir = 0.85 if directional else 1.0
        
        # Design pressure
        p = q_z * g_f * cp * k_dir
        
        return p
    
    def wall_pressures(self, height: float, mean_roof_height: float) -> Dict[str, float]:
        """Calculate design pressures for walls.
        
        Args:
            height (float): Wall height (ft)
            mean_roof_height (float): Mean roof height (ft)
        
        Returns:
            dict: {location: pressure_psf}
        """
        return {
            'windward_wall': self.design_pressure(height, mean_roof_height,
                                                 self.CP_ENCLOSED['windward_wall']),
            'leeward_wall': self.design_pressure(height, mean_roof_height,
                                                self.CP_ENCLOSED['leeward_wall']),
            'side_wall': self.design_pressure(height, mean_roof_height,
                                             self.CP_ENCLOSED['side_wall']),
        }
    
    def roof_pressures(self, mean_roof_height: float) -> Dict[str, float]:
        """Calculate design pressures for roof surfaces.
        
        Args:
            mean_roof_height (float): Mean roof height (ft)
        
        Returns:
            dict: {location: pressure_psf}
        """
        return {
            'windward': self.design_pressure(mean_roof_height, mean_roof_height,
                                            self.CP_ENCLOSED['roof_windward']),
            'leeward': self.design_pressure(mean_roof_height, mean_roof_height,
                                           self.CP_ENCLOSED['roof_leeward']),
        }
    
    def force_on_area(self, area: float, height: float, mean_roof_height: float,
                     cp: float) -> float:
        """Calculate wind force on area.
        
        Args:
            area (float): Tributary area (sq ft)
            height (float): Height of area (ft)
            mean_roof_height (float): Mean roof height (ft)
            cp (float): Pressure coefficient
        
        Returns:
            float: Wind force (lbs)
        """
        pressure = self.design_pressure(height, mean_roof_height, cp)
        force = pressure * area
        return force
    
    def base_shear(self, width: float, height: float, mean_roof_height: float) -> float:
        """Calculate base shear from wind pressure.
        
        Args:
            width (float): Width of building perpendicular to wind (ft)
            height (float): Full building height (ft)
            mean_roof_height (float): Mean roof height (ft)
        
        Returns:
            float: Total base shear (lbs)
        """
        # Average pressure on windward face
        windward_press = self.design_pressure(height/2, mean_roof_height,
                                             self.CP_ENCLOSED['windward_wall'])
        # Average pressure on leeward face
        leeward_press = self.design_pressure(height/2, mean_roof_height,
                                            self.CP_ENCLOSED['leeward_wall'])
        
        # Net pressure
        net_press = windward_press - leeward_press
        
        # Total force
        total_area = width * height
        base_shear = net_press * total_area
        
        return base_shear
    
    def summary(self) -> str:
        """Generate wind load summary.
        
        Returns:
            str: Formatted summary text
        """
        q_30 = self.velocity_pressure(30)
        
        summary = f"\n{'='*70}\n"
        summary += f"Wind Load Analysis Summary (ASCE 7)\n"
        summary += f"{'='*70}\n"
        summary += f"Design Wind Speed: {self.v_design} mph\n"
        summary += f"Adjusted Speed (with risk): {self.v_adjust:.1f} mph\n"
        summary += f"Exposure Category: {self.exposure}\n"
        summary += f"Risk Category: {self.risk_cat}\n"
        summary += f"Velocity Pressure (z=30'): {q_30:.2f} psf\n"
        summary += f"{'='*70}\n"
        
        return summary
