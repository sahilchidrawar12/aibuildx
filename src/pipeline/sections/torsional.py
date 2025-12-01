"""
Torsional Property Calculator for calculating J and Cw properties for advanced analysis.
Essential for members subject to twisting and lateral-torsional buckling analysis.
"""
import math


class TorsionalPropertyCalculator:
    """Calculate torsional properties J and Cw for advanced analysis"""
    
    @staticmethod
    def torsional_constant_i_beam(width_mm, depth_mm, flange_thk_mm, web_thk_mm):
        """
        Approximate torsional constant J for I-beam.
        
        J = (1/3) * (sum of b*t^3 for each element)
        This is a simplified formula; exact calculation requires integration.
        
        Args:
            width_mm: Flange width in mm
            depth_mm: Overall depth in mm
            flange_thk_mm: Flange thickness in mm
            web_thk_mm: Web thickness in mm
            
        Returns:
            Torsional constant J in mm4
        """
        # Flange contribution (two flanges, but effective width is not full width for torsion)
        effective_flange_width = width_mm - web_thk_mm / 2
        j_flange = 2 * effective_flange_width * (flange_thk_mm ** 3)
        
        # Web contribution
        web_height = depth_mm - 2 * flange_thk_mm
        j_web = web_height * (web_thk_mm ** 3)
        
        # Total (with 1/3 factor)
        return (j_flange + j_web) / 3
    
    @staticmethod
    def torsional_constant_box_section(outer_width_mm, outer_height_mm, thickness_mm):
        """
        Torsional constant for hollow rectangular (box) section.
        
        J ≈ (4 * A^2 * t) / perimeter
        where A is enclosed area, t is thickness
        
        Args:
            outer_width_mm: Outer width in mm
            outer_height_mm: Outer height in mm
            thickness_mm: Wall thickness in mm
            
        Returns:
            Torsional constant J in mm4
        """
        inner_width = outer_width_mm - 2 * thickness_mm
        inner_height = outer_height_mm - 2 * thickness_mm
        
        # Enclosed area
        A = inner_width * inner_height
        
        # Perimeter (mean line)
        perimeter = 2 * (inner_width + inner_height)
        
        # Torsional constant
        if perimeter > 0:
            j = (4 * A * A * thickness_mm) / perimeter
        else:
            j = 0
        
        return j
    
    @staticmethod
    def warping_constant_i_beam(width_mm, depth_mm, flange_thk_mm, web_thk_mm):
        """
        Approximate warping constant Cw for I-beam.
        
        Cw relates to resistance to non-uniform torsion (warping).
        
        Cw ≈ (1/12) * (width^2) * (depth - flange_thk)^2 * flange_thk / (3*width + depth)
        
        Args:
            width_mm: Flange width in mm
            depth_mm: Overall depth in mm
            flange_thk_mm: Flange thickness in mm
            web_thk_mm: Web thickness in mm
            
        Returns:
            Warping constant Cw in mm6
        """
        h = depth_mm - flange_thk_mm  # Clear web height
        
        denominator = 3 * width_mm + depth_mm if (3 * width_mm + depth_mm) > 0 else 1
        
        cw = ((width_mm ** 2) * (h ** 2) * flange_thk_mm) / (36 * denominator)
        
        return cw
    
    @staticmethod
    def ltb_critical_moment(e_gpa, fy_mpa, lb_m, iy_mm4, j_mm4, cw_mm6):
        """
        Calculate critical moment for lateral-torsional buckling (LTB).
        
        Uses AISC F2 formula (simplified):
        Mcr = (π/Lb) * √(E*Iy*GJ + (π*E*Iy*Cw)/Lb^2)
        
        Args:
            e_gpa: Young's modulus in GPa
            fy_mpa: Yield stress in MPa
            lb_m: Unbraced length in meters
            iy_mm4: Moment of inertia about weak axis in mm4
            j_mm4: Torsional constant in mm4
            cw_mm6: Warping constant in mm6
            
        Returns:
            Critical bending moment Mcr in kNm
        """
        # Convert units
        E_Pa = e_gpa * 1e9
        G_Pa = e_gpa * 1e9 / 2.6  # Approximate shear modulus
        Lb_m = lb_m
        
        # Convert to consistent units (N, mm)
        Iy = iy_mm4 * 1e-12  # mm4 to m4
        J = j_mm4 * 1e-12
        Cw = cw_mm6 * 1e-18
        
        if Lb_m <= 0 or Iy <= 0:
            return float('inf')
        
        # Term under square root
        term1 = E_Pa * Iy * G_Pa * J
        term2 = (math.pi * E_Pa * Iy * Cw) / (Lb_m ** 2)
        
        try:
            sqrt_term = math.sqrt(term1 + term2)
        except:
            sqrt_term = 0
        
        Mcr_Nm = (math.pi / Lb_m) * sqrt_term
        Mcr_kNm = Mcr_Nm / 1e6
        
        return Mcr_kNm
    
    @staticmethod
    def torsional_analysis_summary(member_type, width_mm, depth_mm, thickness_mm, unbraced_length_m, fy_mpa=345):
        """
        Generate summary of torsional properties and LTB susceptibility.
        
        Args:
            member_type: 'I-beam', 'box', 'angle', etc.
            width_mm: Section width in mm
            depth_mm: Section depth in mm
            thickness_mm: Material thickness in mm
            unbraced_length_m: Unbraced length for lateral-torsional buckling
            fy_mpa: Yield strength in MPa
            
        Returns:
            Dictionary with torsional analysis
        """
        E_gpa = 200  # Steel modulus
        
        if member_type == 'I-beam':
            J = TorsionalPropertyCalculator.torsional_constant_i_beam(width_mm, depth_mm, thickness_mm, thickness_mm/2)
            Cw = TorsionalPropertyCalculator.warping_constant_i_beam(width_mm, depth_mm, thickness_mm, thickness_mm/2)
            Iy = (depth_mm * (width_mm/2) ** 3) / 12
        elif member_type == 'box':
            J = TorsionalPropertyCalculator.torsional_constant_box_section(width_mm, depth_mm, thickness_mm)
            Cw = 0  # Box sections have minimal warping
            Iy = (depth_mm * width_mm ** 3) / 12
        else:
            J = 100  # Placeholder
            Cw = 100
            Iy = 1000
        
        Mcr = TorsionalPropertyCalculator.ltb_critical_moment(E_gpa, fy_mpa, unbraced_length_m, Iy, J, Cw)
        
        return {
            'member_type': member_type,
            'J_mm4': J,
            'Cw_mm6': Cw,
            'Iy_mm4': Iy,
            'unbraced_length_m': unbraced_length_m,
            'Mcr_kNm': Mcr,
            'ltb_susceptible': Mcr < 500,  # If Mcr < 500 kNm, warping/torsion important
            'recommendations': 'Add lateral bracing' if Mcr < 500 else 'Torsion check not critical'
        }
