"""Scheduler agent: assigns simple sequence order and estimated timestamps."""
from typing import Dict, Any, List
from datetime import datetime, timedelta


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    tasks: List[Dict[str, Any]] = payload.get('tasks', [])
    start = payload.get('start')
    if start:
        try:
            start_dt = datetime.fromisoformat(start)
        except Exception:
            start_dt = datetime.now()
    else:
        start_dt = datetime.now()
    interval_mins = int(payload.get('interval_mins', 30))
    schedule = []
    cur = start_dt
    for i, t in enumerate(tasks):
        schedule.append({'task': t, 'index': i, 'eta': cur.isoformat()})
        cur = cur + timedelta(minutes=interval_mins)
    return {'status': 'ok', 'schedule': schedule}


class SchedulerAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
