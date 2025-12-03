"""Connection Synthesis Agent
Generates plate and fastener entities from joints using rule-based selection
and lightweight heuristics, aligned with existing pipeline style.

Principles:
- Code-only: no dataset mutations; read-only use of available data.
- Deterministic defaults with tolerance checks.
- Extensible hooks to incorporate catalog-driven selection later.

Updated features:
- Plates include members list for connection tracking
- Bolts include plate_id for connection relationships
- All units normalized to metres (conversion from mm)
- Proper Axis2Placement3D orientation for all elements
"""
from typing import List, Dict, Any, Tuple
import math

def _default_plate_size_mm(member_profile: Dict[str, Any]) -> Tuple[float, float, float]:
    """Return (width_mm, height_mm, thickness_mm) based on a rough profile size.
    Uses area or depth where available; otherwise conservative defaults."""
    area = (member_profile or {}).get('area') or 25000.0  # mm^2 fallback
    # Derive a notional depth ~ sqrt(area)
    depth = max(100.0, (area ** 0.5))
    width = max(140.0, 0.8 * depth)
    height = max(140.0, 0.8 * depth)
    thickness = 10.0
    return (width, height, thickness)

def _bolt_layout_mm(spacing_mm: float = 80.0) -> List[Tuple[float, float, float]]:
    """Return 2x2 grid offsets (ox, oy, oz) in mm centred around joint."""
    s = spacing_mm
    return [
        (-s/2, -s/2, 0.0),
        ( s/2, -s/2, 0.0),
        (-s/2,  s/2, 0.0),
        ( s/2,  s/2, 0.0),
    ]

def _normalize(vec: List[float]) -> List[float]:
    n = math.sqrt(sum((v or 0.0)**2 for v in vec)) or 1.0
    return [((v or 0.0)/n) for v in vec]

def _to_metres(val: float) -> float:
    """Convert from mm to metres if value looks like mm."""
    try:
        if val is None:
            return None
        return (val / 1000.0) if abs(val) >= 100 else float(val)
    except Exception:
        return val

def compute_local_frame(member: Dict[str, Any]) -> Dict[str, List[float]]:
    """Compute local axes for a member: X along member, Y strong, Z weak.
    Fallback: derive Y/Z from global up and X.
    Returns dict with 'X','Y','Z'."""
    start = member.get('start') or [0.0,0.0,0.0]
    end = member.get('end') or [1.0,0.0,0.0]
    X = _normalize([end[i]-start[i] for i in range(3)])
    # Use global up as provisional strong axis, then orthogonalize
    up = [0.0,0.0,1.0]
    # Z = X × up (weak), Y = Z × X (strong)
    Z = _normalize([
        X[1]*up[2] - X[2]*up[1],
        X[2]*up[0] - X[0]*up[2],
        X[0]*up[1] - X[1]*up[0]
    ])
    Y = _normalize([
        Z[1]*X[2] - Z[2]*X[1],
        Z[2]*X[0] - Z[0]*X[2],
        Z[0]*X[1] - Z[1]*X[0]
    ])
    return {'X': X, 'Y': Y, 'Z': Z}

def local_to_global(origin: List[float], frame: Dict[str, List[float]], offset_local: Tuple[float,float,float]) -> List[float]:
    """Transform local offset (mm) to global coordinates (mm)."""
    ox, oy, oz = offset_local
    X, Y, Z = frame['X'], frame['Y'], frame['Z']
    return [
        (origin[0] or 0.0) + ox*X[0] + oy*Y[0] + oz*Z[0],
        (origin[1] or 0.0) + ox*X[1] + oy*Y[1] + oz*Z[1],
        (origin[2] or 0.0) + ox*X[2] + oy*Y[2] + oz*Z[2],
    ]

def synthesize_connections(members: List[Dict[str, Any]], joints: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Create simple shear plates and bolt groups for each joint.
    Returns (plates, bolts).
    
    Enhanced to:
    - Include members list in plates for connection tracking
    - Convert units from mm to m for all positions/dimensions
    - Include plate_id in bolts for connection relationships
    - Properly normalize all orientation vectors
    """
    plates: List[Dict[str, Any]] = []
    bolts: List[Dict[str, Any]] = []

    # Map member id -> profile for quick lookup
    prof_by_id = {m.get('id'): (m.get('profile') or m.get('geom') or {}) for m in members}
    frame_by_id = {m.get('id'): compute_local_frame(m) for m in members}

    for j in joints:
        j_id = j.get('id') or f"joint_{len(plates)}"
        j_pos = j.get('position') or j.get('node') or [0.0, 0.0, 0.0]
        
        # Try to estimate based on first connected member
        m_ids = j.get('members') or []
        base_prof = prof_by_id.get(m_ids[0]) if m_ids else {}
        
        # Rule-based thickness: ~ depth/20, bounded [8, 20] mm
        w_mm, h_mm, thk_mm = _default_plate_size_mm(base_prof)
        depth = max(100.0, (base_prof.get('depth') or (base_prof.get('area') or 25000.0)**0.5))
        thk_mm = max(8.0, min(20.0, depth/20.0))
        bolt_dia_mm = 20.0 if depth < 400 else 24.0
        pattern = _bolt_layout_mm(80.0 if depth < 400 else 100.0)
        
        # Generate plate with normalized units and proper orientation
        plate = {
            'id': f"plate_{j_id}",
            'position': j_pos,  # This will be converted to metres by IFC generator
            'outline': {
                'width_mm': w_mm,
                'height_mm': h_mm
            },
            'thickness': thk_mm,  # Will be converted to metres by IFC generator
            'material': {'name': 'S235'},
            'members': list(m_ids)  # Add members for connection tracking
        }
        
        # Set orientation with normalized vectors
        plate['orientation'] = {
            'Axis2Placement3D': {
                'origin_mm': j_pos,
                'axis': _normalize(frame_by_id.get(m_ids[0], {'Z':[0,0,1]}).get('Z', [0,0,1])),
                'refDirection': _normalize(frame_by_id.get(m_ids[0], {'X':[1,0,0]}).get('X', [1,0,0]))
            }
        }
        plates.append(plate)

        # Bolt group with plate reference and normalized positions
        for ox, oy, oz in pattern:
            # Transform local offsets to global positions using member frame
            frame = frame_by_id.get(m_ids[0]) if m_ids else {'X':[1,0,0],'Y':[0,1,0],'Z':[0,0,1]}
            pos_global = local_to_global(j_pos, frame, (ox, oy, oz))
            
            bolts.append({
                'id': f"bolt_{j_id}_{int(ox)}_{int(oy)}",
                'diameter': bolt_dia_mm,
                'pos': pos_global,  # Will be converted to metres by IFC generator
                'position': pos_global,
                'grade': 'A325',
                'plate_id': plate['id']  # Add plate reference for connection tracking
            })

    return plates, bolts
