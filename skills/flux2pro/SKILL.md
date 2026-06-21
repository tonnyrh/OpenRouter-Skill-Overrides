---
name: flux2pro
description: Generate images and game graphics via OpenRouter. Supports FLUX.2 Pro (Black Forest Labs) and chat-based image models (GPT-5 Image, GPT-5 Image Mini, Gemini Flash Image). Use when the user wants game sprites, backgrounds, textures, concept art, UI icons, or any image generation through OpenRouter. Trigger on mentions of FLUX, FLUX.2, FLUX Pro, GPT-5 Image, Gemini image, game graphics, sprite generation, or image generation via OpenRouter.
---

# OpenRouter Image Generation

Generate high-quality images using FLUX.2 Pro or chat-based image models (GPT-5 Image, Gemini Flash Image, etc.) through OpenRouter.

## Prerequisites

`OPENROUTER_API_KEY` must be set. Get a key at https://openrouter.ai/keys

## Model Families

Two payload styles — the script detects automatically from the model ID:

| Family | Example models | Payload style |
|---|---|---|
| FLUX-style | `black-forest-labs/flux.2-pro`, Recraft models | `modalities: ["image"]` + optional `image_config` |
| Chat-based | `openai/gpt-5-image`, `openai/gpt-5-image-mini`, `google/gemini-2.5-flash-image` | `max_tokens: 8192` (minimum) |

Both families return the image in `choices[0].message.images[0].image_url.url` (base64 data URL).

**Chat-based models:** `message.content` is null. `finish_reason=length` means `max_tokens` was too low — the default 8192 avoids this. Response bodies are larger (~2 MB) due to encrypted reasoning.

## Quick Start

```powershell
# FLUX.2 Pro (default)
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "a glowing crystal sword on a dark background"

# GPT-5 Image Mini
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "a cute Smurf, blue skin, white hat, cheerful cartoon style" --model openai/gpt-5-image-mini

# GPT-5 Image (premium)
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "NumberQuest game icon, precise text, clean cartoon style" --model openai/gpt-5-image
```

## Game Graphics Presets (FLUX-style models)

Use `--preset` to inject optimized style tokens for common game art types:

| Preset | Best for |
|---|---|
| `sprite` | Characters, items, enemies |
| `background` | Scene/level backgrounds |
| `texture` | Materials, surfaces |
| `icon` | UI, HUD, inventory items |
| `concept` | Concept art, world design |
| `portrait` | Character portraits, NPCs |

```powershell
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "knight warrior in armor" --preset sprite
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "dark forest with glowing mushrooms" --preset background --aspect-ratio 16:9
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "health potion red bottle" --preset icon --aspect-ratio 1:1 --image-size 0.5K
```

## All Options

```
Usage: generate_flux.py "prompt" [options]

Options:
  --model <id>        OpenRouter model ID (default: black-forest-labs/flux.2-pro)
  --output <path>     Output file path (default: image-YYYYMMDD-HHmmss.png)
  --aspect-ratio      Requested ratio, e.g. 1:1 or 16:9 (FLUX-style only)
  --image-size        Requested size: 0.5K, 1K, 2K, or 4K (FLUX-style only)
  --max-tokens <n>    max_tokens for chat-based models (default: 8192, minimum safe value)
  --seed <n>          Optional deterministic seed
  --preset <name>     Game art preset: sprite|background|texture|icon|concept|portrait
  --n <count>         Number of separate generation calls (default: 1)
  --json              Save raw response JSON beside each image
```

## Common Ratios

| Use case | Aspect ratio |
|---|---|
| Square (sprite, icon, texture) | `1:1` |
| Wide background | `16:9` |
| Portrait | `3:4` or `9:16` |
| Wide banner | `21:9` |

## Workflow

1. Check `OPENROUTER_API_KEY` is set.
2. Use `openrouter-model-advisor` if model choice is non-obvious — it knows pricing and quality tiers for both FLUX and chat-based image models.
3. Choose a preset for game art (FLUX-style models only).
4. Display the saved image to the user and report the output path.

## API Details

All calls go to `POST https://openrouter.ai/api/v1/chat/completions`.

Response shape (same for all models):
```json
{
  "choices": [{
    "message": {
      "content": null,
      "images": [{ "image_url": { "url": "data:image/png;base64,..." } }]
    }
  }]
}
```
