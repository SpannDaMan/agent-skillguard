#!/usr/bin/env python3
"""Validate the strict Agent SkillGuard v1 JSON report contract with stdlib only."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT_FIELDS = {"schema_version", "tool", "claim_boundary", "scan", "summary", "findings"}
FINDING_FIELDS = {
    "rule_id", "rule_version", "title", "severity", "uncertainty", "path", "line", "column",
    "evidence", "message", "remediation", "fingerprint", "suppressed", "suppression_reason",
}
SEVERITIES = {"low", "medium", "high", "critical"}
UNCERTAINTIES = {"low", "medium", "high"}


def validate_report(report: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(report, dict):
        return ["report must be a JSON object"]
    if set(report) != ROOT_FIELDS:
        errors.append(f"root fields must be exactly: {', '.join(sorted(ROOT_FIELDS))}")
        return errors
    if report.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    tool = report.get("tool")
    if not isinstance(tool, dict) or set(tool) != {"name", "version"} or tool.get("name") != "agent-skillguard":
        errors.append("tool metadata is invalid")
    if not isinstance(report.get("claim_boundary"), str) or "does not establish" not in report["claim_boundary"]:
        errors.append("claim_boundary must retain the safety and intent non-claim")
    scan = report.get("scan")
    required_scan = {"root", "files_scanned", "bytes_scanned", "scan_digest_sha256", "rule_pack", "rule_count", "minimum_severity", "symlinks_followed"}
    if not isinstance(scan, dict) or set(scan) != required_scan:
        errors.append("scan metadata fields are invalid")
    elif scan.get("root") != "." or scan.get("symlinks_followed") is not False or not re.fullmatch(r"[a-f0-9]{64}", str(scan.get("scan_digest_sha256", ""))):
        errors.append("scan metadata is not portable or digest-bound")
    summary = report.get("summary")
    if not isinstance(summary, dict) or set(summary) != {"active_findings", "suppressed_findings", "by_severity", "result"}:
        errors.append("summary fields are invalid")
    findings = report.get("findings")
    if not isinstance(findings, list):
        return errors + ["findings must be an array"]
    active = 0
    suppressed = 0
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict) or set(finding) != FINDING_FIELDS:
            errors.append(f"finding[{index}] fields are invalid")
            continue
        if finding.get("severity") not in SEVERITIES or finding.get("uncertainty") not in UNCERTAINTIES:
            errors.append(f"finding[{index}] severity or uncertainty is invalid")
        if not re.fullmatch(r"[a-f0-9]{64}", str(finding.get("fingerprint", ""))):
            errors.append(f"finding[{index}] fingerprint is invalid")
        if not isinstance(finding.get("line"), int) or finding["line"] < 1 or not isinstance(finding.get("column"), int) or finding["column"] < 1:
            errors.append(f"finding[{index}] location is invalid")
        if Path(str(finding.get("path", ""))).is_absolute() or "\\" in str(finding.get("path", "")):
            errors.append(f"finding[{index}] path must be portable and relative")
        if finding.get("suppressed") is True:
            suppressed += 1
            if not finding.get("suppression_reason"):
                errors.append(f"finding[{index}] suppressed finding needs a reason")
        elif finding.get("suppressed") is False:
            active += 1
            if finding.get("suppression_reason") is not None:
                errors.append(f"finding[{index}] active finding cannot have a suppression reason")
        else:
            errors.append(f"finding[{index}] suppressed must be boolean")
    if isinstance(summary, dict):
        if summary.get("active_findings") != active or summary.get("suppressed_findings") != suppressed:
            errors.append("summary counts do not match findings")
        expected = "review_required" if active else "no_actionable_findings"
        if summary.get("result") != expected:
            errors.append("summary result does not match active findings")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        errors = validate_report(report)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    print(json.dumps({"status": "pass" if not errors else "fail", "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
