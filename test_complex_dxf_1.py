"""
Generate 4 most challenging DXF files for testing:
1. Curved truss with arcs and splines
2. Spiral staircase with helical members
3. Double-curved dome with elliptical sections
4. Complex junction with multiple intersecting members
"""
import os
import json
from ezdxf import new
import math

def create_curved_truss_dxf():
    """Curved truss bridge with arc members and varying sections"""
    dwg = new()
    msp = dwg.modelspace()
    
    # Main arc (parabolic)
    points = []
    for i in range(21):
        x = i * 2.0  # 0 to 40m
        y = -0.01 * (x - 20) ** 2 + 15  # Parabolic arch
        z = 0
        points.append((x, y, z))
    
    # Add parabolic arch as spline
    msp.add_lwpolyline([(p[0], p[1]) for p in points], dxfattribs={'layer': 'ARCH'})
    
    # Vertical members along arch
    for i in range(len(points) - 1):
        x1, y1, _ = points[i]
        x2, y2, _ = points[i + 1]
        
        # Main chord member (arc)
        msp.add_line((x1, y1), (x2, y2), dxfattribs={'layer': 'CHORDS'})
        
        # Vertical hangers to lower chord (50m span at height 8m)
        msp.add_line((x1, y1), (x1, 8), dxfattribs={'layer': 'HANGERS'})
        msp.add_line((x2, y2), (x2, 8), dxfattribs={'layer': 'HANGERS'})
        
        # Cross bracing with curves
        if i < len(points) - 1:
            angle = math.atan2(y2 - y1, x2 - x1)
            # Add curved X-bracing
            msp.add_line(
                (x1, y1),
                (x2, 8),
                dxfattribs={'layer': 'BRACING', 'color': 4}
            )
            msp.add_line(
                (x2, y2),
                (x1, 8),
                dxfattribs={'layer': 'BRACING', 'color': 4}
            )
    
    # Lower horizontal chord
    msp.add_line((0, 8), (40, 8), dxfattribs={'layer': 'CHORD_LOWER'})
    
    # Support pylons (tapered with curves)
    for x in [0, 40]:
        # Pylon base 2m x 2m
        rect_pts = [(x-1, -2), (x+1, -2), (x+1, 0), (x-1, 0)]
        msp.add_lwpolyline(rect_pts + [rect_pts[0]], dxfattribs={'layer': 'PYLONS'})
        
        # Pylon top tapered to 0.5m x 0.5m
        rect_pts_top = [(x-0.25, 12), (x+0.25, 12), (x+0.25, 15), (x-0.25, 15)]
        msp.add_lwpolyline(rect_pts_top + [rect_pts_top[0]], dxfattribs={'layer': 'PYLONS'})
        
        # Slanted edges (curved taper)
        msp.add_line((x-1, 0), (x-0.25, 12), dxfattribs={'layer': 'PYLONS'})
        msp.add_line((x+1, 0), (x+0.25, 12), dxfattribs={'layer': 'PYLONS'})
    
    # Save
    path = '/Users/sahil/Documents/aibuildx/test_dxf_1_curved_truss.dxf'
    dwg.saveas(path)
    print(f"✓ Created: {path}")
    return path

