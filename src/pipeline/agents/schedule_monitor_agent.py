"""Schedule monitor: checks task progress and flags overdue tasks."""
from typing import Dict, Any, List
from datetime import datetime


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    schedule: List[Dict[str, Any]] = payload.get('schedule', [])
    now = datetime.fromisoformat(payload.get('now')) if payload.get('now') else datetime.now()
    overdue = []
    for item in schedule:
        eta = item.get('eta')
        try:
            eta_dt = datetime.fromisoformat(eta)
            if eta_dt < now:
                overdue.append(item)
        except Exception:
            continue
    return {'status': 'ok', 'overdue_count': len(overdue), 'overdue': overdue}


class ScheduleMonitorAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
