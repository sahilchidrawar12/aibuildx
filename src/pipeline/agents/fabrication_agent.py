"""Fabrication agent: prepares fabrication notes and operations.

Scaffold returns a list of fabrication steps based on member properties.
"""
from typing import Dict, Any, List
from src.pipeline import pipeline_v2 as legacy


def process(input_data: Dict[str, Any]) -> Dict[str, Any]:
    # Accept single member or full model
    member = input_data.get('member') or (input_data.get('data') or {}).get('member')
    members = input_data.get('members') or (input_data.get('data') or {}).get('members')
    if members is not None:
        # If connections present, call legacy fabrication_detailing on the model
        try:
            # Expecting a model-like dict with 'members'
            model = {'members': members}
            detailed = legacy.fabrication_detailing(model)
            return {'status': 'ok', 'fabrication': detailed}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    steps: List[str] = []
    if member is None:
        return {'status': 'error', 'message': 'no member provided'}
    if member.get('length', 0) > 6000:
        steps.append('cut_to_length_at_fabricator')
    else:
        steps.append('cut_to_length_on_site')
    if member.get('requires_weld', False):
        steps.append('weld_according_to_spec')
    steps.append('mark_and_label')
    return {'status': 'ok', 'fabrication_steps': steps}


class FabricationAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
