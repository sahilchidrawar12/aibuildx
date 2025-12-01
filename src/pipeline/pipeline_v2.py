"""
Consolidated pipeline implementation (v2) with agents and IFC geometry exporter.
Enhanced with 20 feature categories: geometry systems, advanced sections, connection design,
weld design, materials, load analysis, code compliance, fabrication, clash detection,
IFC export, CNC/DSTV, Tekla integration, FEA, QA, interoperability, error handling,
performance optimization, visualization, ML enhancements, and regulatory compliance.
"""
import math
import json
import uuid
import os
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any
import warnings

# Deprecation notice: prefer `src.pipeline.pipeline_compat.run_pipeline` or
# the `src.pipeline.agents` package for new integrations. `pipeline_v2.py`
# remains for backwards compatibility during migration but will be removed
# in a future release.
warnings.warn(
    "module src.pipeline.pipeline_v2 is deprecated — use src.pipeline.pipeline_compat or src.pipeline.agents",
    DeprecationWarning,
)

# ============================================================================
# FEATURE 1: GEOMETRY & COORDINATE SYSTEMS
# ============================================================================

class CoordinateSystemManager:
    """Manages transformations between WCS (World), UCS (User), and Tekla CS"""
    def __init__(self):
        self.ucs_origin = [0.0, 0.0, 0.0]
        self.ucs_x = [1.0, 0.0, 0.0]
        self.ucs_y = [0.0, 1.0, 0.0]
        self.ucs_z = [0.0, 0.0, 1.0]
    
    def wcs_to_ucs(self, wcs_point):
        """Convert WCS coordinates to UCS"""
        x = wcs_point[0] - self.ucs_origin[0]
        y = wcs_point[1] - self.ucs_origin[1]
        z = wcs_point[2] - self.ucs_origin[2]
        return [
            x * self.ucs_x[0] + y * self.ucs_y[0] + z * self.ucs_z[0],
            x * self.ucs_x[1] + y * self.ucs_y[1] + z * self.ucs_z[1],
            x * self.ucs_x[2] + y * self.ucs_y[2] + z * self.ucs_z[2],
        ]
    
    def ucs_to_wcs(self, ucs_point):
        """Convert UCS coordinates to WCS"""
        return [
            self.ucs_origin[0] + ucs_point[0] * self.ucs_x[0] + ucs_point[1] * self.ucs_y[0] + ucs_point[2] * self.ucs_z[0],
            self.ucs_origin[1] + ucs_point[0] * self.ucs_x[1] + ucs_point[1] * self.ucs_y[1] + ucs_point[2] * self.ucs_z[1],
            self.ucs_origin[2] + ucs_point[0] * self.ucs_x[2] + ucs_point[1] * self.ucs_y[2] + ucs_point[2] * self.ucs_z[2],
        ]

class RotationMatrix3D:
    """Compute rotation matrices for arbitrary 3D orientations"""
    @staticmethod
    def rotation_matrix_x(angle_rad):
        """Rotation about X-axis"""
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        return [[1, 0, 0], [0, c, -s], [0, s, c]]
    
    @staticmethod
    def rotation_matrix_y(angle_rad):
        """Rotation about Y-axis"""
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    
    @staticmethod
    def rotation_matrix_z(angle_rad):
        """Rotation about Z-axis"""
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        return [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    
    @staticmethod
    def rotation_axis_angle(axis, angle_rad):
        """Rodrigues rotation formula: rotate around arbitrary axis"""
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

class CurvedMemberHandler:
    """Handle arcs, polylines, splines in member geometry"""
    @staticmethod
    def arc_to_polyline(center, radius, start_angle, end_angle, num_segments=20):
        """Discretize arc into polyline segments"""
        points = []
        for i in range(num_segments + 1):
            angle = start_angle + (end_angle - start_angle) * i / num_segments
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = center[2]
            points.append([x, y, z])
        return points
    
    @staticmethod
    def spline_to_polyline(control_points, num_segments=50):
        """Simplified spline interpolation (Catmull-Rom)"""
        # This is a simplified version; production code would use scipy.interpolate
        points = []
        n = len(control_points)
        if n < 2:
            return control_points
        for i in range(n - 1):
            for t in [j / num_segments for j in range(num_segments)]:
                p0 = control_points[max(0, i - 1)]
                p1 = control_points[i]
                p2 = control_points[(i + 1) % n]
                p3 = control_points[(i + 2) % n]
                # Catmull-Rom interpolation
                q = 0.5 * (2*p1 + (-p0 + p2)*t + (2*p0 - 5*p1 + 4*p2 - p3)*t*t + (-p0 + 3*p1 - 3*p2 + p3)*t*t*t)
                points.append(q)
        return points

class CamberCalculator:
    """Calculate fabrication camber to compensate for deflection"""
    @staticmethod
    def camber_from_deflection(load_kN, span_m, moment_of_inertia_cm4, e_gpa=200):
        """Calculate camber offset in mm for deflection compensation"""
        # deflection: delta = (5 * w * L^4) / (384 * E * I)
        # where w = load per unit length, E in Pa, I in m^4
        w = (load_kN * 1000) / span_m if span_m > 0 else 0
        I_m4 = moment_of_inertia_cm4 * 1e-8  # convert cm^4 to m^4
        E_pa = e_gpa * 1e9
        if E_pa == 0 or I_m4 == 0 or span_m == 0:
            return 0
        delta_m = (5 * w * (span_m ** 4)) / (384 * E_pa * I_m4)
        return delta_m * 1000  # convert to mm

class SkewCutGeometry:
    """Calculate bevel angles for non-perpendicular cuts"""
    @staticmethod
    def bevel_angle(member_axis, cutting_plane_normal):
        """Calculate bevel angle between member and cutting plane"""
        # angle between axis and plane = arcsin(dot product)
        dot = sum(member_axis[i] * cutting_plane_normal[i] for i in range(3))
        angle_rad = math.asin(min(1, max(-1, dot)))
        return math.degrees(angle_rad)
    
    @staticmethod
    def cope_radius_for_section(flange_radius_mm, member_depth_mm):
        """Standard cope radius based on section depth and flange radius"""
        # AISC: cope radius typically = flange radius or member depth, whichever is smaller
        return min(flange_radius_mm, member_depth_mm / 2)

class EccentricityResolver:
    """Handle work points vs. centerline offsets in connections"""
    @staticmethod
    def work_point_offset(connection_type, member_section_depth_mm):
        """Return work point offset from centerline (mm)"""
        if connection_type in ['bolted_base_plate', 'welded_base_plate']:
            return member_section_depth_mm / 2  # bottom of column
        elif connection_type in ['bolted_end_plate', 'welded_moment_connection']:
            return 0  # centerline
        else:
            return 0


# ---------------------------------------------------------------------------
# Migration override: replace common utilities (geometry, sections, loads)
# with modular implementations from the new package. This block is executed
# to progressively migrate behavior; it intentionally overrides the local
# definitions so callers of `pipeline_v2` get the modular implementations.
# Set `MIGRATE_COMMON_UTILS=False` to disable.
# ---------------------------------------------------------------------------
MIGRATE_COMMON_UTILS = True
if MIGRATE_COMMON_UTILS:
    try:
        from src.pipeline.geometry import (
            CoordinateSystemManager as _CoordNew,
            RotationMatrix3D as _RotNew,
            CurvedMemberHandler as _CurvedNew,
            CamberCalculator as _CamberNew,
            SkewCutGeometry as _SkewNew,
            EccentricityResolver as _EccNew,
        )
    except Exception:
        _CoordNew = _RotNew = _CurvedNew = _CamberNew = _SkewNew = _EccNew = None

    try:
        from src.pipeline.sections import (
            CompoundSectionBuilder as _CompNew,
            WebOpeningHandler as _WebNew,
            TorsionalPropertyCalculator as _TorsNew,
            PlasticAnalysisProperties as _PlasticNew,
        )
    except Exception:
        _CompNew = _WebNew = _TorsNew = _PlasticNew = None

    try:
        from src.pipeline.loads import (
            LoadCombinationAnalyzer as _LoadNew,
            WindLoadAnalyzer as _WindNew,
            SeismicLoadAnalyzer as _SeismicNew,
            PDeltaAnalyzer as _PDeltaNew,
            InfluenceLineAnalyzer as _InfluenceNew,
        )
    except Exception:
        _LoadNew = _WindNew = _SeismicNew = _PDeltaNew = _InfluenceNew = None

    _g = globals()
    if _CoordNew:
        _g['CoordinateSystemManager'] = _CoordNew
    if _RotNew:
        _g['RotationMatrix3D'] = _RotNew
    if _CurvedNew:
        _g['CurvedMemberHandler'] = _CurvedNew
    if _CamberNew:
        _g['CamberCalculator'] = _CamberNew
    if _SkewNew:
        _g['SkewCutGeometry'] = _SkewNew
    if _EccNew:
        _g['EccentricityResolver'] = _EccNew

    if _CompNew:
        _g['CompoundSectionBuilder'] = _CompNew
    if _WebNew:
        _g['WebOpeningHandler'] = _WebNew
    if _TorsNew:
        _g['TorsionalPropertyCalculator'] = _TorsNew
    if _PlasticNew:
        _g['PlasticAnalysisProperties'] = _PlasticNew

    if _LoadNew:
        _g['LoadCombinationAnalyzer'] = _LoadNew
    if _WindNew:
        _g['WindLoadAnalyzer'] = _WindNew
    if _SeismicNew:
        _g['SeismicLoadAnalyzer'] = _SeismicNew
    if _PDeltaNew:
        _g['PDeltaAnalyzer'] = _PDeltaNew
    if _InfluenceNew:
        _g['InfluenceLineAnalyzer'] = _InfluenceNew

# ============================================================================
# FEATURE 2: ADVANCED SECTION PROPERTIES
# ============================================================================

class CompoundSectionBuilder:
    """Build compound sections from plates and basic shapes"""
    @staticmethod
    def built_up_i_beam(flange_width_mm, flange_thickness_mm, web_height_mm, web_thickness_mm):
        """Calculate properties of built-up I-beam"""
        area_mm2 = 2 * flange_width_mm * flange_thickness_mm + web_height_mm * web_thickness_mm
        # moment of inertia about neutral axis
        web_ix = (web_thickness_mm * web_height_mm ** 3) / 12
        flange_dist = (web_height_mm / 2 + flange_thickness_mm / 2)
        flange_ix = 2 * ((flange_width_mm * flange_thickness_mm ** 3) / 12 + flange_width_mm * flange_thickness_mm * (flange_dist ** 2))
        ix = web_ix + flange_ix
        return {'area_mm2': area_mm2, 'Ixx_mm4': ix, 'weight_kg_per_m': area_mm2 * 7.85 / 1e6}

class WebOpeningHandler:
    """Handle castellated and cellular beams with web openings"""
    @staticmethod
    def opening_loss(opening_height_mm, opening_width_mm, num_openings, beam_depth_mm):
        """Estimate loss in moment of inertia due to web openings"""
        # simplified: loss proportional to opening area relative to web area
        loss_factor = (num_openings * opening_height_mm * opening_width_mm) / (beam_depth_mm * beam_depth_mm * 100)
        return min(0.3, loss_factor)  # cap at 30% loss
    
    @staticmethod
    def shear_capacity_reduction(num_openings, beam_height_mm, web_thickness_mm):
        """Reduce shear capacity for each opening"""
        base_capacity_mm2 = beam_height_mm * web_thickness_mm
        loss_per_opening = base_capacity_mm2 * 0.1  # 10% per opening (simplified)
        return max(base_capacity_mm2 * 0.5, base_capacity_mm2 - num_openings * loss_per_opening)

class TorsionalPropertyCalculator:
    """Calculate torsional properties J and Cw for advanced analysis"""
    @staticmethod
    def torsional_constant_i_beam(width_mm, depth_mm, flange_thk_mm, web_thk_mm):
        """Approximate torsional constant J for I-beam"""
        # J = (1/3) * (sum of b*t^3 for each element)
        j_flange = 2 * width_mm * (flange_thk_mm ** 3)
        j_web = depth_mm * (web_thk_mm ** 3)
        return (j_flange + j_web) / 3
    
    @staticmethod
    def warping_constant_i_beam(width_mm, depth_mm, flange_thk_mm, web_thk_mm):
        """Approximate warping constant Cw for I-beam"""
        # Cw = (1/12) * width^2 * (depth - flange_thk)^2 * flange_thk / (3*width + depth)
        h = depth_mm - flange_thk_mm
        cw = (width_mm ** 2) * (h ** 2) * flange_thk_mm / (36 * (3 * width_mm + depth_mm))
        return cw

class PlasticAnalysisProperties:
    """Calculate plastic section moduli and moment capacity"""
    @staticmethod
    def plastic_section_modulus(area_mm2, yield_stress_mpa, depth_mm):
        """Estimate plastic section modulus Zp"""
        # Zp typically 1.1-1.2x Sx for I-beams
        sx = area_mm2 * depth_mm / 4  # approximate elastic modulus
        zp = 1.15 * sx
        return zp
    
    @staticmethod
    def plastic_moment_capacity(zp_mm3, fy_mpa):
        """Calculate plastic moment capacity Mp"""
        return (zp_mm3 * fy_mpa) / 1e6  # return in kNm

# Small catalog
SECTION_CATALOG = [
    {"name": "W8x10", "area": 0.013, "Ixx": 8e-5, "weight_kg_per_m": 12.0, "price_per_kg": 1.2},
    {"name": "W10x12", "area": 0.020, "Ixx": 2.0e-4, "weight_kg_per_m": 17.0, "price_per_kg": 1.15},
    {"name": "HSS100x100x6", "area": 0.018, "Ixx": 1.6e-4, "weight_kg_per_m": 15.5, "price_per_kg": 1.25},
]

# section geometry approximations for IFC swept profiles
SECTION_GEOM = {
    'W8x10':{'type':'I','width':0.203,'depth':0.203,'web_thk':0.005,'flange_thk':0.006},
    'W10x12':{'type':'I','width':0.254,'depth':0.254,'web_thk':0.006,'flange_thk':0.007},
    'HSS100x100x6':{'type':'HollowRect','outer_w':0.100,'outer_h':0.100,'thickness':0.006},
    'REC200x50':{'type':'Rect','width':0.200,'depth':0.050,'thickness':0.005},
}

# ============================================================================
# FEATURE 5: MATERIAL SPECIFICATIONS & DATABASE
# ============================================================================

MATERIAL_DATABASE = {
    'A36': {'Fy': 250, 'Fu': 400, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850, 'use': 'general', 'cost_premium': 1.0, 'availability': 'excellent', 'fracture_toughness_cvn': 20},
    'A572_Gr50': {'Fy': 345, 'Fu': 450, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850, 'use': 'high_strength', 'cost_premium': 1.15, 'availability': 'good', 'fracture_toughness_cvn': 25},
    'A572_Gr65': {'Fy': 450, 'Fu': 550, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850, 'use': 'very_high_strength', 'cost_premium': 1.35, 'availability': 'moderate', 'fracture_toughness_cvn': 20},
    'A992': {'Fy': 345, 'Fu': 450, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850, 'use': 'general_high_strength', 'cost_premium': 1.12, 'availability': 'excellent', 'fracture_toughness_cvn': 27},
    'A500_Gr_B_Round': {'Fy': 317, 'Fu': 413, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850, 'use': 'hss', 'cost_premium': 1.25, 'availability': 'good', 'fracture_toughness_cvn': 22},
    'A588': {'Fy': 345, 'Fu': 485, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850, 'use': 'weathering_steel', 'cost_premium': 1.4, 'availability': 'moderate', 'fracture_toughness_cvn': 25},
    'A913': {'Fy': 450, 'Fu': 620, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850, 'use': 'high_strength_railroad', 'cost_premium': 1.5, 'availability': 'limited', 'fracture_toughness_cvn': 27},
    'A514': {'Fy': 690, 'Fu': 760, 'E': 200000, 'G': 77000, 'density_kg_m3': 7850, 'use': 'quenched_tempered', 'cost_premium': 1.8, 'availability': 'limited', 'fracture_toughness_cvn': 30},
    'S355': {'Fy': 355, 'Fu': 510, 'E': 210000, 'G': 81000, 'density_kg_m3': 7850, 'use': 'european', 'cost_premium': 1.2, 'availability': 'good', 'fracture_toughness_cvn': 27},
}

BOLT_SPECIFICATIONS = {
    'M12': {'dia_mm': 12, 'tensile_area_mm2': 84.3, 'grades': ['4.6', '5.8', '8.8', '10.9']},
    'M16': {'dia_mm': 16, 'tensile_area_mm2': 156.7, 'grades': ['4.6', '5.8', '8.8', '10.9']},
    'M20': {'dia_mm': 20, 'tensile_area_mm2': 244.8, 'grades': ['4.6', '5.8', '8.8', '10.9']},
    'M24': {'dia_mm': 24, 'tensile_area_mm2': 352.5, 'grades': ['5.8', '8.8', '10.9']},
    'M32': {'dia_mm': 32, 'tensile_area_mm2': 561, 'grades': ['5.8', '8.8', '10.9']},
    'M39': {'dia_mm': 39, 'tensile_area_mm2': 817, 'grades': ['8.8', '10.9']},
}

BOLT_STRENGTH = {
    '4.6': {'ultimate_mpa': 400, 'yield_mpa': 240, 'preload_factor': 0.7},
    '5.8': {'ultimate_mpa': 500, 'yield_mpa': 400, 'preload_factor': 0.7},
    '8.8': {'ultimate_mpa': 800, 'yield_mpa': 640, 'preload_factor': 0.7},
    '10.9': {'ultimate_mpa': 1000, 'yield_mpa': 900, 'preload_factor': 0.7},
}

class MaterialSelector:
    """Select optimal material grade based on load, cost, availability"""
    @staticmethod
    def select_grade(axial_kN, moment_kNm, cost_priority=0.5, availability_priority=0.3):
        """Select material grade (0.0=cost optimized, 1.0=strength optimized)"""
        required_fy = max(250, (abs(axial_kN) * 1000) / (100 * 250) + (abs(moment_kNm) * 1000) / (100 * 250))
        candidates = []
        for grade, props in MATERIAL_DATABASE.items():
            if props['Fy'] >= required_fy * 0.8:
                score = (cost_priority * (1 / props['cost_premium']) + 
                        availability_priority * {'excellent': 1.0, 'good': 0.8, 'moderate': 0.5, 'limited': 0.2}.get(props['availability'], 0.5))
                candidates.append((score, grade))
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]
        return 'A36'  # default fallback

