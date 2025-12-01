import pytest
from src.pipeline.profile_db import profile_mapper, SECTION_GEOM

def test_profile_mapper_direct_match():
    res = profile_mapper("IPE300")
    assert res is not None
    assert "Ix" in res

def test_profile_mapper_fuzzy():
    res = profile_mapper("W14")
    assert res is not None

def test_profile_mapper_unknown():
    res = profile_mapper("UNKNOWN_SECTION_9999")
    assert res is None
