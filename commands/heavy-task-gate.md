---
description: Decision gate — evaluate whether the current task is heavy enough to benefit from a GLM 5.2 second pass, then ask the user before calling OpenRouter. Use proactively when a task looks large, risky, or architectural.
---

Use this command as a decision gate before spending OpenRouter credits or sending project context to GLM 5.2.

## Gate Rule

When `$ARGUMENTS` describes a task (or the current conversation task looks heavy), evaluate it against the criteria below. If it qualifies, pause and ask:

> Denne oppgaven er tung nok til at GLM 5.2 kan være nyttig som second pass. Vil du at jeg kjører /glm52 på relevant kontekst før jeg implementerer?

Proceed based on the answer:
- **Ja / Yes** — collect minimal relevant context (relevant diffs, errors, file summaries, constraints) and run `/glm52` with a focused question for GLM to answer. Do not send entire repos or secrets.
- **Nei / No** — continue with normal local analysis and implementation.
- **Urgent or destructive task** — still ask before calling GLM unless the user explicitly requested OpenRouter in the same turn.

## What Counts as Heavy

Ask before using GLM 5.2 for:
- Architecture decisions, migration plans, or large design changes
- Refactors spanning multiple modules, services, or repositories
- Difficult bugs where local evidence is unclear or contradictory
- CI/test failures with multiple possible root causes
- Tasks touching production, deployment, databases, auth, security, or data-loss risk
- Performance, concurrency, caching, or distributed-system investigations
- Any task where a second independent review could catch hidden risks

Do **not** ask for: routine edits, small bug fixes, simple tests, formatting, documentation wording, or narrow single-file changes — unless the user explicitly asks for a second pass.

## Preparing the GLM Prompt

When the user approves, build a focused prompt:
1. State the specific question you want GLM to answer (not an open-ended "review everything").
2. Include only the minimum context: relevant file snippets, diffs, error messages, constraints.
3. Strip secrets, credentials, and unrelated code.
4. Pass to `/glm52` or call the script directly:
   ```powershell
   python "C:\Users\TonnyRogerHolm(Test)\.claude\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 3000 "$focusedPrompt"
   ```
5. Treat GLM output as advice. Validate locally before implementing.
