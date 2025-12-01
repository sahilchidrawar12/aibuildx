"""Validator agent: validates input JSON, required fields, and simple rules.

Returns a list of warnings/errors if any problems found.
"""
from typing import Dict, Any, List


def process(input_data: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    model = input_data.get('model') or input_data.get('data') or input_data
    members = model.get('members', []) if isinstance(model, dict) else []
    if not members:
        errors.append({'err': 'no_members', 'fix': 'provide members list'})

    # Basic checks per member
    for m in members:
        if m.get('length', 0) <= 0:
            errors.append({'id': m.get('id'), 'err': 'nonpositive_length'})
        sel = m.get('selection') or {}
        if not sel.get('section_name'):
            warnings.append({'id': m.get('id'), 'warn': 'no_section_selected'})
        # simple shear check
        shear_kN = m.get('loads', {}).get('shear_kN', 0.0)
        if shear_kN > 500:
            warnings.append({'id': m.get('id'), 'warn': 'high_shear', 'shear_kN': shear_kN})
        # bending capacity check (scaffold): if member provides a bending capacity
        moment_Nm = m.get('loads', {}).get('moment_Nm') or m.get('loads', {}).get('moment_kNm') and m.get('loads', {}).get('moment_kNm') * 1000
        bending_capacity = sel.get('bending_capacity_Nm') or sel.get('capacity_Nm')
        if moment_Nm and bending_capacity:
            try:
                if float(moment_Nm) > float(bending_capacity):
                    errors.append({'id': m.get('id'), 'err': 'bending_capacity_exceeded', 'moment_Nm': moment_Nm, 'bending_capacity_Nm': bending_capacity, 'fix': 'upsample_section'})
            except Exception:
                pass

    return {'status': 'ok' if not errors else 'error', 'errors': errors, 'warnings': warnings}


class ValidatorAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
