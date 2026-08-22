# Security policy

Report vulnerabilities through GitHub Security Advisories at `https://github.com/SpannDaMan/agent-skillguard/security/advisories/new`. Do not include live credentials, private artifacts, or harmful payloads in a public issue.

Agent SkillGuard is intentionally local and dependency-free at runtime. It does not execute scanned files, follow symlinks, make network calls, load credentials, or send telemetry.

Security-sensitive changes require a failing regression test, a threat-model update when the trust boundary changes, and maintainer review. A scan result is evidence for review, not a security certification.
