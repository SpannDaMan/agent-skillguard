# Release Evidence Contract

Agent SkillGuard binds release evidence to a non-self-referential product revision.

## Product revision digest

The product file set is every regular candidate file except:

- files below `validation/`;
- `.git/`, build, cache, bytecode, and packaging-residue paths;
- symlinks, which are forbidden by the release validator.

For each included file, sort by POSIX-style relative path and append this UTF-8 record:

```text
relative_path<TAB>byte_count<TAB>file_sha256<LF>
```

The SHA-256 of the complete record sequence is `product_revision_sha256`. Generated receipts live below `validation/`, so writing a receipt does not change the product revision it attests.

## Required binding

Evaluation, package, Codex-plugin, Claude-plugin, JSON-schema, cross-platform, override, and composite receipts must name the exact current `product_revision_sha256`. The composite release validator recomputes the digest and rejects missing, stale, conflicting, or private-route receipts.

This binding identifies which product bytes a receipt names. It does not prove semantic equivalence, security, hosted behavior, adoption, marketplace acceptance, or market demand.
