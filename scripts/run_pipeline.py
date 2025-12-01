"""CLI to run the pipeline on a DXF or sample JSON and write outputs."""
import argparse
import json
import os
import sys

from src.pipeline.pipeline_v2 import Pipeline

try:
    import ezdxf
except Exception:
    ezdxf = None

parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', required=True, help='Input DXF file or JSON file describing line entities')
parser.add_argument('--out_dir', '-o', default='outputs')
args = parser.parse_args()

if not os.path.exists(args.out_dir):
    os.makedirs(args.out_dir)

# load input
entities = None
if args.input.lower().endswith('.dxf'):
    if ezdxf is None:
        print('ezdxf not installed. Install dependencies first.'); sys.exit(1)
    doc = ezdxf.readfile(args.input)
    msp = doc.modelspace()
    entities = []
    for e in msp:
        if e.dxftype() == 'LINE':
            # ezdxf may give 2D lines; we include z=0 if not present
            start = (float(e.dxf.start.x), float(e.dxf.start.y), float(getattr(e.dxf.start, 'z', 0.0)))
            end = (float(e.dxf.end.x), float(e.dxf.end.y), float(getattr(e.dxf.end, 'z', 0.0)))
            entities.append({'start': start, 'end': end, 'layer': e.dxf.layer})
else:
    # assume JSON
    with open(args.input, 'r') as f:
        entities = json.load(f)

p = Pipeline()
outputs = p.run_from_dxf_entities(entities, out_dir=args.out_dir)
# write agent outputs
for k,v in outputs.items():
    path = os.path.join(args.out_dir, f'{k}.json')
    with open(path, 'w') as f:
        json.dump(v, f, indent=2, default=str)
print('Pipeline completed. Outputs written to', args.out_dir)
