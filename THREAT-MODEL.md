# Threat model

## Protected outcome

Give a maintainer a deterministic, inspectable signal before an agent skill or plugin is installed or trusted.

## Trust boundary

The target directory is untrusted data. Skill Risk Check reads eligible bounded UTF-8 files but never imports, executes, sources, installs, enables, or uploads them. Symlinks are not followed. Common dependency and generated directories are excluded. An eligible file that is oversized, contains binary NUL bytes, or is not valid UTF-8 makes the scan fail with tool-error exit `2`; it cannot silently produce a clean result.

## Covered risks

- Review-worthy shell and permission patterns hidden in manifests, skills, docs, and scripts.
- Evidence accidentally echoing common credential shapes.
- Broad or stale suppressions hiding future findings.
- CI ambiguity between a clean scan, an actionable finding, and a tool error.
- Non-portable reports leaking absolute workstation paths.

## Out of scope

- Proving an artifact safe, malicious, correct, or exploitable.
- Runtime code generation, reflection, packed binaries, steganography, or behavior fetched after installation.
- Transitive dependency compromise or registry integrity.
- Compromised interpreters, operating systems, build agents, scanners, or rule packs.
- Resource exhaustion from an untrusted custom regular-expression rule pack; custom packs are trusted local configuration.
- Semantic intent beyond observable deterministic patterns.
- Complete secret detection.

## Expected failures

False positives and false negatives are possible. A reviewed exact-fingerprint suppression reduces repeat noise, but invalidates when the rule version or matched line changes. High-uncertainty findings require more contextual review than low-uncertainty findings.
