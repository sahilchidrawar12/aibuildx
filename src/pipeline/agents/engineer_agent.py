"""Engineer agent: performs member-level checks and summaries.

API:
    process(input_data: dict) -> dict
"""
from typing import Dict, Any
from src.pipeline import pipeline_v2 as legacy


def process(input_data: Dict[str, Any]) -> Dict[str, Any]:
    # Accept raw miner output, a dict with 'members', or the full model
    members = []
    if input_data.get('members') is not None:
        members = input_data.get('members')
    elif isinstance(input_data.get('data'), dict) and input_data['data'].get('members'):
        members = input_data['data']['members']
    elif input_data.get('model') and input_data['model'].get('members'):
        members = input_data['model']['members']

    # If members are raw (no local axes, orientation), run legacy standardize
    needs_standardize = any('orientation' not in m or 'local_axes' not in m for m in members)
    if needs_standardize:
        try:
            std = legacy.engineer_standardize({'members': members})
            members = std.get('members', members)
        except Exception:
            pass

    summary = {
        'total_members': len(members),
        'steel_members': sum(1 for m in members if str(m.get('material', '')).lower().startswith('a')),
    }
    return {'status': 'ok', 'summary': summary, 'members': members}


class EngineerAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
