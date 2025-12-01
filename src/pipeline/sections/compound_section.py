"""
Compound Section Builder for creating sections from plates and basic shapes.
Handles built-up I-beams, box sections, and composite section calculations.
"""


class CompoundSectionBuilder:
    """Build compound sections from plates and basic shapes"""
    
    @staticmethod
    def built_up_i_beam(flange_width_mm, flange_thickness_mm, web_height_mm, web_thickness_mm):
        """
        Calculate properties of built-up I-beam from component dimensions.
        
        Args:
            flange_width_mm: Flange width in mm
            flange_thickness_mm: Flange thickness in mm
            web_height_mm: Web height (clear distance between flanges) in mm
            web_thickness_mm: Web thickness in mm
            
        Returns:
            Dictionary with calculated properties
        """
        # Calculate gross area
        area_mm2 = 2 * flange_width_mm * flange_thickness_mm + web_height_mm * web_thickness_mm
        
        # Moment of inertia about neutral axis (X-X)
        # Web contribution
        web_ix = (web_thickness_mm * web_height_mm ** 3) / 12
        
        # Flange contribution (distance from centerline to flange centerline)
        flange_dist = (web_height_mm / 2 + flange_thickness_mm / 2)
        flange_ix = 2 * (
            (flange_width_mm * flange_thickness_mm ** 3) / 12 +
            flange_width_mm * flange_thickness_mm * (flange_dist ** 2)
        )
        
        ix_total = web_ix + flange_ix
        
        # Y-Y axis (perpendicular to web)
        iy_web = (web_height_mm * web_thickness_mm ** 3) / 12
        iy_flange = 2 * ((flange_thickness_mm * flange_width_mm ** 3) / 12)
        iy_total = iy_web + iy_flange
        
        # Weight (assuming steel density = 7850 kg/m³ = 7.85e-6 kg/mm³)
        weight_kg_per_m = area_mm2 * 7.85 / 1e6
        
        # Elastic section modulus (about X-X)
        total_height = 2 * flange_thickness_mm + web_height_mm
        sx = ix_total / (total_height / 2) if total_height > 0 else 0
        
        # Elastic section modulus (about Y-Y)
        sy = iy_total / (flange_width_mm / 2) if flange_width_mm > 0 else 0
        
        return {
            'area_mm2': area_mm2,
            'Ixx_mm4': ix_total,
            'Iyy_mm4': iy_total,
            'Sx_mm3': sx,
            'Sy_mm3': sy,
            'weight_kg_per_m': weight_kg_per_m,
            'height_mm': total_height,
            'width_mm': flange_width_mm
        }
    
    @staticmethod
    def box_section(outer_width_mm, outer_height_mm, thickness_mm):
        """
        Calculate properties of hollow rectangular/box section.
        
        Args:
            outer_width_mm: Outer width in mm
            outer_height_mm: Outer height in mm
            thickness_mm: Wall thickness in mm
            
        Returns:
            Dictionary with calculated properties
        """
        # Outer area
        outer_area = outer_width_mm * outer_height_mm
        
        # Inner dimensions
        inner_width = max(0, outer_width_mm - 2 * thickness_mm)
        inner_height = max(0, outer_height_mm - 2 * thickness_mm)
        
        # Net area
        area_mm2 = outer_area - (inner_width * inner_height)
        
        # Moment of inertia (about X-X, through center)
        ix_outer = (outer_width_mm * outer_height_mm ** 3) / 12
        ix_inner = (inner_width * inner_height ** 3) / 12 if inner_width > 0 and inner_height > 0 else 0
        ix_total = ix_outer - ix_inner
        
        # Moment of inertia (about Y-Y)
        iy_outer = (outer_height_mm * outer_width_mm ** 3) / 12
        iy_inner = (inner_height * inner_width ** 3) / 12 if inner_width > 0 and inner_height > 0 else 0
        iy_total = iy_outer - iy_inner
        
        # Weight
        weight_kg_per_m = area_mm2 * 7.85 / 1e6
        
        # Section moduli
        sx = ix_total / (outer_height_mm / 2) if outer_height_mm > 0 else 0
        sy = iy_total / (outer_width_mm / 2) if outer_width_mm > 0 else 0
        
        return {
            'area_mm2': area_mm2,
            'Ixx_mm4': ix_total,
            'Iyy_mm4': iy_total,
            'Sx_mm3': sx,
            'Sy_mm3': sy,
            'weight_kg_per_m': weight_kg_per_m,
            'outer_width_mm': outer_width_mm,
            'outer_height_mm': outer_height_mm,
            'thickness_mm': thickness_mm
        }
    
    @staticmethod
    def composite_section(components):
        """
        Calculate properties of composite section from component list.
        
        Each component: {'shape': 'rect'|'circle'|'I', 'position': [x, y], ...properties}
        
        Args:
            components: List of component dictionaries
            
        Returns:
            Composite section properties
        """
        total_area = 0
        centroid_x = 0
        centroid_y = 0
        ix_about_origin = 0
        iy_about_origin = 0
        
        # First pass: calculate centroid
        for comp in components:
            shape = comp.get('shape', 'rect')
            x, y = comp.get('position', [0, 0])
            
            if shape == 'rect':
                w = comp.get('width_mm', 100)
                h = comp.get('height_mm', 100)
                area = w * h
            elif shape == 'circle':
                r = comp.get('radius_mm', 50)
                area = 3.14159 * r * r
            else:
                area = comp.get('area_mm2', 100)
            
            total_area += area
            centroid_x += area * x
            centroid_y += area * y
        
        if total_area > 0:
            centroid_x /= total_area
            centroid_y /= total_area
        
        # Second pass: calculate moment of inertia about centroid
        for comp in components:
            shape = comp.get('shape', 'rect')
            x, y = comp.get('position', [0, 0])
            
            if shape == 'rect':
                w = comp.get('width_mm', 100)
                h = comp.get('height_mm', 100)
                area = w * h
                Ix = (w * h ** 3) / 12
                Iy = (h * w ** 3) / 12
            elif shape == 'circle':
                r = comp.get('radius_mm', 50)
                area = 3.14159 * r * r
                Ix = Iy = (3.14159 * r ** 4) / 4
            else:
                area = comp.get('area_mm2', 100)
                Ix = Iy = 0
            
            dx = x - centroid_x
            dy = y - centroid_y
            
            ix_about_origin += Ix + area * dy * dy
            iy_about_origin += Iy + area * dx * dx
        
        return {
            'area_mm2': total_area,
            'centroid_x_mm': centroid_x,
            'centroid_y_mm': centroid_y,
            'Ixx_mm4': ix_about_origin,
            'Iyy_mm4': iy_about_origin,
            'weight_kg_per_m': total_area * 7.85 / 1e6,
            'num_components': len(components)
        }
