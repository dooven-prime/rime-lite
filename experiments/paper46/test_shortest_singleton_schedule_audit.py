import unittest

from shortest_singleton_schedule_audit import audit, is_rotation_family_word


class ShortestSingletonScheduleAuditTests(unittest.TestCase):
    def test_small_exact_classification(self):
        results = audit(range(2, 8))
        self.assertEqual([len(results[n]) for n in range(2, 8)], [4, 4, 8, 16, 32, 64])
        for n in range(3, 8):
            self.assertTrue(all(is_rotation_family_word(word, n) for word in results[n]))

    def test_n_two_has_genuine_extra_schedules(self):
        words = audit(range(2, 3))[2]
        self.assertIn(("v", "p1", "d0", "v"), words)
        self.assertIn(("v", "d0", "p1", "v"), words)


if __name__ == "__main__":
    unittest.main()
