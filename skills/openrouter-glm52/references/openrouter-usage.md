# OpenRouter Usage

## Official Skills

The upstream skills repository is `OpenRouterTeam/skills`.

Install all OpenRouter skills globally for Codex or Claude Code:

```powershell
gh skill install OpenRouterTeam/skills --agent codex --scope user
gh skill install OpenRouterTeam/skills --agent claude --scope user
```

Install specific upstream skills globally:

```powershell
gh skill install OpenRouterTeam/skills openrouter-typescript-sdk --agent codex --scope user
gh skill install OpenRouterTeam/skills openrouter-models --agent codex --scope user
gh skill install OpenRouterTeam/skills openrouter-generations --agent codex --scope user
gh skill install OpenRouterTeam/skills openrouter-typescript-sdk --agent claude --scope user
gh skill install OpenRouterTeam/skills openrouter-models --agent claude --scope user
gh skill install OpenRouterTeam/skills openrouter-generations --agent claude --scope user
```

Use exact paths for faster installs from large repositories:

```powershell
gh skill install OpenRouterTeam/skills skills/openrouter-typescript-sdk --agent codex --scope user
```

## GLM 5.2 Facts

- OpenRouter model slug: `z-ai/glm-5.2`
- Supports text input and output.
- Advertised context window: 1M tokens.
- Released on OpenRouter: 2026-06-16.
- Listed use cases include long-horizon agent workflows, project-level software engineering, and complex multi-step automation.
- Reasoning efforts `high` and `xhigh` are supported; `xhigh` maps to maximum reasoning.
- OpenRouter's API is OpenAI-compatible; most OpenAI SDKs can be reused by changing the base URL and model.

## Minimal Python SDK Pattern

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

response = client.chat.completions.create(
    model="z-ai/glm-5.2",
    messages=[{"role": "user", "content": "Review this patch."}],
    extra_body={"reasoning": {"effort": "high"}},
)

print(response.choices[0].message.content)
```

## Minimal HTTP Pattern

```http
POST https://openrouter.ai/api/v1/chat/completions
Authorization: Bearer ${OPENROUTER_API_KEY}
Content-Type: application/json

{
  "model": "z-ai/glm-5.2",
  "messages": [{"role": "user", "content": "Review this plan."}],
  "reasoning": {"effort": "high"}
}
```
