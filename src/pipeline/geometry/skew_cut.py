"""
Skew Cut Geometry for computing bevel angles and cope radii for non-perpendicular cuts.
Handles member end cuts, chamfers, and complex connection geometries.
"""
import math


class SkewCutGeometry:
    """Calculate bevel angles for non-perpendicular cuts"""
    
    @staticmethod
    def bevel_angle(member_axis, cutting_plane_normal):
        """
        Calculate bevel angle between member and cutting plane.
        
        The angle between the axis and plane is: angle = arcsin(dot product / (norm1 * norm2))
        
        Args:
            member_axis: [x, y, z] unit vector along member
            cutting_plane_normal: [x, y, z] unit normal to cutting plane
            
        Returns:
            Bevel angle in degrees (0-90)
        """
        dot = sum(member_axis[i] * cutting_plane_normal[i] for i in range(3))
        # Clamp to avoid numerical issues with arcsin
        dot = max(-1.0, min(1.0, dot))
        angle_rad = math.asin(abs(dot))
        return math.degrees(angle_rad)
    
    @staticmethod
    def cope_radius_for_section(flange_radius_mm, member_depth_mm):
        """
        Standard cope radius based on section depth and flange radius.
        
        AISC: cope radius typically = flange radius or member depth/2, whichever is smaller.
        
        Args:
            flange_radius_mm: Flange corner radius in mm
            member_depth_mm: Member overall depth in mm
            
        Returns:
            Recommended cope radius in mm
        """
        return min(flange_radius_mm, member_depth_mm / 2)
    
    @staticmethod
    def cope_dimensions(member_depth_mm, member_width_mm, flange_thickness_mm, cope_type='standard'):
        """
        Calculate cope cut dimensions.
        
        Args:
            member_depth_mm: Overall member depth
            member_width_mm: Flange width
            flange_thickness_mm: Flange thickness
            cope_type: 'standard', 'short_leg', 'clip_angle', etc.
            
        Returns:
            Dictionary with cope dimensions
        """
        if cope_type == 'standard':
            cope_depth = 50  # Standard AISC cope depth
            cope_length = 100  # Along flange
            radius = SkewCutGeometry.cope_radius_for_section(20, member_depth_mm)
        elif cope_type == 'short_leg':
            cope_depth = 30
            cope_length = 80
            radius = 15
        elif cope_type == 'clip_angle':
            cope_depth = 60
            cope_length = 120
            radius = 25
        else:
            cope_depth = 50
            cope_length = 100
            radius = 20
        
        return {
            'cope_depth_mm': cope_depth,
            'cope_length_mm': cope_length,
            'corner_radius_mm': radius,
            'cope_type': cope_type,
            'notes': f'{cope_type} cope: {cope_depth}mm deep x {cope_length}mm long'
        }
    
    @staticmethod
    def skew_cut_angle_compensation(member_axis, desired_cut_plane_normal):
        """
        Calculate compensation angle when cut is not perpendicular to member.
        
        Args:
            member_axis: [x, y, z] unit vector along member
            desired_cut_plane_normal: [x, y, z] normal to desired cutting plane
            
        Returns:
            Angle in degrees to rotate cutting setup
        """
        # Calculate angle between axis and plane normal
        bevel = SkewCutGeometry.bevel_angle(member_axis, desired_cut_plane_normal)
        return bevel
    
    @staticmethod
    def check_cope_clearance(adjacent_member, member_depth_mm, cope_depth_mm):
        """
        Verify cope doesn't interfere with connected members.
        
        Args:
            adjacent_member: Connected member data
            member_depth_mm: Current member depth
            cope_depth_mm: Proposed cope depth
            
        Returns:
            {'clearance_ok': bool, 'warning': str or None}
        """
        # Simple interference check
        required_clearance = member_depth_mm - cope_depth_mm
        adjacent_depth = adjacent_member.get('depth_mm', 200)
        
        if required_clearance < 50:
            return {
                'clearance_ok': False,
                'warning': f'Cope depth {cope_depth_mm}mm leaves insufficient flange ({required_clearance}mm)',
                'suggestion': 'Reduce cope depth or use shallower member'
            }
        
        return {'clearance_ok': True, 'warning': None}
