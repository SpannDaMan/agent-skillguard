from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "plugins" / "agent-skillguard" / "rules" / "default-rules.json"
NON_COVERAGE = ROOT / "plugins" / "agent-skillguard" / "rules" / "non-coverage.json"
FIXTURE_ROOT = ROOT / "plugins" / "agent-skillguard" / "fixtures"
MANIFEST = FIXTURE_ROOT / "fixture-manifest.json"
SCRIPT = ROOT / "plugins" / "agent-skillguard" / "scripts" / "skillguard.py"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_NON_COVERAGE = {
    "runtime-behavior",
    "malware-certainty",
    "sandbox-proof",
    "remote-scanning",
    "certification",
    "automatic-remediation",
}


class CorpusError(ValueError):
    pass


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CorpusError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
    except (OSError, UnicodeError, json.JSONDecodeError, CorpusError) as exc:
        raise CorpusError(f"cannot read {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CorpusError(f"{path.name} must contain a JSON object")
    return payload


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_skillguard():
    spec = importlib.util.spec_from_file_location("skillguard_fixture_verifier", SCRIPT)
    if spec is None or spec.loader is None:
        raise CorpusError("cannot load the local Agent SkillGuard module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CorpusError(f"{label} must be a non-empty string")
    return value.strip()


def verify(product_revision: str) -> dict[str, Any]:
    if not SHA256_RE.fullmatch(product_revision):
        raise CorpusError("--product-revision must be a lowercase SHA-256 digest")
    manifest = load_json(MANIFEST)
    if set(manifest) != {"schema_version", "corpus_version", "fixtures"}:
        raise CorpusError("fixture manifest fields are invalid")
    if manifest.get("schema_version") != "1.0":
        raise CorpusError("fixture manifest schema_version must be 1.0")
    corpus_version = require_text(manifest.get("corpus_version"), "corpus_version")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise CorpusError("fixture manifest must contain fixtures")

    non_coverage = load_json(NON_COVERAGE)
    if set(non_coverage) != {"schema_version", "registry_version", "items"}:
        raise CorpusError("non-coverage registry fields are invalid")
    items = non_coverage.get("items")
    if not isinstance(items, list):
        raise CorpusError("non-coverage items must be a list")
    non_coverage_ids = {
        require_text(item.get("id"), "non-coverage id")
        for item in items
        if isinstance(item, dict) and set(item) == {"id", "statement"} and require_text(item.get("statement"), "non-coverage statement")
    }
    if not REQUIRED_NON_COVERAGE.issubset(non_coverage_ids):
        raise CorpusError("non-coverage registry is incomplete")

    skillguard = load_skillguard()
    rules = skillguard.load_rules(RULES)
    rule_ids = {rule.id for rule in rules}
    covered: set[str] = set()
    seen_ids: set[str] = set()
    class_counts = {"positive": 0, "negative": 0}
    results: list[dict[str, Any]] = []
    for index, raw in enumerate(fixtures):
        expected_fields = {"id", "class", "path", "expected_rule_ids", "description"}
        if not isinstance(raw, dict) or set(raw) != expected_fields:
            raise CorpusError(f"fixtures[{index}] fields are invalid")
        fixture_id = require_text(raw.get("id"), f"fixtures[{index}].id")
        fixture_class = require_text(raw.get("class"), f"fixtures[{index}].class")
        relative = require_text(raw.get("path"), f"fixtures[{index}].path")
        require_text(raw.get("description"), f"fixtures[{index}].description")
        expected = raw.get("expected_rule_ids")
        if fixture_id in seen_ids or fixture_class not in class_counts:
            raise CorpusError(f"fixture identity or class is invalid: {fixture_id}")
        if not isinstance(expected, list) or not all(isinstance(item, str) for item in expected):
            raise CorpusError(f"{fixture_id} expected_rule_ids must be a string list")
        expected_ids = sorted(set(expected))
        if len(expected_ids) != len(expected) or not set(expected_ids).issubset(rule_ids):
            raise CorpusError(f"{fixture_id} expected_rule_ids are invalid")
        if fixture_class == "positive" and not expected_ids:
            raise CorpusError(f"positive fixture has no expected rule: {fixture_id}")
        if fixture_class == "negative" and expected_ids:
            raise CorpusError(f"negative fixture must expect no findings: {fixture_id}")
        fixture_path = (FIXTURE_ROOT / relative).resolve()
        try:
            fixture_path.relative_to(FIXTURE_ROOT.resolve())
        except ValueError as exc:
            raise CorpusError(f"fixture escapes corpus root: {fixture_id}") from exc
        if not fixture_path.is_file() or fixture_path.is_symlink():
            raise CorpusError(f"fixture is missing or symlinked: {fixture_id}")
        report = skillguard.scan_path(fixture_path, rules_path=RULES)
        actual_ids = sorted({item["rule_id"] for item in report["findings"]})
        status = "pass" if actual_ids == expected_ids else "fail"
        if fixture_class == "positive":
            covered.update(actual_ids)
        seen_ids.add(fixture_id)
        class_counts[fixture_class] += 1
        results.append(
            {
                "id": fixture_id,
                "class": fixture_class,
                "path": relative.replace("\\", "/"),
                "fixture_sha256": file_sha256(fixture_path),
                "expected_rule_ids": expected_ids,
                "actual_rule_ids": actual_ids,
                "status": status,
            }
        )
    uncovered = sorted(rule_ids - covered)
    status = "pass" if class_counts["positive"] and class_counts["negative"] and not uncovered and all(item["status"] == "pass" for item in results) else "fail"
    return {
        "schema_version": "1.0",
        "artifact": "Agent SkillGuard Rule Corpus Receipt",
        "tool": {"name": "agent-skillguard", "version": skillguard.VERSION},
        "corpus_version": corpus_version,
        "product_revision_sha256": product_revision,
        "rule_pack_sha256": file_sha256(RULES),
        "fixture_manifest_sha256": file_sha256(MANIFEST),
        "non_coverage_sha256": file_sha256(NON_COVERAGE),
        "class_counts": class_counts,
        "covered_rule_ids": sorted(covered),
        "uncovered_rule_ids": uncovered,
        "results": results,
        "status": status,
        "claim_boundary": "Fixture matches demonstrate deterministic rule behavior only; they do not establish that any artifact is safe or malicious and do not cover runtime behavior.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the public Agent SkillGuard rule corpus.")
    parser.add_argument("--product-revision", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        receipt = verify(args.product_revision)
        if args.output:
            if args.output.exists() or args.output.is_symlink():
                raise CorpusError(f"refusing to overwrite output: {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(receipt, indent=2))
        else:
            print(f"{receipt['status'].upper()}: {len(receipt['results'])} fixtures, {len(receipt['covered_rule_ids'])} rules covered")
        return 0 if receipt["status"] == "pass" else 1
    except (CorpusError, OSError, ValueError) as exc:
        print(f"rule-corpus: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
