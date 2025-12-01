"""
3D Rotation Matrix calculations for arbitrary 3D orientations and transformations.
Includes rotation about X, Y, Z axes and Rodrigues rotation formula for arbitrary axes.
"""
import math


class RotationMatrix3D:
    """Compute rotation matrices for arbitrary 3D orientations"""
    
    @staticmethod
    def rotation_matrix_x(angle_rad):
        """
        Rotation matrix about X-axis.
        
        Args:
            angle_rad: Rotation angle in radians
            
        Returns:
            3x3 rotation matrix as list of lists
        """
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        return [[1, 0, 0], [0, c, -s], [0, s, c]]
    
    @staticmethod
    def rotation_matrix_y(angle_rad):
        """
        Rotation matrix about Y-axis.
        
        Args:
            angle_rad: Rotation angle in radians
            
        Returns:
            3x3 rotation matrix as list of lists
        """
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    
    @staticmethod
    def rotation_matrix_z(angle_rad):
        """
        Rotation matrix about Z-axis.
        
        Args:
            angle_rad: Rotation angle in radians
            
        Returns:
            3x3 rotation matrix as list of lists
        """
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        return [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    
    @staticmethod
    def rotation_axis_angle(axis, angle_rad):
        """
        Rodrigues rotation formula: rotate around arbitrary axis.
        
        Args:
            axis: [x, y, z] unit vector defining rotation axis
            angle_rad: Rotation angle in radians
            
        Returns:
            3x3 rotation matrix as list of lists
        """
        ax, ay, az = axis
        norm = math.sqrt(ax*ax + ay*ay + az*az)
        if norm == 0:
            return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        ax, ay, az = ax/norm, ay/norm, az/norm
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        t = 1 - c
        return [
            [t*ax*ax + c, t*ax*ay - az*s, t*ax*az + ay*s],
            [t*ax*ay + az*s, t*ay*ay + c, t*ay*az - ax*s],
            [t*ax*az - ay*s, t*ay*az + ax*s, t*az*az + c],
        ]
    
    @staticmethod
    def matrix_multiply(m1, m2):
        """
        Multiply two 3x3 rotation matrices.
        
        Args:
            m1, m2: 3x3 matrices as list of lists
            
        Returns:
            Result matrix m1 @ m2
        """
        result = [[0]*3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    result[i][j] += m1[i][k] * m2[k][j]
        return result
    
    @staticmethod
    def apply_rotation(point, rotation_matrix):
        """
        Apply rotation matrix to a point.
        
        Args:
            point: [x, y, z] coordinates
            rotation_matrix: 3x3 matrix
            
        Returns:
            Rotated point [x', y', z']
        """
        result = [0, 0, 0]
        for i in range(3):
            for j in range(3):
                result[i] += rotation_matrix[i][j] * point[j]
        return result
