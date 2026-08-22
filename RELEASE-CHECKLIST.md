# Release checklist

- [ ] Unit and adversarial tests pass.
- [ ] Unsafe fixture produces the expected rule families.
- [ ] Clean fixture produces no active findings.
- [ ] Repeated scan output is byte-for-byte deterministic.
- [ ] JSON, Markdown, and SARIF outputs validate.
- [ ] Exact suppressions and stale-version failures are tested.
- [ ] Fresh wheel installs in an isolated environment with no runtime dependency.
- [ ] Codex plugin metadata validates locally.
- [ ] Claude marketplace and plugin manifests validate locally.
- [ ] OpenAI submission packet validates against its committed schema.
- [ ] Privacy, terms, support, and funding disclosures are present and public-safe.
- [ ] Transparent master and all five derivatives pass alpha and safe-fill QA.
- [ ] Public-boundary scan finds no secrets, workstation paths, or private product names.
- [ ] Current package, evaluation, Codex, Claude, schema, and cross-platform receipts bind to one frozen product revision.
- [ ] One final frozen-candidate full gate passes after all product bytes are frozen.
- [ ] The publication override still states that the private pilot was not completed.
- [ ] Hosted CI, public installation, tags, releases, and provider submissions are separately evidenced if they occur.
