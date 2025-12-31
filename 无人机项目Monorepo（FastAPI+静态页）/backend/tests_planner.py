import unittest
from schemas import PlanningRequest
from planner import straight_line_planner


class TestPlanner(unittest.TestCase):
    def test_straight_line(self):
        req = PlanningRequest(start=[0, 0, 0], end=[10, 0, 0])
        resp = straight_line_planner(req, steps=10)
        self.assertEqual(len(resp.path), 11)
        self.assertAlmostEqual(resp.path[-1].x, 10.0, places=6)


if __name__ == "__main__":
    unittest.main()