def create_spiral_staircase_dxf():
    """Spiral staircase with helical members and varying sections"""
    dwg = new()
    msp = dwg.modelspace()
    
    # Helical central spine (modeled as spiral)
    radius = 3.0
    steps = 20
    height_per_step = 0.5
    
    prev_pt = None
    for i in range(steps):
        angle = (i / steps) * 4 * math.pi  # 2 full rotations
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = i * height_per_step
        
        if prev_pt:
            msp.add_line(prev_pt, (x, y, z), dxfattribs={'layer': 'SPINE', 'color': 1})
        prev_pt = (x, y, z)
    
    # Treads (curved steps)
    for i in range(steps):
        angle = (i / steps) * 4 * math.pi
        z = i * height_per_step
        
        # Inner radius tread
        inner_pts = []
        for j in range(9):
            theta = angle + (j / 8) * (2 * math.pi / 20)
            x = (radius - 0.5) * math.cos(theta)
            y = (radius - 0.5) * math.sin(theta)
            inner_pts.append((x, y, z))
        
        msp.add_lwpolyline(inner_pts, dxfattribs={'layer': 'TREADS', 'color': 3})
        
        # Outer radius tread
        outer_pts = []
        for j in range(9):
            theta = angle + (j / 8) * (2 * math.pi / 20)
            x = (radius + 0.5) * math.cos(theta)
            y = (radius + 0.5) * math.sin(theta)
            outer_pts.append((x, y, z))
        
        msp.add_lwpolyline(outer_pts, dxfattribs={'layer': 'TREADS', 'color': 3})
        
        # Radial stringers (connection beams)
        for k in range(0, 8, 2):
            theta = angle + (k / 8) * (2 * math.pi / 20)
            x_inner = (radius - 0.5) * math.cos(theta)
            y_inner = (radius - 0.5) * math.sin(theta)
            x_outer = (radius + 0.5) * math.cos(theta)
            y_outer = (radius + 0.5) * math.sin(theta)
            
            msp.add_line(
                (x_inner, y_inner, z),
                (x_outer, y_outer, z),
                dxfattribs={'layer': 'STRINGERS', 'color': 5}
            )
    
    # Handrail (circular arc spiral)
    rail_radius = radius + 1.2
    prev_rail = None
    for i in range(steps):
        angle = (i / steps) * 4 * math.pi
        x = rail_radius * math.cos(angle)
        y = rail_radius * math.sin(angle)
        z = i * height_per_step
        
        if prev_rail:
            msp.add_line(prev_rail, (x, y, z), dxfattribs={'layer': 'HANDRAIL', 'color': 2})
        prev_rail = (x, y, z)
    
    # Central support column (tapered)
    for i in range(0, steps, 2):
        z = i * height_per_step
        z_next = (i + 2) * height_per_step
        
        # Draw tapered cylinder as circles
        radius_taper = 0.3 * (1 - i / steps)  # Taper to top
        
        # Square cross-section simplification
        size = radius_taper
        pts = [(-size, -size, z), (size, -size, z), (size, size, z), (-size, size, z)]
        
        if i > 0:
            prev_pts = [(-prev_size, -prev_size, z-2*height_per_step), 
                       (prev_size, -prev_size, z-2*height_per_step), 
                       (prev_size, prev_size, z-2*height_per_step), 
                       (-prev_size, prev_size, z-2*height_per_step)]
            
            for j in range(4):
                msp.add_line(prev_pts[j], pts[j], dxfattribs={'layer': 'COLUMN', 'color': 6})
        
        prev_size = size
    
    path = '/Users/sahil/Documents/aibuildx/test_dxf_2_spiral_staircase.dxf'
    dwg.saveas(path)
    print(f"✓ Created: {path}")
    return path

