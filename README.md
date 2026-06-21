# OpenRouter Skill Overrides

Local OpenRouter skill overrides for Codex and Claude Code.

This repository is the source of truth for user-maintained OpenRouter routing, helper scripts, and decision gates that are not part of the upstream [`OpenRouterTeam/skills`](https://github.com/OpenRouterTeam/skills) project.

It is intentionally not a fork of upstream. Treat upstream OpenRouter skills as a dependency, and treat this repository as the local customization layer installed into each tool runtime.

## What This Project Is

- A shared source tree for local OpenRouter custom skills.
- A safe place to track custom routing rules, model preferences, and helper scripts.
- A bridge between Codex and Claude Code that keeps common OpenRouter logic shared while installing tool-specific files into the correct runtime directory.
- A lightweight installer/sync layer for Windows PowerShell.

## What This Project Is Not

- It is not the upstream `OpenRouterTeam/skills` repository.
- It is not locked to GLM 5.2. GLM 5.2 is the current local default for heavy text, coding, long-context analysis, and second-pass review, but model routing should stay dynamic.
- It is not a replacement for official OpenRouter skills such as `openrouter-models`, `openrouter-generations`, or `openrouter-typescript-sdk`.
- It should not make Codex and Claude Code share runtime directories. They must be installed separately.

## Repository Layout

```text
OpenRouter-Skill-Overrides/
  README.md
  skills/
    openrouter-glm52/
    openrouter-heavy-task-gate/
    openrouter-model-advisor/
    openrouter-flux2-pro/      ← Codex image skill
    flux2pro/                  ← Claude Code image skill
  claude/
    commands/
      glm52.md
      heavy-task-gate.md
  scripts/
    sync.py                    ← cross-platform; use --tool claude|codex
    check.py                   ← cross-platform; use --tool claude|codex
  docs/
    archive/
      claude-glm52-setup-note.md
```

Shared code lives in `skills/`, but not every skill is installed into every runtime. The sync scripts decide what is safe for each tool.

Claude Code slash commands live in `claude/commands/` because Codex does not use Claude Code's command format.

The `scripts/` directory contains separate installers/checks for each runtime. Codex scripts only write to `.codex`. Claude scripts only write to `.claude`.

`skills/openrouter-flux2-pro` is the active Codex image skill. `skills/flux2pro` is the Claude Code compatibility variant with the older Claude skill name `flux2pro`; both use the same current OpenRouter API contract.

## Runtime Separation

Keep these boundaries clear:

| Area | Purpose |
|---|---|
| `C:\vscode\OpenRouter-Skill-Overrides` | Git-tracked source of truth |
| `%USERPROFILE%\.codex\skills` | Active Codex skill runtime |
| `%USERPROFILE%\.claude\skills` | Active Claude Code skill runtime |
| `%USERPROFILE%\.claude\commands` | Active Claude Code slash commands |
| `%USERPROFILE%\.claude\openrouter-skills` | Local upstream OpenRouterTeam/skills clone for Claude Code |

Do not manually edit runtime copies first. Edit this repository, then run the relevant sync script.

## Model Routing Policy

The project should stay model-open.

Current local defaults and preferences:

- Prefer `z-ai/glm-5.2` for heavy coding, long-context repository analysis, architecture review, migration risk review, and difficult debugging when a second pass is useful.
- Use `openrouter-model-advisor` when the model choice matters.
- Use official upstream OpenRouter skills for raw model discovery, generations inspection, TypeScript SDK usage, and other provider-specific workflows.

If a better default model appears later, update `openrouter-model-advisor` notes and gate guidance instead of hard-coding GLM 5.2 everywhere.

Use live OpenRouter model lookup when:

- the task asks for cheapest, fastest, best quality, or current availability
- the task is image, vision, audio, video, or another non-text modality
- a project has a known current model and a switch may be needed
- pricing, context length, provider speed, or supported parameters could affect the decision
- a cheaper specialized model may be enough and GLM 5.2 would be overkill

Avoid noisy model shopping when:

- the task is a small local edit
- the user explicitly selected a model
- the heavy-task gate already approved the normal GLM 5.2 second-pass path
- model choice is unlikely to change the outcome

## Prerequisites

- Python 3.10 or newer available as `python`.
- Git.
- Optional but recommended: GitHub CLI (`gh`) for cloning private repositories.
- `OPENROUTER_API_KEY` set in the local environment for live model calls.

Set the API key for the current session (any shell):

```bash
export OPENROUTER_API_KEY="sk-or-..."   # bash / zsh / macOS / Linux
```

```powershell
$env:OPENROUTER_API_KEY = "sk-or-..."   # PowerShell (Windows)
```

Set it persistently on Windows:

```powershell
[System.Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-...", "User")
```

Never paste the API key into Codex or Claude chat unless you deliberately choose to expose it.

## Install For Codex

Ask Codex to read this README, then run:

```bash
cd /path/to/OpenRouter-Skill-Overrides
python scripts/sync.py --tool codex
python scripts/check.py --tool codex
```

For a minimal live GLM call:

```bash
python scripts/check.py --tool codex --live-glm
```

Expected result:

- syntax checks pass for repo and Codex runtime Python files
- live model-advisor lookup recommends a current OpenRouter model, often `z-ai/glm-5.2` for heavy coding
- optional `--live-glm` returns `OK`

Codex runtime files installed:

```text
~/.codex/skills/openrouter-glm52
~/.codex/skills/openrouter-heavy-task-gate
~/.codex/skills/openrouter-model-advisor
~/.codex/skills/openrouter-flux2-pro
```

## Install For Claude Code

Ask Claude Code to read this README, then run:

```bash
cd /path/to/OpenRouter-Skill-Overrides
python scripts/sync.py --tool claude
python scripts/check.py --tool claude
```

For a minimal live GLM call:

```bash
python scripts/check.py --tool claude --live-glm
```

For a billed live FLUX.2 Pro image call:

```bash
python scripts/check.py --tool claude --live-flux
```

For a billed live GPT-5 Image Mini call:

```bash
python scripts/check.py --tool claude --live-gpt5-image
```

`--live-flux` and `--live-gpt5-image` generate one image each and must only be used when a billed image request is intended.

Claude Code runtime files installed:

```text
~/.claude/skills/openrouter-glm52
~/.claude/skills/openrouter-heavy-task-gate
~/.claude/skills/openrouter-model-advisor
~/.claude/skills/flux2pro
~/.claude/commands/glm52.md
~/.claude/commands/heavy-task-gate.md
```

Claude Code may also keep an upstream clone at `~/.claude/openrouter-skills`. That clone is separate; update it from upstream, not from this repository.

## Updating An Existing Install

From the source checkout:

```bash
cd /path/to/OpenRouter-Skill-Overrides
git pull
python scripts/sync.py --tool codex
python scripts/check.py --tool codex
```

For Claude Code:

```bash
git pull
python scripts/sync.py --tool claude
python scripts/check.py --tool claude
```

Run both sync calls only when the same machine uses both tools.

## Development Workflow

1. Edit files in this repository.
2. Sync and check.
3. Commit and push.

```bash
python scripts/sync.py --tool claude   # or --tool codex
python scripts/check.py --tool claude
git add -p
git commit -m "Describe the change"
git push
```

## Notes On Current Local State

- Codex active skills: `~/.codex/skills/`
- Claude Code active skills: `~/.claude/skills/`
- Claude Code active slash commands: `~/.claude/commands/`
- Claude Code may also have `~/.claude/openrouter-skills/`, a separate upstream OpenRouterTeam/skills clone.

This repository deliberately mirrors only the local custom layer. It does not vendor the full upstream OpenRouter skills tree.

The previous Claude-only setup note is archived at `docs/archive/claude-glm52-setup-note.md`. It is retained as migration context only; use this README for installation.

## Troubleshooting

If `sync.py` fails with a permission error, run it from a shell with appropriate filesystem access.

If `check.py` fails with a network error, verify that your proxy/firewall allows access to:

```text
https://openrouter.ai/api/v1/models
https://openrouter.ai/api/v1/chat/completions
```

If GLM 5.2 returns empty text for a tiny prompt, increase `--max-tokens`. GLM may spend completion tokens on reasoning before normal message content. The local `call_glm52.py` handles `content: null` without printing `None`.

If a chat-based image model (GPT-5 Image, Gemini Flash Image) returns `finish_reason=length`, increase `--max-tokens` above 8192. The script detects this and prints a clear error.
