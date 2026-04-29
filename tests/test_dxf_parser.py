import tempfile
import os

import pytest


def test_parse_dxf_file_extracts_text_annotations():
    ezdxf = pytest.importorskip('ezdxf')
    from src.pipeline.dxf_parser import parse_dxf_file

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    msp.add_line((0, 0, 0), (1000, 0, 0), dxfattribs={'layer': 'BEAMS'})
    text_entity = msp.add_text('IPE300', dxfattribs={'height': 10, 'layer': 'ANNOTATIONS'})
    try:
        text_entity.dxf.insert = (500, 20, 0)
    except Exception:
        pass

    with tempfile.TemporaryDirectory() as tmpdir:
        dxf_path = os.path.join(tmpdir, 'sample.dxf')
        doc.saveas(dxf_path)
        result = parse_dxf_file(dxf_path)

    assert 'members' in result
    assert len(result['members']) == 1
    assert any('annotation' in m and 'IPE300' in m['annotation'] for m in result['members'])
    assert 'annotations' in result
    assert any('IPE300' in ann['text'] for ann in result['annotations'])


def test_parse_dxf_file_extracts_circle_markers():
    ezdxf = pytest.importorskip('ezdxf')
    from src.pipeline.dxf_parser import parse_dxf_file

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    msp.add_line((0, 0, 0), (1000, 0, 0), dxfattribs={'layer': 'BEAMS'})
    msp.add_circle((1000, 0, 0), radius=50, dxfattribs={'layer': 'CONNECTIONS'})

    with tempfile.TemporaryDirectory() as tmpdir:
        dxf_path = os.path.join(tmpdir, 'circle_test.dxf')
        doc.saveas(dxf_path)
        result = parse_dxf_file(dxf_path)

    assert 'circles' in result
    assert len(result['circles']) == 1
    assert result['circles'][0]['radius'] == 50
    assert result['circles'][0]['center'] == [1000.0, 0.0, 0.0]
