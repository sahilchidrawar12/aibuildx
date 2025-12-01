import os
import uuid
import tempfile

from src.pipeline import pipeline_v2 as pv2


def make_sample_members():
    return {
        'members': [
            {'id': str(uuid.uuid4()), 'start': [0.0, 0.0, 0.0], 'end': [6.0, 0.0, 0.0], 'length': 6.0, 'type': 'beam', 'selection': {'section_name': 'W8x10'}, 'connection': {'bolt_count': 4, 'bolt_dia_mm': 20}, 'fabrication': {'holes': {'type':'slotted','size_mm':[22,40]}}},
            {'id': str(uuid.uuid4()), 'start': [6.0, 0.0, 0.0], 'end': [6.0, 0.0, 4.0], 'length': 4.0, 'type': 'column', 'selection': {'section_name': 'HSS100x100x6'}, 'connection': {'bolt_count': 0}},
        ]
    }


def test_dstv_exporter_creates_files(tmp_path):
    sample = make_sample_members()
    out = pv2.dstv_exporter(sample, out_dir=str(tmp_path))
    assert out is not None
    assert 'index' in out and os.path.exists(out['index'])
    # check that per-part files exist
    for r in out.get('rows', []):
        p = os.path.join(out.get('parts_dir'), r['file'])
        assert os.path.exists(p)
        with open(p, 'r') as f:
            txt = f.read()
            assert '*** DSTV PART FILE ***' in txt
            assert 'PART_ID:' in txt
