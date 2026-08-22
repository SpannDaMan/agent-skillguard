from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "verify_rule_corpus.py"
SPEC = importlib.util.spec_from_file_location("skillguard_rule_corpus_verifier", SCRIPT)
assert SPEC and SPEC.loader
verifier = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verifier
SPEC.loader.exec_module(verifier)


class RuleCorpusTests(unittest.TestCase):
    def test_all_rules_have_exact_positive_fixture_coverage(self) -> None:
        receipt = verifier.verify("a" * 64)
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["covered_rule_ids"], [f"SG{index:03d}" for index in range(1, 9)])
        self.assertEqual(receipt["uncovered_rule_ids"], [])
        self.assertEqual(receipt["class_counts"], {"positive": 8, "negative": 4})

    def test_negative_fixtures_have_no_active_findings(self) -> None:
        receipt = verifier.verify("a" * 64)
        negatives = [item for item in receipt["results"] if item["class"] == "negative"]
        self.assertTrue(negatives)
        self.assertTrue(all(item["actual_rule_ids"] == [] for item in negatives))

    def test_receipt_is_deterministic(self) -> None:
        self.assertEqual(verifier.verify("a" * 64), verifier.verify("a" * 64))


if __name__ == "__main__":
    unittest.main()
