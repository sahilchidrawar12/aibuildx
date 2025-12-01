"""
Curved Member Handler for handling arcs, polylines, splines, and other curved geometry.
Discretizes complex curves into manageable polyline segments for analysis and fabrication.
"""
import math


class CurvedMemberHandler:
    """Handle arcs, polylines, splines in member geometry"""
    
    @staticmethod
    def arc_to_polyline(center, radius, start_angle, end_angle, num_segments=20):
        """
        Discretize arc into polyline segments.
        
        Args:
            center: [x, y, z] arc center
            radius: Arc radius in same units
            start_angle: Start angle in radians
            end_angle: End angle in radians
            num_segments: Number of segments to create
            
        Returns:
            List of [x, y, z] points along arc
        """
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
        """
        Simplified spline interpolation using Catmull-Rom approximation.
        
        Args:
            control_points: List of [x, y, z] control points
            num_segments: Number of segments per control interval
            
        Returns:
            List of interpolated [x, y, z] points
        """
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
                
                # Catmull-Rom interpolation per axis
                q = [
                    0.5 * (2*p1[j] + (-p0[j] + p2[j])*t + (2*p0[j] - 5*p1[j] + 4*p2[j] - p3[j])*t*t + 
                           (-p0[j] + 3*p1[j] - 3*p2[j] + p3[j])*t*t*t)
                    for j in range(3)
                ]
                points.append(q)
        
        return points
    
    @staticmethod
    def polyline_length(points):
        """
        Calculate total length of polyline.
        
        Args:
            points: List of [x, y, z] points
            
        Returns:
            Total length (accumulated distance between consecutive points)
        """
        if len(points) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dz = p2[2] - p1[2]
            segment_length = math.sqrt(dx*dx + dy*dy + dz*dz)
            total_length += segment_length
        
        return total_length
    
    @staticmethod
    def resample_polyline(points, num_points=20):
        """
        Resample polyline to have specified number of points.
        
        Args:
            points: List of [x, y, z] points
            num_points: Desired number of output points
            
        Returns:
            Resampled list of [x, y, z] points
        """
        if len(points) <= 1:
            return points
        
        total_length = CurvedMemberHandler.polyline_length(points)
        target_spacing = total_length / max(1, num_points - 1)
        
        resampled = [points[0]]
        current_pos = 0.0
        point_idx = 0
        
        for target_pos in [i * target_spacing for i in range(1, num_points)]:
            while point_idx < len(points) - 1:
                p1 = points[point_idx]
                p2 = points[point_idx + 1]
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                dz = p2[2] - p1[2]
                segment_length = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if current_pos + segment_length >= target_pos:
                    # Interpolate within this segment
                    if segment_length > 0:
                        t = (target_pos - current_pos) / segment_length
                    else:
                        t = 0.5
                    
                    interp = [
                        p1[j] + t * (p2[j] - p1[j])
                        for j in range(3)
                    ]
                    resampled.append(interp)
                    break
                
                current_pos += segment_length
                point_idx += 1
        
        if len(resampled) < num_points:
            resampled.append(points[-1])
        
        return resampled
