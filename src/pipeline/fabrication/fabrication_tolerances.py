"""Fabrication tolerances, spacing and edge distance checks."""

def check_edge_distance(plate_thickness_mm: float, edge_distance_mm: float, min_factor: float=8.0) -> bool:
    # Conservative rule: edge distance >= 8*thickness
    return edge_distance_mm >= (min_factor * plate_thickness_mm)

def check_bolt_spacing(bolt_dia_mm: float, spacing_mm: float, min_factor: float=3.0) -> bool:
    # spacing >= 3*bolt diameter
    return spacing_mm >= (min_factor * bolt_dia_mm)
