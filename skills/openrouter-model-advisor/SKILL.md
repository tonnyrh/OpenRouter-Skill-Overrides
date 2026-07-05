---
name: openrouter-model-advisor
description: Recommend the best OpenRouter model or model family when a cloud model choice actually matters. Use when choosing between OpenRouter models, changing a project model, selecting image/text/coding/vision/reasoning models, estimating lowest-cost acceptable models, checking live pricing/capabilities, or deciding whether a premium model is worth asking the user about before spending credits. Do not use for routine local coding edits that ollama-worker can handle or when GLM 5.2 is already the explicit approved default.
---

# OpenRouter Model Advisor

Use this skill before spending OpenRouter credits when the model choice matters. The goal is smooth routing: take obvious low-risk choices without ceremony, and ask the user only before a materially more expensive quality choice or a model switch that changes existing project behavior.

For coding work, prefer the routing ladder first: `ollama-worker` for small bounded edits, `openrouter-heavy-task-gate` for heavy work, then this advisor only when the OpenRouter model choice is non-obvious.

## Decision Policy

- Use live OpenRouter data for model IDs, pricing, modalities, context, supported parameters, and availability-sensitive fields.
- Use local project preferences when they exist. Treat them as experience notes, not universal truth.
- Prefer `z-ai/glm-5.2` as a local default/fallback for text, coding, long-context, and analysis tasks when no cheaper, more specialized, or project-specific model is clearly better.
- Warn when a recommendation changes an existing project model. Ask before switching only if the change is material for cost, quality, latency, or output type.
- Ask before starting a premium model when a cheaper adequate option exists and the user did not explicitly request best quality, unless the expected cost is clearly minor for the sprint.
- Do not ask for obvious choices: explicit user model selection, very low-cost exploratory work, or a project preference that matches the user's quality requirement and does not switch the configured model.
- Present sources by type: live facts, official/provider docs, benchmark or community evaluation, and local project evidence.

## Quick Start

Call the script from either the override checkout or the installed runtime copy that matches the host tool.

Recommend a model for a task:

```powershell
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-model-advisor\scripts\recommend_model.py" --task "Generate final NumberQuest game asset icons with precise text and consistent style" --project NumberQuest
```

Recommend with known current project model:

```powershell
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-model-advisor\scripts\recommend_model.py" --task "Create NumberQuest image assets" --project NumberQuest --current-model black-forest-labs/flux.2-pro
```

Find the cheapest acceptable option:

```powershell
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-model-advisor\scripts\recommend_model.py" --task "Draft a short changelog summary" --priority cost
```

Force an image-generation search:

```powershell
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-model-advisor\scripts\recommend_model.py" --task "Prototype a small game background" --mode image --priority balanced
```

## Output Contract

The script prints JSON with:

- `recommended_model`: best current choice for the task.
- `requires_confirmation`: true when the agent should ask before using it.
- `confirmation_reason`: why user confirmation is needed.
- `alternatives`: cheaper or higher-quality candidates.
- `sources`: live and local sources used.
- `decision_notes`: short rationale suitable for user-facing summary.

When `requires_confirmation` is true, ask one concise question before the model call. Example:

`Dette bytter NumberQuest fra black-forest-labs/flux.2-pro til openai/gpt-5-image for bedre bildekvalitet, men det kan koste mer. Skal jeg bruke GPT-5 Image for denne oppgaven?`

## Source Files

- Read `references/source-policy.md` for how to classify evidence and communicate uncertainty.
- Update `references/project-preferences.json` when a project-specific model result is observed.
- Update `references/model-notes.json` when adding durable model notes, official docs, or benchmark/evaluation links.

## Relationship To Other OpenRouter Skills

- Use `openrouter-models` for raw model search, comparison, and provider endpoint inspection.
- Use this skill when the user needs a decision, not just model facts.
- Use task-specific skills such as `openrouter-glm52` or `openrouter-flux2-pro` only after the advisor has selected or confirmed that model when the choice is non-obvious.