class CoatingSpecifier:
    """Specify paint systems and galvanizing thickness"""
    @staticmethod
    def paint_system_recommendation(environment, section_thickness_mm, cost_priority=0.5):
        """Recommend paint system based on environment"""
        if environment == 'marine':
            return {'system': 'High-build epoxy', 'total_thickness_mm': 250, 'coats': 3, 'cost_factor': 1.5}
        elif environment == 'industrial':
            return {'system': 'Two-coat epoxy', 'total_thickness_mm': 150, 'coats': 2, 'cost_factor': 1.2}
        elif environment == 'mild':
            return {'system': 'Shop primer + field paint', 'total_thickness_mm': 100, 'coats': 2, 'cost_factor': 1.0}
        else:
            return {'system': 'Mill scale + shop primer', 'total_thickness_mm': 50, 'coats': 1, 'cost_factor': 0.7}
    
    @staticmethod
    def hot_dip_galvanize_thickness(thickness_mm):
        """ASTM A123 galvanizing thickness based on steel thickness"""
        if thickness_mm < 1.6:
            return 55  # µm, minimum
        elif thickness_mm < 3.2:
            return 70
        elif thickness_mm < 6.4:
            return 85
        else:
            return 100

# ============================================================================
# FEATURE 6: LOAD ANALYSIS ENGINE
# ============================================================================

class LoadCombinationGenerator:
    """Generate LRFD and ASD load combinations per AISC 360 and ASCE 7"""
    @staticmethod
    def aisc_lrfd_combinations():
        """AISC 360 LRFD load combinations"""
        return [
            {'name': 'LRFD-1', 'combo': '1.4D', 'dead': 1.4, 'live': 0, 'wind': 0, 'snow': 0, 'seismic': 0},
            {'name': 'LRFD-2', 'combo': '1.2D+1.6L', 'dead': 1.2, 'live': 1.6, 'wind': 0, 'snow': 0, 'seismic': 0},
            {'name': 'LRFD-3', 'combo': '1.2D+1.6S', 'dead': 1.2, 'live': 0, 'wind': 0, 'snow': 1.6, 'seismic': 0},
            {'name': 'LRFD-4', 'combo': '1.2D+1.0W+0.5L', 'dead': 1.2, 'live': 0.5, 'wind': 1.0, 'snow': 0, 'seismic': 0},
            {'name': 'LRFD-5', 'combo': '1.2D+1.0E', 'dead': 1.2, 'live': 0, 'wind': 0, 'snow': 0, 'seismic': 1.0},
        ]
    
    @staticmethod
    def aisc_asd_combinations():
        """AISC 360 ASD load combinations"""
        return [
            {'name': 'ASD-1', 'combo': 'D', 'dead': 1.0, 'live': 0, 'wind': 0},
            {'name': 'ASD-2', 'combo': 'D+L', 'dead': 1.0, 'live': 1.0, 'wind': 0},
            {'name': 'ASD-3', 'combo': 'D+0.75L+0.75W', 'dead': 1.0, 'live': 0.75, 'wind': 0.75},
        ]

class WindLoadCalculator:
    """Calculate wind loads per ASCE 7-22"""
    @staticmethod
    def velocity_pressure(basic_wind_speed_mph, exposure_category='B', importance_factor=1.0):
        """Calculate velocity pressure"""
        # ASCE 7: qz = 0.613 * Kd * Kct * Kl * Ke * V^2 * I / 1000 (psf)
        kd = {'A': 0.85, 'B': 0.90, 'C': 0.98, 'D': 1.00}.get(exposure_category, 0.90)
        kct = 1.0  # directional reduction factor
        kl = 0.85  # topographic factor
        ke = 1.15  # ground elevation factor
        qz_psf = (0.613 * kd * kct * kl * ke * (basic_wind_speed_mph ** 2) * importance_factor) / 1000
        return qz_psf * 47.88  # convert to Pa

class SeismicLoadCalculator:
    """Calculate seismic loads per ASCE 7-22"""
    @staticmethod
    def design_base_shear(ss, s1, t, w, r, ie_factor=1.0):
        """Calculate design base shear V"""
        # ASCE 7 Chapter 12
        sds = (2/3) * ss
        sd1 = (2/3) * s1
        cs = sd1 / (r / ie_factor) / t
        cs_max = sds / (r / ie_factor)
        cs = min(cs, cs_max)
        cs_min = 0.044 * sds * ie_factor
        cs = max(cs, cs_min)
        v = cs * w
        return v

class PDeltaAnalyzer:
    """Analyze P-Delta (second-order) effects"""
    @staticmethod
    def amplification_factor(gravity_load_kN, lateral_drift_m, story_height_m):
        """Calculate P-Delta amplification factor θ"""
        if story_height_m == 0:
            return 1.0
        theta = gravity_load_kN * lateral_drift_m / (story_height_m * 100)  # simplified
        return max(1.0, min(1.5, 1.0 + theta))

class InfluenceLineGenerator:
    """Generate influence lines for moving loads on continuous members"""
    @staticmethod
    def simple_span_influence(span_m, num_points=21):
        """Influence line for simple span (shear at mid-span)"""
        lines = []
        for i in range(num_points):
            x = span_m * i / (num_points - 1)
            # Shear influence line: V(x) = 1 - 2*x/L for 0 <= x <= L/2
            if x <= span_m / 2:
                influence = 1.0 - 2 * x / span_m
            else:
                influence = -1.0 + 2 * x / span_m
            lines.append({'x_m': x, 'influence': influence})
        return lines

# ============================================================================
# FEATURE 7: CODE COMPLIANCE CHECKERS
# ============================================================================

class AISC360Checker:
    """Complete AISC 360-16 compliance checks"""
    @staticmethod
    def chapter_d_tension(axial_kN, section_area_mm2, fy_mpa, fu_mpa, num_bolts_per_line=4, bolt_dia_mm=20):
        """AISC 360 Chapter D: Members in Tension"""
        # Gross section yielding: Tn = Fy * Ag
        ag_mm2 = section_area_mm2
        tn_kn_yield = (fy_mpa * ag_mm2) / 1e6
        
        # Net section rupture: Tn = 0.75 * Fu * An (conservative)
        an_mm2 = ag_mm2 - (num_bolts_per_line * bolt_dia_mm * 2)  # subtract bolt holes
        tn_kn_rupture = (0.75 * fu_mpa * an_mm2) / 1e6
        
        capacity_kn = min(tn_kn_yield, tn_kn_rupture)
        demand_kn = abs(axial_kN)
        
        return {
            'capacity_kN': capacity_kn,
            'demand_kN': demand_kn,
            'unity_check': demand_kn / capacity_kn if capacity_kn > 0 else 0,
            'governing': 'yield' if tn_kn_yield < tn_kn_rupture else 'rupture',
            'pass': demand_kn <= capacity_kn
        }
    
    @staticmethod
    def chapter_e_compression(axial_kN, section_area_mm2, radius_gyration_mm, kl_m, fy_mpa, e_gpa=200):
        """AISC 360 Chapter E: Members in Compression"""
        kl_mm = kl_m * 1000
        slenderness = kl_mm / radius_gyration_mm if radius_gyration_mm > 0 else 0
        
        # Elastic buckling stress
        fe = (math.pi ** 2 * e_gpa * 1000) / (slenderness ** 2) if slenderness > 0 else fy_mpa
        
        if fe >= fy_mpa * 0.5:
            # Inelastic buckling
            fcr = (0.658 ** (fy_mpa / fe)) * fy_mpa
        else:
            # Elastic buckling
            fcr = 0.877 * fe
        
        capacity_kn = (fcr * section_area_mm2) / 1e6
        demand_kn = abs(axial_kN)
        
        return {
            'capacity_kN': capacity_kn,
            'demand_kN': demand_kn,
            'slenderness': slenderness,
            'unity_check': demand_kn / capacity_kn if capacity_kn > 0 else 0,
            'pass': demand_kn <= capacity_kn
        }
    
    @staticmethod
    def chapter_f_flexure(moment_kNm, section_modulus_mm3, fy_mpa, lb_m, ly_m, depth_mm):
        """AISC 360 Chapter F: Members in Bending"""
        # Simplified: assume yielding controls
        mn = (fy_mpa * section_modulus_mm3) / 1e6
        capacity_kNm = mn
        demand_kNm = abs(moment_kNm)
        
        # Check lateral-torsional buckling if unbraced
        lp = 1.76 * (depth_mm / 1000) * math.sqrt(200000 / fy_mpa)
        if lb_m > lp:
            # Lateral-torsional buckling applies (simplified)
            capacity_kNm *= 0.85
        
        return {
            'capacity_kNm': capacity_kNm,
            'demand_kNm': demand_kNm,
            'unity_check': demand_kNm / capacity_kNm if capacity_kNm > 0 else 0,
            'pass': demand_kNm <= capacity_kNm
        }
    
    @staticmethod
    def chapter_h_combined(axial_kN, moment_kNm, axial_capacity_kN, moment_capacity_kNm, connection_type='standard'):
        """AISC 360 Chapter H: Combined Forces and Torsion"""
        if axial_capacity_kN == 0 or moment_capacity_kNm == 0:
            return {'pass': False, 'unity_check': float('inf')}
        
        # H1-1a: P/2Pc + (Cmx*Mx)/(1 - P/Pe)*Mcx + (Cmy*My)/(1 - P/Pe)*Mcy <= 1.0
        # Simplified for uniaxial bending:
        unity = abs(axial_kN) / (2 * axial_capacity_kN) + abs(moment_kNm) / moment_capacity_kNm
        
        return {
            'unity_check': unity,
            'pass': unity <= 1.0
        }

class AISC341SeismicChecker:
    """AISC 341 Seismic Provisions"""
    @staticmethod
    def width_thickness_check(flange_width_mm, flange_thickness_mm, web_depth_mm, web_thickness_mm, sds=0.5):
        """Check width-thickness ratios for special moment frames"""
        # AISC 341 Table D1.1: Limiting Width-Thickness Ratios
        limits_smf = {'flange': 0.30, 'web': 2.45}
        
        flange_ratio = (flange_width_mm / 2) / flange_thickness_mm
        web_ratio = web_depth_mm / web_thickness_mm
        
        return {
            'flange_ratio': flange_ratio,
            'flange_limit': limits_smf['flange'] * math.sqrt(200000 / 345),  # per AISC F2 scaling
            'web_ratio': web_ratio,
            'web_limit': limits_smf['web'] * math.sqrt(200000 / 345),
            'flange_pass': flange_ratio <= limits_smf['flange'] * math.sqrt(200000 / 345),
            'web_pass': web_ratio <= limits_smf['web'] * math.sqrt(200000 / 345),
        }

