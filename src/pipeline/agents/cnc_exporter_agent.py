"""CNC Exporter agent: lightweight wrapper around existing exporters.

This agent expects `parts` list in payload and returns CSV export paths (simulated).
"""
from typing import Dict, Any, List
import os


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Accept full model (members) or explicit parts list
    parts: List[Dict[str, Any]] = payload.get('parts', [])
    if not parts and payload.get('members'):
        # construct minimal parts from members
        parts = [{'id': m.get('id'), 'qty': 1, 'section': m.get('selection', {}).get('section_name'), 'length_m': m.get('length')} for m in payload.get('members')]
    out_dir = payload.get('out_dir', 'outputs/cnc_parts')
    os.makedirs(out_dir, exist_ok=True)
    exported = []
    for p in parts:
        pid = p.get('id', 'part')
        fname = f"{pid}_part.csv"
        path = os.path.join(out_dir, fname)
        # lightweight simulation: write a single-line CSV
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('part_id,qty,section,length_m\n')
                f.write(f"{pid},{p.get('qty',1)},{p.get('section','')},{p.get('length_m', p.get('length_m', ''))}\n")
            exported.append(path)
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    return {'status': 'ok', 'exported_files': exported}


class CNCExporterAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
