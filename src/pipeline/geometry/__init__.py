"""
Geometry module init - provides access to all geometry calculation classes.
Includes coordinate systems, rotations, curved members, camber, skew cuts, and eccentricity.
"""

from .coordinate_system import CoordinateSystemManager
from .rotation_matrix import RotationMatrix3D
from .curved_member import CurvedMemberHandler
from .camber_calculator import CamberCalculator
from .skew_cut import SkewCutGeometry
from .eccentricity import EccentricityResolver

__all__ = [
    'CoordinateSystemManager',
    'RotationMatrix3D',
    'CurvedMemberHandler',
    'CamberCalculator',
    'SkewCutGeometry',
    'EccentricityResolver',
]
