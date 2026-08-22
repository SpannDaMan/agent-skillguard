---
name: agent-skillguard
description: Scan an agent skill or plugin before installation with a deterministic local Versioned Rule Corpus, explain bounded potential-risk findings, and state explicit non-coverage without certifying safety.
---

# Agent SkillGuard

Use this skill when the user asks whether an agent skill or plugin should be trusted, installed, reviewed, or admitted.

## Non-negotiable boundary

Scanning is read-only. Never execute, source, import, install, or enable the target artifact during review. A clean report is not proof that an artifact is safe, and a finding is not proof of malicious intent.

## Workflow

1. Identify the exact local target and its provenance.
2. Run `skillguard scan <path> --format markdown` before any installation step.
3. Review every active finding at its exact file and line.
4. Separate confirmed behavior, ambiguous behavior, and false positives.
5. If a false positive is accepted, suppress only its exact fingerprint, rule ID, and rule version with a concrete reason.
6. Re-run the scan and report both active and suppressed counts.
7. Stop before installation or permission grants unless the user separately authorized them.
8. When evaluating the scanner itself, require the public positive/negative fixture corpus and non-coverage registry to pass `tools/verify_rule_corpus.py`.

## Exit codes

- `0`: no active findings at or above the selected severity.
- `1`: at least one active finding requires review.
- `2`: the scan could not be completed reliably.

Exit `0` means only that the configured deterministic rules found no active match. It is not a safety certification.
