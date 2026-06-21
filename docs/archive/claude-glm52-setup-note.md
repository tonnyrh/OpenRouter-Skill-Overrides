# Historical Claude GLM 5.2 Setup Note

This file replaces the old `Claude-openrouter-glm52-ReadMe.md`.

The old document was useful during the first Claude Code-only setup, but it is no longer the install guide for this repository. It had several assumptions that are now outdated:

- the project was Claude-only
- GLM 5.2 was described as the central model rather than the current text/coding default
- Claude slash commands lived in top-level `commands/`
- custom files were copied manually into `.claude`

The current source of truth is the repository root [`README.md`](../../README.md).

Current direction:

- shared OpenRouter custom skills live in `skills/`
- Claude Code slash commands live in `claude/commands/`
- Codex is installed with `scripts/sync-codex.ps1`
- Claude Code is installed with `scripts/sync-claude.ps1`
- model routing remains dynamic through `openrouter-model-advisor`
- GLM 5.2 is a default/preference for heavy text and coding second-pass work, not a permanent lock-in

Keep this note only as migration context. Do not use it as an installation procedure.
