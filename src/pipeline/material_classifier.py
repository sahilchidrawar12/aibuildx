from typing import Dict, Any, Optional
from .profile_db import MATERIAL_CATALOG
from .logging_setup import get_logger

logger = get_logger("material_classifier")

def classify_material(entity: Dict[str,Any]) -> Dict[str,Any]:
    # if material already provided as dict, return it
    existing = entity.get('material')
    if isinstance(existing, dict) and existing.get('name'):
        return existing

    # look for explicit material tags
    mat = entity.get("material") or entity.get("mat") or ""
    if mat and isinstance(mat, str):
        mat_norm = mat.strip()
        if mat_norm in MATERIAL_CATALOG:
            logger.debug("Material assigned: %s", mat_norm)
            return {"name": mat_norm, **MATERIAL_CATALOG[mat_norm]}
    # try annotations
    ann = entity.get("annotation") or ""
    for key in MATERIAL_CATALOG:
        if key.lower() in ann.lower():
            logger.debug("Material inferred from annotation: %s", key)
            return {"name": key, **MATERIAL_CATALOG[key]}
    # default
    default = "S355" if "column" in (entity.get("role") or "").lower() else "S235"
    logger.info("Defaulting material to %s for entity %s", default, entity.get("id"))
    return {"name": default, **MATERIAL_CATALOG[default]}
