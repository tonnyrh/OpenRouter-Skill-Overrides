#!/usr/bin/env python3
"""Generate images with FLUX.2 Pro through OpenRouter chat completions."""

from __future__ import annotations

import argparse
import base64
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "black-forest-labs/flux.2-pro"

PRESETS: dict[str, str] = {
    "sprite": "pixel art, game sprite, centered subject, clean outline, no background clutter",
    "background": "wide panoramic game environment, detailed scene, atmospheric lighting, game background art",
    "texture": "seamless tileable texture, top-down orthographic view, no visible seams, repeating pattern",
    "icon": "game UI icon, simple bold design, readable at small size, clean edges",
    "concept": "concept art, detailed professional game illustration, cinematic composition",
    "portrait": "character portrait, detailed face and bust, dramatic lighting, centered composition",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate images with FLUX.2 Pro via OpenRouter.")
    parser.add_argument("prompt", nargs="*", help="Image prompt. If omitted, read stdin.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output", default=None, help="Output path; timestamped PNG by default.")
    parser.add_argument("--aspect-ratio", default=None, help="Optional ratio such as 1:1, 16:9, or 9:16.")
    parser.add_argument("--image-size", choices=["0.5K", "1K", "2K", "4K"], default=None)
    parser.add_argument("--width", type=int, default=None, help="Deprecated compatibility option; used to infer aspect ratio.")
    parser.add_argument("--height", type=int, default=None, help="Deprecated compatibility option; used to infer aspect ratio.")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--preset", choices=list(PRESETS), default=None)
    parser.add_argument("--n", type=int, default=1, help="Number of separate generation calls.")
    parser.add_argument("--json", action="store_true", help="Write raw response JSON beside each image.")
    return parser.parse_args()


def build_prompt(parts: list[str], preset: str | None) -> str:
    text = " ".join(parts).strip()
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    if not text:
        raise SystemExit("No prompt provided. Pass a prompt or pipe text on stdin.")
    return f"{text}, {PRESETS[preset]}" if preset else text


def default_output_path() -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(f"flux-{stamp}.png").resolve()


def inferred_ratio(width: int | None, height: int | None) -> str | None:
    if not width or not height:
        return None
    ratio = width / height
    choices = {"1:1": 1.0, "4:3": 4 / 3, "3:4": 3 / 4, "16:9": 16 / 9, "9:16": 9 / 16, "21:9": 21 / 9}
    return min(choices, key=lambda key: abs(choices[key] - ratio))


def call_api(api_key: str, payload: dict) -> dict:
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://claude.ai/code",
            "X-Title": "Claude Code FLUX.2 Pro Skill",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenRouter HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"OpenRouter request failed: {exc}") from exc


def extract_image_url(data: dict) -> str:
    try:
        first = data["choices"][0]["message"]["images"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit("No image found in response:\n" + json.dumps(data, indent=2, ensure_ascii=False)) from exc
    image_obj = first.get("image_url") or first.get("imageUrl")
    if isinstance(image_obj, dict) and isinstance(image_obj.get("url"), str):
        return image_obj["url"]
    if isinstance(first.get("url"), str):
        return first["url"]
    raise SystemExit("Unexpected image response:\n" + json.dumps(data, indent=2, ensure_ascii=False))


def save_image(image_url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if image_url.startswith("data:"):
        output_path.write_bytes(base64.b64decode(image_url.split(",", 1)[1]))
        return
    with urllib.request.urlopen(image_url, timeout=120) as response:
        output_path.write_bytes(response.read())


def indexed_path(base: Path, index: int, total: int) -> Path:
    return base if total == 1 else base.with_name(f"{base.stem}-{index + 1}{base.suffix}")


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set.")
    if args.n < 1:
        raise SystemExit("--n must be at least 1.")

    prompt = build_prompt(args.prompt, args.preset)
    output_base = Path(args.output).expanduser().resolve() if args.output else default_output_path()
    aspect_ratio = args.aspect_ratio or inferred_ratio(args.width, args.height)
    saved: list[str] = []

    for index in range(args.n):
        payload: dict[str, object] = {
            "model": args.model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image"],
            "stream": False,
        }
        image_config: dict[str, str] = {}
        if aspect_ratio:
            image_config["aspect_ratio"] = aspect_ratio
        if args.image_size:
            image_config["image_size"] = args.image_size
        if image_config:
            payload["image_config"] = image_config
        if args.seed is not None:
            payload["seed"] = args.seed + index

        data = call_api(api_key, payload)
        output_path = indexed_path(output_base, index, args.n)
        save_image(extract_image_url(data), output_path)
        if args.json:
            output_path.with_suffix(output_path.suffix + ".json").write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        saved.append(str(output_path))

    print(json.dumps({"model": args.model, "prompt": prompt, "images_saved": saved}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
