from typing import Dict, Any, Optional
from ..profiles.profile_db import MATERIAL_CATALOG
from ..utils.logging_setup import get_logger

logger = get_logger("material_classifier")

# Material hierarchy for optimal selection (Phase 1 Enhancement)
MATERIAL_HIERARCHY = {
    "ultra_high_strength": ["Q460", "ASTM A913 Gr65", "ASTM A572 Gr65", "ASTM A852 Gr70"],
    "high_strength": ["ASTM A709 Gr70W", "S460", "Q390", "ASTM A709 Gr50W"],
    "standard_high": ["ASTM A992", "A572 G50", "S355", "Q345"],
    "standard": ["S275", "IS2062 E350"],
    "basic": ["ASTM A36", "S235", "IS2062 E250"]
}

def classify_material(entity: Dict[str,Any]) -> Dict[str,Any]:
    """Enhanced material classifier with optimal selection logic."""

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

    # Intelligent material selection based on structural requirements
    optimal_material = _select_optimal_material(entity)
    if optimal_material:
        logger.info("Optimal material selected: %s for entity %s", optimal_material, entity.get("id"))
        return {"name": optimal_material, **MATERIAL_CATALOG[optimal_material]}

    # fallback to defaults
    default = "ASTM A992" if "column" in (entity.get("role") or "").lower() else "ASTM A36"
    logger.info("Defaulting material to %s for entity %s", default, entity.get("id"))
    return {"name": default, **MATERIAL_CATALOG[default]}

def _select_optimal_material(entity: Dict[str,Any]) -> Optional[str]:
    """Select optimal material based on structural analysis."""

    role = entity.get("role", "").lower()
    length = entity.get("length", 0)
    profile = entity.get("profile", {})
    loads = entity.get("loads", {})
    seismic_zone = loads.get("seismic_zone", "").lower()
    environment = loads.get("environment", "").lower()

    # Calculate approximate loading (simplified analysis)
    area = profile.get("area", 0)
    moment_estimate = entity.get("_ml_selection", {}).get("moment_estimate_Nmm", 0) / 1e9  # kNm

    # For high seismic zones, prefer ultra-high strength materials
    if seismic_zone in ["high", "very_high"]:
        for mat in MATERIAL_HIERARCHY["ultra_high_strength"]:
            if mat in MATERIAL_CATALOG:
                return mat

    # For moderate seismic zones, prefer ASTM A913 Gr65
    if seismic_zone == "moderate":
        if "ASTM A913 Gr65" in MATERIAL_CATALOG:
            return "ASTM A913 Gr65"
        for mat in MATERIAL_HIERARCHY["high_strength"]:
            if mat in MATERIAL_CATALOG:
                return mat

    # For low seismic zones, prefer ASTM A709 Gr50W
    if seismic_zone == "low":
        if "ASTM A709 Gr50W" in MATERIAL_CATALOG:
            return "ASTM A709 Gr50W"
        for mat in MATERIAL_HIERARCHY["standard_high"]:
            if mat in MATERIAL_CATALOG:
                return mat

    # For corrosive/exposed environments, prefer weathering/corrosion-resistant materials
    if environment in ["corrosive", "exposed", "weathering"]:
        for mat in MATERIAL_HIERARCHY["high_strength"]:
            if mat in MATERIAL_CATALOG:
                return mat

    # For long-span or high-load members, prefer ultra-high strength
    if length > 20000 or moment_estimate > 5000:  # >20m span or >5000 kNm moment
        for mat in MATERIAL_HIERARCHY["ultra_high_strength"]:
            if mat in MATERIAL_CATALOG:
                return mat

    # For seismic-critical or stadium applications
    if "stadium" in str(entity).lower() or role in ["column", "primary"]:
        for mat in MATERIAL_HIERARCHY["high_strength"]:
            if mat in MATERIAL_CATALOG:
                return mat

    # For standard applications
    for mat in MATERIAL_HIERARCHY["standard_high"]:
        if mat in MATERIAL_CATALOG:
            return mat

    return None
