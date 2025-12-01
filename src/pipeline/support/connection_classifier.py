"""Stub ML classifier for connection types — returns label based on simple rules."""
from typing import Dict, Any


def predict(features: Dict[str, Any]) -> Dict[str, Any]:
    # very small heuristic: if thickness > 20 and tension > 50 -> 'bolted_heavy'
    t = float(features.get('thickness', 0.0))
    tension = float(features.get('tension', 0.0))
    if t > 20 and tension > 50:
        label = 'bolted_heavy'
    elif tension > 50:
        label = 'bolted'
    else:
        label = 'welded'
    return {'label': label, 'confidence': 0.7}


__all__ = ['predict']
