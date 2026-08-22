#!/usr/bin/env python3
"""Run the deterministic Agent SkillGuard evaluation suite."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "plugins" / "agent-skillguard" / "scripts" / "skillguard.py"
SPEC = importlib.util.spec_from_file_location("skillguard_evals", MODULE)
assert SPEC and SPEC.loader
skillguard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = skillguard
SPEC.loader.exec_module(skillguard)


def run_suite(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []
    for case in payload["cases"]:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            (target / case["filename"]).write_text(case["content"], encoding="utf-8")
            report = skillguard.scan_path(target)
        found = sorted({item["rule_id"] for item in report["findings"] if not item["suppressed"]})
        missing = sorted(set(case["expected_rules"]) - set(found))
        forbidden = sorted(set(case["forbidden_rules"]) & set(found))
        results.append({"id": case["id"], "status": "pass" if not missing and not forbidden else "fail", "found_rules": found, "missing_rules": missing, "forbidden_rules_found": forbidden})
    passed = sum(result["status"] == "pass" for result in results)
    return {
        "schema_version": "1.0",
        "suite": payload["suite"],
        "status": "pass" if passed == len(results) else "fail",
        "passed": passed,
        "total": len(results),
        "score": passed / len(results) if results else 0,
        "cases": results,
        "publication_action": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=ROOT / "evals" / "skillguard-suite.json")
    args = parser.parse_args()
    result = run_suite(args.suite)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
