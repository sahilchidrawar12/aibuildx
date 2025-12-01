"""Simple anomaly detector stub using z-score on a numeric series."""
from typing import List, Dict, Any
import statistics


def detect(values: List[float], threshold: float = 3.0) -> Dict[str, Any]:
    if not values:
        return {'status': 'ok', 'anomalies': []}
    mean = statistics.mean(values)
    stdev = statistics.pstdev(values) if len(values) > 1 else 0
    anomalies = []
    for i, v in enumerate(values):
        if stdev == 0:
            z = 0
        else:
            z = abs((v - mean) / stdev)
        if z >= threshold:
            anomalies.append({'index': i, 'value': v, 'z': z})
    return {'status': 'ok', 'anomalies': anomalies, 'mean': mean, 'stdev': stdev}


__all__ = ['detect']
