"""Regression tests for Agent SkillGuard Claude package parity."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "agent-skillguard"


class ClaudePackagingTests(unittest.TestCase):
    def test_marketplace_and_plugin_identity_match(self) -> None:
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        entry = marketplace["plugins"][0]
        self.assertEqual(marketplace["owner"]["name"], "Orbral")
        self.assertEqual(entry["name"], "skill-risk-check")
        self.assertEqual(entry["source"], "./plugins/agent-skillguard")
        self.assertEqual(entry["version"], "0.1.2")
        self.assertEqual(plugin["name"], entry["name"])
        self.assertEqual(plugin["version"], entry["version"])
        self.assertEqual(plugin["author"]["name"], "Orbral")

    def test_no_mcp_manifest_is_present(self) -> None:
        self.assertFalse(any(path.name == ".mcp.json" for path in PLUGIN.rglob(".mcp.json")))
