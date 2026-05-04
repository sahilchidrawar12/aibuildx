#!/usr/bin/env python3
"""Extract Tekla model data from birds nest DXF for verification."""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/Users/sahil/Documents/aibuildx')

from ..pipeline.agents.main_pipeline_agent import process

def extract_tekla_data(dxf_path: str):
    """Extract Tekla model data from DXF."""
    
    payload = {
        'data': {
            'dxf_entities': dxf_path
        }
    }
    
    result = process(payload)
    
    # Save full result to JSON
    output_file = '/Users/sahil/Documents/aibuildx/outputs/tekla_birds_nest_data.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Data extracted and saved to {output_file}")
    
    return result

if __name__ == '__main__':
    dxf_path = '/Users/sahil/Documents/aibuildx/test_birds_nest_stadium.dxf'
    
    if Path(dxf_path).exists():
        extract_tekla_data(dxf_path)
    else:
        print(f"DXF file not found: {dxf_path}")
        sys.exit(1)