# Install In Codex

Skill Risk Check is a skills-only Codex plugin with a local CLI. It does not install an MCP server, request credentials, make network calls, execute the target, install the target, enable the target, or upload the target.

Validate a local checkout:

```bash
python -m pip install .
skillguard --version
python tools/demo.py
python -m unittest discover -s tests -v
```

After the repository is public, the Codex plugin flow is:

```bash
codex plugin marketplace add SpannDaMan/agent-skillguard
codex plugin add agent-skillguard@agent-skillguard
```

Run a new Codex session after installation so the current plugin snapshot is loaded. A local package pass does not establish hosted installability, directory acceptance, or public availability.
