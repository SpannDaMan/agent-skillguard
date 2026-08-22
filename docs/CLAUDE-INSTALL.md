# Install In Claude Code

Agent SkillGuard ships as a skills-only Claude Code plugin with a local CLI. It does not install an MCP server, request credentials, make network calls, execute the target, install the target, enable the target, or upload the target.

After the repository is public:

```text
/plugin marketplace add SpannDaMan/agent-skillguard
/plugin install agent-skillguard@agent-skillguard
```

Start a new Claude Code session after installation so the current plugin snapshot is loaded.

## Local validation

From the repository root:

```bash
claude plugin validate .
claude plugin marketplace add .
```

The second command is for local testing only. A successful local install does not establish acceptance into Anthropic's official marketplace.

## Optional command-line tool

Installing the repository as a Python package also provides the `skillguard` command:

```bash
python -m pip install .
skillguard --version
```

See [SUPPORT.md](../SUPPORT.md) for the supported boundary.
