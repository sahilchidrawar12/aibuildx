"""
Camber Calculator for computing fabrication camber to compensate for deflection.
Used to pre-deflect beams to account for applied loads during service.
"""
import math


class CamberCalculator:
    """Calculate fabrication camber to compensate for deflection"""
    
    @staticmethod
    def camber_from_deflection(load_kN, span_m, moment_of_inertia_cm4, e_gpa=200):
        """
        Calculate camber offset in mm for deflection compensation.
        
        Uses standard deflection formula: delta = (5 * w * L^4) / (384 * E * I)
        
        Args:
            load_kN: Total load applied (kN)
            span_m: Member span in meters
            moment_of_inertia_cm4: Moment of inertia in cm^4
            e_gpa: Young's modulus in GPa (default 200 for steel)
            
        Returns:
            Camber offset in mm (positive means upward camber)
        """
        if span_m <= 0 or moment_of_inertia_cm4 <= 0 or e_gpa <= 0:
            return 0.0
        
        # Convert units
        w = (load_kN * 1000) / span_m  # Load per unit length in N/m
        I_m4 = moment_of_inertia_cm4 * 1e-8  # Convert cm^4 to m^4
        E_pa = e_gpa * 1e9  # Convert GPa to Pa
        
        # Deflection in meters
        delta_m = (5 * w * (span_m ** 4)) / (384 * E_pa * I_m4)
        
        # Convert to mm
        return delta_m * 1000
    
    @staticmethod
    def camber_profile(load_kN, span_m, I_cm4, num_points=21, e_gpa=200):
        """
        Generate camber profile along member length.
        
        Args:
            load_kN: Total load (uniformly distributed)
            span_m: Member span
            I_cm4: Moment of inertia
            num_points: Number of points in profile
            e_gpa: Young's modulus
            
        Returns:
            List of {'x_m': position, 'camber_mm': offset} along span
        """
        profile = []
        max_camber = CamberCalculator.camber_from_deflection(load_kN, span_m, I_cm4, e_gpa)
        
        for i in range(num_points):
            x = span_m * i / (num_points - 1)
            # Parabolic deflection: max at center
            # deflection = camber * (4*x*(L-x) / L^2) normalized
            if span_m > 0:
                relative_defl = 4 * x * (span_m - x) / (span_m * span_m)
                camber_mm = max_camber * relative_defl
            else:
                camber_mm = 0.0
            
            profile.append({'x_m': x, 'camber_mm': camber_mm})
        
        return profile
    
    @staticmethod
    def camber_fabrication_notes(max_camber_mm, member_length_m):
        """
        Generate fabrication notes for camber specification.
        
        Args:
            max_camber_mm: Maximum camber in mm
            member_length_m: Member length in meters
            
        Returns:
            Dictionary with fabrication guidance
        """
        return {
            'max_camber_mm': max_camber_mm,
            'camber_type': 'parabolic',
            'assembly_notes': f'Apply upward camber of {max_camber_mm:.1f}mm at midspan',
            'verification': 'Measure camber with level or laser transit at midspan',
            'tolerance_mm': max(2, max_camber_mm * 0.1),  # ±10% or minimum 2mm
        }
