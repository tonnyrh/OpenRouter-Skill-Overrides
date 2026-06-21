---
name: flux2pro
description: Generate images and game graphics using FLUX.2 Pro through OpenRouter. Use when the user wants to create game sprites, backgrounds, textures, concept art, UI icons, or any high-quality image generation with FLUX.2 Pro. Trigger on mentions of FLUX, FLUX.2, FLUX Pro, Black Forest Labs, game graphics generation, sprite generation, game art, or when the user wants photorealistic or artistic image generation distinct from Gemini-based image tools.
---

# FLUX.2 Pro Image Generation

Generate high-quality images and game graphics using Black Forest Labs' FLUX.2 Pro model through OpenRouter's images API.

## Prerequisites

The `OPENROUTER_API_KEY` environment variable must be set. Get a key at https://openrouter.ai/keys

## Model

- Default: `black-forest-labs/flux-2-pro`
- Fallback/check models: `black-forest-labs/flux-1.1-pro`, `black-forest-labs/flux-pro`
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
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "dark forest with glowing mushrooms" --preset background --width 1920 --height 1080

# Seamless ground texture
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "mossy stone bricks" --preset texture

# Inventory icon
python "$env:USERPROFILE\.claude\skills\flux2pro\scripts\generate_flux.py" "health potion red bottle" --preset icon --width 512 --height 512
```

## All Options

```
Usage: generate_flux.py "prompt" [options]

Options:
  --model <id>        OpenRouter model ID (default: black-forest-labs/flux-2-pro)
  --output <path>     Output file path (default: flux-YYYYMMDD-HHmmss.png)
  --width <px>        Image width in pixels (default: 1024)
  --height <px>       Image height in pixels (default: 1024)
  --steps <n>         Inference steps (default: model default)
  --preset <name>     Game art preset: sprite|background|texture|icon|concept|portrait
  --n <count>         Number of images to generate (default: 1)
  --json              Print raw JSON API response
```

## Common Sizes

| Use case | Width × Height |
|---|---|
| Square (sprite, icon) | 1024 × 1024 |
| HD background | 1920 × 1080 |
| Portrait | 768 × 1024 |
| Wide banner | 1536 × 640 |
| Texture (power of 2) | 512 × 512 or 1024 × 1024 |

## Workflow

1. Check `OPENROUTER_API_KEY` is set before calling.
2. Choose a preset for game art — presets significantly improve relevance of output.
3. Describe subject clearly; FLUX excels at photorealistic and painterly styles.
4. For sprites: follow up with a background-removal tool if needed (FLUX does not natively remove backgrounds).
5. Display the saved image to the user and report the output path.

## API Details

Uses `POST https://openrouter.ai/api/v1/images/generations` (OpenAI-compatible images endpoint).

Response shape:
```json
{
  "data": [
    { "b64_json": "<base64>" }
  ]
}
```
