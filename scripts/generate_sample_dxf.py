#!/usr/bin/env python3
"""
Generate a small, valid ACAD2018 DXF with simple structural entities:
- Two beams (LINES)
- One column (LINE)
- One base plate (LWPOLYLINE closed)
- Four bolt circles (CIRCLE)
- Layers: BEAMS, COLUMNS, PLATES, BOLTS

Output: uploads/generated_test.dxf
"""
import os
from pathlib import Path

def main():
    import ezdxf

    # Create a new DXF R2018 document
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()

    # Define layers
    for lname, color in [("BEAMS", 1), ("COLUMNS", 3), ("PLATES", 2), ("BOLTS", 4)]:
        if lname not in doc.layers:
            doc.layers.add(lname, color=color)

    # Add beams (simple lines)
    msp.add_line((0, 0), (6000, 0), dxfattribs={"layer": "BEAMS"})  # 6m beam
    msp.add_line((0, 3000), (6000, 3000), dxfattribs={"layer": "BEAMS"})  # 6m beam at 3m elevation (plan view offset)

    # Add a column (vertical line in plan as small stub)
    msp.add_line((3000, -500), (3000, 500), dxfattribs={"layer": "COLUMNS"})

    # Base plate (square 300x300 at column base)
    plate_pts = [(2850, -150), (3150, -150), (3150, 150), (2850, 150)]
    pl = msp.add_lwpolyline(plate_pts, dxfattribs={"layer": "PLATES"})
    pl.closed = True

    # Bolt pattern: 4 bolts on 200x200 pattern
    bolt_centers = [(2900, -100), (3100, -100), (3100, 100), (2900, 100)]
    for cx, cy in bolt_centers:
        msp.add_circle((cx, cy), radius=12.5, dxfattribs={"layer": "BOLTS"})

    # Ensure output folder
    out_path = Path("uploads") / "generated_test.dxf"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc.saveas(str(out_path))
    print(f"DXF generated: {out_path}")

if __name__ == "__main__":
    main()
"""Generate a sample complex framed DXF using ezdxf for demo/testing."""
import ezdxf
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--out', '-o', default='examples/sample_frame.dxf')
args = parser.parse_args()

def make_frame(doc):
    msp = doc.modelspace()
    # create a grid of beams and columns with varying heights and a diagonal brace
    spacing = [0, 5, 10]
    for i,x in enumerate(spacing):
        for j,y in enumerate(spacing):
            # vertical column
            z0 = 0
            z1 = 3 + i # vary heights
            msp.add_line((x,y,z0), (x,y,z1), dxfattribs={'layer':'COLUMNS'})
    # beams between columns
    for i in range(len(spacing)-1):
        x1 = spacing[i]
        x2 = spacing[i+1]
        msp.add_line((x1,0,3), (x2,0,3), dxfattribs={'layer':'BEAMS'})
        msp.add_line((x1,5,3), (x2,5,3), dxfattribs={'layer':'BEAMS'})
    # diagonal brace
    msp.add_line((0,0,3), (10,10,0), dxfattribs={'layer':'BRACES'})

if __name__ == '__main__':
    doc = ezdxf.new(dxfversion='R2010')
    make_frame(doc)
    out = args.out
    doc.saveas(out)
    print('Wrote sample DXF to', out)
