#!/usr/bin/env python3
"""Verify OpenRouter skill installation and routing policy for Claude Code or Codex."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Verify OpenRouter skill installation.")
    p.add_argument("--tool", choices=["claude", "codex", "cursor"], required=True, help="Target runtime.")
    p.add_argument("--live-glm", action="store_true", help="Run a billed live GLM 5.2 call.")
    p.add_argument("--live-flux", action="store_true", help="Run a billed live FLUX generation.")
    p.add_argument(
        "--live-gpt5-image", action="store_true",
        help="Run a billed live GPT-5 Image Mini generation (claude only).",
    )
    return p.parse_args()


def syntax_check(paths: list[Path]) -> None:
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8"))
        print(f"syntax OK: {path}")


def ensure_openrouter_only(paths: list[Path]) -> None:
    forbidden = ("call_ollama", "localhost:11434", "127.0.0.1:11434", "/api/generate")
    for path in paths:
        content = path.read_text(encoding="utf-8").lower()
        matches = [marker for marker in forbidden if marker.lower() in content]
        if matches:
            joined = ", ".join(matches)
            raise SystemExit(f"FAIL: local Ollama reference in OpenRouter script {path}: {joined}")
    print("OpenRouter-only script policy OK")


def run_advisor(advisor: Path, *extra_args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(advisor), *extra_args],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(f"advisor exited {result.returncode}")
    print(result.stdout, end="")
    return json.loads(result.stdout)


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    if args.tool == "cursor":
        runtime = Path.home() / ".cursor"
    else:
        runtime = Path.home() / f".{args.tool}"
    skills = runtime / "skills"

    cursor_wrappers = [
        repo_root / ".cursor" / "rules" / "agent-routing.mdc",
        repo_root / "AGENTS.md",
    ]
    cursor_wrappers.extend(sorted((repo_root / ".cursor" / "skills").glob("*/SKILL.md")))
    if args.tool == "cursor":
        missing = [path for path in cursor_wrappers if not path.exists()]
        if missing:
            for path in missing:
                print(f"FAIL: missing Cursor file: {path}", file=sys.stderr)
            return 1
        for path in cursor_wrappers:
            print(f"cursor layout OK: {path}")

    if args.tool == "claude":
        image_skill = "flux2pro"
        image_script = "generate_flux.py"
    else:
        image_skill = "openrouter-flux2-pro"
        image_script = "generate_flux2_pro.py"

    repo_python_files = [
        repo_root / "skills" / "openrouter-glm52" / "scripts" / "call_glm52.py",
        repo_root / "skills" / "openrouter-model-advisor" / "scripts" / "recommend_model.py",
        repo_root / "skills" / image_skill / "scripts" / image_script,
        repo_root / "skills" / "openrouter-pdf-extract" / "scripts" / "extract_pdf.py",
    ]
    python_files = list(repo_python_files)
    if args.tool != "cursor":
        python_files.extend([
            skills / "openrouter-glm52" / "scripts" / "call_glm52.py",
            skills / "openrouter-model-advisor" / "scripts" / "recommend_model.py",
            skills / image_skill / "scripts" / image_script,
            skills / "openrouter-pdf-extract" / "scripts" / "extract_pdf.py",
        ])
    syntax_check(python_files)
    ensure_openrouter_only(repo_python_files)

    advisor = skills / "openrouter-model-advisor" / "scripts" / "recommend_model.py"
    if not advisor.exists():
        advisor = repo_root / "skills" / "openrouter-model-advisor" / "scripts" / "recommend_model.py"
        if args.tool == "cursor":
            print(f"WARN: personal Cursor skills not synced; using repo advisor at {advisor}", file=sys.stderr)

    run_advisor(advisor,
        "--task", "Second-pass review of a large coding task in a local repository",
        "--mode", "coding", "--priority", "balanced", "--limit", "2")

    cheap = run_advisor(advisor,
        "--task", "Draft a cheap short changelog summary",
        "--mode", "text", "--priority", "cost", "--limit", "2")
    if cheap["recommended_model"]["quality_tier"] == "premium" or cheap["requires_confirmation"]:
        print("FAIL: cost routing regression — expected non-premium without confirmation", file=sys.stderr)
        return 1

    nq = run_advisor(advisor,
        "--task", "Generate final NumberQuest game assets with precise style",
        "--project", "NumberQuest",
        "--current-model", "black-forest-labs/flux.2-pro",
        "--mode", "image", "--priority", "balanced", "--limit", "2")
    if nq["recommended_model"]["id"] != "openai/gpt-5-image" or not nq["requires_confirmation"]:
        print("FAIL: NumberQuest routing regression — expected GPT-5 Image with switch confirmation", file=sys.stderr)
        return 1

    print("advisor policy OK: cheap routing and NumberQuest switch gate")

    if args.live_glm:
        glm_script = skills / "openrouter-glm52" / "scripts" / "call_glm52.py"
        if not glm_script.exists():
            glm_script = repo_root / "skills" / "openrouter-glm52" / "scripts" / "call_glm52.py"
        subprocess.run([
            sys.executable,
            str(glm_script),
            "--max-tokens", "300", "Answer only with: OK",
        ], check=True)

    if args.live_flux:
        out = Path(tempfile.gettempdir()) / f"{args.tool}-flux2pro-live-check.png"
        flux_script = skills / image_skill / "scripts" / image_script
        if not flux_script.exists():
            flux_script = repo_root / "skills" / image_skill / "scripts" / image_script
        subprocess.run([
            sys.executable,
            str(flux_script),
            "Tiny blue dot centered on a white background",
            "--aspect-ratio", "1:1", "--image-size", "0.5K",
            "--seed", "7", "--output", str(out),
        ], check=True)
        if not out.exists():
            print(f"FAIL: FLUX live check did not create {out}", file=sys.stderr)
            return 1
        print(f"FLUX live check OK: {out}")

    if args.live_gpt5_image:
        if args.tool != "claude":
            print("--live-gpt5-image is only supported for --tool claude", file=sys.stderr)
            return 1
        out = Path(tempfile.gettempdir()) / "claude-gpt5-image-mini-live-check.png"
        subprocess.run([
            sys.executable,
            str(skills / "flux2pro" / "scripts" / "generate_flux.py"),
            "A tiny blue circle on a white background",
            "--model", "openai/gpt-5-image-mini", "--output", str(out),
        ], check=True)
        if not out.exists():
            print(f"FAIL: GPT-5 Image Mini live check did not create {out}", file=sys.stderr)
            return 1
        print(f"GPT-5 Image Mini live check OK: {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
