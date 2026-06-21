---
name: openrouter-glm52
description: Use GLM 5.2 through OpenRouter for long-context coding, repository analysis, planning, refactoring assistance, multi-step automation, and comparison with the active Codex model. Trigger when the user mentions OpenRouter, GLM 5.2, z-ai/glm-5.2, external model assistance, long-horizon agent work, or wants to ask another model for a second pass on code or architecture.
---

# OpenRouter GLM 5.2

Use this skill when GLM 5.2 should assist with coding or analysis through OpenRouter. Keep API keys out of files, logs, commits, and final answers.

## Defaults

- Model slug: `z-ai/glm-5.2`
- API base: `https://openrouter.ai/api/v1`
- Auth env var: `OPENROUTER_API_KEY`
- Best use: long-context repo analysis, project-level software engineering, agentic coding plans, refactor review, and complex multi-step automation.
- Reasoning: prefer `high` for hard engineering tasks; use `xhigh` only when the task justifies extra cost and latency.

## Workflow

1. Check whether `OPENROUTER_API_KEY` is already available in the current shell before calling OpenRouter.
2. If it is missing, ask the user to set it locally; never ask them to paste the key into chat unless they explicitly choose to.
3. Use local project context first. Summarize only the relevant files, errors, tests, and constraints for GLM 5.2 instead of sending unnecessary secrets or entire repos.
4. For direct calls, use `scripts/call_glm52.py` or the project's existing OpenAI-compatible SDK setup with `base_url=https://openrouter.ai/api/v1`.
5. Treat model output as advice. Validate code changes locally with the project's tests, linters, or smoke checks before presenting results.

## Direct Call

Run a quick prompt:

```powershell
python "$env:USERPROFILE\.codex\skills\openrouter-glm52\scripts\call_glm52.py" "Review this migration plan for hidden risks: ..."
```

Pipe larger context:

```powershell
Get-Content .\notes\architecture.md | python "$env:USERPROFILE\.codex\skills\openrouter-glm52\scripts\call_glm52.py" --system "You are a senior software architect. Be concise."
```

Use higher reasoning:

```powershell
python "$env:USERPROFILE\.codex\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high "Find likely bugs in this patch summary: ..."
```

## Project Integration

When adding OpenRouter to a codebase:

- Prefer the project's existing OpenAI-compatible client if present.
- Set only the base URL, model slug, and API key env var; avoid introducing a new SDK unless the repo needs OpenRouter-specific features.
- Use `.env.example` or existing configuration docs for variable names, but never write the real key.
- Keep request metadata optional: `HTTP-Referer` and `X-Title` are useful for OpenRouter dashboards but should not be required for local tests.
- For TypeScript SDK, model lookup, analytics, image, TTS, STT, and video work, install or consult the official OpenRouter skills from `OpenRouterTeam/skills`.

## References

Read `references/openrouter-usage.md` when you need install commands for the official OpenRouter skills, model facts, or API examples.