# ============================================================================
# CONNECTION TYPES CATALOG (Tekla/Revit Standards)
# ============================================================================
CONNECTION_TYPES = {
    'beam_to_column': {
        'description': 'Beam to column connection',
        'subtypes': [
            {
                'name': 'bolted_end_plate',
                'category': 'beam_to_column',
                'properties': {
                    'plate_thickness_mm': [10, 12, 14, 16, 18, 20],
                    'bolt_diameter_mm': [16, 20, 24],
                    'bolt_grade': ['4.6', '5.8', '8.8', '10.9'],
                    'bolt_min_count': 4,
                    'bolt_max_count': 16,
                    'edge_distance_mm': 50,
                    'gauge_distance_mm': 100,
                },
                'weld_types': ['none'],  # bolted connection
                'ai_selection_rules': 'Calculate plate thickness based on beam moment; use 8.8 grade for high load'
            },
            {
                'name': 'welded_moment_connection',
                'category': 'beam_to_column',
                'properties': {
                    'weld_size_mm': [6, 8, 10, 12, 14],
                    'weld_type': 'fillet_both_sides',
                    'penetration_full': True,
                    'reinforcement_mm': 3,
                    'stiffener_plate': True,
                },
                'weld_types': ['fillet_weld', 'cjp_groove_weld'],
                'ai_selection_rules': 'Use for moment frames; ensure column web stiffeners'
            },
            {
                'name': 'clip_angle_bolted',
                'category': 'beam_to_column',
                'properties': {
                    'angle_size_mm': [75, 90, 100],
                    'leg_length_mm': [80, 100, 120],
                    'thickness_mm': [8, 10, 12],
                    'bolt_count_per_leg': [2, 3, 4],
                    'bolt_diameter_mm': [16, 20],
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'Simple beam-column for pin connections; quick fabrication'
            },
            {
                'name': 'flush_end_plate',
                'category': 'beam_to_column',
                'properties': {
                    'plate_thickness_mm': [8, 10, 12, 14],
                    'bolt_diameter_mm': [16, 20],
                    'bolt_count': [4, 6, 8],
                    'flush_face': True,
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'For architecturally exposed steel with hidden bolting'
            },
        ]
    },
    'beam_to_beam': {
        'description': 'Beam to beam connection (secondary)',
        'subtypes': [
            {
                'name': 'bolted_web_cleat',
                'category': 'beam_to_beam',
                'properties': {
                    'cleat_thickness_mm': [6, 8, 10],
                    'cleat_height_mm': [150, 200, 250],
                    'bolt_count': [4, 6, 8],
                    'bolt_diameter_mm': [16, 20],
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'Standard for secondary beams; minimize fabrication'
            },
            {
                'name': 'bolted_seat_cleat',
                'category': 'beam_to_beam',
                'properties': {
                    'cleat_thickness_mm': [10, 12],
                    'cleat_length_mm': [200, 250, 300],
                    'bearing_plate': True,
                    'bolt_count': [3, 4],
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'For gravity loads on secondary beams'
            },
            {
                'name': 'welded_web_connection',
                'category': 'beam_to_beam',
                'properties': {
                    'weld_size_mm': [5, 6, 8],
                    'weld_length_mm': [100, 150, 200],
                    'weld_both_sides': True,
                },
                'weld_types': ['fillet_weld', 'pjp_weld'],
                'ai_selection_rules': 'For structural continuity; higher strength'
            },
        ]
    },
    'column_to_base': {
        'description': 'Column to foundation base plate',
        'subtypes': [
            {
                'name': 'bolted_base_plate',
                'category': 'column_to_base',
                'properties': {
                    'plate_thickness_mm': [12, 16, 20, 25, 30],
                    'plate_dimensions_mm': [[400, 400], [500, 500], [600, 600], [700, 700]],
                    'anchor_bolt_diameter_mm': [20, 25, 32],
                    'anchor_bolt_count': [4, 8, 12],
                    'stud_height_mm': [50, 75, 100],
                    'grout_thickness_mm': 50,
                },
                'weld_types': ['none'],  # welded to column in plant
                'ai_selection_rules': 'Calculate for axial + moment; ensure bearing capacity'
            },
            {
                'name': 'welded_base_plate',
                'category': 'column_to_base',
                'properties': {
                    'plate_thickness_mm': [16, 20, 25],
                    'weld_size_mm': [8, 10, 12, 14],
                    'weld_all_around': True,
                    'stiffener_plates': True,
                },
                'weld_types': ['fillet_weld', 'pjp_weld', 'cjp_weld'],
                'ai_selection_rules': 'For rigid connections; typically shop-welded'
            },
            {
                'name': 'expansion_base_plate',
                'category': 'column_to_base',
                'properties': {
                    'plate_thickness_mm': [12, 16, 20],
                    'expansion_slot_length_mm': 50,
                    'anchor_bolt_count': [4, 8],
                    'bolt_diameter_mm': [20, 25],
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'Allow thermal expansion; common in long-span frames'
            },
        ]
    },
    'bracing': {
        'description': 'Bracing and diagonal connections',
        'subtypes': [
            {
                'name': 'bolted_gusset_plate',
                'category': 'bracing',
                'properties': {
                    'gusset_thickness_mm': [8, 10, 12, 14],
                    'bolt_diameter_mm': [16, 20],
                    'bolt_count': [4, 6, 8, 12],
                    'gusset_shape': ['triangular', 'rectangular', 'polygonal'],
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'Calculate for axial tension/compression in diagonals'
            },
            {
                'name': 'welded_gusset_plate',
                'category': 'bracing',
                'properties': {
                    'gusset_thickness_mm': [8, 10, 12],
                    'weld_size_mm': [6, 8, 10],
                    'weld_all_sides': True,
                    'shear_tab': True,
                },
                'weld_types': ['fillet_weld', 'pjp_weld'],
                'ai_selection_rules': 'Shop-welded gussets; higher efficiency'
            },
            {
                'name': 'tube_splice',
                'category': 'bracing',
                'properties': {
                    'splice_plate_thickness_mm': [6, 8, 10],
                    'bolt_count': [4, 8, 12],
                    'bolt_diameter_mm': [16, 20],
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'For hollow sections (HSS); minimize eccentricity'
            },
        ]
    },
    'truss': {
        'description': 'Truss member connections',
        'subtypes': [
            {
                'name': 'bolted_chord_connection',
                'category': 'truss',
                'properties': {
                    'gusset_thickness_mm': [6, 8, 10],
                    'bolt_diameter_mm': [12, 16, 20],
                    'bolt_count': [3, 4, 6, 8],
                    'eccentricity_tolerance_mm': 10,
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'Minimize eccentricity; check chord stress'
            },
            {
                'name': 'welded_chord_connection',
                'category': 'truss',
                'properties': {
                    'weld_size_mm': [4, 5, 6, 8],
                    'weld_all_around': True,
                    'penetration_full': True,
                },
                'weld_types': ['pjp_weld', 'cjp_weld'],
                'ai_selection_rules': 'For shop-fabricated trusses; calculate weld capacity'
            },
            {
                'name': 'tube_node',
                'category': 'truss',
                'properties': {
                    'node_reinforcement_mm': [3, 5],
                    'through_brace': True,
                },
                'weld_types': ['pjp_weld', 'cjp_weld'],
                'ai_selection_rules': 'For tubular trusses; check AISC/Eurocode formulas'
            },
        ]
    },
    'secondary_steel': {
        'description': 'Secondary steel and misc. connections',
        'subtypes': [
            {
                'name': 'stair_carriage_bolted',
                'category': 'secondary_steel',
                'properties': {
                    'bolt_diameter_mm': [12, 16, 20],
                    'bolt_count': [2, 3, 4],
                    'washer_thickness_mm': 3,
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'For stairs, platforms; minimal bolting'
            },
            {
                'name': 'ledger_bolted',
                'category': 'secondary_steel',
                'properties': {
                    'bolt_spacing_mm': [400, 600, 800],
                    'bolt_diameter_mm': [20, 24],
                    'bolt_count': [4, 6, 8],
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'Connection for floor beams to walls/columns'
            },
            {
                'name': 'equipment_anchor',
                'category': 'secondary_steel',
                'properties': {
                    'anchor_bolt_diameter_mm': [16, 20, 24],
                    'anchor_bolt_count': [4, 8],
                    'leveling_plate': True,
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'For machinery/equipment mounting'
            },
        ]
    },
    'plate_attachment': {
        'description': 'Plate and attachment connections',
        'subtypes': [
            {
                'name': 'bolted_cover_plate',
                'category': 'plate_attachment',
                'properties': {
                    'plate_thickness_mm': [6, 8, 10, 12],
                    'plate_width_mm': [100, 150, 200, 300],
                    'bolt_spacing_mm': [100, 150, 200],
                    'bolt_diameter_mm': [12, 16, 20],
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'For reinforcing members; calculate bearing/tension'
            },
            {
                'name': 'welded_stiffener',
                'category': 'plate_attachment',
                'properties': {
                    'stiffener_thickness_mm': [6, 8, 10],
                    'weld_size_mm': [5, 6, 8],
                    'weld_length_mm': [200, 300, 400],
                },
                'weld_types': ['fillet_weld', 'pjp_weld'],
                'ai_selection_rules': 'For column/beam web stiffening; prevent buckling'
            },
            {
                'name': 'bolted_splice_plate',
                'category': 'plate_attachment',
                'properties': {
                    'splice_plate_thickness_mm': [10, 12, 14, 16],
                    'bolt_count': [6, 8, 10, 12],
                    'bolt_diameter_mm': [20, 24],
                    'bolt_rows': [2, 3],
                },
                'weld_types': ['none'],
                'ai_selection_rules': 'For member splices; ensure full capacity transfer'
            },
        ]
    },
}

# ============================================================================
# WELD TYPES CATALOG (AISC 2016, AWS D1.1, Eurocode 3)
# ============================================================================
WELD_TYPES = {
    'basic': {
        'fillet_weld': {
            'description': 'Fillet weld (most common)',
            'sizes_mm': [3, 4, 5, 6, 8, 10, 12, 14, 16],
            'throat_thickness_mm_formula': 'leg_size * 0.707',  # a = s * 0.707
            'leg_sizes_mm': [3, 4, 5, 6, 8, 10, 12, 14, 16],
            'effective_length_ratio': 0.85,  # reduce for short segments
            'reinforcement_mm': 1.5,  # typical reinforcement
            'attributes': ['intermittent', 'stitch', 'tack', 'all-around'],
            'limitations': {
                'min_size_mm': 3,
                'max_size_single_pass_mm': 8,
                'max_size_multi_pass_mm': 16,
            },
            'ai_rules': 'Calculate throat thickness for shear/tension; common in shop & field'
        },
        'butt_weld': {
            'description': 'Butt weld (full joint penetration)',
            'types': ['groove', 'flare-groove'],
            'groove_types': ['V', 'U', 'J', 'bevel', 'edge'],
            'root_opening_mm': [2, 3, 4, 5, 6],
            'bevel_angle_deg': [30, 37.5, 45],
            'depth_of_bevel_mm': [4, 5, 6, 8],
            'back_chip': False,
            'back_bead': True,
            'reinforcement_mm': 2,
            'ai_rules': 'Full penetration; used for splice plates, primary tension members'
        },
        'plug_weld': {
            'description': 'Plug weld through lap joint',
            'hole_diameter_mm': [12, 16, 20, 25, 32],
            'hole_spacing_mm': [50, 75, 100, 150],
            'minimum_hole_diameter_mm': 10,
            'penetration_depth_mm': 6,  # at least 0.5 * material thickness
            'ai_rules': 'Use for lap joints; limited shear capacity'
        },
        'slot_weld': {
            'description': 'Slot weld (elliptical hole)',
            'slot_length_mm': [50, 75, 100, 150, 200],
            'slot_width_mm': [12, 16, 20, 25],
            'penetration_depth_mm': 6,
            'corner_radius_mm': 8,
            'ai_rules': 'For load transfer in lap joints; higher capacity than plug'
        },
        'spot_weld': {
            'description': 'Spot weld (resistance weld)',
            'diameter_mm': [6, 8, 10, 12, 16],
            'spacing_mm': [50, 75, 100, 150],
            'ai_rules': 'Automated; mainly for deck/grating; limited structural use'
        },
        'seam_weld': {
            'description': 'Seam weld (continuous spot welds)',
            'width_mm': [6, 8, 10, 12],
            'spacing_between_spots_mm': [6, 8, 10],
            'ai_rules': 'Continuous line; similar to fillet but faster in automation'
        },
    },
    'advanced': {
        'cjp_groove_weld': {
            'description': 'Complete Joint Penetration (CJP) groove weld',
            'minimum_effective_length_mm': 1.4 * 25,  # Minimum 1.4x25mm for 25mm thk
            'bevel_types': ['V', 'bevel', 'U', 'J', 'double-bevel'],
            'root_opening_mm': [2, 3, 4, 5, 6],
            'bevel_angle_deg': [30, 37.5, 45],
            'back_chip': True,  # CRITICAL: must remove slag
            'back_bead': True,
            'penetration_full': True,
            'reinforcement_mm': [2, 3],
            'ai_rules': 'CJP = full strength; required for tension member splices; check AISC Table 8-42'
        },
        'pjp_groove_weld': {
            'description': 'Partial Joint Penetration (PJP) groove weld',
            'minimum_thickness_mm': 10,
            'minimum_penetration_depth_mm': 10,  # depends on thickness
            'penetration_depth_ratio': 0.5,  # typically 50% of material thickness
            'bevel_types': ['V', 'bevel', 'U', 'J'],
            'root_opening_mm': [2, 3, 4, 5],
            'bevel_angle_deg': [30, 37.5, 45],
            'reinforcement_mm': 1.5,
            'ai_rules': 'PJP = reduced strength factor (0.5-0.85); used for members with shear dominance'
        },
        'corner_weld': {
            'description': 'Corner weld (90° joint)',
            'leg_sizes_mm': [3, 4, 5, 6, 8, 10],
            'weld_type': 'fillet or groove',
            'ai_rules': 'Common in flanged connections; calculate based on loading'
        },
        'edge_weld': {
            'description': 'Edge weld (along member edge)',
            'leg_sizes_mm': [3, 4, 5, 6, 8],
            'penetration_partial': True,
            'ai_rules': 'Lightweight welds; acceptable for secondary connections'
        },
    },
    'attributes': {
        'back_chip': {
            'description': 'Remove slag from weld root, then reweld',
            'process': 'pneumatic chipping → reweld',
            'inspection': 'required after chipping',
            'cost_premium': 1.3,  # 30% more expensive
        },
        'intermittent': {
            'description': 'Intermittent fillet weld (skip pattern)',
            'pitch_mm': [150, 200, 300, 400],  # spacing between weld segments
            'length_mm': [50, 75, 100, 150],  # length of each segment
            'efficiency_factor': 0.7,  # reduce capacity vs continuous
            'ai_rules': 'Cost reduction; verify capacity reduction acceptable'
        },
        'stitch': {
            'description': 'Stitch weld (similar to intermittent)',
            'segment_length_mm': [50, 75, 100],
            'gap_mm': [25, 50, 100],
            'ai_rules': 'For field assembly; ensures alignment'
        },
        'tack': {
            'description': 'Temporary tack welds (removed before final weld)',
            'size_mm': [3, 4, 5],
            'length_mm': [25, 50],
            'final_removal': True,
            'ai_rules': 'For assembly holding; not counted in capacity'
        },
        'all_around': {
            'description': 'Weld all around circumference',
            'note': 'AISC symbol: circle around weld',
            'ai_rules': 'Applies to circular connections, tube splices'
        },
    },
}

try:
    from .ml_models import load_member_type_classifier
    from .miner import extract_from_dxf, extract_from_ifc
except Exception:
    def load_member_type_classifier():
        return None
    def extract_from_dxf(path_or_entities):
        # fallback: if given a list of simple entities, use the internal miner_from_dxf
        try:
            return miner_from_dxf(path_or_entities)
        except Exception:
            raise RuntimeError('miner.extract_from_dxf not available and fallback failed')
    def extract_from_ifc(path_or_model):
        raise RuntimeError('miner.extract_from_ifc not available in this environment')
try:
    from .ml_models import load_section_selector
except Exception:
    def load_section_selector():
        return None


def length(p0, p1):
    return math.dist((p0[0], p0[1], p0[2]), (p1[0], p1[1], p1[2]))


def unit_vector(p0, p1):
    L = length(p0, p1)
    if L == 0:
        return (0,0,0)
    return ((p1[0]-p0[0])/L, (p1[1]-p0[1])/L, (p1[2]-p0[2])/L)


def vec_angle_deg(v):
    vx,vy,vz = v
    horiz = math.hypot(vx, vy)
    return math.degrees(math.atan2(abs(vz), horiz))


def pick_section_for_member(axial_force, bending_moment, span):
    candidates = []
    for s in SECTION_CATALOG:
        axial_capacity = s['area'] * 250e6 * 0.6
        bending_capacity = s['Ixx'] * 250e6 * 0.6 / (span/2 if span>0.01 else 0.01)
        if axial_force <= axial_capacity and bending_moment <= bending_capacity:
            cost = s['weight_kg_per_m'] * span * s['price_per_kg']
            candidates.append((cost, s))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]
    return SECTION_CATALOG[0]


def miner_from_dxf(dxf_entities):
    members = []
    for ent in dxf_entities:
        members.append({'id': str(uuid.uuid4()), 'start': ent['start'], 'end': ent['end'], 'length': length(ent['start'], ent['end']), 'layer': ent.get('layer')})
    return {'members': members}


def engineer_standardize(input_json):
    # normalize input from miner: ensure start/end are mutable lists, length present, and include source/raw info
    clf = None
    try:
        clf = load_member_type_classifier()
    except Exception:
        clf = None
    members = input_json.get('members', [])
    out = {'members': []}
    for m in members:
        # normalize coordinate types to lists of floats so later agents can modify them
        s = list(m.get('start') if m.get('start') is not None else (0.0, 0.0, 0.0))
        e = list(m.get('end') if m.get('end') is not None else (0.0, 0.0, 0.0))
        s = [float(s[0]), float(s[1]), float(s[2])] if len(s) >= 3 else [float(s[0]), float(s[1]), 0.0]
        e = [float(e[0]), float(e[1]), float(e[2])] if len(e) >= 3 else [float(e[0]), float(e[1]), 0.0]
        L = m.get('length') if m.get('length') is not None else length(s, e)
        v = unit_vector(s, e)
        angle = vec_angle_deg(v)
        # midpoint and local axes: useful for later geometry ops and CNC orientation
        mid = [(s[0] + e[0]) / 2.0, (s[1] + e[1]) / 2.0, (s[2] + e[2]) / 2.0]
        # choose a reference direction for local Y (prefer global Z unless parallel)
        if abs(v[2]) < 0.9:
            ref_cand = (0.0, 0.0, 1.0)
        else:
            ref_cand = (0.0, 1.0, 0.0)
        # orthonormalize: project out component along v
        proj = v[0]*ref_cand[0] + v[1]*ref_cand[1] + v[2]*ref_cand[2]
        ref = (ref_cand[0] - proj*v[0], ref_cand[1] - proj*v[1], ref_cand[2] - proj*v[2])
        # normalize ref
        rlen = math.sqrt(ref[0]*ref[0] + ref[1]*ref[1] + ref[2]*ref[2]) or 1.0
        ydir = (ref[0]/rlen, ref[1]/rlen, ref[2]/rlen)
        # local x is axis direction, local z is cross(x,y)
        xdir = (v[0], v[1], v[2])
        zdir = (xdir[1]*ydir[2] - xdir[2]*ydir[1], xdir[2]*ydir[0] - xdir[0]*ydir[2], xdir[0]*ydir[1] - xdir[1]*ydir[0])
        # rotation about global Z for simple orientation (useful for CNC/labels)
        rot_z = math.degrees(math.atan2(xdir[1], xdir[0]))
        typ = None
        if clf is not None:
            try:
                pred = clf.predict([[float(L), float(angle)]])[0]
                typ = {0: 'beam', 1: 'column', 2: 'brace'}.get(int(pred), None)
            except Exception:
                typ = None
        # layer heuristics can override classifier
        layer_hint = (m.get('layer') or '').upper() if m.get('layer') else ((m.get('raw',{}) or {}).get('layer') or '')
        if layer_hint:
            lh = layer_hint.upper()
            if 'COL' in lh or 'COLUMN' in lh: typ = 'column'
            elif 'BEAM' in lh or 'BM' in lh: typ = 'beam'
        if typ is None:
            if angle > 60:
                typ = 'column'
            elif angle < 20:
                typ = 'beam'
            else:
                typ = 'brace'
        layer = m.get('layer') or (m.get('raw', {}) or {}).get('layer') or (m.get('raw', {}) or {}).get('dxf_layer')
        out['members'].append({'id': m.get('id', str(uuid.uuid4())), 'start': s, 'end': e, 'length': float(L), 'type': typ, 'orientation': v, 'midpoint': mid, 'local_axes': {'x': xdir, 'y': ydir, 'z': zdir}, 'rotation_z_deg': rot_z, 'layer': layer, 'source': m.get('source'), 'raw': m.get('raw')})
    return out


def load_path_resolver(std_json):
    out = {'members': []}
    for m in std_json['members']:
        span = m['length']
        if m['type']=='beam':
            w=5.0; axial=0.1*span; moment=w*span**2/8.0; shear=w*span/2.0
        elif m['type']=='column':
            axial=50.0*(1 if span<3 else span/3); moment=0.2*axial*span; shear=axial*0.05
        else:
            axial=20.0; moment=0.1*axial*span; shear=axial*0.05
        out['members'].append({**m, 'loads': {'axial_kN': axial, 'moment_kNm': moment, 'shear_kN': shear}})
    return out


def stability_agent(loaded_json):
    out={'members':[]}
    for m in loaded_json['members']:
        L=m['length']; r=max(0.02,0.05*L); sl=L/r if r>0 else float('inf')
        br='low'
        if sl>200: br='high'
        elif sl>120: br='medium'
        out['members'].append({**m, 'stability': {'slenderness': sl, 'buckling_risk': br}})
    return out


def optimizer_agent(stable_json):
    out={'members':[],'totals':{}}
    tw=0.0; tc=0.0
    selector = None
    try:
        selector = load_section_selector()
    except Exception:
        selector = None
    # cost DB stub (section -> price override per kg)
    COST_DB = {s['name']: s.get('price_per_kg', None) for s in SECTION_CATALOG}
    for m in stable_json['members']:
        axial=m['loads']['axial_kN']*1000.0; moment=m['loads']['moment_kNm']*1000.0; span=m['length']
        # respect any manually locked selection from previous correction iterations
        locked_sel = m.get('selection', {}) if isinstance(m.get('selection', {}), dict) else {}
        if locked_sel and locked_sel.get('locked'):
            sec_name = locked_sel.get('section_name')
            sec = next((s for s in SECTION_CATALOG if s['name']==sec_name), None)
            if sec is None:
                sec = pick_section_for_member(axial, moment, span)
        else:
            section = None
            if selector is not None:
                try:
                    idx = int(selector.predict([[axial, moment, span]])[0])
                    # map idx to SECTION_CATALOG safely
                    if 0 <= idx < len(SECTION_CATALOG):
                        section = SECTION_CATALOG[idx]
                except Exception:
                    section = None
            if section is None:
                section = pick_section_for_member(axial, moment, span)
            sec = section

        # compute weight and cost using section properties (fall back to catalog values)
        w_per_m = sec.get('weight_kg_per_m') or sec.get('weight_kg', 0.0)
        price_per_kg = COST_DB.get(sec['name']) or sec.get('price_per_kg', 0.0)
        w = w_per_m * span
        cost = w * price_per_kg
        tw += w; tc += cost
        sel_out = {'section_name': sec['name'], 'weight_kg': w, 'estimated_cost': cost, 'locked': bool(locked_sel.get('locked', False))}
        out['members'].append({**m, 'selection': sel_out})
    out['totals']={'weight_kg':tw,'cost_currency':tc}
    return out


def connection_designer(opt_json):
    """
    AI-driven connection designer using comprehensive CONNECTION_TYPES catalog.
    Selects optimal connection type, size, bolts, welds based on member type and loads.
    """
    out={'members':[]}
    
    for m in opt_json['members']:
        member_type = m.get('type', 'beam')
        length = m.get('length', 1.0)
        axial_load = m.get('loads', {}).get('axial_kN', 0.0)
        moment_load = m.get('loads', {}).get('moment_kNm', 0.0)
        shear_load = m.get('loads', {}).get('shear_kN', 0.0)
        
        # AI LOGIC: Select connection type based on member type and loads
        # ===================================================================
        
        conn = {}
        weld_design = {}
        
        if member_type == 'beam':
            # Beam connections: typically beam-to-column (primary) or beam-to-beam (secondary)
            # Rule: If moment significant, use moment-resisting connection; else use simple connection
            
            if moment_load > axial_load * 0.5:  # Moment-dominated
                # Use moment-resisting bolted end plate or welded connection
                conn_subtype = CONNECTION_TYPES['beam_to_column']['subtypes'][1]  # welded_moment_connection
                conn = {
                    'type': 'beam_to_column_welded_moment',
                    'connection_name': 'welded_moment_connection',
                    'primary_type': 'beam_to_column',
                    'weld_type': 'fillet_weld',
                    'weld_size_mm': 10 if axial_load > 100 else 8,
                    'weld_both_sides': True,
                    'stiffener_required': True,
                    'stiffener_thickness_mm': 12,
                }
                weld_design = {
                    'type': 'fillet_weld',
                    'size_mm': conn['weld_size_mm'],
                    'leg_sizes_mm': conn['weld_size_mm'],
                    'throat_mm': conn['weld_size_mm'] * 0.707,
                    'both_sides': True,
                    'reinforcement_mm': 1.5,
                    'ai_notes': f'Moment-resisting weld for {axial_load}kN axial + {moment_load}kNm moment'
                }
            else:
                # Shear-dominated: use bolted end plate or clip angle
                if length > 5:
                    # Longer beams: use end plate (more robust)
                    conn_subtype = CONNECTION_TYPES['beam_to_column']['subtypes'][0]  # bolted_end_plate
                    bolt_count = max(4, int((axial_load + shear_load) / 50))  # 50kN per bolt
                    bolt_count = min(bolt_count, 16)  # Cap at 16 bolts
                    conn = {
                        'type': 'beam_to_column_bolted_end_plate',
                        'connection_name': 'bolted_end_plate',
                        'primary_type': 'beam_to_column',
                        'plate_thickness_mm': 12 if (axial_load + shear_load) > 150 else 10,
                        'bolt_diameter_mm': 20 if (axial_load + shear_load) > 150 else 16,
                        'bolt_grade': '8.8',
                        'bolt_count': bolt_count,
                        'bolt_rows': max(2, int(bolt_count / 4)),
                        'edge_distance_mm': 50,
                        'ai_notes': f'Bolted end plate for {shear_load}kN shear load'
                    }
                else:
                    # Shorter beams: use clip angles (economical)
                    conn_subtype = CONNECTION_TYPES['beam_to_column']['subtypes'][2]  # clip_angle_bolted
                    conn = {
                        'type': 'beam_to_column_clip_angle',
                        'connection_name': 'clip_angle_bolted',
                        'primary_type': 'beam_to_column',
                        'angle_size_mm': 100,
                        'leg_length_mm': 100,
                        'thickness_mm': 10,
                        'bolt_count_per_leg': 2,
                        'bolt_diameter_mm': 16,
                        'ai_notes': f'Clip angle connection for secondary beam, {length}m span'
                    }
        
        elif member_type == 'column':
            # Column connections: typically column-to-base (foundation) or column-to-column (splice)
            # Rule: Always welded for primary columns, bolted for secondary/splices
            
            # For LOD500, assume base plate connection
            conn_subtype = CONNECTION_TYPES['column_to_base']['subtypes'][0]  # bolted_base_plate
            conn = {
                'type': 'column_to_base_bolted',
                'connection_name': 'bolted_base_plate',
                'primary_type': 'column_to_base',
                'plate_thickness_mm': 25 if axial_load > 200 else (20 if axial_load > 100 else 16),
                'plate_dimensions_mm': [600, 600] if axial_load > 200 else [500, 500],
                'anchor_bolt_diameter_mm': 25 if axial_load > 200 else 20,
                'anchor_bolt_count': 8 if axial_load > 200 else 4,
                'anchor_bolt_grade': '8.8',
                'stud_height_mm': 75,
                'ai_notes': f'Base plate for {axial_load}kN axial load'
            }
        
        elif member_type == 'brace':
            # Brace/diagonal connections: typically gusset-based (bolted or welded)
            # Rule: Use welded gussets for high tension/compression; bolted for gravity braces
            
            if abs(axial_load) > 150:
                # High axial load: use welded gusset (full strength)
                conn_subtype = CONNECTION_TYPES['bracing']['subtypes'][1]  # welded_gusset_plate
                conn = {
                    'type': 'brace_welded_gusset',
                    'connection_name': 'welded_gusset_plate',
                    'primary_type': 'bracing',
                    'gusset_thickness_mm': 12,
                    'weld_type': 'fillet_weld',
                    'weld_size_mm': 10,
                    'weld_all_sides': True,
                    'shear_tab_required': True,
                }
                weld_design = {
                    'type': 'fillet_weld',
                    'size_mm': 10,
                    'leg_sizes_mm': 10,
                    'throat_mm': 10 * 0.707,
                    'all_sides': True,
                    'ai_notes': f'Welded gusset for tension/compression diagonal, {axial_load}kN'
                }
            else:
                # Lower load: use bolted gusset (economical)
                conn_subtype = CONNECTION_TYPES['bracing']['subtypes'][0]  # bolted_gusset_plate
                conn = {
                    'type': 'brace_bolted_gusset',
                    'connection_name': 'bolted_gusset_plate',
                    'primary_type': 'bracing',
                    'gusset_thickness_mm': 10,
                    'bolt_diameter_mm': 20,
                    'bolt_count': 6,
                    'bolt_grade': '8.8',
                    'ai_notes': f'Bolted gusset for brace connection, {axial_load}kN'
                }
        
        else:
            # Fallback/unknown member type: use generic bolted connection
            conn = {
                'type': 'generic_bolted',
                'connection_name': 'bolted_gusset_plate',
                'primary_type': 'plate_attachment',
                'bolt_diameter_mm': 16,
                'bolt_count': 4,
                'bolt_grade': '8.8',
            }
        
        # Add weld design info if welded connection
        if weld_design:
            conn['weld_design'] = weld_design
        
        # Add connection catalog reference for fabrication details
        conn['catalog_reference'] = f"CONNECTION_TYPES['{conn.get('primary_type', 'unknown')}']: {conn.get('connection_name', 'unknown')}"
        
        out['members'].append({**m, 'connection': conn})
    
    return out


def fabrication_detailing(conn_json):
    """
    Add detailed fabrication specs including weld types, bolt patterns, copes, holes, bevels.
    Uses WELD_TYPES and CONNECTION_TYPES catalogs for comprehensive details.
    """
    out={'members':[]}
    
    for m in conn_json['members']:
        details = {
            'connection_details': {},
            'weld_details': {},
            'bolt_details': {},
            'geometry_prep': {}
        }
        
        member_type = m.get('type', 'beam')
        conn = m.get('connection', {})
        
        # ===== CONNECTION-SPECIFIC DETAILING =====
        
        if conn.get('connection_name') == 'bolted_end_plate':
            # Beam-to-column bolted end plate
            details['connection_details'] = {
                'type': 'bolted_end_plate',
                'plate_thickness_mm': conn.get('plate_thickness_mm', 12),
                'plate_grade': 'S355',
                'edge_distance_mm': 50,
                'gauge_distance_mm': 100,
            }
            details['bolt_details'] = {
                'diameter_mm': conn.get('bolt_diameter_mm', 20),
                'grade': conn.get('bolt_grade', '8.8'),
                'count': conn.get('bolt_count', 4),
                'arrangement': 'single_column' if conn.get('bolt_count', 4) <= 4 else 'double_column',
                'pattern': 'rectangular',
                'hole_type': 'standard_clearance',
                'hole_dia_mm': conn.get('bolt_diameter_mm', 20) + 2,  # +2mm for standard bolt hole
                'washers': 'hardened',
                'paint_spec': 'shop_primed'
            }
            details['geometry_prep'] = {
                'end_prep': 'mill_cut',
                'surface_finish': 'clean_blast',
            }
        
        elif conn.get('connection_name') == 'welded_moment_connection':
            # Moment-resisting welded connection
            details['connection_details'] = {
                'type': 'welded_moment_connection',
                'column_web_stiffener': True,
                'stiffener_thickness_mm': conn.get('stiffener_thickness_mm', 12),
                'backing_bar': 'required',
            }
            details['weld_details'] = {
                'primary_weld': 'fillet_weld',
                'size_mm': conn.get('weld_size_mm', 10),
                'leg_sizes_mm': conn.get('weld_size_mm', 10),
                'throat_thickness_mm': conn.get('weld_size_mm', 10) * 0.707,
                'both_sides': True,
                'reinforcement_mm': 1.5,
                'process': 'GMAW (MIG)',
                'electrode': 'E70S-2 or equivalent',
                'preheat': 'required' if conn.get('weld_size_mm', 10) > 8 else 'optional',
                'inspection': 'visual + UT sample',
            }
            details['geometry_prep'] = {
                'surface_prep': 'clean_blast_SSPC-SP6',
                'chamfer': 'not_required',
                'gaps': 'maintain 3-5mm for weld access',
            }
        
        elif conn.get('connection_name') == 'clip_angle_bolted':
            # Clip angle connection
            details['connection_details'] = {
                'type': 'clip_angle_bolted',
                'angle_size_mm': conn.get('angle_size_mm', 100),
                'leg_length_mm': conn.get('leg_length_mm', 100),
                'thickness_mm': conn.get('thickness_mm', 10),
                'grade': 'A36',
            }
            details['bolt_details'] = {
                'diameter_mm': conn.get('bolt_diameter_mm', 16),
                'grade': '8.8',
                'per_leg': conn.get('bolt_count_per_leg', 2),
                'hole_type': 'standard_clearance',
                'hole_dia_mm': conn.get('bolt_diameter_mm', 16) + 2,
                'washers': 'standard',
            }
            details['geometry_prep'] = {
                'angle_cut': 'bandsaw or plasma',
                'hole_drilling': 'CNC',
                'tolerance': '±1/16"',
            }
        
        elif conn.get('connection_name') == 'bolted_base_plate':
            # Column base plate (foundation)
            details['connection_details'] = {
                'type': 'bolted_base_plate',
                'plate_thickness_mm': conn.get('plate_thickness_mm', 25),
                'plate_dimensions_mm': conn.get('plate_dimensions_mm', [600, 600]),
                'plate_grade': 'A36',
                'finish': 'mill_scale',
            }
            details['bolt_details'] = {
                'anchor_bolt_diameter_mm': conn.get('anchor_bolt_diameter_mm', 25),
                'anchor_bolt_grade': conn.get('anchor_bolt_grade', '8.8'),
                'anchor_bolt_count': conn.get('anchor_bolt_count', 4),
                'stud_height_mm': conn.get('stud_height_mm', 75),
                'pattern': 'square_or_rectangular',
            }
            details['geometry_prep'] = {
                'leveling_pads': 'epoxy or shim',
                'grout_thickness_mm': 50,
                'weld_to_column': 'fillet_weld_8mm_all_around',
            }
        
        elif conn.get('connection_name') == 'welded_gusset_plate':
            # Welded gusset (bracing)
            details['connection_details'] = {
                'type': 'welded_gusset_plate',
                'gusset_thickness_mm': conn.get('gusset_thickness_mm', 12),
                'gusset_shape': 'triangular_or_rectangular',
            }
            details['weld_details'] = {
                'type': 'fillet_weld',
                'size_mm': conn.get('weld_size_mm', 10),
                'leg_sizes_mm': conn.get('weld_size_mm', 10),
                'throat_thickness_mm': conn.get('weld_size_mm', 10) * 0.707,
                'all_sides': conn.get('weld_all_sides', True),
                'reinforcement_mm': 1.5,
                'process': 'GMAW',
                'inspection': 'visual + dye_penetrant',
            }
            details['geometry_prep'] = {
                'bevel_cut': 'plasma_or_oxy',
                'corner_radius_mm': 10,
                'surface_prep': 'clean_blast',
            }
        
        elif conn.get('connection_name') == 'bolted_gusset_plate':
            # Bolted gusset (bracing)
            details['connection_details'] = {
                'type': 'bolted_gusset_plate',
                'gusset_thickness_mm': conn.get('gusset_thickness_mm', 10),
                'gusset_grade': 'A36',
            }
            details['bolt_details'] = {
                'diameter_mm': conn.get('bolt_diameter_mm', 20),
                'grade': conn.get('bolt_grade', '8.8'),
                'count': conn.get('bolt_count', 6),
                'hole_type': 'standard_clearance',
                'hole_dia_mm': conn.get('bolt_diameter_mm', 20) + 2,
            }
            details['geometry_prep'] = {
                'cutting': 'plasma_or_bandsaw',
                'drilling': 'CNC_multi_spindle',
                'tolerance': '±1/16"',
            }
        
        # ===== MEMBER-SPECIFIC GEOMETRY PREP =====
        
        if member_type == 'beam':
            # Beam end preparation (copes, holes, bevels for connections)
            if 'geometry_prep' not in details:
                details['geometry_prep'] = {}
            
            details['geometry_prep'].update({
                'end_copes': {
                    'top_cope': True,
                    'bottom_cope': True,
                    'cope_depth_mm': 30,
                    'cope_length_mm': 100,
                    'cope_radius_mm': 20,  # Match beam flange radius
                },
                'connection_holes': {
                    'type': 'slotted_or_standard',
                    'size_mm': conn.get('bolt_diameter_mm', 20) + 2 if conn.get('bolt_diameter_mm') else 22,
                    'pattern': 'vertical_line',
                    'spacing_mm': 100,
                },
                'mill_tolerances': '±1/8" length, ±1/16" for connection holes',
            })
        
        elif member_type == 'column':
            # Column-specific prep (stiffeners, bevels, anchor bolt access)
            if 'geometry_prep' not in details:
                details['geometry_prep'] = {}
            
            details['geometry_prep'].update({
                'web_stiffeners': conn.get('stiffener_required', False),
                'stiffener_thickness_mm': conn.get('stiffener_thickness_mm', 12) if conn.get('stiffener_required') else None,
                'flange_bevels': {
                    'on': True,
                    'angle_deg': 45,
                    'depth_mm': 10,
                },
                'base_prep': 'mill_cut_flat_within_1/32"',
            })
        
        elif member_type == 'brace':
            # Brace-specific (minimal prep, gusset interface)
            if 'geometry_prep' not in details:
                details['geometry_prep'] = {}
            
            details['geometry_prep'].update({
                'end_cut': 'plasma_or_bandsaw',
                'tolerance': '±1/4"',
                'gusset_interface': 'verify fit after gusset cutting',
            })
        
        out['members'].append({**m, 'fabrication': details})
    
    return out


def fabrication_standards(fab_json):
    """
    Validate and enforce fabrication standards from CONNECTION_TYPES and WELD_TYPES catalogs.
    - Minimum/maximum dimensions per AISC 360 and AWS D1.1
    - Weld sizing and penetration rules
    - Bolt grade compatibility
    - Material grade validation
    - CJP vs. PJP weld penetration requirements
    """
    out = {'members': []}
    errors = []
    warnings = []
    
    for m in fab_json['members']:
        fab = m.get('fabrication', {})
        conn = m.get('connection', {})
        mid = m.get('midpoint', [0, 0, 0])
        
        member_id = m.get('id', 'unknown')
        weld = None  # Track if member has welds
        
        # ===== WELD STANDARDS VALIDATION =====
        if fab.get('weld_details'):
            weld = fab['weld_details']
            weld_size = weld.get('size_mm', 0)
            
            # Minimum weld size: 3mm (AWS D1.1)
            if weld_size > 0 and weld_size < 3:
                weld['size_mm'] = 3
                warnings.append({
                    'id': member_id,
                    'warn': 'weld_undersized',
                    'requested_mm': weld_size,
                    'min_standard_mm': 3,
                    'action': 'increased_to_3mm'
                })
            
            # Maximum single-pass weld: 8mm
            if weld_size > 8 and weld.get('process') in ['GMAW', 'SMAW']:
                if 'multi_pass' not in weld:
                    weld['multi_pass'] = True
                    weld['passes'] = max(2, int(weld_size / 8))
                    warnings.append({
                        'id': member_id,
                        'warn': 'weld_requires_multi_pass',
                        'size_mm': weld_size,
                        'passes': weld['passes'],
                    })
            
            # Check penetration requirements for CJP welds
            if weld.get('type') in ['cjp_groove_weld', 'pjp_groove_weld']:
                material_thickness = m.get('selection', {}).get('thickness_mm', 10)
                
                if weld.get('type') == 'cjp_groove_weld':
                    # CJP: Full penetration required
                    required_penetration = material_thickness
                    weld['penetration_required_mm'] = required_penetration
                    weld['back_chip'] = True  # CRITICAL
                    weld['inspection'] = 'visual + UT'
                
                elif weld.get('type') == 'pjp_groove_weld':
                    # PJP: Partial penetration (typically 50% of thickness)
                    required_penetration = max(10, int(material_thickness * 0.5))
                    weld['penetration_required_mm'] = required_penetration
                    weld['inspection'] = 'visual + dye_penetrant'
            
            # Fillet weld throat thickness = leg size * 0.707
            if weld.get('type') == 'fillet_weld':
                leg_size = weld.get('leg_sizes_mm', weld_size)
                weld['throat_thickness_mm'] = leg_size * 0.707
                
                # Weld length constraints: minimum 4x weld size (AWS)
                min_weld_length = max(25, 4 * leg_size)  # mm
                weld['min_length_mm'] = min_weld_length
                
                # Intermittent weld efficiency factor (0.7x capacity)
                if weld.get('intermittent'):
                    weld['efficiency_factor'] = 0.7
        
        # ===== BOLT STANDARDS VALIDATION =====
        if fab.get('bolt_details'):
            bolt = fab['bolt_details']
            bolt_dia = bolt.get('diameter_mm', 16)
            bolt_grade = bolt.get('grade', '8.8')
            
            # Bolt diameter limits: M12 to M39 (std ASTM F563)
            # M12 = 12mm, M16 = 16mm, M20 = 20mm, M24 = 24mm, M32 = 32mm, M39 = 39mm
            std_bolts = [12, 16, 20, 24, 32, 39]
            if bolt_dia not in std_bolts:
                closest = min(std_bolts, key=lambda x: abs(x - bolt_dia))
                bolt['diameter_mm'] = closest
                warnings.append({
                    'id': member_id,
                    'warn': 'bolt_diameter_non_standard',
                    'requested_mm': bolt_dia,
                    'corrected_to_mm': closest,
                })
            
            # Hole size per AISC: standard hole = bolt_dia + 2mm
            bolt['hole_diameter_mm'] = bolt_dia + 2
            
            # Minimum edge distance: 1.5 * bolt_dia
            bolt['min_edge_distance_mm'] = 1.5 * bolt_dia
            
            # Minimum spacing between bolts: 3 * bolt_dia (or 2.67x in some standards)
            bolt['min_spacing_mm'] = 3 * bolt_dia
            
            # Bolt grade verification
            valid_grades = ['4.6', '5.8', '8.8', '10.9']
            if bolt_grade not in valid_grades:
                bolt['grade'] = '8.8'
                warnings.append({
                    'id': member_id,
                    'warn': 'bolt_grade_invalid',
                    'requested': bolt_grade,
                    'corrected_to': '8.8',
                })
        
        # ===== PLATE THICKNESS STANDARDS VALIDATION =====
        if fab.get('connection_details'):
            conn_detail = fab['connection_details']
            
            # Minimum plate thickness: 1/4" (6mm)
            for thickness_key in ['plate_thickness_mm', 'gusset_thickness_mm', 'stiffener_thickness_mm']:
                if thickness_key in conn_detail:
                    thk = conn_detail[thickness_key]
                    if thk > 0 and thk < 6:
                        conn_detail[thickness_key] = 6
                        warnings.append({
                            'id': member_id,
                            'warn': 'plate_undersized',
                            'param': thickness_key,
                            'requested_mm': thk,
                            'min_standard_mm': 6,
                            'corrected_to_mm': 6,
                        })
            
            # Material grade: default A36 or A572
            if 'plate_grade' not in conn_detail:
                conn_detail['plate_grade'] = 'A36'
        
        # ===== GEOMETRY PREP STANDARDS =====
        if fab.get('geometry_prep'):
            geom = fab['geometry_prep']
            
            # Hole tolerance per AISC: typically ±1/16" (±1.6mm)
            if 'hole_tol_mm' not in geom:
                geom['hole_tol_mm'] = 1.6
            
            # Surface finish: clean blast per SSPC-SP6 for welds
            if 'surface_prep' not in geom and weld is not None:
                geom['surface_prep'] = 'clean_blast_SSPC-SP6'
        
        # Mark standards as checked
        fab['standards_checked'] = True
        fab['standards_notes'] = []
        if warnings:
            fab['standards_notes'].extend([w for w in warnings if w.get('id') == member_id])
        
        out['members'].append({**m, 'fabrication': fab, 'standards_checked': True})
    
    return out


def erection_planner(std_json):
    members=std_json['members']
    def midz(m): return (m['start'][2]+m['end'][2])/2.0
    sorted_members=sorted(members,key=lambda mm:(0 if mm['type']=='column' else 1,-midz(mm)))
    for i,m in enumerate(sorted_members): m['erection_order']=i+1
    return {'members':sorted_members}


def safety_compliance(erect_json):
    out={'members':[]}
    for m in erect_json['members']:
        risk='ok'; notes=[]
        if m['type']=='column' and m['length']>10: risk='review'; notes.append('temporary bracing recommended')
        if m.get('connection',{}).get('bolt_count',0)>=8: notes.append('heavy bolting operation')
        out['members'].append({**m,'safety':{'status':risk,'notes':notes}})
    return out


def analysis_model_generator(full_json):
    nodes={}; node_list=[]
    def get_node_id(coord):
        key=tuple(round(c,4) for c in coord)
        if key in nodes: return nodes[key]
        nid=len(nodes)+1; nodes[key]=nid; node_list.append({'id':nid,'coord':coord}); return nid
    elements=[]
    for m in full_json['members']:
        n1=get_node_id(m['start']); n2=get_node_id(m['end'])
        elements.append({'id':m['id'],'n1':n1,'n2':n2,'section':m.get('selection',{}).get('section_name')})
    return {'nodes':node_list,'elements':elements}


def validator_agent(full_json):
    errors = []
    warnings = []
    # helper to find section properties
    def get_section_by_name(name):
        for s in SECTION_CATALOG:
            if s['name'] == name:
                return s
        return None

    for m in full_json.get('members', []):
        if m.get('length', 0.0) <= 0:
            errors.append({'id': m['id'], 'err': 'nonpositive length', 'fix': None})
            continue
        sel = m.get('selection') or {}
        section_name = sel.get('section_name')
        if not section_name:
            warnings.append({'id': m['id'], 'warn': 'no section selected', 'fix': 'select_section'})
            continue
        sec = get_section_by_name(section_name)
        if sec is None:
            warnings.append({'id': m['id'], 'warn': f'unknown section {section_name}', 'fix': 'select_section'})
            continue
        # compute capacities consistent with optimizer logic (axial in N, moment in N*m)
        axial_N = (m.get('loads', {}).get('axial_kN', 0.0)) * 1000.0
        moment_Nm = (m.get('loads', {}).get('moment_kNm', 0.0)) * 1000.0
        span = max(0.01, m.get('length', 0.0))
        axial_capacity_N = sec['area'] * 250e6 * 0.6
        bending_capacity_Nm = sec['Ixx'] * 250e6 * 0.6 / (span/2 if span > 0.01 else 0.01)
        if axial_N > axial_capacity_N:
            errors.append({'id': m['id'], 'err': 'axial_capacity_exceeded', 'axial_N': axial_N, 'axial_capacity_N': axial_capacity_N, 'fix': 'upsample_section'})
        if moment_Nm > bending_capacity_Nm:
            errors.append({'id': m['id'], 'err': 'bending_capacity_exceeded', 'moment_Nm': moment_Nm, 'bending_capacity_Nm': bending_capacity_Nm, 'fix': 'upsample_section'})

        # approximate shear capacity check (simplified)
        shear_kN = m.get('loads', {}).get('shear_kN', 0.0)
        shear_capacity_N = sec['area'] * 250e6 * 0.6 * 0.5 if sec is not None else 0.0
        if (shear_kN * 1000.0) > shear_capacity_N:
            errors.append({'id': m['id'], 'err': 'shear_capacity_exceeded', 'shear_kN': shear_kN, 'shear_capacity_N': shear_capacity_N, 'fix': 'upsample_section'})

        # slenderness check: use stability info if available
        slenderness = m.get('stability', {}).get('slenderness')
        if slenderness is not None:
            if slenderness > 200:
                warnings.append({'id': m['id'], 'warn': 'very_slender_member', 'slenderness': slenderness, 'fix': 'add_bracing_or_increase_section'})
            elif slenderness > 120:
                warnings.append({'id': m['id'], 'warn': 'slender_member', 'slenderness': slenderness, 'fix': 'check_buckling'})

        # clearance checks: if user provided min_clearance_mm on member or global requirement
        min_clear_req = m.get('fabrication', {}).get('min_clearance_mm') or full_json.get('min_clearance_mm')
        if min_clear_req is not None:
            # quick check against connected elements in clash_list if provided
            for c in full_json.get('clash_list', []):
                if c.get('a') == m['id'] or c.get('b') == m['id']:
                    # if reported distance less than required, flag
                    if c.get('dist_m') is not None and c.get('dist_m')*1000.0 < float(min_clear_req):
                        warnings.append({'id': m['id'], 'warn': 'insufficient_clearance', 'measured_mm': c.get('dist_m')*1000.0, 'required_mm': min_clear_req, 'fix': 'increase_clearance_or_offset'})
        # simple bolt/weld checks
        conn = m.get('connection', {})
        if conn:
            bolt_count = int(conn.get('bolt_count', 0)) if conn.get('bolt_count') is not None else 0
            # nominal shear capacity per bolt (simplified conservative estimate in kN)
            bolt_capacity_kN = 100
            if bolt_count * bolt_capacity_kN < m.get('loads', {}).get('shear_kN', 0.0):
                warnings.append({'id': m['id'], 'warn': 'insufficient_bolt_shear_capacity', 'fix': 'increase_bolts', 'required_kN': m.get('loads', {}).get('shear_kN', 0.0)})
            if conn.get('weld_size_mm') and conn.get('weld_size_mm') < 3:
                warnings.append({'id': m['id'], 'warn': 'undersized_weld', 'fix': 'increase_weld'} )

    return {'errors': errors, 'warnings': warnings}


def builder_ifc(full_json, out_path=None):
    try:
        import ifcopenshell
    except Exception:
        return {'ifc':None,'note':'ifcopenshell not installed, returning JSON fallback','model_json':full_json}
    if out_path is None: out_path=os.path.join('outputs','model.ifc')
    ifc=ifcopenshell.file(schema='IFC4')
    person=ifc.create_entity('IfcPerson',GivenName='AI')
    org=ifc.create_entity('IfcOrganization',Name='aibuildx')
    pao=ifc.create_entity('IfcPersonAndOrganization',ThePerson=person,TheOrganization=org)
    app=ifc.create_entity('IfcApplication',ApplicationDeveloper=org,Version='0.1')
    ow_hist=ifc.create_entity('IfcOwnerHistory',OwningUser=pao,OwningApplication=app)
    project=ifc.create_entity('IfcProject',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),Name='AI Project',OwnerHistory=ow_hist)
    context=ifc.create_entity('IfcGeometricRepresentationContext',ContextIdentifier='Model',ContextType='Model',CoordinateSpaceDimension=3,Precision=1e-5)
    project.RepresentationContexts=[context]
    site=ifc.create_entity('IfcSite',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),Name='Site')
    building=ifc.create_entity('IfcBuilding',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),Name='Building')
    storey=ifc.create_entity('IfcBuildingStorey',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),Name='Storey')
    ifc.create_entity('IfcRelAggregates',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),RelatingObject=project,RelatedObjects=[site])
    ifc.create_entity('IfcRelAggregates',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),RelatingObject=site,RelatedObjects=[building])
    ifc.create_entity('IfcRelAggregates',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),RelatingObject=building,RelatedObjects=[storey])

    SECTION_GEOM={
        'W8x10':{'type':'I','width':0.203,'depth':0.203,'web_thk':0.005,'flange_thk':0.006},
        'W10x12':{'type':'I','width':0.254,'depth':0.254,'web_thk':0.006,'flange_thk':0.007},
        'HSS100x100x6':{'type':'HollowRect','outer_w':0.100,'outer_h':0.100,'thickness':0.006},
        'REC200x50':{'type':'Rect','width':0.200,'depth':0.050,'thickness':0.005},
    }

    products=[]
    rel_connects = []
    for m in full_json['members']:
        gid = ifcopenshell.guid.compress(uuid.uuid4().hex)
        name = m.get('selection', {}).get('section_name') or m.get('type')
        # choose an appropriate IFC class for structural members
        if m.get('type') == 'column':
            elem = ifc.create_entity('IfcColumn', GlobalId=gid, Name=str(name))
        elif m.get('type') == 'beam':
            elem = ifc.create_entity('IfcBeam', GlobalId=gid, Name=str(name))
        else:
            elem = ifc.create_entity('IfcBuildingElementProxy', GlobalId=gid, Name=str(name))
        start = m['start']
        start_coords = (float(start[0]), float(start[1]), float(start[2]))
        placement_point = ifc.create_entity('IfcCartesianPoint', start_coords)
        # compute axis and a stable ref direction for profile orientation
        axis_vec = unit_vector(m['start'], m['end'])
        # choose a reference direction not parallel to axis_vec
        if abs(axis_vec[2]) < 0.9:
            ref_candidate = (0.0, 0.0, 1.0)
        else:
            ref_candidate = (0.0, 1.0, 0.0)
        # ensure ref is not parallel: simple Gram-Schmidt
        import math as _math
        ax = _math.sqrt(axis_vec[0]*axis_vec[0] + axis_vec[1]*axis_vec[1] + axis_vec[2]*axis_vec[2]) or 1.0
        a_norm = (axis_vec[0]/ax, axis_vec[1]/ax, axis_vec[2]/ax)
        # projection of ref_candidate onto axis
        proj = (a_norm[0]*ref_candidate[0] + a_norm[1]*ref_candidate[1] + a_norm[2]*ref_candidate[2])
        ref = (ref_candidate[0] - proj*a_norm[0], ref_candidate[1] - proj*a_norm[1], ref_candidate[2] - proj*a_norm[2])
        # normalize ref
        ref_len = (_math.sqrt(ref[0]*ref[0] + ref[1]*ref[1] + ref[2]*ref[2]) or 1.0)
        ref_dir = (ref[0]/ref_len, ref[1]/ref_len, ref[2]/ref_len)
        axis_dir = (float(a_norm[0]), float(a_norm[1]), float(a_norm[2]))
        ref_dir = (float(ref_dir[0]), float(ref_dir[1]), float(ref_dir[2]))
        axis_point = ifc.create_entity('IfcCartesianPoint', start_coords)
        axis_entity = ifc.create_entity('IfcDirection', axis_dir)
        ref_entity = ifc.create_entity('IfcDirection', ref_dir)
        axis2placement = ifc.create_entity('IfcAxis2Placement3D', axis_point, axis_entity, ref_entity)
        local_placement = ifc.create_entity('IfcLocalPlacement', PlacementRelTo=None, RelativePlacement=axis2placement)
        elem.ObjectPlacement = local_placement
        geom=SECTION_GEOM.get(name); rep_items=[]
        if geom is not None:
            if geom['type']=='I':
                prof=ifc.create_entity('IfcIShapeProfileDef',ProfileType='AREA',ProfileName=name,OverallWidth=geom['width'],OverallDepth=geom['depth'],WebThickness=geom['web_thk'],FlangeThickness=geom['flange_thk'])
            elif geom['type']=='Rect':
                prof=ifc.create_entity('IfcRectangleProfileDef',ProfileType='AREA',ProfileName=name,XDim=geom['width'],YDim=geom['depth'])
            elif geom['type']=='HollowRect':
                # ifcopenshell/IFC doesn't have a simple hollow rectangle profile type; approximate using outer rectangle
                prof=ifc.create_entity('IfcRectangleProfileDef',ProfileType='AREA',ProfileName=name,XDim=geom['outer_w'],YDim=geom['outer_h'])
                # we add a property to indicate wall thickness so downstream tools can interpret as hollow
                if 'thickness' in geom:
                    # will be added to PSET below
                    pass
            else:
                prof=ifc.create_entity('IfcRectangleProfileDef',ProfileType='AREA',ProfileName=name,XDim=geom.get('width',0.1),YDim=geom.get('depth',0.05))
            axis=unit_vector(m['start'],m['end']); depth=m.get('length',0.0)
            origin_pt=ifc.create_entity('IfcCartesianPoint',(0.0,0.0,0.0))
            prof_pos=ifc.create_entity('IfcAxis2Placement3D', origin_pt, ifc.create_entity('IfcDirection',(0.0,0.0,1.0)), ifc.create_entity('IfcDirection',(1.0,0.0,0.0)))
            try:
                dir_vals=(float(axis[0]), float(axis[1]), float(axis[2]))
                extruded=ifc.create_entity('IfcExtrudedAreaSolid', SweptArea=prof, Position=prof_pos, ExtrudedDirection=ifc.create_entity('IfcDirection', dir_vals), Depth=depth)
                rep_items.append(extruded)
            except Exception:
                rep_items=[]
        props=[]
        def make_prop(namep,val):
            if isinstance(val,(int,float)):
                nominal=ifc.create_entity('IfcReal',float(val))
            else:
                nominal=ifc.create_entity('IfcText',str(val))
            return ifc.create_entity('IfcPropertySingleValue',Name=str(namep),NominalValue=nominal)
        props.append(make_prop('start',m['start'])); props.append(make_prop('end',m['end'])); props.append(make_prop('length_m',m.get('length')))
        props.append(make_prop('member_type',m.get('type'))); sel=m.get('selection',{}); props.append(make_prop('section',sel.get('section_name')))
        props.append(make_prop('weight_kg',sel.get('weight_kg')))
        pset=ifc.create_entity('IfcPropertySet',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),Name='Pset_AIBuildX',HasProperties=props)
        ifc.create_entity('IfcRelDefinesByProperties',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),RelatedObjects=[elem],RelatingPropertyDefinition=pset)
        if rep_items:
            shape = ifc.create_entity('IfcShapeRepresentation', ContextOfItems=context, RepresentationIdentifier='Body', RepresentationType='SweptSolid', Items=rep_items)
            pd = ifc.create_entity('IfcProductDefinitionShape', Representations=[shape])
            elem.Representation = pd

        # create simple connection representation if connection info exists
        conn = m.get('connection') or {}
        if conn:
            try:
                conn_gid = ifcopenshell.guid.compress(uuid.uuid4().hex)
                conn_name = f"conn_{m.get('id')}"
                conn_proxy = ifc.create_entity('IfcBuildingElementProxy', GlobalId=conn_gid, Name=conn_name)
                # place connection at member end (naive)
                end_pt = ifc.create_entity('IfcCartesianPoint', (float(m['end'][0]), float(m['end'][1]), float(m['end'][2])))
                conn_axis = ifc.create_entity('IfcDirection', (0.0, 0.0, 1.0))
                conn_ref = ifc.create_entity('IfcDirection', (1.0, 0.0, 0.0))
                conn_place = ifc.create_entity('IfcAxis2Placement3D', end_pt, conn_axis, conn_ref)
                conn_local = ifc.create_entity('IfcLocalPlacement', PlacementRelTo=None, RelativePlacement=conn_place)
                conn_proxy.ObjectPlacement = conn_local
                # attach a richer PSET for connection (bolt/weld info)
                cprops = [make_prop('conn_type', conn.get('type')), make_prop('bolt_count', conn.get('bolt_count')), make_prop('bolt_dia_mm', conn.get('bolt_dia_mm')), make_prop('weld_size_mm', conn.get('weld_size_mm'))]
                cpset = ifc.create_entity('IfcPropertySet', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='Pset_Connection', HasProperties=cprops)
                ifc.create_entity('IfcRelDefinesByProperties', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatedObjects=[conn_proxy], RelatingPropertyDefinition=cpset)
                products.append(conn_proxy)
                # link connection to member with IfcRelConnectsElements (preferred) or fallback
                try:
                    rel = ifc.create_entity('IfcRelConnectsElements', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingElement=elem, RelatedElement=conn_proxy)
                    rel_connects.append(rel)
                except Exception:
                    try:
                        ifc.create_entity('IfcRelAssociates', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatedObjects=[elem], RelatingReference=cpset)
                    except Exception:
                        pass

                # add bolt fasteners when bolt information is present
                try:
                    bolt_count = int(conn.get('bolt_count', 0)) if conn.get('bolt_count') is not None else 0
                    bolt_dia = int(conn.get('bolt_dia_mm', 0)) if conn.get('bolt_dia_mm') is not None else 0
                except Exception:
                    bolt_count = 0; bolt_dia = 0
                for bi in range(bolt_count):
                    try:
                        fast_gid = ifcopenshell.guid.compress(uuid.uuid4().hex)
                        fast_name = f"bolt_{m.get('id')}_{bi+1}"
                        fast = ifc.create_entity('IfcFastener', GlobalId=fast_gid, Name=fast_name)
                        # place bolt near the connection proxy: slight offset along Z and spacing along X
                        end = (float(m['end'][0]), float(m['end'][1]), float(m['end'][2]))
                        spacing = 0.05
                        bolt_pt = ifc.create_entity('IfcCartesianPoint', (end[0] + bi*spacing, end[1], end[2] + 0.02))
                        bolt_axis = ifc.create_entity('IfcDirection', (0.0, 0.0, 1.0))
                        bolt_ref = ifc.create_entity('IfcDirection', (1.0, 0.0, 0.0))
                        bolt_place = ifc.create_entity('IfcAxis2Placement3D', bolt_pt, bolt_axis, bolt_ref)
                        bolt_local = ifc.create_entity('IfcLocalPlacement', PlacementRelTo=None, RelativePlacement=bolt_place)
                        fast.ObjectPlacement = bolt_local
                        # attach bolt PSET
                        bprops = [make_prop('bolt_dia_mm', bolt_dia), make_prop('bolt_grade', conn.get('bolt_grade', ''))]
                        bpset = ifc.create_entity('IfcPropertySet', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), Name='Pset_Bolt', HasProperties=bprops)
                        ifc.create_entity('IfcRelDefinesByProperties', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatedObjects=[fast], RelatingPropertyDefinition=bpset)
                        products.append(fast)
                        # connect bolt to connection proxy and element
                        try:
                            ifc.create_entity('IfcRelConnectsElements', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingElement=conn_proxy, RelatedElement=fast)
                        except Exception:
                            pass
                        try:
                            ifc.create_entity('IfcRelConnectsElements', GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex), RelatingElement=elem, RelatedElement=fast)
                        except Exception:
                            pass
                    except Exception:
                        # ignore individual bolt failures
                        pass
            except Exception:
                pass

        products.append(elem)
    ifc.create_entity('IfcRelContainedInSpatialStructure',GlobalId=ifcopenshell.guid.compress(uuid.uuid4().hex),RelatingStructure=storey,RelatedElements=products)
    try:
        out_dir=os.path.dirname(out_path);
        if out_dir and not os.path.exists(out_dir): os.makedirs(out_dir,exist_ok=True)
        ifc.write(out_path)
        return {'ifc':out_path,'note':'IFC written with basic swept solids and PSETs.'}
    except Exception as e:
        return {'ifc':None,'note':f'Failed to write IFC: {e}'}


