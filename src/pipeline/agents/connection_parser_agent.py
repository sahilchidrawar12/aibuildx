"""Connection Parser Agent
Converts DXF circle markers (connection points) into joint objects with member links.

This agent:
1. Takes circles from DXF CONNECTIONS layer
2. Finds which members intersect near each circle
3. Creates joint objects with member references
4. Determines connection type (bolted/welded) based on member angles

Input: 
  - circles: List of circle markers with center position and radius
  - members: List of beam/column members with start/end coordinates
  
Output:
  - joints: List of joint objects with member links and connection type
"""

from typing import List, Dict, Any, Tuple
import math
import uuid


def _distance_3d(p1: List[float], p2: List[float]) -> float:
    """Calculate 3D Euclidean distance."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


def _point_to_line_distance(point: List[float], line_start: List[float], line_end: List[float]) -> float:
    """Calculate perpendicular distance from point to line segment."""
    # Vector from line_start to line_end
    line_vec = [line_end[i] - line_start[i] for i in range(3)]
    line_len_sq = sum(v ** 2 for v in line_vec)
    
    if line_len_sq == 0:
        return _distance_3d(point, line_start)
    
    # Vector from line_start to point
    point_vec = [point[i] - line_start[i] for i in range(3)]
    
    # Project point onto line
    t = max(0, min(1, sum(point_vec[i] * line_vec[i] for i in range(3)) / line_len_sq))
    
    # Closest point on line
    closest = [line_start[i] + t * line_vec[i] for i in range(3)]
    
    return _distance_3d(point, closest)


def _member_angle_2d(member1: Dict[str, Any], member2: Dict[str, Any]) -> float:
    """Calculate 2D angle between two members (in XY plane).
    Returns angle in degrees (0-90)."""
    
    def get_direction(m):
        """Get 2D direction vector of member."""
        start = m.get('start', [0, 0, 0])
        end = m.get('end', [1, 0, 0])
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx**2 + dy**2) or 1.0
        return [dx / length, dy / length]
    
    d1 = get_direction(member1)
    d2 = get_direction(member2)
    
    # Dot product and angle
    dot = d1[0] * d2[0] + d1[1] * d2[1]
    cos_angle = max(-1.0, min(1.0, dot))  # Clamp for numerical stability
    angle_rad = math.acos(cos_angle)
    angle_deg = math.degrees(angle_rad)
    
    # Return acute angle (0-90)
    return min(angle_deg, 180 - angle_deg)


def parse_connections(circles: List[Dict[str, Any]], members: List[Dict[str, Any]], 
                      search_radius_mm: float = 150.0, 
                      member_angle_threshold_deg: float = 20.0) -> List[Dict[str, Any]]:
    """
    Convert DXF circles into joints with member links.
    
    Args:
        circles: List of circle markers from DXF with 'center', 'radius', 'layer'
        members: List of structural members with 'start', 'end', 'id'
        search_radius_mm: How far from circle center to search for intersecting members
        member_angle_threshold_deg: Threshold for determining connection type
        
    Returns:
        List of joint objects with member links
    """
    
    joints = []
    
    for circle in circles:
        center = circle.get('center', [0, 0, 0])
        radius = circle.get('radius', 100.0)
        layer = circle.get('layer', 'CONNECTIONS')
        
        # Find members that intersect or are very close to this circle
        intersecting_members = []
        
        for member in members:
            start = member.get('start', [0, 0, 0])
            end = member.get('end', [1, 0, 0])
            
            # Calculate distance from circle center to member line
            dist = _point_to_line_distance(center, start, end)
            
            # If member passes within search radius, it's a candidate
            if dist <= search_radius_mm:
                intersecting_members.append({
                    'id': member.get('id'),
                    'distance': dist,
                    'member': member
                })
        
        # Sort by distance (closest first)
        intersecting_members.sort(key=lambda x: x['distance'])
        
        # Create joint if we have member(s) nearby
        if intersecting_members:
            member_ids = [m['id'] for m in intersecting_members]
            
            # Determine connection type based on member angles
            connection_type = 'generic_bolted'  # Default
            
            if len(intersecting_members) >= 2:
                # Get angle between first two members
                angle = _member_angle_2d(
                    intersecting_members[0]['member'],
                    intersecting_members[1]['member']
                )
                
                # Simple heuristic: perpendicular = moment connection, parallel = splice
                if angle < member_angle_threshold_deg:
                    connection_type = 'splice_bolted'  # Members nearly parallel
                elif angle > (90 - member_angle_threshold_deg):
                    connection_type = 'moment_bolted'  # Members nearly perpendicular
                else:
                    connection_type = 'angle_bolted'  # Angle connections
            
            joint = {
                'id': f"joint_{uuid.uuid4().hex[:8]}",
                'position': center,
                'members': member_ids,
                'member_count': len(member_ids),
                'connection_type': connection_type,
                'layer': layer,
                'search_radius': search_radius_mm,
                'detected_members': [
                    {
                        'id': m['id'],
                        'distance_from_center': m['distance']
                    } for m in intersecting_members
                ]
            }
            
            joints.append(joint)
    
    return joints


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process connection parsing for the pipeline."""
    
    circles = payload.get('circles', [])
    members = payload.get('members', [])
    
    if not circles:
        return {'status': 'ok', 'joints': [], 'note': 'No circles found in input'}
    
    if not members:
        return {'status': 'ok', 'joints': [], 'note': 'No members found in input'}
    
    try:
        joints = parse_connections(circles, members)
        return {
            'status': 'ok',
            'joints': joints,
            'summary': {
                'circles_processed': len(circles),
                'members_available': len(members),
                'joints_created': len(joints)
            }
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'joints': []}


class ConnectionParserAgent:
    """Agent for parsing DXF circles into joints."""
    
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run the connection parser."""
        return process(payload)
