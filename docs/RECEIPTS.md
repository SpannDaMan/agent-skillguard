# Receipts

Receipts provide bounded local evidence; they are not release authorization.

## Required receipt fields

- `product_revision_sha256`: the exact non-self-referential candidate digest.
- `status`: `pass`, `incomplete`, or another explicit non-passing state.
- `publication_action`: always `none` for local evidence.
- `command`, `exit_code`, and tool identity when a local validator ran.
- `evidence_boundary`: what the receipt establishes and what it does not establish.

## Current versus historical evidence

Only receipts dated for the frozen candidate can support a release claim. Historical evidence may be retained outside the public candidate for context, but it cannot be relabeled as current or used to pass the frozen-candidate gate.

The scoped private-pilot override records that no 30-day private pilot was completed. It does not establish user validation, external approval, hosted CI, repository release, or provider acceptance.

## Privacy

Do not store credentials, private conversations, container identifiers, workstation paths, unpublished route details, or unredacted target contents in public receipts. Use hashes, relative paths, exit codes, and bounded summaries instead.
