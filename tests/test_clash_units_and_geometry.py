import unittest
import numpy as np
from src.pipeline.agents.comprehensive_clash_detector_v2 import ComprehensiveClashDetector, ClashCategory
from src.pipeline.agents.tolerance_and_standards_providers import ToleranceProvider, StandardsProvider

class TestUnitsAndGeometry(unittest.TestCase):
    def setUp(self):
        tol = ToleranceProvider()
        std = StandardsProvider()
        self.detector = ComprehensiveClashDetector(tolerance_provider=tol, standards_provider=std)

    def test_segment_distance_true_metric(self):
        p1 = np.array([0.0, 0.0, 0.0])
        p2 = np.array([1.0, 0.0, 0.0])
        p3 = np.array([0.5, 0.5, 0.0])
        p4 = np.array([0.5, -0.5, 0.0])
        d, c1, c2 = self.detector._distance_between_lines(p1, p2, p3, p4)
        self.assertAlmostEqual(d, 0.0, places=6)
        self.assertAlmostEqual(c1[0], 0.5, places=6)
        self.assertAlmostEqual(c2[0], 0.5, places=6)

    def test_member_penetrates_plate_xy_and_z(self):
        plate = {
            'id': 'plate_base',
            'position': [0.0, 0.0, 0.0],
            'outline': {'width_mm': 300, 'height_mm': 300},
            'thickness_mm': 20
        }
        member = {
            'id': 'M1',
            'start': [-0.1, 0.0, -0.2],
            'end': [0.1, 0.0, 0.2]
        }
        self.assertTrue(self.detector._member_penetrates_plate(member, plate))

    def test_unit_normalization_mm_to_m(self):
        self.assertEqual(self.detector.mm_to_m(1000), 1.0)
        self.assertAlmostEqual(self.detector.mm_to_m(25), 0.025, places=6)

    def test_plate_elevation_mismatch_uses_tolerance(self):
        members = [{'id': 'M1', 'start': [0,0,0.0], 'end': [0,0,0.0]}]
        plates = [{'id': 'P1', 'position': [0,0,0.06], 'members': ['M1']}]
        joints = []
        self.detector.detect_all_clashes({'members': members, 'plates': plates, 'joints': joints})
        categories = [c.category for c in self.detector.clashes]
        self.assertIn(ClashCategory.PLATE_ELEVATION_MISMATCH, categories)

if __name__ == '__main__':
    unittest.main()
