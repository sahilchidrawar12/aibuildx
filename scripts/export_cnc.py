"""Run the pipeline and export CNC CSV to outputs/cnc.csv

Usage: python scripts/export_cnc.py --input examples/sample_input.json
"""
import json, os, sys
from src.pipeline.pipeline_v2 import Pipeline

if __name__=='__main__':
    inp = sys.argv[1] if len(sys.argv)>1 else 'examples/sample_input.json'
    with open(inp,'r') as f:
        entities = json.load(f)
    p = Pipeline()
    out = p.run_from_dxf_entities(entities, out_dir='outputs')
    print('CNC CSV written to', out.get('cnc',{}).get('cnc_csv'))