def _segment_segment_distance(a0,a1,b0,b1):
    """Pure Python fallback for segment-segment distance (no numpy dependency)."""
    try:
        import numpy as _np
        u=_np.array([a1[i]-a0[i] for i in range(3)]); v=_np.array([b1[i]-b0[i] for i in range(3)])
        w0=_np.array([a0[i]-b0[i] for i in range(3)]); a=_np.dot(u,u); b=_np.dot(u,v); c=_np.dot(v,v)
        d=_np.dot(u,w0); e=_np.dot(v,w0); denom=a*c-b*b
        s=0.0; t=0.0
        if denom!=0.0: s=(b*e-c*d)/denom; t=(a*e-b*d)/denom
        s=max(0.0,min(1.0,s)); t=max(0.0,min(1.0,t))
        cp=_np.array(a0)+s*u; cq=_np.array(b0)+t*v
        return float(_np.linalg.norm(cp-cq))
    except Exception:
        # Fallback: pure Python implementation
        def vec_sub(v1, v2):
            return [v1[i] - v2[i] for i in range(3)]
        def vec_dot(v1, v2):
            return sum(v1[i] * v2[i] for i in range(3))
        def vec_scale(v, s):
            return [v[i] * s for i in range(3)]
        def vec_add(v1, v2):
            return [v1[i] + v2[i] for i in range(3)]
        def vec_norm(v):
            return math.sqrt(sum(vi**2 for vi in v))
        
        u = vec_sub(a1, a0)
        v = vec_sub(b1, b0)
        w0 = vec_sub(a0, b0)
        a = vec_dot(u, u)
        b_dot = vec_dot(u, v)
        c = vec_dot(v, v)
        d = vec_dot(u, w0)
        e = vec_dot(v, w0)
        denom = a * c - b_dot * b_dot
        
        s = 0.0; t = 0.0
        if denom != 0.0:
            s = (b_dot * e - c * d) / denom
            t = (a * e - b_dot * d) / denom
        s = max(0.0, min(1.0, s))
        t = max(0.0, min(1.0, t))
        
        cp = vec_add(a0, vec_scale(u, s))
        cq = vec_add(b0, vec_scale(v, t))
        return float(vec_norm(vec_sub(cp, cq)))


