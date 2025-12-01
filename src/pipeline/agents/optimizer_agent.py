"""Optimizer agent: simple heuristic-based section/material optimizer scaffold.

Returns best-of-candidates by a simple cost-per-capacity metric.
"""
from typing import Dict, Any, List, Optional, Tuple
from src.pipeline import pipeline_v2 as legacy


def process(input_data: Dict[str, Any]) -> Dict[str, Any]:
    # If provided a full model, run legacy pipeline stages to get optimizer input
    members = input_data.get('members') or (input_data.get('data') or {}).get('members')
    if members is not None:
        # ensure loads and stability exist
        try:
            eng = legacy.engineer_standardize({'members': members})
            loads = legacy.load_path_resolver(eng)
            stab = legacy.stability_agent(loads)
            opt = legacy.optimizer_agent(stab)
            return {'status': 'ok', 'result': opt}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # Fallback: simple candidate selection
    candidates: List[Dict[str, Any]] = input_data.get('candidates', [])
    if not candidates:
        return {'status': 'error', 'message': 'no candidates'}
    best = None
    best_score = float('inf')
    for c in candidates:
        cost = c.get('cost', 1.0)
        capacity = c.get('capacity', 1.0)
        score = cost / max(1e-6, capacity)
        if score < best_score:
            best_score = score
            best = c
    return {'status': 'ok', 'best': best, 'score': best_score}


class OptimizerAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
