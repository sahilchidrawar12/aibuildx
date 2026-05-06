#!/usr/bin/env python3
"""Generate a 2D DXF plan for a 3-floor building with a gable roof outline."""

from pathlib import Path

try:
    import ezdxf
except ImportError:
    raise ImportError("ezdxf is required. Install with: pip install ezdxf")


def create_3floor_gable_plan(output_path: Path):
    doc = ezdxf.new('R2010')
    doc.layers.new('FLOOR', dxfattribs={'color': 3})
    doc.layers.new('ROOF', dxfattribs={'color': 1})
    doc.layers.new('COLUMNS', dxfattribs={'color': 2})
    doc.layers.new('ANNOTATION', dxfattribs={'color': 7})

    msp = doc.modelspace()

    width = 12000.0
    depth = 8000.0
    floor_spacing = 2000.0
    floor_count = 3

    # Draw floor outlines and interior structural axes
    for level in range(floor_count):
        y_offset = level * (depth + 800)
        base_y = y_offset
        floor_name = f'FLOOR_{level + 1}'

        # Outer boundary
        msp.add_lwpolyline([
            (0, base_y),
            (width, base_y),
            (width, base_y + depth),
            (0, base_y + depth),
            (0, base_y)
        ], dxfattribs={'layer': 'FLOOR'})

        # Main interior grid lines
        msp.add_line((width * 0.25, base_y), (width * 0.25, base_y + depth), dxfattribs={'layer': 'FLOOR'})
        msp.add_line((width * 0.75, base_y), (width * 0.75, base_y + depth), dxfattribs={'layer': 'FLOOR'})
        msp.add_line((0, base_y + depth * 0.5), (width, base_y + depth * 0.5), dxfattribs={'layer': 'FLOOR'})

        # Corner column circles
        columns = [
            (0, base_y),
            (width, base_y),
            (width, base_y + depth),
            (0, base_y + depth)
        ]
        for cx, cy in columns:
            msp.add_circle((cx, cy), radius=150, dxfattribs={'layer': 'COLUMNS'})

        # Floor annotation
        text = msp.add_text(floor_name, dxfattribs={'layer': 'ANNOTATION', 'height': 250})
        text.dxf.insert = (width + 400, base_y + depth * 0.5, 0.0)

    # Gable roof outline above the top floor
    roof_base = floor_count * (depth + 800)
    overhang = 800
    ridge_y = roof_base + 1200
    msp.add_line((-overhang, roof_base), (width + overhang, roof_base), dxfattribs={'layer': 'ROOF'})
    msp.add_line((-overhang, roof_base), (width / 2, ridge_y), dxfattribs={'layer': 'ROOF'})
    msp.add_line((width + overhang, roof_base), (width / 2, ridge_y), dxfattribs={'layer': 'ROOF'})

    roof_text = msp.add_text('GABLE ROOF PLAN', dxfattribs={'layer': 'ANNOTATION', 'height': 250})
    roof_text.dxf.insert = (width * 0.5, ridge_y + 400, 0.0)

    doc.saveas(str(output_path))


def main():
    output = Path('outputs/3_floor_gable_plan.dxf')
    output.parent.mkdir(parents=True, exist_ok=True)
    create_3floor_gable_plan(output)
    print(f'✅ Created DXF: {output.resolve()}')


if __name__ == '__main__':
    main()