def clasher_agent(full_json,tol=0.02):
    clashes=[]; mems=full_json['members']; n=len(mems)
    for i in range(n):
        for j in range(i+1,n):
            a=mems[i]; b=mems[j]
            if a['start']==b['start'] or a['end']==b['end'] or a['start']==b['end'] or a['end']==b['start']: continue
            d=_segment_segment_distance(a['start'],a['end'],b['start'],b['end'])
            if d<tol: clashes.append({'a':a['id'],'b':b['id'],'dist_m':d})
    return {'clashes':clashes}


def mesh_clasher_agent(full_json, tol=0.0):
    """Coarse mesh/solid clash approximation:
    - Stage 1: AABB overlap check using member length and section outer dims
    - Stage 2: precise centerline segment-segment distance compared to bounding radii
    Returns: {'clashes': [...]}
    """
    # Try higher-fidelity precise clashing if available, otherwise run coarse method
    try:
        res = precise_mesh_clasher(full_json, tol=tol)
        # return early if precise detector runs (may return empty clashes)
        return res
    except Exception:
        # precise clasher not available or failed; fall back to coarse method
        clashes = []
    mems = full_json['members']
    # helper to get outer half-diagonal (approx bounding radius) from selection/section
    def bounding_radius(m):
        sel = m.get('selection', {})
        name = sel.get('section_name')
        # fallback dims
        w = 0.05; h = 0.05
        if name and name in SECTION_GEOM:
            g = SECTION_GEOM[name]
            if g.get('type') in ('I','Rect','HollowRect'):
                if g.get('type') == 'I':
                    w = g.get('width', w); h = g.get('depth', h)
                elif g.get('type') == 'Rect':
                    w = g.get('width', w); h = g.get('depth', h)
                elif g.get('type') == 'HollowRect':
                    w = g.get('outer_w', w); h = g.get('outer_h', h)
        # radius ~ half diagonal
        return 0.5 * math.hypot(w, h)

    def aabb_for_member(m):
        x_coords = [m['start'][0], m['end'][0]]
        y_coords = [m['start'][1], m['end'][1]]
        z_coords = [m['start'][2], m['end'][2]]
        r = bounding_radius(m)
        return (min(x_coords)-r, min(y_coords)-r, min(z_coords)-r), (max(x_coords)+r, max(y_coords)+r, max(z_coords)+r), r

    n = len(mems)
    for i in range(n):
        for j in range(i+1, n):
            a = mems[i]; b = mems[j]
            if a['id'] == b['id']: continue
            # quick skip for shared nodes
            if a['start'] == b['start'] or a['end'] == b['end'] or a['start'] == b['end'] or a['end'] == b['start']:
                continue
            a_min, a_max, ra = aabb_for_member(a)
            b_min, b_max, rb = aabb_for_member(b)
            # check AABB overlap
            overlap = not (a_max[0] < b_min[0] or a_min[0] > b_max[0] or a_max[1] < b_min[1] or a_min[1] > b_max[1] or a_max[2] < b_min[2] or a_min[2] > b_max[2])
            if not overlap:
                continue
            # refined check: segment-segment distance
            d = _segment_segment_distance(a['start'], a['end'], b['start'], b['end'])
            # compare against sum of bounding radii (plus tolerance)
            if d <= (ra + rb + tol):
                clashes.append({'a': a['id'], 'b': b['id'], 'dist_m': d, 'radius_sum': (ra + rb)})
    return {'clashes': clashes}


