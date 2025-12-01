"""Section and material catalogs plus a PROFILE_MAPPER with fuzzy matching.
This is intentionally compact but includes common families and simple geometry.
"""
from typing import Dict, Any, Optional
import re

# SECTION_CATALOG: family -> list of typical sizes (string keys)
SECTION_CATALOG = {
    "AISC_W": [f"W{w}" for w in [6,8,10,12,14,16,18,21,24,27,30,33,36,40,44,48]],
    "AISC_S": [f"S{n}" for n in [3,4,5,6,8,10,12,14]],
    "AISC_C": [f"C{n}" for n in [6,8,10,12,14]],
    "ASS_HSS": [f"HSS{n}x{n}" for n in [50,65,80,100,125,150]],
    "AISC_PIPE": ["PIPE1/2","PIPE3/4","PIPE1","PIPE2"],
    "EURO_HE": [f"HEA{n}" for n in [100,120,140,160,180,200,220,240,260,300]],
    "EURO_IPE": [f"IPE{n}" for n in [80,100,120,140,160,180,200,220,240,300]],
    "IS_ISMB": [f"ISMB{n}" for n in [100,125,150,200,250,300]],
    "IS_ISMC": [f"ISMC{n}" for n in [75,100,125,150,200]]
}

# SECTION_GEOM: example entries (values are simplified geometry dicts)
SECTION_GEOM: Dict[str, Dict[str, Any]] = {}

def _add_section(name: str, area: float, Ix: float, Iy: float, Zx: float, Zy: float, r: float, wpm: float, thickness: Optional[float]=None, dims: Optional[Dict[str,float]]=None):
    SECTION_GEOM[name.upper()] = {
        "area": area,
        "Ix": Ix,
        "Iy": Iy,
        "Zx": Zx,
        "Zy": Zy,
        "r": r,
        "wpm": wpm,
        "thickness": thickness,
        "dims": dims or {}
    }

# Populate a few representative profiles (not exhaustive but representative)
_add_section("W14", 0.095, 0.0009, 0.0002, 0.00012, 0.00003, 45.0, 115.0, thickness=12.7, dims={"bf":380,"tf":25,"tw":12})
_add_section("W10", 0.08, 0.0006, 0.00018, 0.00011, 0.00003, 40.0, 95.0, thickness=12.0, dims={"bf":300,"tf":22,"tw":10})
_add_section("IPE300", 0.042, 0.00025, 0.00006, 0.00008, 0.00002, 30.0, 33.0, thickness=10.0, dims={"h":300,"b":150,"tf":9,"tw":6})
_add_section("HEA200", 0.06, 0.0005, 0.00012, 0.00009, 0.000025, 35.0, 47.0, thickness=11.0, dims={"h":200,"b":200})
_add_section("ISMB200", 0.045, 0.00034, 0.00008, 0.00007, 0.000018, 32.0, 35.0, thickness=10.5, dims={"h":200,"b":100})

# MATERIAL_CATALOG
MATERIAL_CATALOG = {
    "ASTM A36": {"fy": 250.0, "fu": 400.0, "unit": "MPa"},
    "ASTM A992": {"fy": 345.0, "fu": 450.0, "unit": "MPa"},
    "A572 G50": {"fy": 345.0, "fu": 450.0, "unit": "MPa"},
    "S235": {"fy": 235.0, "fu": 360.0, "unit": "MPa"},
    "S355": {"fy": 355.0, "fu": 510.0, "unit": "MPa"},
    "IS2062 E250": {"fy": 250.0, "fu": 410.0, "unit": "MPa"},
    "IS2062 E350": {"fy": 350.0, "fu": 510.0, "unit": "MPa"}
}

def normalize_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", name).upper()

def profile_mapper(query: str, layer: Optional[str]=None, annotations: Optional[str]=None) -> Optional[Dict[str,Any]]:
    """Fuzzy map a profile name to SECTION_GEOM entry.
    Heuristics:
    - direct uppercase key
    - startswith match
    - contains numeric size like W14 or IPE300
    - layer/annotation hints prefer families
    """
    if not query and not layer and not annotations:
        return None
    candidates = []
    qnorm = normalize_name(query or "")
    if qnorm in SECTION_GEOM:
        return SECTION_GEOM[qnorm]

    # Try simple startswith/contains against keys in SECTION_GEOM
    for k in SECTION_GEOM:
        if qnorm and (k.startswith(qnorm) or qnorm.startswith(k) or qnorm in k):
            candidates.append((k, 100))
        else:
            # numeric size extraction
            if qnorm and any(ch.isdigit() for ch in qnorm):
                if re.search(r"\d+", k) and re.search(r"\d+", qnorm):
                    if re.search(r"\d+", k).group(0) == re.search(r"\d+", qnorm).group(0):
                        candidates.append((k, 90))
    # layer-based bias
    if layer:
        l = layer.lower()
        if "w" in l or "wide" in l:
            candidates = [(k, s+10) for (k,s) in candidates]
        if "ipe" in l:
            candidates = [(k, s+15 if "IPE" in k else s) for (k,s) in candidates]

    if not candidates:
        # fallback: try to match known families by regex
        if re.match(r"W\d+", qnorm):
            for k in SECTION_GEOM:
                if k.startswith("W"):
                    candidates.append((k, 50))
        if re.match(r"IPE\d+", qnorm):
            for k in SECTION_GEOM:
                if k.startswith("IPE"):
                    candidates.append((k, 50))

    if not candidates:
        return None

    # select highest score, else first
    candidates.sort(key=lambda x: -x[1])
    best = candidates[0][0]
    return SECTION_GEOM.get(best)


def load_section_catalog(csv_path: Optional[str]=None):
    """Load extra entries from data/section_catalog.csv into SECTION_GEOM.
    This allows expanding the in-memory database without hardcoding values.
    """
    import csv, json, os
    # prefer a fuller catalog if available
    p = csv_path or os.path.join(os.getcwd(), 'data', 'section_catalog_full.csv')
    if not os.path.exists(p):
        p = os.path.join(os.getcwd(), 'data', 'section_catalog.csv')
    if not os.path.exists(p):
        return
    with open(p, 'r', encoding='utf-8') as fh:
        rdr = csv.DictReader(fh)
        for row in rdr:
            name = normalize_name(row.get('name',''))
            try:
                area = float(row.get('area_mm2') or row.get('area') or 0.0)
                Ix = float(row.get('Ix_mm4') or 0.0)
                Iy = float(row.get('Iy_mm4') or 0.0)
                Zx = float(row.get('Zx_mm3') or 0.0)
                Zy = float(row.get('Zy_mm3') or 0.0)
                r = float(row.get('r_mm') or 0.0)
                wpm = float(row.get('wpm_kg_per_m') or 0.0)
                thickness = float(row.get('thickness_mm') or 0.0)
                dims = {}
                try:
                    dims = json.loads(row.get('dims') or '{}')
                except Exception:
                    dims = {}
                SECTION_GEOM[name] = {"area": area, "Ix": Ix, "Iy": Iy, "Zx": Zx, "Zy": Zy, "r": r, "wpm": wpm, "thickness": thickness, "dims": dims}
            except Exception:
                continue


# Auto-load the CSV catalog if present
try:
    load_section_catalog()
except Exception:
    pass
