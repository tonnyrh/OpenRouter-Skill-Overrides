---
description: Decide whether the current task is heavy enough to benefit from a GLM 5.2 second pass, then ask before calling OpenRouter.
---

Use this command as a decision gate before spending OpenRouter credits or sending project context to GLM 5.2.

## Gate Rule

When `$ARGUMENTS` describes a task, or the current conversation task looks heavy, evaluate it against the criteria below. If it qualifies, pause and ask:

> This task is heavy enough that GLM 5.2 may be useful as a second pass. Should I run `/glm52` on focused context before implementing?

Proceed based on the answer:

- **Yes**: collect minimal relevant context, including relevant diffs, errors, file summaries, and constraints, then run `/glm52` with a focused question. Do not send entire repositories or secrets.
- **No**: continue with normal local analysis and implementation.
- **Urgent, destructive, production-facing, or security-sensitive task**: still ask before calling GLM unless the user explicitly requested OpenRouter in the same turn.

Keep the default path quiet: for ordinary heavy coding work, GLM 5.2 is the local default and no separate model-shopping step is needed after the user approves OpenRouter.

Use `openrouter-model-advisor` before the model call only when the model choice matters:

- the task is image, vision, audio, video, or another non-text modality
- the user asks for cheapest, fastest, best quality, or a model comparison
- a project already has a known current model and a switch may be needed
- live price, availability, context length, provider speed, or supported parameters could change the decision
- a cheaper specialized model may be enough and GLM 5.2 would be overkill

## What Counts as Heavy

Ask before using GLM 5.2 for:

- architecture decisions, migration plans, or large design changes
- refactors spanning multiple modules, services, or repositories
- difficult bugs where local evidence is unclear or contradictory
- CI/test failures with multiple possible root causes
- production, deployment, database, auth, security, or data-loss risk
- performance, concurrency, caching, or distributed-system investigations
- any task where a second independent review could catch hidden risks

Do not ask for routine edits, small bug fixes, simple tests, formatting, documentation wording, or narrow single-file changes unless the user explicitly asks for a second pass.

## Preparing the GLM Prompt

When the user approves:

1. State the specific question you want GLM to answer.
2. Include only the minimum relevant context.
3. Strip secrets, credentials, and unrelated code.
4. Pass to `/glm52`, or call the script directly:
   ```powershell
   python "$env:USERPROFILE\.claude\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 3000 "$focusedPrompt"
   ```
5. Treat GLM output as advice. Validate locally before implementing.
6. If `openrouter-model-advisor` recommends a premium model or a project model switch, ask one concise follow-up before spending credits unless the user already explicitly approved that exact model.
