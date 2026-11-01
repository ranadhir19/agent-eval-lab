import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import suite, agents, graders
from audit import audit_suite

class TestCleanSuite(unittest.TestCase):
    def test_reference_is_perfect_on_clean(self):
        for t in suite.clean_suite():
            self.assertTrue(graders.passes(agents.reference_agent(t), t), t["id"])

    def test_independent_implementation_agrees(self):
        for t in suite.clean_suite():
            self.assertEqual(suite.independent_expected(t), t["expected"], t["id"])

    def test_null_scores_zero_on_clean(self):
        for t in suite.clean_suite():
            self.assertFalse(graders.passes(agents.null_agent(t), t), t["id"])

class TestAudit(unittest.TestCase):
    def test_audit_flags_nothing_on_clean(self):
        flags = audit_suite(suite.clean_suite(), suite.dev_suite())
        self.assertEqual(flags, {})

    def test_audit_detects_at_least_ten_planted(self):
        flags = audit_suite(suite.flawed_suite(), suite.dev_suite())
        hit = set(suite.PLANTED_FLAWS) & set(flags)
        self.assertGreaterEqual(len(hit), 10)

class TestGraders(unittest.TestCase):
    def test_normalized_accepts_formatting(self):
        self.assertTrue(graders.grade_normalized("1,234", "1234"))
        self.assertTrue(graders.grade_normalized("Positive", "positive"))
        self.assertFalse(graders.grade_normalized("1235", "1234"))

if __name__ == "__main__":
    unittest.main()
