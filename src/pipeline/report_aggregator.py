from typing import Dict, Any, List
from .logging_setup import get_logger

logger = get_logger("report_aggregator")

def aggregate_reports(agent_reports: List[Dict[str,Any]]) -> Dict[str,Any]:
    final = {"agents":{}, "summary":{}}
    for r in agent_reports:
        name = r.get('agent') or r.get('name') or 'unknown'
        final['agents'][name] = r
    # create a short summary
    final['summary']['agent_count'] = len(agent_reports)
    final['summary']['ok'] = all(r.get('ok', True) for r in agent_reports)
    logger.info("Aggregated %d agent reports; overall OK=%s", len(agent_reports), final['summary']['ok'])
    return final
