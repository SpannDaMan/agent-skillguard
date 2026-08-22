"""Tests for the standalone JSON report validator."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


skillguard = load(ROOT / "plugins" / "agent-skillguard" / "scripts" / "skillguard.py", "report_test_skillguard")
validator = load(ROOT / "tools" / "validate_report.py", "report_validator")


class ReportValidatorTests(unittest.TestCase):
    def test_generated_report_passes(self) -> None:
        report = skillguard.scan_path(ROOT / "plugins" / "agent-skillguard" / "examples" / "unsafe-skill")
        self.assertEqual(validator.validate_report(report), [])

    def test_unknown_root_field_fails(self) -> None:
        report = skillguard.scan_path(ROOT / "plugins" / "agent-skillguard" / "examples" / "clean-skill")
        report["unknown"] = True
        self.assertTrue(validator.validate_report(report))

    def test_count_drift_fails(self) -> None:
        report = skillguard.scan_path(ROOT / "plugins" / "agent-skillguard" / "examples" / "unsafe-skill")
        report["summary"]["active_findings"] = 0
        self.assertIn("summary counts do not match findings", validator.validate_report(report))

    def test_suppressed_finding_requires_reason(self) -> None:
        report = skillguard.scan_path(ROOT / "plugins" / "agent-skillguard" / "examples" / "unsafe-skill")
        report["findings"][0]["suppressed"] = True
        report["findings"][0]["suppression_reason"] = None
        self.assertTrue(any("needs a reason" in item for item in validator.validate_report(report)))


if __name__ == "__main__":
    unittest.main()
