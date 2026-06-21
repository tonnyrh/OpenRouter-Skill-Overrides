---
description: Send a prompt to GLM 5.2 via OpenRouter and return the response. Usage: /glm52 <prompt> or pipe context then add a question.
---

Call GLM 5.2 (`z-ai/glm-5.2`) through OpenRouter using the script at `$env:USERPROFILE\.claude\skills\openrouter-glm52\scripts\call_glm52.py`.

## Steps

1. Take `$ARGUMENTS` as the prompt. If empty, ask the user what they want to ask GLM 5.2.
2. Check that `OPENROUTER_API_KEY` is set:
   ```powershell
   $env:OPENROUTER_API_KEY
   ```
   If it is not set, tell the user to set it locally and stop. Never ask the user to paste the key into chat.
3. Run the script with the prompt. Use `--reasoning-effort high` for engineering or analysis tasks. Use enough `--max-tokens` because GLM 5.2 may spend output tokens on reasoning before normal content:
   ```powershell
   python "$env:USERPROFILE\.claude\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 3000 "$prompt"
   ```
   For larger context:
   ```powershell
   "$context`n$question" | python "$env:USERPROFILE\.claude\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 4000
   ```
4. Display GLM's response verbatim, then add a brief synthesis note if the output needs translation to a concrete next action.
5. Never include the API key, raw HTTP headers, or internal reasoning tokens in your reply.

## When to use higher reasoning

- `--reasoning-effort high`: architecture decisions, bug investigations, refactor plans, migration risks, test failures.
- `--reasoning-effort xhigh`: only when the task is extremely complex and the extra latency and cost are justified.
- `--reasoning-effort low` or omitted: quick factual lookup or short code snippet generation.

## Notes

- GLM 5.2 supports up to 1M token context. Keep prompts focused: summarize files instead of sending whole repositories.
- Treat GLM output as advice. Validate suggested code locally with tests or linters before using it.
- Model slug: `z-ai/glm-5.2`; API base: `https://openrouter.ai/api/v1`.