def precise_mesh_clasher(full_json, tol=0.0):
    """Attempt a higher-fidelity clash detection using `trimesh`.
    Builds simple swept boxes for members using `SECTION_GEOM` dims and tests pairwise collisions.
    Falls back or raises if trimesh isn't available.
    """
    try:
        import trimesh
        import numpy as _np
    except Exception as e:
        raise RuntimeError('trimesh not available') from e

    mems = full_json.get('members', [])
    meshes = []
    ids = []
    for m in mems:
        start = m['start']; end = m['end']
        axis = tuple(unit_vector(start, end))
        L = max(1e-6, m.get('length') or length(start, end))
        sel = m.get('selection', {})
        name = sel.get('section_name') if sel else None
        # fallback dims
        w = 0.05; h = 0.05
        if name and name in SECTION_GEOM:
            g = SECTION_GEOM[name]
            if g.get('type') == 'I':
                w = g.get('width', w); h = g.get('depth', h)
            elif g.get('type') == 'Rect':
                w = g.get('width', w); h = g.get('depth', h)
            elif g.get('type') == 'HollowRect':
                w = g.get('outer_w', w); h = g.get('outer_h', h)

        # create a box with length along X axis, centered at origin
        extents = (_np.abs(L), _np.abs(w), _np.abs(h))
        box = trimesh.creation.box(extents=extents)

        # align box X-axis to member axis
        x_axis = _np.array([1.0, 0.0, 0.0])
        tgt = _np.array(axis)
        # if axis is degenerate, skip
        if _np.linalg.norm(tgt) == 0:
            rot = _np.eye(3)
        else:
            try:
                rot = trimesh.geometry.align_vectors(x_axis, tgt)
            except Exception:
                # fallback: compute rotation via simple method
                rot = _np.eye(3)

        # build homogeneous transform
        transform = _np.eye(4)
        transform[:3, :3] = rot
        mid = _np.array([(start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0, (start[2] + end[2]) / 2.0])
        transform[:3, 3] = mid
        box.apply_transform(transform)
        meshes.append(box)
        ids.append(m['id'])

    # broad-phase AABB check then precise collision using trimesh.collision
    clashes = []
    try:
        mgr = trimesh.collision.CollisionManager()
        for i, mesh in enumerate(meshes):
            mgr.add_object(ids[i], mesh)
        pairs = mgr.in_collision_internal()
        # pairs is list of tuple pairs (name1, name2)
        for a,b in pairs:
            # compute approximate distance by centerline segment distance for reporting
            ma = next((m for m in mems if m['id']==a), None)
            mb = next((m for m in mems if m['id']==b), None)
            if ma and mb:
                d = _segment_segment_distance(ma['start'], ma['end'], mb['start'], mb['end'])
            else:
                d = 0.0
            clashes.append({'a': a, 'b': b, 'dist_m': float(d)})
        return {'clashes': clashes}
    except Exception:
        # if CollisionManager or in_collision_internal isn't available, fallback to pairwise intersection sampling
        clashes = []
        for i in range(len(meshes)):
            for j in range(i+1, len(meshes)):
                a = meshes[i]; b = meshes[j]
                if not trimesh.bounds_overlap(a.bounds, b.bounds):
                    continue
                try:
                    inter = a.intersects(b)
                    if inter:
                        ma = mems[i]; mb = mems[j]
                        d = _segment_segment_distance(ma['start'], ma['end'], mb['start'], mb['end'])
                        clashes.append({'a': mems[i]['id'], 'b': mems[j]['id'], 'dist_m': float(d)})
                except Exception:
                    # final fallback: use centerline distance test
                    ma = mems[i]; mb = mems[j]
                    d = _segment_segment_distance(ma['start'], ma['end'], mb['start'], mb['end'])
                    ra = 0.5*math.hypot(extents[1], extents[2])
                    rb = ra
                    if d <= (ra + rb + tol):
                        clashes.append({'a': mems[i]['id'], 'b': mems[j]['id'], 'dist_m': float(d)})
        return {'clashes': clashes}


def risk_detector(full_json):
    out={'members':[]}
    for m in full_json['members']:
        score=0
        if m.get('stability',{}).get('buckling_risk')=='high': score+=50
        if m.get('safety',{}).get('status')=='review': score+=20
        if any(c['dist_m']<0.02 for c in (full_json.get('clash_list') or [])): score+=30
        level='low' if score<20 else 'medium' if score<60 else 'high'
        out['members'].append({'id':m['id'],'risk_score':score,'risk_level':level})
    return out


def reporter_agent(full_json,out_dir=None):
    bom=[]
    for m in full_json['members']:
        sel=m.get('selection',{}); bom.append({'id':m['id'],'section':sel.get('section_name'),'weight_kg':sel.get('weight_kg',0)})
    return {'bom':bom,'members':full_json['members']}


def cnc_exporter(full_json, out_path=None):
    """Export simple CNC/DSTV-style CSV from fabrication details.

    Columns: member_id, section, length_m, weight_kg, bolt_count, hole_type, hole_size_mm
    """
    import csv
    if out_path is None:
        out_path = os.path.join('outputs', 'cnc.csv')
    rows = []
    part_dir = os.path.join(os.path.dirname(out_path) if out_path else 'outputs', 'cnc_parts')
    if not os.path.exists(part_dir):
        os.makedirs(part_dir, exist_ok=True)
    # generate per-member part CSVs (DSTV-like minimal schema) and a master CSV
    for m in full_json['members']:
        sel = m.get('selection', {})
        fab = m.get('fabrication', {})
        conn = m.get('connection', {})
        hole = fab.get('holes', {}) if isinstance(fab.get('holes', {}), dict) else {}
        hole_type = hole.get('type') if hole else ''
        hole_size = ''
        if hole and isinstance(hole.get('size_mm'), (list, tuple)):
            hole_size = 'x'.join(str(int(x)) for x in hole.get('size_mm'))
        elif hole and hole.get('size_mm'):
            hole_size = str(hole.get('size_mm'))

        member_row = {
            'member_id': m['id'],
            'section': sel.get('section_name','UNKNOWN'),
            'length_m': float(m.get('length',0.0)),
            'weight_kg': float(sel.get('weight_kg',0.0)),
            'bolt_count': int(conn.get('bolt_count',0)) if conn else 0,
            'hole_type': hole_type or '',
            'hole_size_mm': hole_size,
        }
        rows.append(member_row)

        # create a per-part CSV with hole coordinates (approximate) for downstream CNC
        part_path = os.path.join(part_dir, f"{m['id']}_part.csv")
        try:
            with open(part_path, 'w', newline='') as pf:
                import csv as _csv
                writer = _csv.writer(pf)
                # header
                writer.writerow(['member_id', 'section', 'length_m', 'hole_index', 'hole_x_mm', 'hole_y_mm', 'hole_dia_mm'])
                # approximate hole layout: distribute along end plate width
                bolt_cnt = int(conn.get('bolt_count', 0)) if conn else 0
                hole_dia = int(hole.get('size_mm')[0]) if hole and isinstance(hole.get('size_mm'), (list, tuple)) and len(hole.get('size_mm'))>0 else (int(conn.get('bolt_dia_mm',0)) if conn else 0)
                # assume holes on a single end plate centered on member midpoint in local y direction
                for idx in range(bolt_cnt):
                    # simple spacing: 50 mm between bolts
                    x_mm = 25 + idx*50
                    y_mm = 0
                    writer.writerow([m['id'], sel.get('section_name','UNKNOWN'), float(m.get('length',0.0)), idx+1, x_mm, y_mm, hole_dia])
        except Exception:
            # fail silently for per-part writing
            pass
    # ensure directory
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, 'w', newline='') as csvfile:
        fieldnames = ['member_id','section','length_m','weight_kg','bolt_count','hole_type','hole_size_mm']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    # return master CSV and per-part directory
    return {'cnc_csv': out_path, 'rows': rows, 'parts_dir': part_dir}


