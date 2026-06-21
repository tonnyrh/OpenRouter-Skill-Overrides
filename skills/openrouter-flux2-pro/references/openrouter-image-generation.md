# OpenRouter Image Generation

## Model

- FLUX.2 Pro model slug: `black-forest-labs/flux.2-pro`
- OpenRouter model name: `Black Forest Labs: FLUX.2 Pro`
- Architecture: `text+image->image`
- Input modalities: `text`, `image`
- Output modalities: `image`
- Supported parameter currently listed by OpenRouter: `seed`

## API Shape

OpenRouter supports image generation through `POST https://openrouter.ai/api/v1/chat/completions`.

Use `modalities` to request image output:

```json
{
  "model": "black-forest-labs/flux.2-pro",
  "messages": [
    {
      "role": "user",
      "content": "Generate a clean product image of a white ceramic mug on a steel table"
    }
  ],
  "modalities": ["image"],
  "stream": false
}
```

For reference-image edits, send message content as parts:

```json
{
  "role": "user",
  "content": [
    { "type": "text", "text": "Keep the same product, change the background to a Nordic kitchen" },
    { "type": "image_url", "image_url": { "url": "data:image/png;base64,..." } }
  ]
}
```

## Image Config

Many OpenRouter image models accept shared `image_config` fields:

- `aspect_ratio`: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`
- `image_size`: `1K`, `2K`, `4K`

FLUX.2 Pro's model record lists `seed` as a supported parameter. If an `image_config` option fails for FLUX.2 Pro, retry without it and report the provider response.

## Response Parsing

Generated images appear on the assistant message under `images`. OpenRouter examples have shown both `image_url` and `imageUrl` casing:

```json
{
  "choices": [
    {
      "message": {
        "images": [
          {
            "image_url": {
              "url": "data:image/png;base64,..."
            }
          }
        ]
      }
    }
  ]
}
```

The URL may be a base64 data URL or a remote URL. Save data URLs by decoding the base64 payload after the comma.
