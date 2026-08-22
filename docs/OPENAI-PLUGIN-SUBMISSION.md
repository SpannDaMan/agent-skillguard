# OpenAI Plugin Submission Packet

Agent SkillGuard is prepared as a skills-only plugin with a local CLI. It has no MCP server, UI, authentication, credentials, network access, telemetry, hosted data storage, target execution, target installation, target enablement, or target upload.

## Local package

- Plugin root: `plugins/agent-skillguard`
- OpenAI/Codex manifest: `plugins/agent-skillguard/.codex-plugin/plugin.json`
- Skill: `plugins/agent-skillguard/skills/agent-skillguard/SKILL.md`
- Local CLI: `plugins/agent-skillguard/scripts/skillguard.py`
- Public submission data: `submission/openai-plugin-submission.json`

## Submission prerequisites

Before any external submission:

1. Run one frozen-candidate full gate and bind every required receipt to the final product revision.
2. Confirm the public website, support, privacy, and terms URLs resolve.
3. Confirm the transparent-master receipt and all derivative asset checks remain passing.
4. Run the five positive and three negative cases in `submission/openai-plugin-submission.json`.
5. Inspect the generated `.codex-plugin/plugin.json` as a skills-only package with no MCP declaration.
6. Submit only through the separately owned provider action.

OpenAI review and directory publication are external actions. A valid local package is not review approval or public availability.