def dstv_exporter(full_json, out_dir=None):
    """Emit a DSTV-like plain text per-part file and an index CSV for downstream machines.

    This is a conservative, simplified DSTV-style exporter that outputs per-part text files
    listing part metadata and hole coordinates in millimeters. It's intended as a bridge
    towards a full DSTV generator.
    """
    if out_dir is None:
        out_dir = os.path.join('outputs', 'dstv_parts')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    index_rows = []
    for m in full_json.get('members', []):
        pid = m['id']
        sel = m.get('selection', {})
        fab = m.get('fabrication', {})
        conn = m.get('connection', {})
        length_mm = int(round(float(m.get('length', 0.0)) * 1000.0))
        filename = f"{pid}.dstv"
        path = os.path.join(out_dir, filename)
        # compute hole list from fabrication details or connection
        hole_list = []
        hole_spec = fab.get('holes') if isinstance(fab.get('holes'), dict) else None
        bolt_cnt = int(conn.get('bolt_count', 0)) if conn else 0
        if hole_spec and isinstance(hole_spec.get('size_mm'), (list, tuple)):
            dia = int(hole_spec.get('size_mm')[0])
        else:
            dia = int(conn.get('bolt_dia_mm', 0)) if conn else 0

        # simple hole placement: if bolt_count, place along member local X from 25mm spacing
        for idx in range(bolt_cnt):
            x_mm = 25 + idx * 50
            y_mm = 0
            hole_list.append({'index': idx + 1, 'x_mm': int(x_mm), 'y_mm': int(y_mm), 'dia_mm': int(dia)})

        # compute global coordinates for holes (if local axes present) for reference
        global_holes = []
        try:
            # member axis unit
            axis = tuple(unit_vector(m['start'], m['end'])) if m.get('start') and m.get('end') else (1.0, 0.0, 0.0)
            # lateral direction (use local y if available)
            lateral = None
            if m.get('local_axes') and isinstance(m.get('local_axes'), dict):
                lat = m['local_axes'].get('y')
                if lat:
                    lateral = tuple(lat)
            if lateral is None:
                # fallback: produce a vector perpendicular to axis
                lateral = ( -axis[1], axis[0], 0.0 )
            # normalize lateral
            llen = math.hypot(lateral[0], lateral[1]) or 1.0
            lateral = (lateral[0]/llen, lateral[1]/llen, lateral[2]/(llen if llen!=0 else 1.0))
            for h in hole_list:
                # position along member from start (mm)
                x_m = h['x_mm'] / 1000.0
                # lateral offset in meters
                y_m = h['y_mm'] / 1000.0
                gx = float(m['start'][0]) + axis[0] * x_m + lateral[0] * y_m
                gy = float(m['start'][1]) + axis[1] * x_m + lateral[1] * y_m
                gz = float(m['start'][2]) + axis[2] * x_m + lateral[2] * y_m
                global_holes.append({'index': h['index'], 'x_mm': h['x_mm'], 'y_mm': h['y_mm'], 'dia_mm': h['dia_mm'], 'gx_mm': int(round(gx*1000)), 'gy_mm': int(round(gy*1000)), 'gz_mm': int(round(gz*1000))})
        except Exception:
            global_holes = []

        # write file
        try:
            with open(path, 'w') as f:
                f.write(f"*** DSTV PART FILE ***\n")
                f.write(f"PART_ID: {pid}\n")
                f.write(f"SECTION: {sel.get('section_name','UNKNOWN')}\n")
                f.write(f"LENGTH_MM: {length_mm}\n")
                f.write(f"CUT_OP: LENGTH,{length_mm}\n")
                f.write(f"HOLE_COUNT: {len(hole_list)}\n")
                f.write("HOLES_LOCAL:\n")
                f.write("index,x_mm,y_mm,dia_mm\n")
                for h in hole_list:
                    f.write(f"{h['index']},{h['x_mm']},{h['y_mm']},{h['dia_mm']}\n")
                if global_holes:
                    f.write("HOLES_GLOBAL_MM:\n")
                    f.write("index,gx_mm,gy_mm,gz_mm,dia_mm\n")
                    for gh in global_holes:
                        f.write(f"{gh['index']},{gh['gx_mm']},{gh['gy_mm']},{gh['gz_mm']},{gh['dia_mm']}\n")
        except Exception:
            # don't fail the pipeline for file write issues
            continue

        index_rows.append({'member_id': pid, 'file': filename, 'length_mm': length_mm, 'hole_count': len(hole_list)})

    # write master index
    index_path = os.path.join(out_dir, 'dstv_index.csv')
    try:
        with open(index_path, 'w', newline='') as cf:
            import csv as _csv
            writer = _csv.DictWriter(cf, fieldnames=['member_id', 'file', 'length_mm', 'hole_count'])
            writer.writeheader()
            for r in index_rows:
                writer.writerow(r)
    except Exception:
        pass

    return {'index': index_path, 'parts_dir': out_dir, 'rows': index_rows}


def soft_clash_detector(full_json, min_clearance_mm=50.0):
    """Detect soft clashes: insufficient clearance between members or with ground.
    Returns: {'soft_clashes': [{'a': id, 'b': id, 'clearance_mm': val, 'required_mm': min_clearance_mm}]}
    """
    soft_clashes = []
    mems = full_json.get('members', [])
    n = len(mems)
    for i in range(n):
        for j in range(i+1, n):
            a = mems[i]; b = mems[j]
            if a['id'] == b['id']:
                continue
            d = _segment_segment_distance(a['start'], a['end'], b['start'], b['end'])
            d_mm = d * 1000.0
            if 0 < d_mm < min_clearance_mm:
                soft_clashes.append({'a': a['id'], 'b': b['id'], 'clearance_mm': d_mm, 'required_mm': min_clearance_mm})
    for m in mems:
        min_z = min(m['start'][2], m['end'][2])
        if min_z < 0.5:
            soft_clashes.append({'type': 'ground_clearance', 'member_id': m['id'], 'min_height_m': min_z, 'required_m': 0.5})
    return {'soft_clashes': soft_clashes}


def functional_clash_detector(full_json):
    """Detect functional clashes: misalignments, hole mismatches, wrong part orientation.
    Returns: {'functional_clashes': [{'member_id': id, 'issue': desc, 'severity': 'low'|'medium'|'high'}]}
    """
    functional_clashes = []
    mems = full_json.get('members', [])
    for m in mems:
        v = unit_vector(m['start'], m['end'])
        angle = vec_angle_deg(v)
        if m.get('type') == 'column' and angle < 30:
            functional_clashes.append({'member_id': m['id'], 'issue': 'column_orientation_suspect', 'angle_deg': angle, 'severity': 'medium'})
        if m.get('type') == 'beam' and angle > 45:
            functional_clashes.append({'member_id': m['id'], 'issue': 'beam_orientation_suspect', 'angle_deg': angle, 'severity': 'medium'})
        conn = m.get('connection', {})
        if conn.get('type') == 'bolted_end_plate' and conn.get('bolt_count', 0) < 2:
            functional_clashes.append({'member_id': m['id'], 'issue': 'insufficient_bolt_count', 'bolt_count': conn.get('bolt_count'), 'severity': 'high'})
        if conn.get('type') == 'welded_base' and not conn.get('weld_size_mm'):
            functional_clashes.append({'member_id': m['id'], 'issue': 'missing_weld_size', 'severity': 'high'})
    return {'functional_clashes': functional_clashes}


def mep_clash_detector(full_json, mep_data=None):
    """Detect multi-discipline clashes: steel vs MEP (duct, pipe, cable, HVAC).
    mep_data: optional list of MEP objects {'type': 'duct'|'pipe'|'cable', 'start': [...], 'end': [...], 'size': val}
    Returns: {'mep_clashes': [{'member_id': id, 'mep_type': type, 'clash_distance': val}]}
    """
    mep_clashes = []
    if mep_data is None or len(mep_data) == 0:
        return {'mep_clashes': mep_clashes}
    mems = full_json.get('members', [])
    for m in mems:
        for mep in mep_data:
            d = _segment_segment_distance(m['start'], m['end'], mep.get('start'), mep.get('end'))
            min_clear = 0.10
            if d < min_clear:
                mep_clashes.append({'member_id': m['id'], 'mep_type': mep.get('type', 'unknown'), 'clash_distance_m': d, 'required_clearance_m': min_clear, 'severity': 'high' if d == 0 else 'medium'})
    return {'mep_clashes': mep_clashes}


def correction_loop(full_json,max_iters=5):
    model = full_json
    # helper: find next larger section by area
    def next_section(cur_name):
        catalog = sorted(SECTION_CATALOG, key=lambda s: s['area'])
        for i, s in enumerate(catalog):
            if s['name'] == cur_name:
                if i+1 < len(catalog):
                    return catalog[i+1]
                else:
                    return None
        # if not found, return largest
        return catalog[-1] if catalog else None

    accum_corrections = []
    for it in range(max_iters):
        # ensure current model dict tracks corrections across rebuilds
        if not isinstance(model, dict):
            model = {'members': getattr(model, 'members', [])}
        # capture any currently locked selections so we can reapply them after optimizer runs
        locked_selections = {m['id']: m.get('selection') for m in model['members'] if m.get('selection') and isinstance(m.get('selection'), dict) and m.get('selection').get('locked')}
        clashes = clasher_agent(model)['clashes']
        val = validator_agent(model)
        if not clashes and not val['errors']:
            model['correction_iters'] = it
            model['corrections'] = accum_corrections
            return model

        accum_corrections.append({'iter': it, 'clashes': clashes, 'validator': val})

        # attempt fixes from validator errors/warnings first
        for err in val.get('errors', []):
            mid = next((m for m in model['members'] if m['id'] == err['id']), None)
            if not mid:
                continue
            if err.get('fix') == 'upsample_section':
                cur_sel = mid.get('selection', {})
                cur_name = cur_sel.get('section_name') if cur_sel else None
                new_sec = next_section(cur_name) if cur_name else (SECTION_CATALOG[-1] if SECTION_CATALOG else None)
                if new_sec:
                    # apply new selection
                    mid['selection'] = {'section_name': new_sec['name'], 'weight_kg': (new_sec.get('weight_kg_per_m') or new_sec.get('weight_kg',0)) * mid['length'], 'locked': True}
                    accum_corrections.append({'iter': it, 'action': 'upsized_section', 'member': mid['id'], 'to': new_sec['name']})
        for warn in val.get('warnings', []):
            mid = next((m for m in model['members'] if m['id'] == warn['id']), None)
            if not mid:
                continue
            if warn.get('fix') == 'increase_bolts':
                conn = mid.get('connection', {})
                conn['bolt_count'] = int(conn.get('bolt_count', 0)) + 2
                mid['connection'] = conn
                accum_corrections.append({'iter': it, 'action': 'increased_bolts', 'member': mid['id'], 'new_bolt_count': conn['bolt_count']})
            if warn.get('fix') == 'increase_weld':
                conn = mid.get('connection', {})
                conn['weld_size_mm'] = max(3, int(conn.get('weld_size_mm', 0)))
                mid['connection'] = conn
                accum_corrections.append({'iter': it, 'action': 'increased_weld', 'member': mid['id'], 'new_weld_size_mm': conn['weld_size_mm']})

        # if clashes remain, attempt small geometric nudges on one side
        for c in clashes:
            a = next((m for m in model['members'] if m['id'] == c['a']), None)
            b = next((m for m in model['members'] if m['id'] == c['b']), None)
            if a and b:
                v = a.get('orientation') or unit_vector(a['start'], a['end'])
                # nudge a along its orientation by small amount
                nudge = 0.02
                a['start'] = [a['start'][0] + nudge * v[0], a['start'][1] + nudge * v[1], a['start'][2] + nudge * v[2]]
                a['end'] = [a['end'][0] + nudge * v[0], a['end'][1] + nudge * v[1], a['end'][2] + nudge * v[2]]
                accum_corrections.append({'iter': it, 'action': 'nudge', 'member': a['id'], 'nudge_m': nudge})

        # rebuild pipeline stages after applying fixes/nudges
        model = engineer_standardize({'members': [{'start': m['start'], 'end': m['end'], 'length': length(m['start'], m['end']), 'layer': m.get('layer'), 'selection': m.get('selection'), 'connection': m.get('connection')} for m in model['members']]})
        model = load_path_resolver(model)
        model = stability_agent(model)
        # preserve selections we set by copying them back after optimizer runs
        # run optimizer but respect manually set selection if present
        model = optimizer_agent(model)
        # reapply locked selections we captured earlier so manual upsizes persist
        for m in model['members']:
            if m['id'] in locked_selections:
                m['selection'] = locked_selections[m['id']]
            else:
                # if original model (full_json) had connections we wanted preserved, copy them
                orig = next((om for om in full_json.get('members', []) if om['id'] == m['id']), None)
                if orig and orig.get('connection'):
                    m['connection'] = orig.get('connection')

        model = connection_designer(model)
        model = fabrication_detailing(model)
        model = fabrication_standards(model)
        model = erection_planner(model)
        model = safety_compliance(model)
        model['clash_list'] = clasher_agent(model)['clashes']

    model['correction_iters'] = max_iters
    model['corrections'] = accum_corrections
    return model

# ============================================================================
# FEATURE 16: ERROR HANDLING & ROBUSTNESS
# ============================================================================