def create_double_curved_dome_dxf():
    """Double-curved dome with elliptical sections and complex ribs"""
    dwg = new()
    msp = dwg.modelspace()
    
    # Dome parameters
    major_axis = 30.0
    minor_axis = 25.0
    dome_height = 12.0
    ribs = 12
    rings = 6
    
    # Create meridian ribs (curved members from base to apex)
    for rib_num in range(ribs):
        angle = (rib_num / ribs) * 2 * math.pi
        
        points = []
        for ring in range(rings + 1):
            # Progress from base to apex
            progress = ring / rings
            
            # Elliptical cross-section
            x_base = (major_axis / 2) * math.cos(angle)
            y_base = (minor_axis / 2) * math.sin(angle)
            
            # Taper ellipse towards apex
            scale = 1 - progress
            x = x_base * scale
            y = y_base * scale
            z = dome_height * progress
            
            points.append((x, y, z))
        
        # Add rib as polyline
        msp.add_lwpolyline(points, dxfattribs={'layer': 'MERIDIAN_RIBS', 'color': 1})
    
    # Create latitudinal ribs (circular rings)
    for ring in range(1, rings + 1):
        progress = ring / rings
        scale = 1 - progress
        
        points = []
        for i in range(50):
            theta = (i / 50) * 2 * math.pi
            x = (major_axis / 2) * scale * math.cos(theta)
            y = (minor_axis / 2) * scale * math.sin(theta)
            z = dome_height * progress
            
            points.append((x, y, z))
        
        # Close ring
        points.append(points[0])
        
        msp.add_lwpolyline(points, dxfattribs={'layer': 'LATITUDINAL_RIBS', 'color': 2})
    
    # Add diagonal cross-bracing
    for rib_num in range(ribs):
        angle1 = (rib_num / ribs) * 2 * math.pi
        angle2 = ((rib_num + 1) % ribs / ribs) * 2 * math.pi
        
        for ring in range(1, rings):
            progress1 = ring / rings
            progress2 = (ring + 1) / rings
            
            scale1 = 1 - progress1
            scale2 = 1 - progress2
            
            # Start point on rib 1 at ring 1
            x1 = (major_axis / 2) * scale1 * math.cos(angle1)
            y1 = (minor_axis / 2) * scale1 * math.sin(angle1)
            z1 = dome_height * progress1
            
            # End point on adjacent rib at next ring
            x2 = (major_axis / 2) * scale2 * math.cos(angle2)
            y2 = (minor_axis / 2) * scale2 * math.sin(angle2)
            z2 = dome_height * progress2
            
            msp.add_line((x1, y1, z1), (x2, y2, z2), dxfattribs={'layer': 'BRACING', 'color': 3})
    
    # Support ring at base (elliptical)
    base_points = []
    for i in range(100):
        theta = (i / 100) * 2 * math.pi
        x = (major_axis / 2) * math.cos(theta)
        y = (minor_axis / 2) * math.sin(theta)
        z = 0
        base_points.append((x, y, z))
    
    base_points.append(base_points[0])
    msp.add_lwpolyline(base_points, dxfattribs={'layer': 'BASE_RING', 'color': 4})
    
    # Support columns at 4 points
    for i, angle in enumerate([0, math.pi/2, math.pi, 3*math.pi/2]):
        x_base = (major_axis / 2) * math.cos(angle)
        y_base = (minor_axis / 2) * math.sin(angle)
        
        # Tapered column from -5 to 0
        msp.add_line((x_base, y_base, -5), (x_base, y_base, 0), 
                    dxfattribs={'layer': 'SUPPORTS', 'color': 5})
        
        # Base pad
        pad_size = 1.5
        pad_pts = [
            (x_base - pad_size, y_base - pad_size, -5),
            (x_base + pad_size, y_base - pad_size, -5),
            (x_base + pad_size, y_base + pad_size, -5),
            (x_base - pad_size, y_base + pad_size, -5),
        ]
        msp.add_lwpolyline(pad_pts + [pad_pts[0]], dxfattribs={'layer': 'SUPPORTS', 'color': 5})
    
    path = '/Users/sahil/Documents/aibuildx/test_dxf_3_double_curved_dome.dxf'
    dwg.saveas(path)
    print(f"✓ Created: {path}")
    return path

