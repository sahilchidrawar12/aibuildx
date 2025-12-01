"""Validation helpers for pipeline inputs and payloads."""
from typing import Any, Dict


def required_keys(payload: Dict[str, Any], keys):
    missing = [k for k in keys if k not in payload]
    if missing:
        raise KeyError(f"Missing required keys: {missing}")
    return True


def is_number(val: Any) -> bool:
    try:
        float(val)
        return True
    except Exception:
        return False


__all__ = ['required_keys', 'is_number']
