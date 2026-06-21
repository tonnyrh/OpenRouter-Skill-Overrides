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
    flux2pro/
  claude/
    commands/
      glm52.md
      heavy-task-gate.md
  scripts/
    sync-codex.ps1
    check-codex.ps1
    sync-claude.ps1
    check-claude.ps1
```

Shared code lives in `skills/`, but not every skill is installed into every runtime. The sync scripts decide what is safe for each tool.

Claude Code slash commands live in `claude/commands/` because Codex does not use Claude Code's command format.

The `scripts/` directory contains separate installers/checks for each runtime. Codex scripts only write to `.codex`. Claude scripts only write to `.claude`.

`skills/flux2pro` is a legacy Claude Code image-generation helper with the Claude skill name `flux2pro`. It is installed by `sync-claude.ps1` only. Codex has a separate active skill named `openrouter-flux2-pro`, so `sync-codex.ps1` deliberately does not install `flux2pro`.

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

- Windows PowerShell 7 or Windows PowerShell 5.1.
- Python 3.10 or newer available as `python`.
- Git.
- Optional but recommended: GitHub CLI (`gh`) for cloning private repositories.
- `OPENROUTER_API_KEY` set in the local environment for live model calls.

Set the API key for the current PowerShell session:

```powershell
$env:OPENROUTER_API_KEY = "sk-or-..."
```

Set it persistently for the Windows user:

```powershell
[System.Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-...", "User")
```

Never paste the API key into Codex or Claude chat unless you deliberately choose to expose it.

## Install For Codex

Ask Codex to read this README, then run:

```powershell
cd C:\vscode
git clone https://github.com/tonnyrh/OpenRouter-Skill-Overrides.git
cd C:\vscode\OpenRouter-Skill-Overrides
.\scripts\sync-codex.ps1
.\scripts\check-codex.ps1
```

For a minimal live GLM call:

```powershell
.\scripts\check-codex.ps1 -LiveGlm
```

Expected result:

- syntax checks pass for repo and Codex runtime Python files
- live model-advisor lookup recommends a current OpenRouter model, often `z-ai/glm-5.2` for heavy coding
- optional `-LiveGlm` returns `OK`

Codex runtime files installed:

```text
%USERPROFILE%\.codex\skills\openrouter-glm52
%USERPROFILE%\.codex\skills\openrouter-heavy-task-gate
%USERPROFILE%\.codex\skills\openrouter-model-advisor
```

## Install For Claude Code

Ask Claude Code to read this README, then run:

```powershell
cd C:\vscode
git clone https://github.com/tonnyrh/OpenRouter-Skill-Overrides.git
cd C:\vscode\OpenRouter-Skill-Overrides
.\scripts\sync-claude.ps1
.\scripts\check-claude.ps1
```

For a minimal live GLM call:

```powershell
.\scripts\check-claude.ps1 -LiveGlm
```

Claude Code runtime files installed:

```text
%USERPROFILE%\.claude\skills\openrouter-glm52
%USERPROFILE%\.claude\skills\openrouter-heavy-task-gate
%USERPROFILE%\.claude\skills\openrouter-model-advisor
%USERPROFILE%\.claude\skills\flux2pro
%USERPROFILE%\.claude\commands\glm52.md
%USERPROFILE%\.claude\commands\heavy-task-gate.md
```

Claude Code may also keep an upstream clone at:

```text
%USERPROFILE%\.claude\openrouter-skills
```

That upstream clone is separate. Update it from upstream, not from this repository.

## Updating An Existing Install

From the source checkout:

```powershell
cd C:\vscode\OpenRouter-Skill-Overrides
git pull
.\scripts\sync-codex.ps1
.\scripts\check-codex.ps1
```

For Claude Code:

```powershell
cd C:\vscode\OpenRouter-Skill-Overrides
git pull
.\scripts\sync-claude.ps1
.\scripts\check-claude.ps1
```

Run both sync scripts only when the same machine uses both tools.

## Development Workflow

1. Edit files in this repository.
2. Run the relevant sync script.
3. Run the relevant check script.
4. Commit and push.

Codex:

```powershell
.\scripts\sync-codex.ps1
.\scripts\check-codex.ps1
git status
git add .
git commit -m "Describe the OpenRouter override change"
git push
```

Claude Code:

```powershell
.\scripts\sync-claude.ps1
.\scripts\check-claude.ps1
git status
git add .
git commit -m "Describe the Claude OpenRouter override change"
git push
```

## Notes On Current Local State

Observed on this Windows machine:

- Codex active skills live under `%USERPROFILE%\.codex\skills`.
- Claude Code active skills live under `%USERPROFILE%\.claude\skills`.
- Claude Code active slash commands live under `%USERPROFILE%\.claude\commands`.
- Claude Code also has `%USERPROFILE%\.claude\openrouter-skills`, a separate upstream OpenRouterTeam/skills clone.

This repository deliberately mirrors only the local custom layer. It does not vendor the full upstream OpenRouter skills tree.

## Troubleshooting

If `sync-*.ps1` fails with access denied, run it from Codex/Claude with filesystem approval or from a normal PowerShell session.

If `check-*.ps1` fails with a network error, rerun it with network approval or verify that local proxy/firewall settings allow access to:

```text
https://openrouter.ai/api/v1/models
https://openrouter.ai/api/v1/chat/completions
```

If GLM 5.2 returns empty text for a tiny prompt, increase `--max-tokens`. GLM may spend completion tokens on reasoning before normal message content. The local `call_glm52.py` handles `content: null` without printing `None`.
