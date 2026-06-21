#!/usr/bin/env python3
"""Generate images with FLUX.2 Pro through OpenRouter's images API."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


API_URL = "https://openrouter.ai/api/v1/images/generations"
DEFAULT_MODEL = "black-forest-labs/flux-2-pro"

PRESETS: dict[str, str] = {
    "sprite": "pixel art, transparent background, game sprite, centered subject, clean outline, no background clutter",
    "background": "wide panoramic game environment, detailed scene, atmospheric lighting, high resolution, game background art",
    "texture": "seamless tileable texture, top-down orthographic view, no visible seams, repeating pattern, material texture",
    "icon": "game UI icon, simple bold design, readable at small size, flat stylized illustration, clean edges",
    "concept": "concept art, game world illustration, detailed painting, professional game art, cinematic composition",
    "portrait": "character portrait, detailed face and bust, game art style, dramatic lighting, centered composition",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate images with FLUX.2 Pro via OpenRouter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("prompt", nargs="*", help="Image prompt. If omitted, reads from stdin.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenRouter model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--output", default=None, help="Output file path (default: flux-YYYYMMDD-HHmmss.png)")
    parser.add_argument("--width", type=int, default=1024, help="Image width in pixels (default: 1024)")
    parser.add_argument("--height", type=int, default=1024, help="Image height in pixels (default: 1024)")
    parser.add_argument("--steps", type=int, default=None, help="Inference steps (model default if omitted)")
    parser.add_argument(
        "--preset",
        choices=list(PRESETS.keys()),
        default=None,
        help="Game art style preset: " + ", ".join(PRESETS.keys()),
    )
    parser.add_argument("--n", type=int, default=1, help="Number of images to generate (default: 1)")
    parser.add_argument("--json", dest="raw_json", action="store_true", help="Print raw JSON API response")
    return parser.parse_args()


def build_prompt(parts: list[str], preset: str | None) -> str:
    text = " ".join(parts).strip()
    if not text:
        if not sys.stdin.isatty():
            text = sys.stdin.read().strip()
    if not text:
        raise SystemExit("No prompt provided. Pass a prompt or pipe text on stdin.")
    if preset:
        text = f"{text}, {PRESETS[preset]}"
    return text


def default_output_path() -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"flux-{stamp}.png"


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
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            raise SystemExit("Error 401: Invalid API key. Check your OPENROUTER_API_KEY.") from exc
        if exc.code == 429:
            raise SystemExit("Error 429: Rate limited. Wait a moment and try again.") from exc
        raise SystemExit(f"OpenRouter HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"OpenRouter request failed: {exc}") from exc


def save_b64_image(b64_data: str, output_path: str) -> str:
    abs_path = str(Path(output_path).resolve())
    Path(abs_path).parent.mkdir(parents=True, exist_ok=True)
    Path(abs_path).write_bytes(base64.b64decode(b64_data))
    return abs_path


def save_url_image(url: str, output_path: str, api_key: str) -> str:
    abs_path = str(Path(output_path).resolve())
    Path(abs_path).parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(request, timeout=60) as response:
        Path(abs_path).write_bytes(response.read())
    return abs_path


def stem_with_index(output_path: str, index: int, total: int) -> str:
    if total == 1:
        return output_path
    p = Path(output_path)
    return str(p.parent / f"{p.stem}-{index + 1}{p.suffix}")


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set. Get a key at https://openrouter.ai/keys")

    prompt = build_prompt(args.prompt, args.preset)
    output_base = args.output or default_output_path()

    payload: dict = {
        "model": args.model,
        "prompt": prompt,
        "n": args.n,
        "size": f"{args.width}x{args.height}",
        "response_format": "b64_json",
    }
    if args.steps is not None:
        payload["steps"] = args.steps

    data = call_api(api_key, payload)

    if args.raw_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    images = data.get("data", [])
    if not images:
        raise SystemExit(f"No images returned. Raw response:\n{json.dumps(data, indent=2)}")

    saved: list[str] = []
    for i, img in enumerate(images):
        out_path = stem_with_index(output_base, i, len(images))
        if "b64_json" in img and img["b64_json"]:
            abs_path = save_b64_image(img["b64_json"], out_path)
        elif "url" in img and img["url"]:
            abs_path = save_url_image(img["url"], out_path, api_key)
        else:
            print(f"Warning: image {i + 1} has no usable data, skipping.", file=sys.stderr)
            continue
        saved.append(abs_path)

    print(json.dumps({
        "model": args.model,
        "prompt": prompt,
        "preset": args.preset,
        "size": f"{args.width}x{args.height}",
        "images_saved": saved,
        "count": len(saved),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
