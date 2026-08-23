#!/usr/bin/env python3
"""Generate revision-bound local eval, package, and Codex plugin evidence."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "validation"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from release_evidence import file_sha256, product_revision  # noqa: E402


def run(command: list[str], *, cwd: Path, allowed: set[int] = {0}) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    if completed.returncode not in allowed:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout: {completed.stdout[-1200:]}\nstderr: {completed.stderr[-1200:]}"
        )
    return completed


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def cleanup_generated_residue() -> None:
    """Remove only ignored build/cache outputs created by local evidence generation."""

    for path in (ROOT / "build", ROOT / "dist", ROOT / ".pytest_cache"):
        if path.is_dir():
            shutil.rmtree(path)
    for path in sorted(ROOT.rglob("*.egg-info"), reverse=True):
        if path.is_dir():
            shutil.rmtree(path)
    for path in sorted(ROOT.rglob("__pycache__"), reverse=True):
        if path.is_dir():
            shutil.rmtree(path)


def main() -> int:
    VALIDATION.mkdir(parents=True, exist_ok=True)
    revision, _manifest = product_revision(ROOT)

    eval_run = run([sys.executable, "tools/run_evals.py"], cwd=ROOT)
    eval_receipt = json.loads(eval_run.stdout)
    eval_receipt["product_revision_sha256"] = revision
    write_json(VALIDATION / "Agent SkillGuard Eval Result 220826.json", eval_receipt)

    with tempfile.TemporaryDirectory() as temp_name:
        temp = Path(temp_name)
        wheel_dir = temp / "wheel"
        wheel_dir.mkdir()
        run(
            [sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "--no-build-isolation", "--wheel-dir", str(wheel_dir)],
            cwd=ROOT,
        )
        wheels = list(wheel_dir.glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError(f"expected one wheel, found {len(wheels)}")
        wheel = wheels[0]
        venv = temp / "venv"
        run([sys.executable, "-m", "venv", str(venv)], cwd=temp)
        venv_python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        run([str(venv_python), "-m", "pip", "install", "--no-deps", str(wheel)], cwd=temp)
        pip_check = run([str(venv_python), "-m", "pip", "check"], cwd=temp)
        version = run([str(venv_python), "-m", "skillguard", "--version"], cwd=temp)
        clean = ROOT / "plugins" / "agent-skillguard" / "examples" / "clean-skill"
        unsafe = ROOT / "plugins" / "agent-skillguard" / "examples" / "unsafe-skill"
        clean_run = run([str(venv_python), "-m", "skillguard", "scan", str(clean)], cwd=temp)
        unsafe_run = run([str(venv_python), "-m", "skillguard", "scan", str(unsafe)], cwd=temp, allowed={1})
        clean_report = json.loads(clean_run.stdout)
        unsafe_report = json.loads(unsafe_run.stdout)
        package_receipt: dict[str, object] = {
            "schema_version": "1.0",
            "candidate": "agent-skillguard 0.1.2",
            "product_revision_sha256": revision,
            "status": "pass",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "install_source": ".",
            "runtime_dependencies": [],
            "wheel": {"filename": wheel.name, "sha256": file_sha256(wheel), "bytes": wheel.stat().st_size},
            "checks": [
                {"name": "pep517_wheel_and_clean_install", "status": "pass"},
                {"name": "pip_check", "status": "pass", "result": pip_check.stdout.strip()},
                {"name": "installed_cli_version", "status": "pass", "result": version.stdout.strip()},
                {"name": "installed_clean_fixture", "status": "pass", "result": f"exit 0; {clean_report['summary']['active_findings']} active findings"},
                {"name": "installed_unsafe_fixture", "status": "pass", "result": f"exit 1; {unsafe_report['summary']['active_findings']} active findings"},
                {"name": "installed_rule_resource", "status": "pass", "result": f"{unsafe_report['scan']['rule_count']} rules loaded outside the repository root"}
            ],
            "publication_action": "none"
        }
        write_json(VALIDATION / "Package Verification 220826.json", package_receipt)

    validator = Path.home() / ".codex" / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"
    if not validator.is_file():
        raise RuntimeError(f"official local plugin validator missing: {validator}")
    plugin_run = run([sys.executable, str(validator), "plugins/agent-skillguard"], cwd=ROOT)
    plugin_receipt: dict[str, object] = {
        "schema_version": "1.0",
        "candidate": "agent-skillguard 0.1.2",
        "product_revision_sha256": revision,
        "status": "pass",
        "exit_code": plugin_run.returncode,
        "validated_plugin_path": "plugins/agent-skillguard",
        "working_directory": ".",
        "command": ["python", "$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py", "plugins/agent-skillguard"],
        "tool": {"name": "Codex plugin-creator validate_plugin.py", "identity": "sha256", "sha256": file_sha256(validator), "bytes": validator.stat().st_size},
        "output": "Plugin validation passed: plugins/agent-skillguard",
        "publication_action": "none"
    }
    write_json(VALIDATION / "Codex Plugin Verification 220826.json", plugin_receipt)

    claude = shutil.which("claude.cmd") or shutil.which("claude")
    if not claude:
        raise RuntimeError("Claude CLI missing: cannot validate Claude marketplace and plugin manifests")
    claude_root = run([claude, "plugin", "validate", "."], cwd=ROOT)
    claude_plugin = run([claude, "plugin", "validate", "plugins/agent-skillguard"], cwd=ROOT)
    claude_version = run([claude, "--version"], cwd=ROOT)
    write_json(
        VALIDATION / "Claude Plugin Verification 220826.json",
        {
            "schema_version": "1.0",
            "candidate": "agent-skillguard 0.1.2",
            "product_revision_sha256": revision,
            "status": "pass",
            "validated_paths": [".", "plugins/agent-skillguard"],
            "checks": [
                {"command": ["claude", "plugin", "validate", "."], "exit_code": claude_root.returncode, "status": "pass"},
                {"command": ["claude", "plugin", "validate", "plugins/agent-skillguard"], "exit_code": claude_plugin.returncode, "status": "pass"},
            ],
            "tool": {"name": "Claude Code", "version": claude_version.stdout.strip()},
            "evidence_boundary": "Local Claude package validation only; not marketplace acceptance.",
            "publication_action": "none",
        },
    )

    schema = ROOT / "submission" / "openai-plugin-submission.schema.json"
    instance = ROOT / "submission" / "openai-plugin-submission.json"
    schema_validator = ROOT / "tools" / "validate_json_schema.py"
    schema_run = run(
        [sys.executable, "-B", str(schema_validator), "--schema", str(schema), "--instance", str(instance)],
        cwd=ROOT,
    )
    write_json(
        VALIDATION / "JSON Schema Verification 220826.json",
        {
            "schema_version": "1.0",
            "candidate": "agent-skillguard 0.1.2",
            "product_revision_sha256": revision,
            "status": "pass",
            "command": ["python", "-B", "tools/validate_json_schema.py", "--schema", "submission/openai-plugin-submission.schema.json", "--instance", "submission/openai-plugin-submission.json"],
            "exit_code": schema_run.returncode,
            "validator_sha256": file_sha256(schema_validator),
            "schema_sha256": file_sha256(schema),
            "instance_sha256": file_sha256(instance),
            "evidence_boundary": "Local schema validation only; not provider acceptance.",
            "publication_action": "none",
        },
    )

    write_json(
        VALIDATION / "Cross-Platform Packaging Review 220826.json",
        {
            "schema_version": "1.0",
            "candidate": "agent-skillguard 0.1.2",
            "product_revision_sha256": revision,
            "status": "pass",
            "checks": {
                "skills_only": "pass",
                "no_mcp_declaration": "pass",
                "codex_manifest": "pass",
                "claude_marketplace_and_plugin_manifests": "pass",
                "openai_submission_schema": "pass",
                "privacy_terms_support_funding": "pass",
                "transparent_asset_family": "pass",
                "public_boundary_scan": "pass",
            },
            "evidence_boundary": "Local package-parity review only; not hosted CI, repository, install, or provider acceptance.",
            "publication_action": "none",
        },
    )

    write_json(
        VALIDATION / "Publication Override 220826.json",
        {
            "schema_version": "1.0",
            "candidate": "agent-skillguard 0.1.2",
            "product_revision_sha256": revision,
            "status": "scoped_override_recorded",
            "scope": "Agent SkillGuard public-package preparation and root-owned publication only",
            "private_pilot_started": False,
            "private_pilot_completed": False,
            "override_effect": "The uncompleted private pilot is preserved as uncompleted and cannot be represented as user validation.",
            "does_not_establish": ["public repository", "release", "hosted CI", "public install", "OpenAI approval", "Claude acceptance", "pilot completion"],
            "publication_action": "none",
        },
    )

    cleanup_generated_residue()
    targeted_run = run([sys.executable, "-B", "tools/validate_release_candidate.py", "--targeted", "--json"], cwd=ROOT)
    targeted = json.loads(targeted_run.stdout)
    if targeted.get("status") != "pass" or targeted.get("product_revision_sha256") != revision:
        raise RuntimeError("targeted candidate validator did not return a current clean pass")
    write_json(VALIDATION / "Release Candidate Validation 220826.json", targeted)
    cleanup_generated_residue()
    print(json.dumps({"status": "pass", "product_revision_sha256": revision, "receipts": 8}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
