# Privacy

Agent SkillGuard is a local, skills-only plugin and dependency-free command-line tool.

## Data handling

- It does not send scanned targets, reports, findings, or validation results over the network.
- It does not include telemetry, analytics, advertising, hosted accounts, authentication, or tracking code.
- It does not require API keys or other credentials.
- It reads only the local target path selected by the user and writes output only to the local path selected by the user.

Reports may contain bounded redacted evidence from the scanned artifact. Keep reports local, review them before sharing, and never place credentials or secrets in a scanned fixture.

## Host products

When Agent SkillGuard is installed through Codex, Claude Code, GitHub, or another host, that host's own privacy terms and telemetry settings still apply. Agent SkillGuard does not control or expand them.

## Contact

Use the repository security-reporting path for private security concerns and GitHub Issues for non-sensitive privacy defects. See [SECURITY.md](SECURITY.md) and [SUPPORT.md](SUPPORT.md).