def create_complex_junction_dxf():
    """Complex junction with multiple intersecting members, welds, and bolts"""
    dwg = new()
    msp = dwg.modelspace()
    
    # Central node at origin
    junction_pt = (0, 0, 0)
    
    # 8 radiating beam members (like a compass star)
    directions = [
        (1, 0, 0), (-1, 0, 0),  # X-axis
        (0, 1, 0), (0, -1, 0),  # Y-axis
        (1, 1, 0), (-1, -1, 0),  # XY diagonal
        (1, -1, 0), (-1, 1, 0),  # XY anti-diagonal
    ]
    
    # Normalize and scale
    members = []
    for i, (dx, dy, dz) in enumerate(directions):
        length = 10.0
        norm = math.sqrt(dx**2 + dy**2 + dz**2)
        if norm > 0:
            dx, dy, dz = dx/norm, dy/norm, dz/norm
        
        end_pt = (length * dx, length * dy, length * dz)
        members.append((junction_pt, end_pt))
        
        # Draw main member
        msp.add_line(junction_pt, end_pt, dxfattribs={'layer': 'MAIN_MEMBERS', 'color': 1})
        
        # Draw member cross-section (box)
        # For simplicity, show as rectangular profile
        perp_x = -dy
        perp_y = dx
        section_size = 0.2
        
        profile_start = [
            (section_size * perp_x, section_size * perp_y, 0),
            (-section_size * perp_x, section_size * perp_y, 0),
            (-section_size * perp_x, -section_size * perp_y, 0),
            (section_size * perp_x, -section_size * perp_y, 0),
        ]
        
        profile_end = [
            (end_pt[0] + section_size * perp_x, end_pt[1] + section_size * perp_y, end_pt[2]),
            (end_pt[0] - section_size * perp_x, end_pt[1] + section_size * perp_y, end_pt[2]),
            (end_pt[0] - section_size * perp_x, end_pt[1] - section_size * perp_y, end_pt[2]),
            (end_pt[0] + section_size * perp_x, end_pt[1] - section_size * perp_y, end_pt[2]),
        ]
    
    # Central gusset plate (multiple overlapping plates at junction)
    for angle in [0, math.pi/4, math.pi/2, 3*math.pi/4]:
        plate_w = 1.0
        plate_h = 1.5
        
        # Rotated rectangular plate around Z
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        plate_pts = [
            (plate_w/2 * cos_a - plate_h/2 * sin_a, plate_w/2 * sin_a + plate_h/2 * cos_a, 0.1),
            (-plate_w/2 * cos_a - plate_h/2 * sin_a, -plate_w/2 * sin_a + plate_h/2 * cos_a, 0.1),
            (-plate_w/2 * cos_a + plate_h/2 * sin_a, -plate_w/2 * sin_a - plate_h/2 * cos_a, 0.1),
            (plate_w/2 * cos_a + plate_h/2 * sin_a, plate_w/2 * sin_a - plate_h/2 * cos_a, 0.1),
        ]
        
        msp.add_lwpolyline(plate_pts + [plate_pts[0]], dxfattribs={'layer': 'GUSSET_PLATES', 'color': 2})
    
    # Bolts at junction (M24 bolts in circular pattern)
    bolt_circle_radius = 0.8
    num_bolts = 12
    bolt_size = 0.024  # 24mm
    
    for i in range(num_bolts):
        angle = (i / num_bolts) * 2 * math.pi
        bolt_x = bolt_circle_radius * math.cos(angle)
        bolt_y = bolt_circle_radius * math.sin(angle)
        
        # Bolt hole (circle)
        bolt_pts = []
        for j in range(20):
            theta = (j / 20) * 2 * math.pi
            x = bolt_x + (bolt_size / 2) * math.cos(theta)
            y = bolt_y + (bolt_size / 2) * math.sin(theta)
            bolt_pts.append((x, y, 0))
        
        bolt_pts.append(bolt_pts[0])
        msp.add_lwpolyline(bolt_pts, dxfattribs={'layer': 'BOLTS', 'color': 3})
    
    # Welds (continuous fillet welds)
    for i in range(num_bolts):
        angle = (i / num_bolts) * 2 * math.pi
        # Weld line slightly larger radius
        weld_rad = bolt_circle_radius + 0.3
        weld_x = weld_rad * math.cos(angle)
        weld_y = weld_rad * math.sin(angle)
        
        msp.add_point((weld_x, weld_y, 0), dxfattribs={'layer': 'WELDS', 'color': 4})
    
    # Vertical stiffeners (perpendicular to junction plane)
    for i in range(4):
        angle = (i / 4) * 2 * math.pi
        stiff_x = 1.5 * math.cos(angle)
        stiff_y = 1.5 * math.sin(angle)
        
        # Vertical stiffener plate
        msp.add_line((stiff_x, stiff_y, 0), (stiff_x, stiff_y, 2), 
                    dxfattribs={'layer': 'STIFFENERS', 'color': 5})
        msp.add_line((stiff_x + 0.2, stiff_y, 0), (stiff_x + 0.2, stiff_y, 2), 
                    dxfattribs={'layer': 'STIFFENERS', 'color': 5})
        msp.add_line((stiff_x, stiff_y + 0.2, 0), (stiff_x, stiff_y + 0.2, 2), 
                    dxfattribs={'layer': 'STIFFENERS', 'color': 5})
    
    path = '/Users/sahil/Documents/aibuildx/test_dxf_4_complex_junction.dxf'
    dwg.saveas(path)
    print(f"✓ Created: {path}")
    return path

def main():
    """Generate all 4 challenging DXF files"""
    print("\n" + "="*60)
    print("GENERATING 4 MOST CHALLENGING DXF TEST FILES")
    print("="*60 + "\n")
    
    paths = [
        create_curved_truss_dxf(),
        create_spiral_staircase_dxf(),
        create_double_curved_dome_dxf(),
        create_complex_junction_dxf(),
    ]
    
    print("\n" + "="*60)
    print("✅ All 4 DXF files created successfully!")
    print("="*60)
    print("\nFiles created:")
    for p in paths:
        file_size = os.path.getsize(p)
        print(f"  • {os.path.basename(p)} ({file_size:,} bytes)")
    
    return paths

if __name__ == '__main__':
    main()
