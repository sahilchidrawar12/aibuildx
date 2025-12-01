"""Report exporter: write simple JSON/text reports to disk and return path(s)."""
from typing import Dict, Any, List
import json
import os


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    report = payload.get('report', {})
    out_dir = payload.get('out_dir', 'outputs/reports')
    os.makedirs(out_dir, exist_ok=True)
    fname = payload.get('filename', 'report.json')
    path = os.path.join(out_dir, fname)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            if isinstance(report, (dict, list)):
                json.dump(report, f, indent=2)
            else:
                f.write(str(report))
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    return {'status': 'ok', 'path': path}


class ReportExporterAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
