# OpenRouter Skill Overrides — Cursor Agent Instructions

This repository contains Cursor/Codex-compatible OpenRouter skill overrides and helper scripts.
The canonical skill implementations live under `skills/`.

## Primary routing

- Use `ollama-worker` from `C:\vscode\SharedOllama` first for bounded local coding edits when that worker is available.
- Use `openrouter-heavy-task-gate` to decide whether work should stay on local Ollama or go to OpenRouter.
- Use `openrouter-glm52` for heavy coding analysis, long-context repository work, and second-pass review.
- Use `openrouter-model-advisor` only when model choice is non-obvious or cost/quality tradeoffs matter.
- Use `openrouter-pdf-extract` for native PDF extraction tasks.
- Use `openrouter-flux2-pro` for FLUX.2 Pro image generation and editing.
- Treat `flux2pro` as the legacy multi-model image skill and prefer `openrouter-flux2-pro` unless the legacy presets are specifically needed.

## Cursor support

- Project rule: `.cursor/rules/agent-routing.mdc`
- Cursor-discoverable skill wrappers: `.cursor/skills/*`
- Canonical skill implementations remain in `skills/*`
- Local `ollama-worker` lives in `C:\vscode\SharedOllama`, not in this repository
- Personal install (all workspaces): `python scripts/sync.py --tool cursor`

Open `C:\vscode\OpenRouter-Skill-Overrides` in Cursor for project-local routing, or sync
skills into `%USERPROFILE%\.cursor\skills\` for cross-project use.

## Operating rules

- Keep secrets out of prompts, files, logs, and commits.
- Prefer minimal relevant context in OpenRouter prompts.
- Treat model output as advice and validate locally before presenting results.
- Avoid asking the user for confirmation unless credentials, sensitive context, destructive actions, or material cost/model changes require it.

