from src.pipeline.connection_design import plate_thickness_from_moment, plate_width_from_flange, min_edge_distance

def test_plate_width_and_thickness():
    w = plate_width_from_flange(200.0, cover=40.0)
    assert w == 280.0
    t = plate_thickness_from_moment(1000.0, width=200.0, fy=355.0)
    assert t >= 6.0
    assert min_edge_distance(10.0) == 80.0
