"""Generate load combinations (simple LRFD/ASD templates)."""
from typing import Dict, Any, List

def generate_lrfd(loads: Dict[str, float]) -> List[Dict[str, Any]]:
    # loads: {'dead': D, 'live': L, 'wind': W, 'seismic': E}
    D = loads.get('dead', 0.0)
    L = loads.get('live', 0.0)
    W = loads.get('wind', 0.0)
    E = loads.get('seismic', 0.0)
    combos = [
        {"name":"1.4D","D":1.4*D},
        {"name":"1.2D+1.6L+0.5W","D":1.2*D, "L":1.6*L, "W":0.5*W},
        {"name":"1.2D+1.0E+0.5L","D":1.2*D, "E":1.0*E, "L":0.5*L},
        {"name":"0.9D+1.0E","D":0.9*D, "E":1.0*E}
    ]
    return combos

def generate_asd(loads: Dict[str,float]) -> List[Dict[str,float]]:
    D = loads.get('dead', 0.0)
    L = loads.get('live', 0.0)
    return [{"name":"1.0D+1.0L","D":D,"L":L}, {"name":"1.4D","D":1.4*D}]
