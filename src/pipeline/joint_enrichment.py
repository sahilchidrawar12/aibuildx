"""Joint enrichment utilities.

Adds AI- and geometry-driven joint metadata to improve connection synthesis without
breaking existing flow. Safe to call; failures fall back to original joints.

Capabilities (lightweight):
- Merge provided joints with model-inferred joints (JointInferenceNet fallback)
- Detect near-miss/hidden joints (endpoint proximity within tolerance)
- Tag joint categories (brace/truss/support_base/splice/haunch/standard)
- Capture slant/offset info for non-orthogonal or gapped intersections
- Prefer weld-only for hidden/low-clearance joints

This module is intentionally conservative to avoid regressions.
"""
from __future__ import annotations
from typing import List, Dict, Any, Tuple, Optional
import math

# Lazy import to avoid cycles
try:  # pragma: no cover - optional
    from src.pipeline.agents.connection_synthesis_agent_enhanced import ModelInferenceEngine
except Exception:  # pragma: no cover - optional
    ModelInferenceEngine = None  # type: ignore


def _distance(p1: List[float], p2: List[float]) -> float:
    return math.sqrt(sum((p1[i] - p2[i]) ** 2 for i in range(3)))


def _vec(a: List[float], b: List[float]) -> List[float]:
    return [b[i] - a[i] for i in range(3)]


def _angle_deg(v1: List[float], v2: List[float]) -> float:
    n1 = math.sqrt(sum(x * x for x in v1)) or 1.0
    n2 = math.sqrt(sum(x * x for x in v2)) or 1.0
    dot = sum(v1[i] * v2[i] for i in range(3)) / (n1 * n2)
    dot = max(-1.0, min(1.0, dot))
    return math.degrees(math.acos(dot))


def _collinear(v1: List[float], v2: List[float], tol_deg: float = 8.0) -> bool:
    ang = _angle_deg(v1, v2)
    return ang < tol_deg or abs(180 - ang) < tol_deg


def _member_dir(member: Dict[str, Any]) -> List[float]:
    s = member.get("start") or [0.0, 0.0, 0.0]
    e = member.get("end") or [0.0, 0.0, 0.0]
    return _vec(s, e)


def _maybe_model_infer_joints(members: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not ModelInferenceEngine:
        return []
    try:
        return ModelInferenceEngine.predict_joint_location(members)
    except Exception:
        return []


def _near_miss_hidden_joints(members: List[Dict[str, Any]], tol: float = 75.0) -> List[Dict[str, Any]]:
    joints: List[Dict[str, Any]] = []
    for i, m1 in enumerate(members):
        s1, e1 = m1.get("start"), m1.get("end")
        for m2 in members[i + 1 :]:
            s2, e2 = m2.get("start"), m2.get("end")
            if not (s1 and e1 and s2 and e2):
                continue
            # endpoint-to-endpoint proximity
            candidates = [
                (s1, s2), (s1, e2), (e1, s2), (e1, e2)
            ]
            for p, q in candidates:
                if _distance(p, q) <= tol:
                    joints.append({
                        "id": f"hidden_{len(joints)}",
                        "position": [(p[i] + q[i]) / 2 for i in range(3)],
                        "members": [m1.get("id"), m2.get("id")],
                        "hidden": True,
                        "joint_category": "hidden"
                    })
                    break
    return joints


def _classify_category(joint: Dict[str, Any], members_by_id: Dict[str, Dict[str, Any]]) -> str:
    m_ids = joint.get("members") or []
    if len(m_ids) >= 4:
        return "multiway"
    if joint.get("hidden"):
        return "hidden"
    # brace detection
    brace_count = sum(1 for mid in m_ids if (members_by_id.get(mid, {}).get("role") or "").lower() == "brace")
    if brace_count >= 1:
        return "brace"
    # support detection (column near base)
    for mid in m_ids:
        m = members_by_id.get(mid) or {}
        role = (m.get("role") or "").lower()
        if role == "column":
            zmin = min((m.get("start", [0, 0, 0])[2], m.get("end", [0, 0, 0])[2]))
            if zmin <= 50:
                return "support_base"
    return joint.get("joint_category") or "standard"


def _detect_splices(members: List[Dict[str, Any]], gap_tol: float = 120.0) -> List[Dict[str, Any]]:
    splices: List[Dict[str, Any]] = []
    for i, m1 in enumerate(members):
        v1 = _member_dir(m1)
        for m2 in members[i + 1 :]:
            v2 = _member_dir(m2)
            if not _collinear(v1, v2):
                continue
            # gap between closest endpoints
            endpoints = [m1.get("start"), m1.get("end")]
            endpoints2 = [m2.get("start"), m2.get("end")]
            if not all(endpoints) or not all(endpoints2):
                continue
            min_gap = min(_distance(p, q) for p in endpoints for q in endpoints2)
            if 0 < min_gap <= gap_tol:
                pos = [
                    (m1.get("end", [0, 0, 0])[i] + m2.get("start", [0, 0, 0])[i]) / 2
                    for i in range(3)
                ]
                splices.append({
                    "id": f"splice_{len(splices)}",
                    "position": pos,
                    "members": [m1.get("id"), m2.get("id")],
                    "joint_category": "splice",
                    "splice_type": "bolted"
                })
    return splices


def merge_joints(base: List[Dict[str, Any]], new: List[Dict[str, Any]], tol: float = 15.0) -> List[Dict[str, Any]]:
    merged = list(base)
    for j in new:
        pos = j.get("position") or j.get("location")
        if not pos:
            merged.append(j)
            continue
        duplicate = False
        for k in merged:
            kpos = k.get("position") or k.get("location")
            if kpos and _distance(pos, kpos) <= tol:
                duplicate = True
                break
        if not duplicate:
            merged.append(j)
    return merged


def enrich_joints(members: List[Dict[str, Any]], joints: List[Dict[str, Any]], plate_markers: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Return enriched joints without breaking existing flow."""
    joints = joints or []

    # 1) Add model-inferred joints if none or sparse
    model_joints = _maybe_model_infer_joints(members)
    joints = merge_joints(joints, model_joints, tol=10.0)

    # 2) Add near-miss hidden joints
    hidden = _near_miss_hidden_joints(members, tol=75.0)
    joints = merge_joints(joints, hidden, tol=10.0)

    # 3) Add splice joints
    splices = _detect_splices(members, gap_tol=120.0)
    joints = merge_joints(joints, splices, tol=10.0)

    # 4) Plate markers (optional)
    if plate_markers:
        for pm in plate_markers:
            pos = pm.get("position") or pm.get("center")
            if not pos:
                continue
            joints.append({
                "id": pm.get("id") or f"plate_joint_{len(joints)}",
                "position": pos,
                "members": pm.get("members", []),
                "joint_category": pm.get("plate_type", "plate_mark")
            })

    # 5) Classify categories and weld preferences
    members_by_id = {m.get("id"): m for m in members}
    for j in joints:
        j["joint_category"] = _classify_category(j, members_by_id)
        # slant/offset hints
        pos = j.get("position") or [0, 0, 0]
        loc = j.get("location") or pos
        if pos != loc:
            j["offset_vector"] = [loc[i] - pos[i] for i in range(3)]
        # weld preference for hidden/brace/splice
        if j.get("joint_category") in {"hidden", "brace", "splice"}:
            j["weld_preferred"] = True

    return joints
