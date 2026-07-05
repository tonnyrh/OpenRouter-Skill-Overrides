---
name: openrouter-flux2-pro
description: Generate and edit raster images with Black Forest Labs FLUX.2 Pro through OpenRouter. Use when the user mentions OpenRouter, FLUX.2 Pro, black-forest-labs/flux.2-pro, AI image generation, text-to-image, reference-image based image editing, product/mockup/illustration/photo asset creation, or wants a local scriptable way to create image files via OpenRouter.
---

# OpenRouter FLUX.2 Pro

Use this skill when FLUX.2 Pro should generate or edit images through OpenRouter. Keep API keys out of files, logs, commits, and final answers.

## Defaults

- Model slug: `black-forest-labs/flux.2-pro`
- API endpoint: `https://openrouter.ai/api/v1/chat/completions`
- Auth env var: `OPENROUTER_API_KEY`
- Output modality: `image`
- Best use: high-quality image generation, visual assets, product/mockup imagery, typography-sensitive prompts, style or character consistency with references, and image edits from one or more reference images.
- Supported generic parameter: `seed`

## Workflow

1. Check whether `OPENROUTER_API_KEY` is available in the current shell before calling OpenRouter.
2. If it is missing, ask the user to set it locally; never ask them to paste the key into chat unless they explicitly choose to.
3. Use `scripts/generate_flux2_pro.py` for direct image generation or editing. It uses only Python standard library modules.
4. Save generated images into a user-specified output path or a local project output folder such as `generated/`, `assets/generated/`, or `public/generated/`.
5. Inspect the result when quality matters. If the image will be used in an app/site, verify that dimensions, file type, framing, and text rendering fit the target UI.
6. Treat OpenRouter errors as actionable API responses: report the HTTP status and concise error body, but never print secrets.

## Direct Generation

Call the script from either the override checkout or the installed runtime copy that matches the host tool.

Generate a square image:

```powershell
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-flux2-pro\scripts\generate_flux2_pro.py" "A clean product photo of a matte black desk lamp on a walnut desk, soft daylight" --output .\generated\desk-lamp.png
```

Choose aspect ratio and size:

```powershell
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-flux2-pro\scripts\generate_flux2_pro.py" "Editorial hero image of a modern Oslo waterfront logistics dashboard, realistic, sharp UI screens" --aspect-ratio 16:9 --image-size 2K --output .\generated\hero.png
```

Use a deterministic seed:

```powershell
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-flux2-pro\scripts\generate_flux2_pro.py" "Minimal app icon, folded map pin made of glass, white background" --seed 42 --output .\generated\icon.png
```

## Reference Images

Pass one or more reference files for image editing or style/character consistency:

```powershell
python "C:\vscode\OpenRouter-Skill-Overrides\skills\openrouter-flux2-pro\scripts\generate_flux2_pro.py" "Keep the same product, place it in a premium Scandinavian kitchen, natural light" --reference .\input\product.jpg --output .\generated\product-kitchen.png
```

The script embeds reference images as base64 data URLs in the chat message. Use small, relevant references; avoid sending private or unrelated images.

## Prompting Notes

- State the image subject, environment, composition, lighting, material/texture, style, and any text that must appear.
- For UI or product assets, include target use such as `website hero`, `app icon`, `transparent-looking product render`, or `16:9 dashboard illustration`.
- For text in images, quote the exact text and describe placement. Verify output manually because image models can still misspell text.
- Prefer positive instructions. Use short negative constraints only when they reduce ambiguity.

## References

Read `references/openrouter-image-generation.md` when you need the current API shape, supported aspect ratios, or response parsing details.
