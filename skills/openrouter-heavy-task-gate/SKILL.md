---
name: openrouter-heavy-task-gate
description: Ask the user before using GLM 5.2 through OpenRouter on heavy coding work. Use when working in local projects under C:\vscode or similar repositories and the task is large, risky, architectural, cross-file, cross-service, production-impacting, hard to debug, involves major refactoring, migration planning, complex test failures, security-sensitive changes, performance investigations, or would benefit from a second model review. Trigger even when the user does not explicitly mention OpenRouter or GLM 5.2.
---

# OpenRouter Heavy Task Gate

Use this skill as a decision gate before spending OpenRouter credits or sending project context to GLM 5.2.

## Gate Rule

When the task looks heavy, pause before calling OpenRouter and ask one concise question:

`Denne oppgaven er tung nok til at GLM 5.2 kan være nyttig som second pass. Vil du at jeg kjører OpenRouter-skillen på relevant kontekst før jeg implementerer?`

Proceed based on the user's answer:

- If yes, use `openrouter-glm52` with a focused prompt containing only relevant repo context, errors, diffs, constraints, and the specific question GLM should answer.
- If no, continue with normal local analysis and implementation.
- If the request is urgent, destructive, production-facing, or security-sensitive, still ask before GLM unless the user explicitly requested OpenRouter/GLM in the same turn.

Keep the default path quiet: for ordinary heavy coding work, GLM 5.2 is the local default and no separate model-shopping step is needed after the user approves OpenRouter.

Use `openrouter-model-advisor` before the model call only when the model choice matters:

- the task is image, vision, audio, video, or another non-text modality
- the user asks for cheapest, fastest, best quality, or a model comparison
- a project already has a known current model and a switch may be needed
- live price, availability, context length, provider speed, or supported parameters could change the decision
- a cheaper specialized model may be enough and GLM 5.2 would be overkill

## What Counts As Heavy

Ask before using GLM 5.2 for:

- architecture decisions, migration plans, or large design changes
- refactors spanning multiple modules, services, or repositories
- difficult bugs after local evidence is unclear
- CI/test failures with multiple possible root causes
- production, deploy, database, auth, security, or data-loss risk
- performance, concurrency, caching, or distributed-system investigations
- tasks where a second independent review could catch hidden risks

Do not ask for routine edits, small bug fixes, simple tests, formatting, command output, documentation wording, or narrow single-file changes unless the user asks for a second pass.

## OpenRouter Use

Before calling OpenRouter:

1. Check `OPENROUTER_API_KEY` is set.
2. Keep secrets out of prompts, logs, files, commits, and final answers.
3. Summarize only the minimum relevant context instead of sending entire files or repositories.
4. Prefer `--reasoning-effort high` for hard engineering analysis and enough `--max-tokens` for final content, since GLM may spend tokens on reasoning before message content.
5. Treat GLM output as advice. Validate any implementation locally with tests, linters, or smoke checks.
6. If `openrouter-model-advisor` recommends a premium model or a project model switch, ask one concise follow-up before spending credits unless the user already explicitly approved that exact model.

## Sandbox Notes

The expected approved command for GLM calls is:

```powershell
python "C:\Users\TonnyRogerHolm(Test)\.codex\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 2000 "..."
```

If sandbox blocks network access, request escalation for that exact script command instead of working around it. For model lookup scripts from `openrouter-models`, `npx tsx ...` may need escalation because `tsx` starts an `esbuild` child process.
