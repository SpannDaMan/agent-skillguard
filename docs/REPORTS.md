# Report contract

JSON reports use schema version `1.0`. The report is deterministic for the same files, rules, suppression file, and severity threshold. It omits timestamps and absolute paths.

The scan digest hashes the ordered list of portable relative paths and SHA-256 values over the exact raw file bytes read for the scan. CRLF and LF therefore produce different digests. It is a change detector, not a signature or provenance proof, and it does not make the directory a stable snapshot if another process edits files during a scan.

Every finding carries:

- stable rule ID and rule version;
- severity and uncertainty;
- portable path, line, and column;
- bounded evidence with common credential shapes redacted;
- remediation;
- exact-finding fingerprint;
- suppression state and reviewed reason.

SARIF output includes only active findings in `results`; suppressions remain visible in the JSON and Markdown report. This prevents a suppressed finding from appearing as a new CI alert while preserving its audit trail in the native report.

Validate a native JSON report without a third-party dependency:

```bash
skillguard scan ./skill --format json --output report.json
python tools/validate_report.py report.json
```

The committed JSON Schema supports external tooling. The standard-library validator is the executable contract used by this candidate; it does not claim to be a general JSON Schema Draft 2020-12 implementation.

SkillGuard severity is a policy-triage label for the potential impact of an observed pattern. It is not CVSS, does not measure exploitability, and must not be converted to a vulnerability score without a separate vulnerability analysis.
