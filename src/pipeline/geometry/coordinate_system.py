"""
Coordinate System Manager for WCS, UCS, and Tekla coordinate transformations.
Handles transformations between World Coordinate System (WCS), User Coordinate System (UCS),
and Tekla-specific coordinate systems.
"""


class CoordinateSystemManager:
    """Manages transformations between WCS (World), UCS (User), and Tekla CS"""
    
    def __init__(self):
        """Initialize with default WCS = UCS (identity transformation)"""
        self.ucs_origin = [0.0, 0.0, 0.0]
        self.ucs_x = [1.0, 0.0, 0.0]
        self.ucs_y = [0.0, 1.0, 0.0]
        self.ucs_z = [0.0, 0.0, 1.0]
    
    def wcs_to_ucs(self, wcs_point):
        """
        Convert WCS coordinates to UCS coordinates.
        
        Args:
            wcs_point: [x, y, z] in World Coordinate System
            
        Returns:
            [x, y, z] in User Coordinate System
        """
        x = wcs_point[0] - self.ucs_origin[0]
        y = wcs_point[1] - self.ucs_origin[1]
        z = wcs_point[2] - self.ucs_origin[2]
        return [
            x * self.ucs_x[0] + y * self.ucs_y[0] + z * self.ucs_z[0],
            x * self.ucs_x[1] + y * self.ucs_y[1] + z * self.ucs_z[1],
            x * self.ucs_x[2] + y * self.ucs_y[2] + z * self.ucs_z[2],
        ]
    
    def ucs_to_wcs(self, ucs_point):
        """
        Convert UCS coordinates to WCS coordinates.
        
        Args:
            ucs_point: [x, y, z] in User Coordinate System
            
        Returns:
            [x, y, z] in World Coordinate System
        """
        return [
            self.ucs_origin[0] + ucs_point[0] * self.ucs_x[0] + ucs_point[1] * self.ucs_y[0] + ucs_point[2] * self.ucs_z[0],
            self.ucs_origin[1] + ucs_point[0] * self.ucs_x[1] + ucs_point[1] * self.ucs_y[1] + ucs_point[2] * self.ucs_z[1],
            self.ucs_origin[2] + ucs_point[0] * self.ucs_x[2] + ucs_point[1] * self.ucs_y[2] + ucs_point[2] * self.ucs_z[2],
        ]
    
    def set_ucs_origin(self, origin):
        """Set UCS origin point"""
        self.ucs_origin = list(origin)
    
    def set_ucs_axes(self, x_axis, y_axis, z_axis):
        """Set UCS axes (should be orthonormal)"""
        self.ucs_x = list(x_axis)
        self.ucs_y = list(y_axis)
        self.ucs_z = list(z_axis)
