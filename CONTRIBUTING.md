# Contributing

Contributions are welcome through GitHub Issues and pull requests after the repository is published. Before opening a change, read the threat model and confirm that the change preserves local-only scanning, no target execution, no target installation, no target enablement, no upload, no network access, and the `0/1/2` exit-code contract.

For a rule change, start with a failing positive fixture and a nearby negative fixture. For an engine change, preserve deterministic output, portable paths, no target execution, no network access, and the `0/1/2` exit-code contract.

Run:

```bash
python -m unittest discover -s tests -v
python tools/demo.py
python tools/validate_release_candidate.py --targeted --json
```

Do not add a dependency without documenting why the standard library cannot meet the requirement and how the new supply-chain risk is controlled.
