# 30-day private maintainer pilot (not completed)

Owner: SpannDaMan

The pilot was not started and was not completed. If run later, it starts only when the owner records a start date and includes no more than five invited maintainers. It is a bounded learning exercise, not a publication prerequisite under the scoped override recorded in `validation/Publication Override 220826.json`.

## Cadence

- Triage the pilot feedback record twice each week.
- Record setup minutes, scan latency, findings reviewed, confirmed useful findings, suppressed false positives, missed fixture expectations, and support minutes.
- Apply change control: every behavior change needs a test, changelog entry, and fresh release receipt.

## Targets

- Every committed malicious-pattern fixture produces at least one active finding.
- Reviewed false-positive suppressions stay at or below 10% of all findings in the bounded pilot sample.
- Median scan time stays below two seconds for a single skill under 1,000 eligible files.
- At least four of five invited maintainers can add the scanner to a local or private CI workflow without live support.

These are pilot targets, not current adoption or accuracy claims.

## Stop conditions

Pause the pilot for target execution, secret disclosure, symlink escape, output overwrite, a known critical fixture that scans clean, repeated exit-code ambiguity, or any open P0-P2 review finding.

## Day-30 decision

Choose one: hold, repair and extend the pilot, archive the candidate, or request a separate publication decision. The pilot itself never authorizes publication.
