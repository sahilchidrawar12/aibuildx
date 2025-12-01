"""
Web Opening Handler for castellated and cellular beams with web openings.
Analyzes the effects of openings on moment of inertia and shear capacity.
"""


class WebOpeningHandler:
    """Handle castellated and cellular beams with web openings"""
    
    @staticmethod
    def opening_loss(opening_height_mm, opening_width_mm, num_openings, beam_depth_mm):
        """
        Estimate loss in moment of inertia due to web openings.
        
        Simplified approach: loss is proportional to opening area relative to web area.
        
        Args:
            opening_height_mm: Height of each opening in mm
            opening_width_mm: Width of each opening in mm
            num_openings: Number of openings
            beam_depth_mm: Beam overall depth in mm
            
        Returns:
            Loss factor (0-1), where 1.0 means complete loss
        """
        # Total opening area
        total_opening_area = num_openings * opening_height_mm * opening_width_mm
        
        # Reference web area (conservative estimate)
        web_area = beam_depth_mm * beam_depth_mm * 100
        
        # Loss factor as fraction of reference area
        loss_factor = total_opening_area / web_area if web_area > 0 else 0
        
        # Cap at 30% loss for safety
        return min(0.3, loss_factor)
    
    @staticmethod
    def reduced_inertia(original_ixx_mm4, opening_height_mm, opening_width_mm, num_openings, beam_depth_mm):
        """
        Calculate effective moment of inertia accounting for web openings.
        
        Args:
            original_ixx_mm4: Original moment of inertia without openings
            opening_height_mm: Height of each opening
            opening_width_mm: Width of each opening
            num_openings: Number of openings
            beam_depth_mm: Beam depth
            
        Returns:
            Reduced moment of inertia in mm4
        """
        loss_factor = WebOpeningHandler.opening_loss(opening_height_mm, opening_width_mm, num_openings, beam_depth_mm)
        return original_ixx_mm4 * (1 - loss_factor)
    
    @staticmethod
    def shear_capacity_reduction(num_openings, beam_height_mm, web_thickness_mm):
        """
        Reduce shear capacity for each opening in web.
        
        Args:
            num_openings: Number of web openings
            beam_height_mm: Beam depth in mm
            web_thickness_mm: Web thickness in mm
            
        Returns:
            Remaining shear capacity area in mm2
        """
        base_capacity_mm2 = beam_height_mm * web_thickness_mm
        
        # Conservative: 10% capacity loss per opening
        loss_per_opening = base_capacity_mm2 * 0.1
        
        # But maintain minimum 50% of original capacity
        return max(base_capacity_mm2 * 0.5, base_capacity_mm2 - num_openings * loss_per_opening)
    
    @staticmethod
    def castellated_beam_properties(base_section_props, opening_height_mm, opening_spacing_mm, web_thickness_mm):
        """
        Calculate effective properties for castellated beam.
        
        Castellated beams have triangular web openings creating an expanded profile.
        
        Args:
            base_section_props: Original section properties dict
            opening_height_mm: Height of hexagonal opening
            opening_spacing_mm: Spacing between openings
            web_thickness_mm: Web thickness
            
        Returns:
            Modified section properties
        """
        # In castellated beams, moment of inertia can actually INCREASE due to greater height
        # but shear capacity reduces and stress concentration factors apply
        
        original_height = base_section_props.get('height_mm', 500)
        new_height = original_height + opening_height_mm / 2  # Approximate effective height
        
        # Moment of inertia scales approximately with height^3
        original_ix = base_section_props.get('Ixx_mm4', 1e6)
        height_ratio = new_height / original_height if original_height > 0 else 1.0
        new_ix = original_ix * (height_ratio ** 3) * 0.85  # Apply 0.85 factor for openings
        
        # Shear capacity reduced
        original_area = base_section_props.get('area_mm2', 100)
        num_openings = int((5000 / opening_spacing_mm) if opening_spacing_mm > 0 else 10)  # Estimate count over 5m
        shear_area = WebOpeningHandler.shear_capacity_reduction(num_openings, original_height, web_thickness_mm)
        
        return {
            'original_height_mm': original_height,
            'expanded_height_mm': new_height,
            'Ixx_mm4_effective': new_ix,
            'shear_area_mm2': shear_area,
            'stress_concentration_factor': 1.3,  # Typical for castellated beam at opening
            'cost_multiplier': 1.2,  # Castellated typically 20% more expensive
            'notes': 'Castellated beam - apply Kf=1.3 at connections'
        }
    
    @staticmethod
    def cellular_beam_properties(outer_width_mm, outer_height_mm, cell_dia_mm, thickness_mm):
        """
        Calculate properties for cellular beam (welded tubes in web).
        
        Args:
            outer_width_mm: Outer width
            outer_height_mm: Outer height
            cell_dia_mm: Diameter of cellular openings
            thickness_mm: Material thickness
            
        Returns:
            Section properties accounting for cells
        """
        # Conservative: approximate loss based on hole pattern
        num_cells = int((outer_height_mm - 200) / (cell_dia_mm + 50))  # Approximate count
        num_cells = max(0, num_cells)
        
        cell_area_total = num_cells * (3.14159 * (cell_dia_mm / 2) ** 2)
        
        base_area = outer_width_mm * outer_height_mm - (outer_width_mm - 2*thickness_mm) * (outer_height_mm - 2*thickness_mm)
        effective_area = base_area - cell_area_total * 0.5  # Half the cell area affects design
        
        return {
            'effective_area_mm2': effective_area,
            'num_cells': num_cells,
            'cell_diameter_mm': cell_dia_mm,
            'reduction_factor': 0.85,
            'cost_multiplier': 1.15,
            'fabrication_notes': 'Cellular beam: verify connection compatibility with cell locations'
        }
