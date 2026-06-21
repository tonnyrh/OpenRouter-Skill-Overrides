#!/usr/bin/env python3
"""Extract text from a PDF file using OpenRouter multimodal models."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash-lite"
DEFAULT_MAX_TOKENS = 32000
DEFAULT_PROMPT = (
    "Extract all text from this PDF document. Return it as structured plain text, "
    "preserving headings, section breaks, tables, product names, prices, article numbers, "
    "and all other content. Do not summarize — include every line of text from the document."
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract text from a PDF via OpenRouter.")
    p.add_argument("pdf", help="Path to the PDF file.")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenRouter model ID (default: {DEFAULT_MODEL}).")
    p.add_argument("--output", "-o", default=None, help="Output file path. Prints to stdout if omitted.")
    p.add_argument("--prompt", default=DEFAULT_PROMPT, help="Extraction prompt.")
    p.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, dest="max_tokens",
                   help=f"max_tokens (default: {DEFAULT_MAX_TOKENS}; increase if finish_reason=length).")
    p.add_argument("--json", action="store_true", dest="save_json",
                   help="Also save raw JSON response beside output file.")
    return p.parse_args()


def build_payload(model: str, pdf_b64: str, filename: str, prompt: str, max_tokens: int) -> dict:
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "file",
                        "file": {
                            "url": f"data:application/pdf;base64,{pdf_b64}",
                            "filename": filename,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        "max_tokens": max_tokens,
        "stream": False,
    }


def call_openrouter(payload: dict) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set.")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/tonnyrh/OpenRouter-Skill-Overrides",
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise SystemExit(f"HTTP {e.code}: {body}") from None


def extract_text(data: dict) -> str:
    choice = data.get("choices", [{}])[0]
    finish = choice.get("finish_reason", "")
    if finish == "length":
        raise SystemExit(
            "finish_reason=length: max_tokens was too low. Retry with a higher --max-tokens value (e.g. --max-tokens 64000)."
        )
    content = choice.get("message", {}).get("content") or ""
    if not content:
        raise SystemExit(f"No text content in response. Raw: {json.dumps(data)[:500]}")
    return content


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"ERROR: file not found: {pdf_path}", file=sys.stderr)
        return 1

    size_kb = pdf_path.stat().st_size // 1024
    print(f"Reading {pdf_path.name} ({size_kb} KB)…", file=sys.stderr)
    pdf_b64 = base64.b64encode(pdf_path.read_bytes()).decode()

    payload = build_payload(args.model, pdf_b64, pdf_path.name, args.prompt, args.max_tokens)
    print(f"Calling {args.model} (max_tokens={args.max_tokens})…", file=sys.stderr)
    data = call_openrouter(payload)

    if args.save_json and args.output:
        json_path = Path(args.output).with_suffix(".json")
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON saved: {json_path}", file=sys.stderr)

    text = extract_text(data)

    if args.output:
        out = Path(args.output)
        out.write_text(text, encoding="utf-8")
        print(f"Saved: {out} ({len(text):,} chars)", file=sys.stderr)
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
