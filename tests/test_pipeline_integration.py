from src.pipeline.auto_repair_engine import repair_pipeline
from src.pipeline.profile_db import SECTION_GEOM

def test_repair_and_enrichment():
    payload = {"members": [{"id":"m1","start":(0,0,0),"end":(1000,0,0), "tag":"W14"}, {"id":"m2","start":(1000,0,0),"end":(2000,0,0)}], "plates": []}
    out = repair_pipeline(payload)
    assert 'joints' in out
    # first member should have profile inferred
    assert out['members'][0].get('profile') is not None
