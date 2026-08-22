"""Regression tests for the Agent SkillGuard release validator."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools" / "validate_release_candidate.py"
SPEC = importlib.util.spec_from_file_location("skillguard_release_validator", PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ReleaseValidatorTests(unittest.TestCase):
    def test_product_revision_excludes_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "validation").mkdir()
            product = root / "README.md"
            receipt = root / "validation" / "receipt.json"
            product.write_text("v1", encoding="utf-8")
            receipt.write_text("one", encoding="utf-8")
            first = validator.product_revision(root)[0]
            receipt.write_text("two", encoding="utf-8")
            second = validator.product_revision(root)[0]
            product.write_text("v2", encoding="utf-8")
            third = validator.product_revision(root)[0]
        self.assertEqual(first, second)
        self.assertNotEqual(second, third)

    def test_png_decoder_rejects_non_png(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.png"
            path.write_bytes(b"not a png")
            with self.assertRaises(ValueError):
                validator.decode_png_rgba(path)

    def test_run_validation_preserves_specific_check_failure(self) -> None:
        names = (
            "validate_required_files", "validate_text_safety", "validate_metadata", "validate_assets",
            "validate_logo_provenance", "validate_submission_schema", "validate_claims_and_behavior",
            "validate_fresh_commands", "validate_full_gate_receipt",
        )
        patches = [mock.patch.object(validator, name, return_value=[]) for name in names]
        with patches[0] as required, patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7], patches[8], mock.patch.object(validator, "current_revision", return_value="a" * 64):
            required.return_value = ["missing required file: x"]
            result = validator.run_validation()
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["checks"]["required_files"], "fail")
        self.assertEqual(result["errors"], ["missing required file: x"])

    def test_transparent_png_requires_transparent_corners(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "icon.png"
            path.write_bytes(b"not a png")
            with mock.patch.object(validator, "ROOT", Path(temp)):
                errors = validator.validate_png(path, (512, 512, True))
        self.assertTrue(errors[0].endswith("PNG decode failed: not a PNG"))

    def test_full_gate_rejects_missing_composite_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "validation").mkdir()
            with mock.patch.object(validator, "ROOT", root), mock.patch.object(validator, "validate_targeted_receipts", return_value=[]):
                errors = validator.validate_full_gate_receipt()
        self.assertTrue(any("missing or invalid frozen-candidate composite receipt" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
