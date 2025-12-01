"""Scheduler refinement: adjust an existing schedule using simple heuristics."""
from typing import Dict, Any, List
from datetime import datetime, timedelta


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    schedule: List[Dict[str, Any]] = payload.get('schedule', [])
    adjust_percent = float(payload.get('adjust_percent', 0.0))
    refined = []
    for item in schedule:
        eta = item.get('eta')
        try:
            dt = datetime.fromisoformat(eta)
        except Exception:
            dt = datetime.now()
        # shorten or lengthen by adjust_percent of the interval (if interval provided)
        interval_mins = int(item.get('interval_mins', payload.get('default_interval_mins', 30)))
        delta = int(interval_mins * (adjust_percent / 100.0))
        new_dt = dt + timedelta(minutes=delta)
        item_copy = dict(item)
        item_copy['eta_refined'] = new_dt.isoformat()
        refined.append(item_copy)
    return {'status': 'ok', 'refined_schedule': refined}


class SchedulerRefinementAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
