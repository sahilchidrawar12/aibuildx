"""Export packager: bundle exported files into a zip (simulation)."""
from typing import Dict, Any, List
import os
import zipfile


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    files: List[str] = payload.get('files', [])
    out_dir = payload.get('out_dir', 'outputs/packages')
    os.makedirs(out_dir, exist_ok=True)
    pkg_name = payload.get('package_name', 'package.zip')
    pkg_path = os.path.join(out_dir, pkg_name)
    try:
        with zipfile.ZipFile(pkg_path, 'w') as z:
            for f in files:
                if os.path.exists(f):
                    z.write(f, arcname=os.path.basename(f))
        return {'status': 'ok', 'package': pkg_path}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


class ExportPackagerAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
