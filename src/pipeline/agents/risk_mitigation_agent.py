"""Risk mitigation agent: suggest simple mitigation actions based on a risk score."""
from typing import Dict, Any, List


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    risk_score = float(payload.get('risk_score', 0.0))
    measures: List[str] = []
    if risk_score >= 0.8:
        measures = ['Immediate stop', 'Full redesign', 'Senior review']
    elif risk_score >= 0.5:
        measures = ['Strengthen connections', 'Add redundancy', 'Detailed inspection']
    elif risk_score >= 0.2:
        measures = ['Monitor during fabrication', 'Add non-critical reinforcements']
    else:
        measures = ['Normal controls', 'Routine inspection']
    return {'status': 'ok', 'risk_score': risk_score, 'measures': measures}


class RiskMitigationAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
