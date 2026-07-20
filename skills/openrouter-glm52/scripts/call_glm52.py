#!/usr/bin/env python3
"""Call GLM 5.2 through OpenRouter using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "z-ai/glm-5.2"
DEFAULT_MAX_TOKENS = 4096


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Call z-ai/glm-5.2 via OpenRouter.")
    parser.add_argument("prompt", nargs="*", help="Prompt text. If omitted, stdin is used.")
    parser.add_argument("--system", default="You are a concise senior software engineer.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning-effort", choices=["low", "medium", "high", "xhigh"], default=None)
    parser.add_argument("--max-tokens", type=int, default=None, help=f"Maximum completion tokens (default: {DEFAULT_MAX_TOKENS}).")
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--json", action="store_true", help="Print the raw JSON response.")
    return parser.parse_args()


def build_prompt(parts: list[str]) -> str:
    prompt = " ".join(parts).strip()
    if prompt:
        return prompt
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise SystemExit("No prompt provided. Pass a prompt argument or pipe text on stdin.")


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set.")

    payload: dict[str, object] = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": args.system},
            {"role": "user", "content": build_prompt(args.prompt)},
        ],
    }
    if args.reasoning_effort:
        payload["reasoning"] = {"effort": args.reasoning_effort}
    payload["max_tokens"] = args.max_tokens if args.max_tokens is not None else DEFAULT_MAX_TOKENS
    if args.temperature is not None:
        payload["temperature"] = args.temperature

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/tonnyrh/OpenRouter-Skill-Overrides",
            "X-Title": "OpenRouter GLM 5.2 Skill",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenRouter HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"OpenRouter request failed: {exc}") from exc

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    try:
        choice = data["choices"][0]
        message = choice["message"]
        content = message.get("content")
        if content:
            print(content)
            return 0
        finish_reason = choice.get("finish_reason")
        usage = data.get("usage", {})
        used = usage.get("completion_tokens", "unknown")
        raise SystemExit(
            "OpenRouter returned no answer content "
            f"(finish_reason={finish_reason!r}, completion_tokens={used}). "
            "Increase --max-tokens or lower --reasoning-effort."
        )
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit(json.dumps(data, indent=2, ensure_ascii=False)) from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


