from typing import Dict, Any, Optional
from .profile_db import profile_mapper
from .logging_setup import get_logger

logger = get_logger("section_classifier")

def classify_section(member: Dict[str,Any]) -> Optional[Dict[str,Any]]:
    # If a profile dict already exists, return it
    prof_field = member.get("profile")
    if isinstance(prof_field, dict):
        return prof_field

    # Try explicit field
    name = member.get("section") or member.get("profile") or member.get("tag")
    layer = member.get("layer")
    ann = member.get("annotation")
    if not name:
        # try to derive from annotation
        name = ann or ""
    prof = profile_mapper(name, layer=layer, annotations=ann)
    if prof:
        logger.debug("Mapped member %s -> profile", member.get("id"))
    else:
        logger.debug("No profile mapping for member %s", member.get("id"))
    return prof
