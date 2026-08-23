# Rule authoring

Skill Risk Check rule packs are strict JSON. Each rule declares a stable ID, semantic version, severity, uncertainty, case-insensitive regular expression, eligible extensions, and bounded remediation.

```json
{
  "id": "ACME001",
  "version": "1.0.0",
  "title": "Example review condition",
  "description": "Describe only the observable pattern.",
  "severity": "medium",
  "uncertainty": "high",
  "pattern": "observable regex",
  "extensions": [".md", ".sh"],
  "remediation": "Give the smallest review or repair step."
}
```

Severity communicates potential impact if the pattern represents real behavior. Uncertainty communicates how much contextual interpretation the match requires. Neither field declares intent.

Every contribution must include:

1. A positive fixture that should match.
2. A nearby negative fixture that must not match.
3. A bounded remediation.
4. A version bump if existing fingerprints or semantics change.

The engine rejects unknown fields, duplicate IDs, invalid regexes, wildcard suppressions, and stale rule-version suppressions.

Custom rule packs are trusted local configuration. SkillGuard validates their shape but does not sandbox their regular expressions or fetch them from the network. Review a custom pack before passing it with `--rules`.
