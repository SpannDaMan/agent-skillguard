# Skill Risk Check

Scan before you install.

Use Skill Risk Check before installing an agent skill or plugin. It scans local files for hidden instructions, broad permissions, suspicious downloads, prompt-injection patterns, and possible secret exposure, then returns ranked findings with file-and-line evidence and remediation. It never runs, installs, enables, or uploads the target, and a clean scan is not a safety certification.

Findings are reviewable **potential policy violations**, not verdicts about author intent or artifact safety.

It never executes, imports, installs, enables, or uploads the target.

## Five-minute demo

From the repository root:

```bash
python tools/demo.py
```

The committed unsafe fixture produces findings for remote content piped to a shell, wildcard permissions, possible secret exfiltration, and authority-override language. The demo then scans a clean fixture and proves deterministic output.

Direct CLI use:

```bash
python plugins/agent-skillguard/scripts/skillguard.py scan \
  plugins/agent-skillguard/examples/unsafe-skill \
  --format markdown
```

The expected process exit is `1`: review is required. A scan error exits `2`; no active findings exits `0`.

## What the result means

| Result | Meaning | It does not mean |
|---|---|---|
| No active findings | The configured deterministic rules did not match at or above the selected severity. | The artifact is safe, correct, benign, or approved to install. |
| Review required | One or more patterns deserve human review. | The author is malicious or the matched behavior is necessarily exploitable. |
| Tool error | The scan could not be completed reliably. | The target passed. |

## Outputs

- JSON for local tooling and durable review records.
- Markdown for maintainers.
- SARIF 2.1.0 for code-scanning interfaces.

Every finding includes `rule_id`, `rule_version`, `severity`, `uncertainty`, portable path and line, bounded redacted evidence, remediation, and a SHA-256 fingerprint.

Validate a JSON report locally with `python tools/validate_report.py report.json`. For a copy-paste CI pattern that preserves SARIF before enforcing exit `1`, see [GitHub Actions integration](docs/GITHUB-ACTIONS.md).

## Reviewed suppressions

Create an empty file:

```bash
skillguard init-suppressions --output .skillguard-ignore.json
```

Copy only a reviewed finding's exact `fingerprint`, `rule_id`, and `rule_version`, then add a reason. Wildcards and rule-wide ignores are intentionally unsupported. A rule version change invalidates the old suppression.

```json
{
  "schema_version": "1.0",
  "suppressions": [
    {
      "fingerprint": "<64 lowercase hex characters>",
      "rule_id": "SG006",
      "rule_version": "1.0.0",
      "reason": "Documentation-only example reviewed by the maintainer."
    }
  ]
}
```

## Install from a local checkout

```bash
python -m pip install .
skillguard --version
skillguard scan path/to/skill --format sarif --output findings.sarif
```

Python 3.10 or later is required. Runtime scanning uses only the Python standard library and does not need credentials, network access, or a hosted service.

Eligible text files are limited to 1 MB by default. An eligible file that exceeds the limit, contains binary NUL bytes, or is not valid UTF-8 fails the entire scan with exit `2`; it is never silently skipped into a clean result.

## Versioned Rule Corpus in v0.1.1

- Remote content piped to a shell.
- Broad recursive deletion.
- Wildcard or administrator-like permission requests.
- Possible secret exfiltration instructions.
- Encoded command execution.
- Persistence-sensitive paths and schedulers.
- Unpinned remote VCS installs.
- Authority-override or concealment instructions.

Rules are intentionally inspectable JSON. Contributions should begin with a failing positive fixture, a negative fixture, and bounded remediation copy.

The candidate now includes a public-safe positive/negative fixture corpus and a deterministic verifier:

```bash
python tools/verify_rule_corpus.py --product-revision <candidate-sha256>
python tools/validate_activation_golden.py --suite evals/agent-skillguard-activation-golden.json --product-revision <candidate-sha256>
```

The explicit non-coverage registry names runtime behavior, malware certainty, sandbox proof, remote scanning, certification, and automatic remediation as unsupported claims.

Severity is a policy-triage label, not CVSS and not an exploitability score.

## Limits

Static pattern analysis cannot observe runtime code generation, transitive dependency behavior, compromised build agents, semantic intent, or behavior hidden outside the scanned files. It can miss harmful behavior and flag legitimate documentation. Read [THREAT-MODEL.md](THREAT-MODEL.md) before relying on a scan in a trust decision.

## Codex plugin

The repository is structured as a skills-only Codex plugin marketplace with one plugin at `plugins/agent-skillguard`. It also includes a local CLI. It does not provide an MCP server, hosted service, credentials, telemetry, target execution, target installation, target enablement, or target upload. See [Codex installation](docs/CODEX-INSTALL.md), [Claude Code installation](docs/CLAUDE-INSTALL.md), and the [OpenAI submission packet](docs/OPENAI-PLUGIN-SUBMISSION.md).

## Status

`v0.1.2` is the current public candidate. It preserves the stable `agent-skillguard` package slug while renaming the public product to Skill Risk Check and tightening provider metadata around the pre-install scan, ranked evidence, remediation result, and no-execution/no-certification boundary. A frozen-candidate full gate, fresh rule-corpus receipt, and activation receipt remain required before release. See [PUBLICATION-GATE.md](PUBLICATION-GATE.md), [release evidence](docs/RELEASE-EVIDENCE.md), and [receipts](docs/RECEIPTS.md).

MIT licensed. Developed by Orbral.
