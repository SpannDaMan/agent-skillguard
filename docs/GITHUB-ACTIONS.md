# GitHub Actions integration

This example is documentation for a future public or private repository. It is not deployed by the private candidate.

The scanner's exit `1` means “review required,” so preserve the SARIF artifact before failing the job. Exit `2` is a tool error and must never be converted to a pass.

```yaml
permissions:
  contents: read
  security-events: write

steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: '3.12'
  - run: python -m pip install .
  - name: Scan agent artifacts
    id: skillguard
    shell: bash
    run: |
      set +e
      skillguard scan ./skills --format sarif --output skillguard.sarif
      code=$?
      echo "exit_code=$code" >> "$GITHUB_OUTPUT"
      if [ "$code" -eq 2 ]; then exit 2; fi
      exit 0
  - uses: github/codeql-action/upload-sarif@v3
    with:
      sarif_file: skillguard.sarif
  - name: Enforce review result
    shell: bash
    run: test "${{ steps.skillguard.outputs.exit_code }}" -eq 0
```

Use `permissions: contents: read` unless SARIF upload is enabled. The upload step requires only `security-events: write`; it does not require repository administration, credential access, or wildcard permissions.
