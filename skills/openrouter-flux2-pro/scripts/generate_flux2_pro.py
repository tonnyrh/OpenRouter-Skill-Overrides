#!/usr/bin/env python3
"""Generate images via OpenRouter — FLUX.2 Pro and chat-based image models (standard library only)."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "black-forest-labs/flux.2-pro"
# Minimum max_tokens for chat-based image models.  Lower values cause finish_reason=length
# before the image is emitted (observed with openai/gpt-5-image-mini at 1024).
CHAT_IMAGE_MAX_TOKENS = 8192


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate images via OpenRouter (FLUX.2 Pro and chat-based image models)."
    )
    parser.add_argument("prompt", nargs="*", help="Image prompt. If omitted, stdin is used.")
    parser.add_argument("--output", "-o", default="image-output.png", help="Output image path.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenRouter model slug.")
    parser.add_argument("--aspect-ratio", default=None, help="Optional aspect ratio, e.g. 1:1, 16:9, 9:16.")
    parser.add_argument("--image-size", default=None, choices=["0.5K", "1K", "2K", "4K"])
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=CHAT_IMAGE_MAX_TOKENS,
        help=f"max_tokens for chat-based image models (default {CHAT_IMAGE_MAX_TOKENS}). Ignored for FLUX-style models.",
    )
    parser.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Optional reference image path. Repeat for multiple references.",
    )
    parser.add_argument("--json", action="store_true", help="Write raw JSON response next to the output image.")
    return parser.parse_args()


def is_flux_style(model_id: str) -> bool:
    """FLUX and similar dedicated image models use modalities payload.
    Chat-based image models (GPT-5 Image, Gemini Flash Image, etc.) use max_tokens instead."""
    slug = model_id.lower()
    return "flux" in slug or "recraft" in slug or slug.startswith("black-forest-labs/")


def build_prompt(parts: list[str]) -> str:
    prompt = " ".join(parts).strip()
    if prompt:
        return prompt
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise SystemExit("No prompt provided. Pass a prompt argument or pipe text on stdin.")


def data_url_for_file(path_text: str) -> str:
    path = Path(path_text).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"Reference image not found: {path}")
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def build_message_content(prompt: str, references: list[str]) -> str | list[dict[str, object]]:
    if not references:
        return prompt
    content: list[dict[str, object]] = [{"type": "text", "text": prompt}]
    for reference in references:
        content.append({"type": "image_url", "image_url": {"url": data_url_for_file(reference)}})
    return content


def build_payload(model: str, prompt: str, references: list[str], aspect_ratio: str | None,
                  image_size: str | None, seed: int | None, max_tokens: int) -> dict:
    payload: dict[str, object] = {
        "model": model,
        "messages": [{"role": "user", "content": build_message_content(prompt, references)}],
        "stream": False,
    }
    if is_flux_style(model):
        payload["modalities"] = ["image"]
        image_config: dict[str, object] = {}
        if aspect_ratio:
            image_config["aspect_ratio"] = aspect_ratio
        if image_size:
            image_config["image_size"] = image_size
        if image_config:
            payload["image_config"] = image_config
    else:
        # Chat-based image model: GPT-5 Image, Gemini Flash Image, etc.
        # These return the image in choices[0].message.images[0].image_url.url (base64).
        # content is null; finish_reason=length if max_tokens is too low.
        payload["max_tokens"] = max_tokens
    if seed is not None:
        payload["seed"] = seed
    return payload


def extract_image_url(data: dict[str, object]) -> str:
    finish = None
    try:
        choice = data["choices"][0]  # type: ignore[index]
        finish = choice.get("finish_reason") or choice.get("native_finish_reason")
        message = choice["message"]  # type: ignore[index]
        first_image = message["images"][0]  # type: ignore[index]
    except (KeyError, IndexError, TypeError) as exc:
        if finish in {"length", "max_output_tokens"}:
            raise SystemExit(
                "Generation cut off: finish_reason=length. Increase --max-tokens and retry."
            ) from exc
        raise SystemExit("No image found in response:\n" + json.dumps(data, indent=2, ensure_ascii=False)) from exc

    if not isinstance(first_image, dict):
        raise SystemExit("Unexpected image response:\n" + json.dumps(data, indent=2, ensure_ascii=False))

    image_obj = first_image.get("image_url") or first_image.get("imageUrl")
    if isinstance(image_obj, dict) and isinstance(image_obj.get("url"), str):
        return image_obj["url"]
    if isinstance(first_image.get("url"), str):
        return first_image["url"]  # type: ignore[return-value]
    raise SystemExit("Unexpected image URL response:\n" + json.dumps(data, indent=2, ensure_ascii=False))


def write_image(image_url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if image_url.startswith("data:"):
        _, encoded = image_url.split(",", 1)
        output_path.write_bytes(base64.b64decode(encoded))
        return
    with urllib.request.urlopen(image_url, timeout=120) as response:
        output_path.write_bytes(response.read())


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set.")

    prompt = build_prompt(args.prompt)
    payload = build_payload(
        args.model, prompt, args.reference,
        args.aspect_ratio, args.image_size, args.seed, args.max_tokens,
    )

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openai.com/codex",
            "X-Title": "Codex OpenRouter Image Generation Skill",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenRouter HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"OpenRouter request failed: {exc}") from exc

    output_path = Path(args.output).expanduser().resolve()
    write_image(extract_image_url(data), output_path)

    if args.json:
        output_path.with_suffix(output_path.suffix + ".json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
