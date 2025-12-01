"""Risk agent: simple risk scoring for members.

Returns a risk score (0-1) based on simple heuristics.
"""
from typing import Dict, Any


def process(input_data: Dict[str, Any]) -> Dict[str, Any]:
    # Accept either a compact payload or a full model dict with members
    hazard = float(input_data.get('hazard', 0.0))
    exposure = float(input_data.get('exposure', 1.0))
    complexity = float(input_data.get('complexity', 1.0))
    base_score = min(1.0, (hazard * 0.5 + exposure * 0.3 + complexity * 0.2))

    members = input_data.get('members') or (input_data.get('data') or {}).get('members') or []
    member_scores = []
    for m in members:
        score = base_score
        # increase score for high slenderness or known issues
        sl = m.get('stability', {}).get('slenderness')
        if sl is not None and sl > 200:
            score = min(1.0, score + 0.4)
        # collisions increase risk
        clashes = (input_data.get('clash_list') or [])
        if any(c.get('a') == m.get('id') or c.get('b') == m.get('id') for c in clashes):
            score = min(1.0, score + 0.3)
        member_scores.append({'id': m.get('id'), 'risk_score': round(score, 3)})

    return {'status': 'ok', 'risk_score_global': round(base_score, 3), 'members': member_scores}


class RiskAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
