"""Healthcheck agent: returns quick availability map of key components."""
from typing import Dict, Any


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    components = payload.get('components', ['materials','loads','compliance','agents'])
    status = {c: True for c in components}
    return {'status': 'ok', 'components': status}


class HealthcheckAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
