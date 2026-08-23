#!/usr/bin/env python3
"""Validate the public-safe Agent SkillGuard candidate without making a release claim."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import subprocess
import sys
import zlib
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "agent-skillguard"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from release_evidence import product_revision  # noqa: E402

REQUIRED_FILES = (
    ".gitattributes", ".gitignore", "LICENSE", "README.md", "BRAND.md", "CHANGELOG.md", "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md", "DESIGN.md", "MAINTAINER-PILOT.md", "PRIVACY.md", "PROVENANCE.md", "PUBLICATION-GATE.md",
    "RELEASE-CHECKLIST.md", "SECURITY.md", "SUPPORT.md", "TERMS.md", "THREAT-MODEL.md", "pyproject.toml",
    ".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json", ".github/FUNDING.yml", ".github/workflows/test.yml",
    "docs/CLAUDE-INSTALL.md", "docs/CODEX-INSTALL.md", "docs/OPENAI-PLUGIN-SUBMISSION.md", "docs/RECEIPTS.md",
    "docs/RELEASE-EVIDENCE.md", "docs/LAUNCH-MEASUREMENT.md", "submission/openai-plugin-submission.json",
    "submission/openai-plugin-submission.schema.json", "plugins/agent-skillguard/.codex-plugin/plugin.json",
    "plugins/agent-skillguard/.claude-plugin/plugin.json", "plugins/agent-skillguard/assets/Agent SkillGuard Transparent Master 220826.png",
    "plugins/agent-skillguard/assets/Agent SkillGuard Agent Smith Palette Source Receipt 210826.md",
    "plugins/agent-skillguard/assets/Logo Generation Manifest 140826.json", "plugins/agent-skillguard/assets/icon.png",
    "plugins/agent-skillguard/assets/logo.png", "plugins/agent-skillguard/assets/logo-dark.png",
    "plugins/agent-skillguard/assets/screenshot1.png", "plugins/agent-skillguard/assets/social-preview.png",
    "tests/test_release_validator.py", "tests/test_submission_metadata.py", "tests/test_claude_packaging.py",
    "tests/test_activation_golden.py", "tools/validate_json_schema.py", "tools/validate_release_candidate.py",
    "tools/validate_activation_golden.py", "tools/verify_rule_corpus.py", "tools/render_brand_assets.ps1",
    "evals/agent-skillguard-activation-golden.json", "plugins/agent-skillguard/rules/non-coverage.json",
    "plugins/agent-skillguard/fixtures/fixture-manifest.json",
)

TEXT_SUFFIXES = {".md", ".json", ".toml", ".yml", ".yaml"}
PRIVATE_MARKERS = (
    "chatgpt.com/g/", "container_route_id", "container_service", "conversation_url", "browser_content_id",
    "agent smith projects", "agent-smith-task-force", "runtime/astf/", "slack-agent-hub", "obsidian brains",
)
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"), re.compile(r"\bghp_[A-Za-z0-9]{16,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{16,}"), re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
ABSOLUTE_PATHS = (re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s]+", re.I), re.compile(r"/(?:Users|home)/[^/\s]+/"))
EXPECTED_PNGS = {
    "plugins/agent-skillguard/assets/Agent SkillGuard Transparent Master 220826.png": (1254, 1254, True),
    "plugins/agent-skillguard/assets/icon.png": (512, 512, True),
    "plugins/agent-skillguard/assets/logo.png": (1024, 1024, True),
    "plugins/agent-skillguard/assets/logo-dark.png": (1024, 1024, True),
    "plugins/agent-skillguard/assets/screenshot1.png": (1600, 900, False),
    "plugins/agent-skillguard/assets/social-preview.png": (1600, 900, False),
}
TARGETED_RECEIPTS = (
    "Agent SkillGuard Eval Result 220826.json", "Package Verification 220826.json", "Codex Plugin Verification 220826.json",
    "Claude Plugin Verification 220826.json", "JSON Schema Verification 220826.json", "Cross-Platform Packaging Review 220826.json",
    "Publication Override 220826.json",
)
COMPOSITE_RECEIPT = "Release Candidate Validation 220826.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def current_revision() -> str:
    return product_revision(ROOT)[0]


def validate_required_files() -> list[str]:
    return [f"missing required file: {item}" for item in REQUIRED_FILES if not (ROOT / item).is_file()]


def public_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT)
        if relative.parts and relative.parts[0] in {"tools", "tests", "evals"}:
            continue
        files.append(path)
    return sorted(files)


def validate_text_safety() -> list[str]:
    errors: list[str] = []
    for path in public_text_files():
        relative = path.relative_to(ROOT).as_posix()
        if path.stat().st_size > 1_000_000:
            errors.append(f"oversized public text file: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"invalid UTF-8: {relative}: {exc}")
            continue
        lowered = text.casefold()
        for marker in PRIVATE_MARKERS:
            if marker in lowered:
                errors.append(f"private route marker in {relative}: {marker}")
        for pattern in (*SECRET_PATTERNS, *ABSOLUTE_PATHS):
            if pattern.search(text):
                errors.append(f"sensitive pattern in {relative}: {pattern.pattern}")
    for residue in ("build", "dist", ".pytest_cache", "__pycache__"):
        residue_root = ROOT / residue
        if residue_root.is_file() or (residue_root.is_dir() and any(path.is_file() for path in residue_root.rglob("*"))):
            errors.append(f"generated residue present: {residue}")
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for retired in (
        "plugins/agent-skillguard/assets/Agent SkillGuard Agent Smith Palette Master 210826.png",
        "plugins/agent-skillguard/assets/Agent SkillGuard GPT Image 2 Master 140826.png",
    ):
        if retired not in ignored:
            errors.append(f"retired local logo input is not excluded from public history: {retired}")
    return errors


def validate_metadata() -> list[str]:
    errors: list[str] = []
    try:
        codex = load_json(PLUGIN / ".codex-plugin" / "plugin.json")
        local_market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
        claude_market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
        claude = load_json(PLUGIN / ".claude-plugin" / "plugin.json")
        submission = load_json(ROOT / "submission" / "openai-plugin-submission.json")
    except (OSError, json.JSONDecodeError) as exc:
        return [f"metadata JSON failed: {exc}"]
    interface = codex.get("interface", {})
    if codex.get("name") != "agent-skillguard" or codex.get("version") != "0.1.2" or codex.get("license") != "MIT":
        errors.append("Codex plugin identity or version mismatch")
    if codex.get("repository") != "https://github.com/SpannDaMan/agent-skillguard":
        errors.append("Codex plugin repository mismatch")
    if interface.get("developerName") != "Orbral" or interface.get("category") != "Security":
        errors.append("Codex developer display or category mismatch")
    if interface.get("shortDescription") != "Scan before you install.":
        errors.append("Codex subtitle mismatch")
    if interface.get("privacyPolicyURL", "").endswith("/PRIVACY.md") is False or interface.get("termsOfServiceURL", "").endswith("/TERMS.md") is False:
        errors.append("Codex privacy or terms URL mismatch")
    if codex.get("mcpServers") or codex.get("mcp"):
        errors.append("Codex manifest must remain skills-only with no MCP declaration")
    if "screenshots" in interface:
        errors.append("skills-only plugin must not declare interface.screenshots")
    expected_prompts = [
        "I downloaded this agent skill from GitHub. Scan it before I install it, show the highest-risk findings, and do not run anything.",
        "Check this plugin for hidden instructions, broad permissions, suspicious downloads, and possible secret exposure.",
        "Turn these scan findings into a short human-review checklist for the risks that still need judgment.",
    ]
    if interface.get("defaultPrompt") != expected_prompts:
        errors.append("Codex starter prompts mismatch")
    entry = local_market.get("plugins", [{}])[0]
    if local_market.get("owner", {}).get("name") != "Orbral" or entry.get("source") != "./plugins/agent-skillguard":
        errors.append("local marketplace identity or source mismatch")
    if entry.get("version") != "0.1.2" or entry.get("category") != "Security" or entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
        errors.append("local marketplace policy mismatch")
    claude_entry = claude_market.get("plugins", [{}])[0]
    if claude_market.get("owner", {}).get("name") != "Orbral" or claude_entry.get("name") != "skill-risk-check" or claude_entry.get("source") != "./plugins/agent-skillguard" or claude_entry.get("version") != "0.1.2":
        errors.append("Claude marketplace metadata mismatch")
    if claude.get("name") != "skill-risk-check" or claude.get("version") != "0.1.2" or claude.get("author", {}).get("name") != "Orbral":
        errors.append("Claude plugin identity mismatch")
    if submission.get("submission_type") != "skills_only" or submission.get("publisher") != "Orbral" or submission.get("category") != "Security":
        errors.append("OpenAI submission identity mismatch")
    if submission.get("short_description") != "Scan before you install." or submission.get("starter_prompts") != expected_prompts:
        errors.append("OpenAI submission copy mismatch")
    if len(submission.get("positive_tests", [])) != 5 or len(submission.get("negative_tests", [])) != 3 or submission.get("publication_action") != "none":
        errors.append("OpenAI submission test matrix or action mismatch")
    return errors


def paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    choices = (left, up, upper_left)
    distances = (abs(estimate - left), abs(estimate - up), abs(estimate - upper_left))
    return choices[distances.index(min(distances))]


def decode_png_rgba(path: Path) -> tuple[int, int, list[bytes]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    offset, width, height, bit_depth, color_type, interlace = 8, None, None, None, None, None
    compressed = bytearray()
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
    if None in (width, height, bit_depth, color_type, interlace):
        raise ValueError("missing IHDR")
    if bit_depth != 8 or color_type not in {2, 6} or interlace != 0:
        raise ValueError(f"unsupported PNG format depth={bit_depth} type={color_type} interlace={interlace}")
    raw = zlib.decompress(bytes(compressed))
    bpp, stride, cursor, previous, rows = (3 if color_type == 2 else 4), width * (3 if color_type == 2 else 4), 0, bytearray(width * (3 if color_type == 2 else 4)), []
    for _ in range(height):
        filter_type, source = raw[cursor], raw[cursor + 1 : cursor + 1 + stride]
        cursor += stride + 1
        row = bytearray(stride)
        for index, value in enumerate(source):
            left = row[index - bpp] if index >= bpp else 0
            up = previous[index]
            upper_left = previous[index - bpp] if index >= bpp else 0
            decoded = value if filter_type == 0 else value + left if filter_type == 1 else value + up if filter_type == 2 else value + ((left + up) // 2) if filter_type == 3 else value + paeth(left, up, upper_left) if filter_type == 4 else None
            if decoded is None:
                raise ValueError(f"unsupported PNG filter {filter_type}")
            row[index] = decoded & 0xFF
        if color_type == 2:
            rgba = bytearray(width * 4)
            for pixel in range(width):
                rgba[pixel * 4 : pixel * 4 + 3] = row[pixel * 3 : pixel * 3 + 3]
                rgba[pixel * 4 + 3] = 255
            rows.append(bytes(rgba))
        else:
            rows.append(bytes(row))
        previous = row
    return width, height, rows


def alpha_bounds(rows: list[bytes], width: int) -> tuple[int, int, int, int] | None:
    points = [(x, y) for y, row in enumerate(rows) for x in range(width) if row[x * 4 + 3] >= 16]
    if not points:
        return None
    xs, ys = zip(*points)
    return min(xs), min(ys), max(xs), max(ys)


def validate_png(path: Path, expected: tuple[int, int, bool]) -> list[str]:
    relative = path.relative_to(ROOT).as_posix()
    try:
        width, height, rows = decode_png_rgba(path)
    except (OSError, ValueError, zlib.error, struct.error) as exc:
        return [f"{relative}: PNG decode failed: {exc}"]
    expected_width, expected_height, transparent = expected
    errors: list[str] = []
    if (width, height) != (expected_width, expected_height):
        errors.append(f"{relative}: expected {expected_width}x{expected_height}, got {width}x{height}")
    corners = (rows[0][3], rows[0][(width - 1) * 4 + 3], rows[-1][3], rows[-1][(width - 1) * 4 + 3])
    if transparent:
        if any(alpha != 0 for alpha in corners):
            errors.append(f"{relative}: transparent asset corners have incorrect alpha")
        bounds = alpha_bounds(rows, width)
        if bounds is None:
            errors.append(f"{relative}: transparent asset has no visible subject")
        elif relative.endswith(("Transparent Master 220826.png", "icon.png", "logo.png", "logo-dark.png")):
            fill = min(bounds[2] - bounds[0] + 1, bounds[3] - bounds[1] + 1) / min(width, height)
            if not 0.79 <= fill <= 0.96:
                errors.append(f"{relative}: transparent subject fill {fill:.3f} is outside 0.79-0.96")
    elif any(alpha != 255 for alpha in corners):
        errors.append(f"{relative}: opaque surface corners have incorrect alpha")
    return errors


def validate_assets() -> list[str]:
    errors: list[str] = []
    for relative, expected in EXPECTED_PNGS.items():
        path = ROOT / relative
        if path.is_file():
            errors.extend(validate_png(path, expected))
    return errors


def validate_logo_provenance() -> list[str]:
    try:
        manifest = load_json(PLUGIN / "assets" / "Logo Generation Manifest 140826.json")
        source_receipt = (PLUGIN / "assets" / "Agent SkillGuard Agent Smith Palette Source Receipt 210826.md").read_text(encoding="utf-8")
        renderer = (ROOT / "tools" / "render_brand_assets.ps1").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"logo provenance failed: {exc}"]
    errors: list[str] = []
    expected = "plugins/agent-skillguard/assets/Agent SkillGuard Transparent Master 220826.png"
    master = ROOT / expected
    if manifest.get("canonical_master") != expected or manifest.get("source_type") != "deterministic_transparent_derivative" or manifest.get("source_background_policy") != "transparent_source":
        errors.append("transparent logo manifest identity mismatch")
    if manifest.get("master_sha256") != "b67972d299813960e9331089788086c1beed435a9fbe5dcf5e3c1894810248d3" or manifest.get("opaque_parent_sha256") != "bd1dbefb2f149aae5c9cc77eb5a9782aa99452693cd62816a5fc32adb5d55970":
        errors.append("transparent logo manifest hash custody mismatch")
    if master.is_file() and hashlib.sha256(master.read_bytes()).hexdigest() != manifest.get("master_sha256"):
        errors.append("transparent master hash does not match manifest")
    for required in ("accepted derivative, not an asserted unedited original", "Opaque parent SHA-256", "transparent master"):
        if required.casefold() not in source_receipt.casefold():
            errors.append(f"source receipt missing required custody statement: {required}")
    for forbidden in ("chat_url", "container_service", "conversation_url", "browser_content_id", "AI Agents"):
        if forbidden.casefold() in json.dumps(manifest).casefold() or forbidden.casefold() in source_receipt.casefold():
            errors.append(f"private provenance detail remains public: {forbidden}")
    for required in ("transparent_source", "New-Canvas 512 512 'transparent'", "accepted_transparent_master_only"):
        if required not in renderer:
            errors.append(f"brand renderer missing transparent-source control: {required}")
    return errors


def validate_submission_schema() -> list[str]:
    schema = ROOT / "submission" / "openai-plugin-submission.schema.json"
    instance = ROOT / "submission" / "openai-plugin-submission.json"
    command = [sys.executable, "tools/validate_json_schema.py", "--schema", str(schema), "--instance", str(instance)]
    completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    return [] if completed.returncode == 0 else [f"submission schema validation failed: {(completed.stdout + completed.stderr).strip()[-500:]}"]


def validate_claims_and_behavior() -> list[str]:
    errors: list[str] = []
    try:
        path = PLUGIN / "scripts" / "skillguard.py"
        spec = importlib.util.spec_from_file_location("release_skillguard", path)
        if not spec or not spec.loader:
            raise ImportError(path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        unsafe = module.scan_path(PLUGIN / "examples" / "unsafe-skill")
        clean = module.scan_path(PLUGIN / "examples" / "clean-skill")
    except Exception as exc:
        return [f"behavior validation failed: {exc}"]
    if clean["summary"]["active_findings"] != 0 or not {"SG001", "SG003", "SG004", "SG008"}.issubset({item["rule_id"] for item in unsafe["findings"]}):
        errors.append("scanner fixtures no longer preserve the documented behavior")
    readme = (ROOT / "README.md").read_text(encoding="utf-8").casefold()
    for phrase in ("potential policy violations", "does not mean", "never executes", "never executes, imports, installs, enables, or uploads"):
        if phrase not in readme:
            errors.append(f"README missing behavior boundary: {phrase}")
    return errors


def validate_targeted_receipts() -> list[str]:
    revision = current_revision()
    errors: list[str] = []
    for name in TARGETED_RECEIPTS:
        path = ROOT / "validation" / name
        try:
            receipt = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"missing or invalid targeted receipt: {name}: {exc}")
            continue
        if receipt.get("product_revision_sha256") != revision:
            errors.append(f"targeted receipt is stale: {name}")
        if receipt.get("publication_action") != "none":
            errors.append(f"targeted receipt action is not none: {name}")
        if name == "Publication Override 220826.json":
            if receipt.get("private_pilot_started") is not False or receipt.get("private_pilot_completed") is not False or receipt.get("status") != "scoped_override_recorded":
                errors.append("private-pilot override does not preserve the uncompleted pilot state")
        elif receipt.get("status") != "pass":
            errors.append(f"targeted receipt is not passing: {name}")
    return errors


def validate_full_gate_receipt() -> list[str]:
    errors = validate_targeted_receipts()
    try:
        composite = load_json(ROOT / "validation" / COMPOSITE_RECEIPT)
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"missing or invalid frozen-candidate composite receipt: {exc}"]
    if composite.get("product_revision_sha256") != current_revision() or composite.get("status") != "pass" or composite.get("publication_action") != "none":
        errors.append("frozen-candidate composite receipt is stale or non-passing")
    return errors


def validate_fresh_commands() -> list[str]:
    errors: list[str] = []
    revision = current_revision()
    commands = (
        ([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], "unit tests"),
        ([sys.executable, "tools/run_evals.py"], "evaluations"),
        ([sys.executable, "tools/demo.py"], "demo"),
        ([sys.executable, "tools/validate_activation_golden.py", "--suite", "evals/agent-skillguard-activation-golden.json", "--product-revision", revision], "activation golden suite"),
        ([sys.executable, "tools/verify_rule_corpus.py", "--product-revision", revision], "versioned rule corpus"),
    )
    for command, label in commands:
        completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
        if completed.returncode != 0:
            errors.append(f"{label} failed: {(completed.stdout + completed.stderr).strip()[-500:]}")
    return errors


def run_validation(*, targeted: bool = False) -> dict[str, Any]:
    checks = {
        "required_files": validate_required_files(),
        "text_safety": validate_text_safety(),
        "metadata": validate_metadata(),
        "assets": validate_assets(),
        "logo_provenance": validate_logo_provenance(),
        "submission_schema": validate_submission_schema(),
    }
    if targeted:
        checks["claims_and_behavior"] = validate_claims_and_behavior()
    else:
        checks["claims_and_behavior"] = validate_claims_and_behavior()
        checks["fresh_commands"] = validate_fresh_commands()
        checks["revision_bound_receipts"] = validate_full_gate_receipt()
    errors = sorted({error for group in checks.values() for error in group})
    return {
        "status": "pass" if not errors else "fail",
        "mode": "targeted" if targeted else "frozen_candidate_full_gate",
        "candidate": "agent-skillguard 0.1.2",
        "product_revision_sha256": current_revision(),
        "checks": {name: "pass" if not group else "fail" for name, group in checks.items()},
        "publication_action": "none",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--targeted", action="store_true", help="Run package-surface checks only; this is not the frozen-candidate gate.")
    args = parser.parse_args()
    result = run_validation(targeted=args.targeted)
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["status"] == "pass":
        print(f"PASS: Skill Risk Check {result['mode']}")
    else:
        print(f"FAIL: Skill Risk Check {result['mode']}", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
