"""Safety report generator: creates a textual summary from safety checks."""
from typing import Dict, Any, List


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = payload.get('checks', [])
    issues = [c for c in checks if not c.get('pass', True)]
    summary = f"Total checks: {len(checks)}. Issues: {len(issues)}."
    return {'status': 'ok', 'summary': summary, 'issues': issues}


class SafetyReportAgent:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return process(payload)