class InputValidator:
    """Validate DXF/IFC input data"""
    @staticmethod
    def validate_member(member):
        """Check member for schema compliance"""
        errors = []
        if 'start' not in member or len(member['start']) != 3:
            errors.append('member missing or invalid start coordinates')
        if 'end' not in member or len(member['end']) != 3:
            errors.append('member missing or invalid end coordinates')
        if member.get('length', 0) <= 0:
            errors.append('member length must be positive')
        return errors

class FallbackHandler:
    """Fallback strategies when ML models fail"""
    @staticmethod
    def heuristic_section_selection(length_m, member_type):
        """Heuristic fallback for section selection if ML fails"""
        if member_type == 'column':
            return 'W8x10' if length_m < 4 else 'W10x12'
        elif member_type == 'beam':
            return 'W8x10' if length_m < 5 else 'W10x12'
        else:
            return 'HSS100x100x6'
    
    @staticmethod
    def heuristic_load_calculation(member_type, span_m):
        """Heuristic fallback for load estimation"""
        if member_type == 'beam':
            return {'axial_kN': 5, 'moment_kNm': 10 * span_m, 'shear_kN': 10}
        elif member_type == 'column':
            return {'axial_kN': 100, 'moment_kNm': 5, 'shear_kN': 2}
        else:
            return {'axial_kN': 20, 'moment_kNm': 2, 'shear_kN': 5}

class StructuredLogger:
    """JSON-based logging with timestamps and severity"""
    @staticmethod
    def log_event(event_type, severity='INFO', message='', details=None):
        """Create structured log entry"""
        import datetime
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'message': message,
            'details': details or {}
        }

class WarningSystem:
    """User-facing warnings with fix suggestions"""
    @staticmethod
    def generate_warning(issue_code, member_id, suggestion):
        """Generate warning with suggested fix"""
        warnings_map = {
            'undersized_section': 'Section capacity exceeded - suggest upsizing',
            'insufficient_bolts': 'Bolt shear capacity exceeded - suggest increasing bolt count',
            'inadequate_weld': 'Weld size insufficient - suggest larger weld',
            'clash_detected': 'Geometric clash detected - suggest geometry offset',
        }
        return {
            'member_id': member_id,
            'issue': issue_code,
            'description': warnings_map.get(issue_code, 'Unknown issue'),
            'suggestion': suggestion
        }

# ============================================================================
# FEATURE 17: PERFORMANCE OPTIMIZATION
# ============================================================================

class ParallelProcessor:
    """Multi-threaded processing for member design"""
    @staticmethod
    def process_members_parallel(members, processor_func, num_threads=4):
        """Process members in parallel (simplified: returns sequential for compatibility)"""
        # Full implementation would use ThreadPoolExecutor
        results = []
        for m in members:
            try:
                result = processor_func(m)
                results.append(result)
            except Exception as e:
                results.append({'id': m.get('id'), 'error': str(e)})
        return results

class SpatialIndex:
    """Simple spatial indexing for fast clash queries"""
    def __init__(self, members, grid_size=10.0):
        self.grid_size = grid_size
        self.grid = defaultdict(list)
        for m in members:
            key = self._grid_key(m)
            self.grid[key].append(m)
    
    def _grid_key(self, member):
        """Map member to grid cell"""
        mid = [(member['start'][i] + member['end'][i]) / 2 for i in range(3)]
        return tuple(int(mid[i] / self.grid_size) for i in range(3))
    
    def nearby_members(self, member, radius=1):
        """Get members near given member"""
        key = self._grid_key(member)
        nearby = []
        for di in [-radius, 0, radius]:
            for dj in [-radius, 0, radius]:
                for dk in [-radius, 0, radius]:
                    new_key = (key[0] + di, key[1] + dj, key[2] + dk)
                    nearby.extend(self.grid.get(new_key, []))
        return nearby

class ResultCache:
    """Memoization cache for repeated calculations"""
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        """Retrieve cached result"""
        return self.cache.get(key)
    
    def set(self, key, value):
        """Store result in cache"""
        self.cache[key] = value
        return value

# ============================================================================
# FEATURE 19: MACHINE LEARNING ENHANCEMENTS
# ============================================================================

class ConnectionTypeClassifier:
    """ML-based connection type selection"""
    @staticmethod
    def predict_connection_type(axial_kN, moment_kNm, shear_kN, member_type):
        """Predict optimal connection type based on loads"""
        if moment_kNm > abs(axial_kN) * 0.5:
            return 'welded_moment_connection'
        elif abs(shear_kN) > 50:
            return 'bolted_end_plate'
        else:
            return 'bolted_gusset_plate'

class LoadPredictor:
    """ML model for load estimation from similar projects"""
    @staticmethod
    def predict_loads(member_type, span_m, building_type='office'):
        """Predict loads for member"""
        # Simplified: in production, use trained model
        if building_type == 'office':
            dead_factor = 1.0
            live_factor = 1.2
        elif building_type == 'warehouse':
            dead_factor = 1.3
            live_factor = 2.0
        else:
            dead_factor = 1.0
            live_factor = 1.0
        
        if member_type == 'beam':
            return {'axial_kN': 10 * dead_factor, 'moment_kNm': 20 * span_m * live_factor, 'shear_kN': 15 * live_factor}
        elif member_type == 'column':
            return {'axial_kN': 200 * dead_factor, 'moment_kNm': 10, 'shear_kN': 5}
        else:
            return {'axial_kN': 30, 'moment_kNm': 5, 'shear_kN': 10}

class AnomalyDetector:
    """Flag unusual member configurations"""
    @staticmethod
    def detect_anomalies(member):
        """Identify unusual geometry or properties"""
        anomalies = []
        length = member.get('length', 0)
        if length > 30:
            anomalies.append({'type': 'unusually_long', 'value': length, 'severity': 'medium'})
        if length < 0.5:
            anomalies.append({'type': 'very_short', 'value': length, 'severity': 'high'})
        return anomalies

# ============================================================================
# FEATURE 20: REGULATORY & STANDARDS COMPLIANCE
# ============================================================================

class IBCChecker:
    """International Building Code compliance"""
    @staticmethod
    def check_occupancy_limits(occupancy_type, building_height_m, building_area_m2):
        """Check height and area limits"""
        limits = {
            'office': {'height_limit_m': 56, 'area_limit_m2': 10000},
            'warehouse': {'height_limit_m': 25, 'area_limit_m2': 15000},
            'school': {'height_limit_m': 35, 'area_limit_m2': 8000},
        }
        limits_obj = limits.get(occupancy_type, {'height_limit_m': 40, 'area_limit_m2': 10000})
        return {
            'height_pass': building_height_m <= limits_obj['height_limit_m'],
            'area_pass': building_area_m2 <= limits_obj['area_limit_m2'],
        }

class FireRatingCalculator:
    """ASTM E119 fire rating and fireproofing"""
    @staticmethod
    def fireproofing_thickness(rating_hours, section_profile):
        """Calculate fireproofing spray thickness for rating"""
        thickness_mm_per_hour = {'W_beam': 25, 'HSS': 30, 'tube': 35}
        base_thickness = thickness_mm_per_hour.get(section_profile, 25)
        return base_thickness * rating_hours

class ADAComplianceChecker:
    """Americans with Disabilities Act accessibility checks"""
    @staticmethod
    def check_clearances(passageway_width_m, door_width_m):
        """Verify ADA clearance requirements"""
        return {
            'passageway_adequate': passageway_width_m >= 0.9,  # 3ft minimum
            'door_adequate': door_width_m >= 0.8,  # 32" minimum
        }

class EmbodiedCarbonCalculator:
    """EPD-based embodied carbon tracking"""
    @staticmethod
    def carbon_for_steel(weight_kg, material_grade='A36', recycled_content_percent=25):
        """Estimate embodied carbon (kg CO2e) for steel member"""
        # Simplified: 1.5-2.0 kg CO2e per kg steel (varies by source, recycled content)
        base_carbon = 1.8
        reduction_per_recycled_percent = 0.008  # 0.8% reduction per 1% recycled content
        carbon_factor = base_carbon * (1.0 - reduction_per_recycled_percent * recycled_content_percent)
        return weight_kg * carbon_factor
    
    @staticmethod
    def total_project_carbon(members):
        """Calculate total embodied carbon for project"""
        total = 0
        for m in members:
            weight = m.get('selection', {}).get('weight_kg', 0)
            carbon = EmbodiedCarbonCalculator.carbon_for_steel(weight)
            total += carbon
        return total

class OSHARequirementsGenerator:
    """OSHA 1926 safety requirements"""
    @staticmethod
    def fall_protection_requirements(work_height_m):
        """OSHA 1926.500: Fall protection requirements"""
        if work_height_m >= 1.8:  # 6 feet
            return {
                'required': True,
                'anchor_points': 'required_5000_lbf_capacity_each',
                'guardrail_height_mm': 1070,  # 42" ± 3"
                'rope_grab_required': True
            }
        else:
            return {'required': False}
    
    @staticmethod
    def wrench_clearance_requirement():
        """OSHA requirement for bolt wrench access"""
        return {'min_clearance_mm': 150, 'standard': 'OSHA_1926.501'}

class RegulatoryComplianceModule:
    """Consolidated regulatory compliance checks"""
    @staticmethod
    def full_compliance_report(members, building_info):
        """Generate comprehensive compliance report"""
        report = {
            'ibc_compliance': IBCChecker.check_occupancy_limits(building_info.get('occupancy'), building_info.get('height_m'), building_info.get('area_m2')),
            'fire_rating': FireRatingCalculator.fireproofing_thickness(building_info.get('fire_rating_hours', 1), 'W_beam'),
            'ada_compliance': ADAComplianceChecker.check_clearances(2.0, 0.9),
            'embodied_carbon_kgCO2e': EmbodiedCarbonCalculator.total_project_carbon(members),
            'osha_fall_protection': OSHARequirementsGenerator.fall_protection_requirements(building_info.get('max_work_height_m', 5)),
        }
        return report


class Pipeline:
    def __init__(self): pass
    def run_from_dxf_entities(self,dxf_entities,out_dir=None):
        import warnings
        warnings.warn('Pipeline.run_from_dxf_entities is deprecated; use pipeline_compat.run_pipeline() or agents.main_pipeline_agent.process()', DeprecationWarning)
        # accept either a DXF path, an IFC path, or list of extracted entities
        if isinstance(dxf_entities, str):
            if dxf_entities.lower().endswith('.ifc'):
                a = extract_from_ifc(dxf_entities)
            else:
                a = extract_from_dxf(dxf_entities)
        else:
            a = extract_from_dxf(dxf_entities)
        b=engineer_standardize(a); c=load_path_resolver(b); d=stability_agent(c)
        e=optimizer_agent(d); f=connection_designer(e); g=fabrication_detailing(f); h=fabrication_standards(g)
        i=erection_planner(h); j=safety_compliance(i); k=analysis_model_generator(j)
        l=builder_ifc(h,out_path=os.path.join(out_dir or 'outputs','model.ifc'))
        v = validator_agent(h)
        clash = clasher_agent(h)
        mesh_clash = mesh_clasher_agent(h)
        soft_clash = soft_clash_detector(h)
        func_clash = functional_clash_detector(h)
        mep_clash = mep_clash_detector(h)
        # prefer mesh-based clashes for final reporting
        h['clash_list'] = mesh_clash['clashes'] if mesh_clash['clashes'] else clash['clashes']
        r = risk_detector({**h, 'clash_list': h['clash_list']})
        rep = reporter_agent(h, out_dir=out_dir)
        final = correction_loop(h)
        cnc = cnc_exporter(h, out_path=os.path.join(out_dir or 'outputs','cnc.csv'))
        dstv = dstv_exporter(h, out_dir=os.path.join(out_dir or 'outputs','dstv_parts'))
        return {
            'miner': a,
            'engineer': b,
            'loads': c,
            'stability': d,
            'optimizer': e,
            'connections': f,
            'fabrication': g,
            'standards': h,
            'erection': i,
            'safety': j,
            'analysis': k,
            'ifc': l,
            'validator': v,
            'clashes': clash,
            'mesh_clashes': mesh_clash,
            'soft_clashes': soft_clash,
            'functional_clashes': func_clash,
            'mep_clashes': mep_clash,
            'risk': r,
            'reporter': rep,
            'final': final,
            'cnc': cnc,
            'dstv': dstv,
        }


if __name__=='__main__':
    sample=[{'start':[0,0,0],'end':[6,0,0],'layer':'BEAMS'},{'start':[6,0,0],'end':[6,0,4],'layer':'COLUMNS'},{'start':[0,0,0],'end':[0,6,0],'layer':'BEAMS'}]
    p=Pipeline(); out=p.run_from_dxf_entities(sample,out_dir='outputs'); print(json.dumps({'summary':{'members':len(out['miner']['members']),'ifc':out['ifc']}},indent=2))
# ---------------------------------------------------------------------------
# Migration override: delegate pipeline orchestration to modular agents package
# If enabled, call the `main_pipeline_agent` orchestration, but preserve the
# legacy pipeline outputs by running the original implementation and attaching
# the agent-driven result under `agents_orchestration` for compatibility.
# Set `MIGRATE_AGENT_ORCHESTRATION=False` to disable.
# ---------------------------------------------------------------------------
MIGRATE_AGENT_ORCHESTRATION = True
if MIGRATE_AGENT_ORCHESTRATION:
    try:
        from src.pipeline.agents import main_pipeline_agent as _main_agent
        # Preserve old implementation
        _old_run = Pipeline.run_from_dxf_entities

        def _delegating_run(self, dxf_entities, out_dir=None):
            # Run legacy pipeline first to preserve behavior
            legacy_out = _old_run(self, dxf_entities, out_dir=out_dir)
            try:
                # Build a compact payload for the agent orchestrator
                payload = {'data': {'items': legacy_out.get('miner', {}), 'hazard': 0.05, 'exposure': 0.1, 'complexity': 0.1}}
                agent_res = _main_agent.process(payload)
                legacy_out['agents_orchestration'] = agent_res
            except Exception as _e:
                # Attach error info but do not break legacy behavior
                legacy_out['agents_orchestration'] = {'error': str(_e)}
            return legacy_out

        Pipeline.run_from_dxf_entities = _delegating_run
    except Exception:
        # If the agents package isn't importable or process fails, leave Pipeline as-is
        pass

# ---------------------------------------------------------------------------
# Compatibility shim (non-destructive)
# If external code imports names from the old monolith `pipeline_v2`, prefer
# existing definitions in this file. If a name is missing, set it from the
# modular `pipeline_compat` shim so older callers keep working during migration.
# ---------------------------------------------------------------------------
try:
    from src.pipeline.pipeline_compat import (
        CoordinateSystemManager as _CoordCompat,
        RotationMatrix3D as _RotCompat,
        CurvedMemberHandler as _CurvedCompat,
        CamberCalculator as _CamberCompat,
        SkewCutGeometry as _SkewCompat,
        EccentricityResolver as _EccComp,
        CompoundSectionBuilder as _CompSec,
        WebOpeningHandler as _WebOpen,
        TorsionalPropertyCalculator as _Torsion,
        PlasticAnalysisProperties as _Plastic,
        LoadCombinationAnalyzer as _LoadComb,
        WindLoadAnalyzer as _Wind,
        SeismicLoadAnalyzer as _Seismic,
        PDeltaAnalyzer as _PDelta,
        InfluenceLineAnalyzer as _Influence,
        AISC360Checker as _AISC360,
        AISC341SeismicChecker as _AISC341,
        MaterialSelector as _MatSel,
        CoatingSpecifier as _CoatSpec,
        MATERIAL_DATABASE as _MATERIAL_DATABASE,
        agents as _agents_package,
        recommend_material_for_section as recommend_material_for_section,
        list_agents as list_agents
    )

    # Only set names that are not already defined in this module (non-destructive)
    g = globals()
    g.setdefault('CoordinateSystemManager', _CoordCompat)
    g.setdefault('RotationMatrix3D', _RotCompat)
    g.setdefault('CurvedMemberHandler', _CurvedCompat)
    g.setdefault('CamberCalculator', _CamberCompat)
    g.setdefault('SkewCutGeometry', _SkewCompat)
    g.setdefault('EccentricityResolver', _EccComp)

    g.setdefault('CompoundSectionBuilder', _CompSec)
    g.setdefault('WebOpeningHandler', _WebOpen)
    g.setdefault('TorsionalPropertyCalculator', _Torsion)
    g.setdefault('PlasticAnalysisProperties', _Plastic)

    g.setdefault('LoadCombinationAnalyzer', _LoadComb)
    g.setdefault('WindLoadAnalyzer', _Wind)
    g.setdefault('SeismicLoadAnalyzer', _Seismic)
    g.setdefault('PDeltaAnalyzer', _PDelta)
    g.setdefault('InfluenceLineAnalyzer', _Influence)

    g.setdefault('AISC360Checker', _AISC360)
    g.setdefault('AISC341SeismicChecker', _AISC341)

    g.setdefault('MaterialSelector', _MatSel)
    g.setdefault('CoatingSpecifier', _CoatSpec)
    g.setdefault('MATERIAL_DATABASE', _MATERIAL_DATABASE)

    # Provide `agents` package under the old module namespace
    g.setdefault('agents', _agents_package)

except Exception:
    # If compat import fails, continue without breaking existing pipeline_v2 behavior
    pass
