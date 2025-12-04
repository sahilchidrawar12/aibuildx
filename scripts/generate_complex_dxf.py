#!/usr/bin/env python3
"""
Generate a complex ACAD2018 DXF with diverse structural geometry and intentional edge cases:
- Multiple beams and columns (LINES)
- Irregular plates (LWPOLYLINE closed) including one with a notch
- Overlapping members to trigger clashes
- Dense bolt patterns with borderline spacing/edge distances
- Hatches, blocks, and text to simulate real-world content
- Mixed layers, units implied by coordinates

Output: uploads/generated_complex.dxf
"""
from pathlib import Path

def main():
    import ezdxf

    doc = ezdxf.new("R2018")
    msp = doc.modelspace()

    # Layers
    for lname, color in [
        ("BEAMS", 1), ("COLUMNS", 3), ("PLATES", 2), ("BOLTS", 4),
        ("FOUNDATION", 6), ("ANNOT", 7), ("BLOCKS", 140)
    ]:
        if lname not in doc.layers:
            doc.layers.add(lname, color=color)

    # Beams: grid of horizontal lines, some overlapping to simulate clashes
    for y in [0, 3000, 6000, 9000]:
        msp.add_line((0, y), (12000, y), dxfattribs={"layer": "BEAMS"})
    # Overlap a beam segment to force a potential clash region
    msp.add_line((2000, 3000), (4000, 3000), dxfattribs={"layer": "BEAMS"})

    # Columns: vertical stubs at grid points
    for x in [0, 3000, 6000, 9000, 12000]:
        msp.add_line((x, -300), (x, 300), dxfattribs={"layer": "COLUMNS"})

    # Plate 1: rectangular base plate under column at (6000, 0)
    plate1 = [(5850, -150), (6150, -150), (6150, 150), (5850, 150)]
    pl1 = msp.add_lwpolyline(plate1, dxfattribs={"layer": "PLATES"}); pl1.closed = True

    # Plate 2: irregular with notch near (3000, 3000)
    plate2 = [(2900, 2850), (3100, 2850), (3100, 3050), (3000, 3050), (3000, 2950), (2900, 2950)]
    pl2 = msp.add_lwpolyline(plate2, dxfattribs={"layer": "PLATES"}); pl2.closed = True

    # Bolt patterns: dense grid near minimum spacing and edge distances
    # Pattern around plate1
    bolts1 = [(5900, -100), (6100, -100), (6100, 100), (5900, 100)]
    for cx, cy in bolts1:
        msp.add_circle((cx, cy), radius=11.0, dxfattribs={"layer": "BOLTS"})

    # Pattern around plate2 (tighter)
    bolts2 = [(2925, 2875), (3075, 2875), (3075, 3025), (2925, 3025)]
    for cx, cy in bolts2:
        msp.add_circle((cx, cy), radius=10.0, dxfattribs={"layer": "BOLTS"})

    # Foundation hatch area
    hatch = msp.add_hatch(dxfattribs={"layer": "FOUNDATION"})
    path = hatch.paths.add_polyline_path([(5700, -300), (6300, -300), (6300, 300), (5700, 300)], is_closed=True)

    # Block with proxy-like content simulation: a simple block reference
    blk = doc.blocks.new(name="BASE_ASSEMBLY")
    blk.add_line((0, 0), (200, 0))
    blk.add_circle((100, 50), 25)
    msp.add_blockref("BASE_ASSEMBLY", (6000, 0), dxfattribs={"layer": "BLOCKS"})

    # Annotation
    msp.add_text("GRID A-B", dxfattribs={"layer": "ANNOT", "height": 200}).set_placement((100, 9800))

    out_path = Path("uploads") / "generated_complex.dxf"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(str(out_path))
    print(f"DXF generated: {out_path}")

if __name__ == "__main__":
    main()
