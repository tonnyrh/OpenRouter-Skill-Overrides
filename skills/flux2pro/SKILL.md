---
name: flux2pro
description: Generate images and game graphics using FLUX.2 Pro through OpenRouter. Use when the user wants to create game sprites, backgrounds, textures, concept art, UI icons, or any high-quality image generation with FLUX.2 Pro. Trigger on mentions of FLUX, FLUX.2, FLUX Pro, Black Forest Labs, game graphics generation, sprite generation, game art, or when the user wants photorealistic or artistic image generation distinct from Gemini-based image tools.
---

# FLUX.2 Pro Image Generation

Generate high-quality images and game graphics using Black Forest Labs' FLUX.2 Pro model through OpenRouter chat completions with image output.

## Prerequisites

The `OPENROUTER_API_KEY` environment variable must be set. Get a key at https://openrouter.ai/keys

## Model

- Default: `black-forest-labs/flux.2-pro`
- Verify alternatives with the model advisor before switching models.
- Verify available FLUX models: use the `openrouter-models` skill or check https://openrouter.ai/models?q=flux

## Quick Start

```powershell
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "a glowing crystal sword on a dark background"
```

## Game Graphics Presets

Use `--preset` to inject optimized style tokens for common game art types:

| Preset | Best for | Auto-appended style |
|---|---|---|
| `sprite` | Characters, items, enemies | pixel art, transparent background, game sprite, centered, clean outline |
| `background` | Scene/level backgrounds | wide panoramic, game environment, detailed, atmospheric |
| `texture` | Materials, surfaces | seamless tileable texture, top-down view, no seams |
| `icon` | UI, HUD, inventory items | game UI icon, simple, readable at small size, flat design |
| `concept` | Concept art, world design | concept art, game world, detailed illustration, professional |
| `portrait` | Character portraits, NPCs | character portrait, detailed face, game art style, bust shot |

```powershell
# Game sprite
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "knight warrior in armor" --preset sprite

# Level background
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "dark forest with glowing mushrooms" --preset background --aspect-ratio 16:9

# Seamless ground texture
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "mossy stone bricks" --preset texture

# Inventory icon
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "health potion red bottle" --preset icon --aspect-ratio 1:1 --image-size 0.5K
```

## All Options

```
Usage: generate_flux.py "prompt" [options]

Options:
  --model <id>        OpenRouter model ID (default: black-forest-labs/flux.2-pro)
  --output <path>     Output file path (default: flux-YYYYMMDD-HHmmss.png)
  --aspect-ratio      Requested ratio, for example 1:1 or 16:9
  --image-size        Requested size: 0.5K, 1K, 2K, or 4K
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

Requested `image_size` is provider-dependent. Inspect the saved file instead of assuming the returned pixel dimensions.

## Workflow

1. Check `OPENROUTER_API_KEY` is set before calling.
2. Choose a preset for game art — presets significantly improve relevance of output.
3. Describe subject clearly; FLUX excels at photorealistic and painterly styles.
4. For sprites: follow up with a background-removal tool if needed (FLUX does not natively remove backgrounds).
5. Display the saved image to the user and report the output path.

## API Details

Uses `POST https://openrouter.ai/api/v1/chat/completions` with `modalities: ["image"]`.

Response shape:
```json
{
  "choices": [{
    "message": {
      "images": [{ "image_url": { "url": "data:image/png;base64,..." } }]
    }
  }]
}
```
