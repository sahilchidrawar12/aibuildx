import ezdxf
from pathlib import Path
from src.pipeline.dxf_parser import parse_dxf_file
from src.pipeline.node_resolution import auto_generate_joints

path = Path('tekla_ai_test.dxf')
if path.exists():
    path.unlink()

doc = ezdxf.new('R2010')
msp = doc.modelspace()
doc.layers.new(name='STR_GRIDS', dxfattribs={'color': 1, 'linetype': 'DASHED'})
doc.layers.new(name='STR_COLUMNS', dxfattribs={'color': 3})
doc.layers.new(name='STR_BEAMS', dxfattribs={'color': 4})
doc.layers.new(name='STR_TEXT', dxfattribs={'color': 7})

msp.add_line((0, 0), (0, 10000), dxfattribs={'layer': 'STR_GRIDS'})
msp.add_line((6000, 0), (6000, 10000), dxfattribs={'layer': 'STR_GRIDS'})
msp.add_line((0, 0), (6000, 0), dxfattribs={'layer': 'STR_GRIDS'})
msp.add_line((0, 10000), (6000, 10000), dxfattribs={'layer': 'STR_GRIDS'})

col_positions = [(0, 0), (6000, 0), (0, 10000), (6000, 10000)]
for pos in col_positions:
    msp.add_circle(pos, radius=100, dxfattribs={'layer': 'STR_COLUMNS'})
    text_ent = msp.add_text('ISMB400', dxfattribs={'layer': 'STR_TEXT', 'height': 200})
    try:
        text_ent.dxf.insert = (pos[0] + 150, pos[1] + 150, 0)
    except Exception:
        pass

msp.add_line((0, 0), (6000, 0), dxfattribs={'layer': 'STR_BEAMS'})
text_ent = msp.add_text('ISMB350', dxfattribs={'layer': 'STR_TEXT', 'height': 200})
try:
    text_ent.dxf.insert = (3000, 200, 0)
except Exception:
    pass

msp.add_line((0, 10000), (6000, 10000), dxfattribs={'layer': 'STR_BEAMS'})
text_ent = msp.add_text('ISMB350', dxfattribs={'layer': 'STR_TEXT', 'height': 200})
try:
    text_ent.dxf.insert = (3000, 10200, 0)
except Exception:
    pass

doc.saveas(path)
print('DXF created at', path.resolve())

parsed = parse_dxf_file(str(path))
print('\nParsed members:', len(parsed['members']))
for m in parsed['members']:
    print('-', m['id'][:8], 'layer=', m['layer'], 'start=', m['start'], 'end=', m['end'], 'annotation=', m.get('annotation'))
print('\nCircles:', len(parsed['circles']))
for c in parsed['circles']:
    print('-', c)

joints = auto_generate_joints(parsed['members'], tolerance=5.0)
print('\nAuto-generated joints:', len(joints))
for j in joints:
    print('-', j['id'], 'pos=', j['position'], 'members=', j['members'], 'type=', j['type'])
