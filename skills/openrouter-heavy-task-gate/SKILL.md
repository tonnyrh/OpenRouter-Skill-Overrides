---
name: openrouter-heavy-task-gate
description: "Route coding work between local ollama-worker and GLM 5.2 through OpenRouter with minimal user interruption. Use when working in local projects under C:\\vscode or similar repositories and the task is large, risky, architectural, cross-file, cross-service, hard to debug, involves major refactoring, migration planning, complex test failures, performance investigations, or would benefit from a second model review. Prefer automatic routing: ollama-worker for small bounded edits, OpenRouter/GLM for heavy analysis. Ask the user only for missing credentials, materially higher-cost model choices, production/destructive actions, unclear requirements that block progress, or sending sensitive/private context."
---

# OpenRouter Heavy Task Gate

Use this skill as a quiet router for long sprints. Prefer progress over confirmation loops. The routing order is:

1. The primary agent handles orchestration, context selection, final edits, and validation.
2. `ollama-worker` from `C:\vscode\SharedOllama` handles small bounded code edits and FILE_OP patches.
3. OpenRouter/GLM handles large context, architecture, ambiguous failures, and second-pass review.

## Routing Rule

When the task looks heavy, route to GLM 5.2 without asking if all of these are true:

- `OPENROUTER_API_KEY` is already set.
- The prompt can exclude secrets, credentials, private customer data, and irrelevant files.
- The default `z-ai/glm-5.2` model is suitable.
- The action is analysis, planning, risk review, or patch guidance, not a production/destructive operation.

Ask one concise question only when an exception applies:

- Missing `OPENROUTER_API_KEY`: ask the user to set it locally.
- Sensitive context is required: ask before sending that context outside the machine.
- A premium/non-default model or existing project model switch is recommended.
- The operation is production-facing, destructive, security-sensitive, or could expose secrets.
- Requirements are ambiguous enough that model routing cannot fix the uncertainty.

If the task can be split into local worker units, use `ollama-worker` for those units and use GLM only for the remaining broad question.

Keep the default path quiet: for ordinary heavy coding work, GLM 5.2 is the cloud default and no separate model-shopping step is needed.

Use `openrouter-model-advisor` before the model call only when the model choice matters:

- the task is image, vision, audio, video, or another non-text modality
- the user asks for cheapest, fastest, best quality, or a model comparison
- a project already has a known current model and a switch may be needed
- live price, availability, context length, provider speed, or supported parameters could change the decision
- a cheaper specialized model may be enough and GLM 5.2 would be overkill

## What Counts As Heavy

Use GLM 5.2 for:

- architecture decisions, migration plans, or large design changes
- refactors spanning multiple modules, services, or repositories
- difficult bugs after local evidence is unclear
- CI/test failures with multiple possible root causes
- production, deploy, database, auth, security, or data-loss risk
- performance, concurrency, caching, or distributed-system investigations
- tasks where a second independent review could catch hidden risks

Do not use GLM for routine edits, small bug fixes, simple tests, formatting, command output, documentation wording, or narrow single-file changes unless the user asks for a second pass.

Use `ollama-worker` instead for:

- one function, method, component, or test file
- targeted replacement with exact context
- small generated scripts
- regex or documentation edits
- local FILE_OP patch generation where the primary agent can review the diff

## Local worker path

Use the canonical local worker from SharedOllama:

```powershell
$worker = "C:\vscode\SharedOllama\skills\ollama-worker"
python "$worker\scripts\call_ollama.py" --list
```

## OpenRouter Use

Before calling OpenRouter:

1. Check `OPENROUTER_API_KEY` is set.
2. Keep secrets out of prompts, logs, files, commits, and final answers.
3. Summarize only the minimum relevant context instead of sending entire files or repositories.
4. Prefer `--reasoning-effort high` for hard engineering analysis and use `--max-tokens 8192` (or higher for long outputs) so reasoning cannot consume the entire response budget, since GLM may spend tokens on reasoning before message content.
5. Treat GLM output as advice. Validate any implementation locally with tests, linters, or smoke checks.
6. If `openrouter-model-advisor` recommends a premium model or a project model switch, ask only when the cost or behavior change is material; otherwise continue and note the choice in the final summary.

## Sandbox Notes

The expected command for this override checkout is:

```powershell
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 8192 "..."
```

An installed runtime path may also be available, for example:

```powershell
python "C:\Users\TonnyRogerHolm(Test)\.codex\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 8192 "..."
python "C:\Users\TonnyRogerHolm(Test)\.claude\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 8192 "..."
```

If sandbox blocks network access, request escalation for that exact script command instead of working around it. For model lookup scripts from `openrouter-models`, `npx tsx ...` may need escalation because `tsx` starts an `esbuild` child process.

