import unittest

from hssm.monitor import Sample, evaluate_sample, load_kg_from_raw, load_status


class MonitorTests(unittest.TestCase):
    def test_low_quality_never_reports_all_clear(self):
        result = evaluate_sample(Sample("t0", 0.2, 70, 30.0, 0.1))
        self.assertEqual(result.status, "SIGNAL_UNRELIABLE")
        self.assertNotIn("all-clear", result.message.lower())

    def test_good_quality_is_only_trend_recorded(self):
        result = evaluate_sample(Sample("t0", 0.9, 70, 30.0, 0.1))
        self.assertEqual(result.status, "TREND_RECORDED")
        self.assertIn("not an all-clear", result.message)

    def test_wearer_concern_is_not_diagnosed(self):
        result = evaluate_sample(Sample("t0", 0.9, check_in="concern"))
        self.assertEqual(result.status, "CHECK_IN_REQUESTED")
        self.assertNotIn("diagnos", result.message.lower())

    def test_invalid_quality_is_rejected_as_unreliable(self):
        result = evaluate_sample(Sample("t0", 2.0))
        self.assertEqual(result.status, "SIGNAL_UNRELIABLE")

    def test_quality_floor_validation(self):
        with self.assertRaises(ValueError):
            evaluate_sample(Sample("t0", 0.8), quality_floor=1.1)

    def test_load_cell_conversion(self):
        self.assertAlmostEqual(load_kg_from_raw(12500, 2500, 1000), 10.0)
        self.assertEqual(load_kg_from_raw(1000, 2500, 1000), 0.0)

    def test_load_limit_is_user_configured(self):
        self.assertEqual(load_status(12.0, 10.0), "ABOVE_USER_SET_LIMIT")
        self.assertEqual(load_status(8.0, 10.0), "WITHIN_USER_SET_LIMIT")

    def test_invalid_load_calibration_rejected(self):
        with self.assertRaises(ValueError):
            load_kg_from_raw(1000, 0, 0)


if __name__ == "__main__":
    unittest.main()
