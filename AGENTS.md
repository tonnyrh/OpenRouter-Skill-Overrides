# OpenRouter Skill Overrides — Cursor Agent Instructions

This repository contains Cursor/Codex-compatible OpenRouter skill overrides and helper scripts.
The canonical skill implementations live under `skills/`.

## Primary routing

- Use `ollama-worker` first for bounded local coding edits: one file, one function, tests, regex, FILE_OP patches, and small scripts.
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

## Operating rules

- Keep secrets out of prompts, files, logs, and commits.
- Prefer minimal relevant context in OpenRouter prompts.
- Treat model output as advice and validate locally before presenting results.
- Avoid asking the user for confirmation unless credentials, sensitive context, destructive actions, or material cost/model changes require it.

