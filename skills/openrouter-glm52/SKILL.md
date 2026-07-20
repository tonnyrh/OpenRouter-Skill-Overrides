---
name: openrouter-glm52
description: Use GLM 5.2 through OpenRouter for heavy coding assistance that is too broad, ambiguous, risky, or long-context for local Ollama. Trigger when the user mentions OpenRouter, GLM 5.2, z-ai/glm-5.2, external model assistance, long-horizon agent work, second-pass review, architecture, migration planning, cross-file refactoring, difficult test failures, or repository-level analysis; also trigger automatically through openrouter-heavy-task-gate when local Ollama is unsuitable. Do not use for routine one-file edits, small tests, regex, documentation wording, or other tasks that ollama-worker can handle locally.
---

# OpenRouter GLM 5.2

Use this skill when GLM 5.2 should assist with heavy coding or analysis through OpenRouter. Keep API keys out of files, logs, commits, and final answers. Do not ask for confirmation merely because OpenRouter is involved when the task is clearly heavy and the API key is already available.

Use `ollama-worker` from `C:\vscode\SharedOllama` first for small bounded edits. Use this skill for broader reasoning, risk review, long-context synthesis, or implementation plans that the primary agent will validate locally.

## Defaults

- Model slug: `z-ai/glm-5.2`
- API base: `https://openrouter.ai/api/v1`
- Auth env var: `OPENROUTER_API_KEY`
- Large code/architecture default: `--reasoning-effort high --max-tokens 8192`
- Best use: long-context repo analysis, project-level software engineering, agentic coding plans, refactor review, complex multi-step automation, and second-pass review after local evidence is gathered.
- Reasoning: prefer `high` for hard engineering tasks; use `xhigh` only when the task justifies extra cost and latency.

## Workflow

1. Confirm the task is not suitable for `ollama-worker`: too much context, cross-file reasoning, architectural judgment, unclear root cause, or risk that benefits from independent review.
2. Check whether `OPENROUTER_API_KEY` is already available in the current shell before calling OpenRouter.
3. If it is missing, ask the user to set it locally; never ask them to paste the key into chat unless they explicitly choose to.
4. Use local project context first. Summarize only the relevant files, errors, tests, diffs, constraints, and decision question for GLM 5.2 instead of sending unnecessary secrets or entire repos.
5. Ask GLM for analysis, risks, plan, or patch guidance. The primary agent performs final edits unless the user explicitly asks for generated patch content.
6. Treat model output as advice. Validate code changes locally with the project's tests, linters, or smoke checks before presenting results.

Ask the user before a call only when sensitive/private context must be sent, a materially more expensive non-default model is required, or the task would perform production/destructive operations.

## Direct Call

Call the script from either the override checkout or the installed runtime copy that matches the host tool.

Run a quick prompt:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 8192 "Review this migration plan for hidden risks: ..."
```

Pipe larger context:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
Get-Content .\notes\architecture.md | python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 8192 --system "You are a senior software architect. Be concise."
```

Use higher reasoning:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 8192 "Find likely bugs in this patch summary: ..."
```

The script also reconfigures `stdout` and `stderr` to UTF-8 internally so Unicode model output does not fail under Windows `cp1252`. Keep the environment line in examples for compatibility with Python launchers and surrounding pipeline commands.

Installed runtime copies may also exist under:

```powershell
$env:USERPROFILE\.codex\skills\openrouter-glm52\
$env:USERPROFILE\.claude\skills\openrouter-glm52\
$env:USERPROFILE\.cursor\skills\openrouter-glm52\
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
