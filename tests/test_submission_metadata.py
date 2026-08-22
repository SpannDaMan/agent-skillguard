"""Regression tests for the OpenAI skills-only submission packet."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SubmissionMetadataTests(unittest.TestCase):
    def test_submission_schema_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "tools/validate_json_schema.py", "--schema", "submission/openai-plugin-submission.schema.json", "--instance", "submission/openai-plugin-submission.json"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_submission_preserves_skills_only_boundary(self) -> None:
        payload = json.loads((ROOT / "submission" / "openai-plugin-submission.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["submission_type"], "skills_only")
        self.assertEqual(payload["publisher"], "Orbral")
        self.assertEqual(payload["short_description"], "Scan before you install.")
        self.assertEqual(len(payload["positive_tests"]), 5)
        self.assertEqual(len(payload["negative_tests"]), 3)
        self.assertEqual(payload["publication_action"], "none")
