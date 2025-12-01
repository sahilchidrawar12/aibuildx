"""DSTV Exporter agent: simple DSTV (.NC1-like) exporter stub."""
from typing import Dict, Any, List
import os


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Accept members or explicit plates
    plates: List[Dict[str, Any]] = payload.get('plates', [])
    if not plates and payload.get('members'):
        plates = [{'id': m.get('id'), 'section': m.get('selection', {}).get('section_name'), 'length_m': m.get('length')} for m in payload.get('members')]
    out_dir = payload.get('out_dir', 'outputs/dstv_parts')
    os.makedirs(out_dir, exist_ok=True)
    exported = []
    for pl in plates:
        pid = pl.get('id', 'plate')
        fname = f"{pid}.nc1"
        path = os.path.join(out_dir, fname)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('# DSTV-like export stub\n')
                f.write(f"PLATE_ID,{pid}\n")
            exported.append(path)
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    return {'status': 'ok', 'exported_files': exported}


class DSTVExporterAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
