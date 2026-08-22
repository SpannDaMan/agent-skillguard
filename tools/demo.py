#!/usr/bin/env python3
"""Run the committed five-minute Agent SkillGuard proof without network access."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "plugins" / "agent-skillguard" / "scripts" / "skillguard.py"
SPEC = importlib.util.spec_from_file_location("agent_skillguard_demo", MODULE)
assert SPEC and SPEC.loader
skillguard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = skillguard
SPEC.loader.exec_module(skillguard)


def main() -> int:
    unsafe = ROOT / "plugins" / "agent-skillguard" / "examples" / "unsafe-skill"
    clean = ROOT / "plugins" / "agent-skillguard" / "examples" / "clean-skill"
    first = skillguard.scan_path(unsafe)
    second = skillguard.scan_path(unsafe)
    clean_report = skillguard.scan_path(clean)
    if first != second:
        raise SystemExit("demo failed: repeated scans were not deterministic")
    if first["summary"]["active_findings"] < 4:
        raise SystemExit("demo failed: unsafe fixture did not produce the expected findings")
    if clean_report["summary"]["active_findings"] != 0:
        raise SystemExit("demo failed: clean fixture produced an active finding")
    print(skillguard.render_markdown(first), end="")
    print("Demo checks: unsafe fixture detected; clean fixture passed; repeated output identical.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
