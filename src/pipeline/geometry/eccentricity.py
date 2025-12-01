"""
Eccentricity Resolver for handling work points vs. centerline offsets in connections.
Manages the relationship between theoretical member centerlines and actual connection work points.
"""


class EccentricityResolver:
    """Handle work points vs. centerline offsets in connections"""
    
    @staticmethod
    def work_point_offset(connection_type, member_section_depth_mm):
        """
        Return work point offset from centerline (mm).
        
        Work point is the theoretical connection point for design purposes.
        - Base plates: often bottom of column (depth/2)
        - Moment connections: often centerline (0)
        - Shear connections: varies
        
        Args:
            connection_type: Type of connection ('bolted_base_plate', 'welded_moment_connection', etc.)
            member_section_depth_mm: Overall member depth in mm
            
        Returns:
            Offset from centerline in mm (negative = below centerline, positive = above)
        """
        offset_map = {
            'bolted_base_plate': member_section_depth_mm / 2,  # Bottom of section
            'welded_base_plate': member_section_depth_mm / 2,
            'bolted_end_plate': 0,  # Centerline for moment connections
            'welded_moment_connection': 0,
            'clip_angle_bolted': member_section_depth_mm / 2,  # Bottom for shear
            'bolted_gusset_plate': 0,  # Gusset typically at centerline
            'welded_gusset_plate': 0,
            'flush_end_plate': 0,  # Centered for architectural exposure
        }
        
        return offset_map.get(connection_type, 0)
    
    @staticmethod
    def eccentricity_check(connection_type, applied_force_direction, member_axis):
        """
        Check for potential eccentricity problems in connection.
        
        Args:
            connection_type: Type of connection
            applied_force_direction: [x, y, z] direction of applied force
            member_axis: [x, y, z] unit vector along member
            
        Returns:
            Dictionary with eccentricity analysis
        """
        # Calculate angle between force and member axis
        dot = sum(applied_force_direction[i] * member_axis[i] for i in range(3))
        import math
        angle_rad = math.acos(max(-1, min(1, dot)))
        angle_deg = math.degrees(angle_rad)
        
        has_moment = angle_deg > 15  # Significant angle suggests moment
        
        return {
            'connection_type': connection_type,
            'force_angle_from_axis_deg': angle_deg,
            'significant_eccentricity': has_moment,
            'warning': 'Connection may develop moment' if has_moment else None
        }
    
    @staticmethod
    def adjust_for_eccentricity(axial_force_kN, moment_kNm, work_point_offset_mm, member_depth_mm):
        """
        Adjust internal forces for work point vs. centerline difference.
        
        Args:
            axial_force_kN: Axial force
            moment_kNm: Bending moment at centerline
            work_point_offset_mm: Offset from centerline in mm
            member_depth_mm: Total member depth
            
        Returns:
            {'axial_kN': adjusted, 'moment_kNm': adjusted}
        """
        offset_m = work_point_offset_mm / 1000.0
        
        # Additional moment from axial force acting at offset work point
        additional_moment_kNm = (axial_force_kN * offset_m) / 1000.0
        
        return {
            'axial_kN': axial_force_kN,
            'moment_kNm': moment_kNm + additional_moment_kNm,
            'eccentricity_contribution_kNm': additional_moment_kNm,
            'offset_mm': work_point_offset_mm
        }
    
    @staticmethod
    def connection_work_point(member_type, connection_type, member_depth_mm):
        """
        Get absolute work point coordinates relative to member centerline.
        
        Args:
            member_type: 'beam', 'column', 'brace', etc.
            connection_type: Type of connection
            member_depth_mm: Member depth in mm
            
        Returns:
            {'offset_mm': z-offset, 'description': str}
        """
        if member_type == 'column':
            offset = EccentricityResolver.work_point_offset(connection_type, member_depth_mm)
            desc = f'Column work point {offset:.0f}mm below centerline (at base)'
        elif member_type == 'beam':
            if 'bolted' in connection_type or 'clip' in connection_type:
                offset = member_depth_mm / 2  # Bottom of beam
                desc = f'Beam work point {offset:.0f}mm below centerline (top of column)'
            else:
                offset = 0
                desc = 'Beam work point at centerline'
        else:
            offset = 0
            desc = 'Work point at centerline'
        
        return {'offset_mm': offset, 'description': desc}
