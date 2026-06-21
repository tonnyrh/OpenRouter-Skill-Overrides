#!/usr/bin/env python3
"""Sync OpenRouter skill overrides to Claude Code or Codex runtime directories."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


SKILLS: dict[str, list[str]] = {
    "claude": ["openrouter-glm52", "openrouter-heavy-task-gate", "openrouter-model-advisor", "flux2pro", "openrouter-pdf-extract"],
    "codex":  ["openrouter-glm52", "openrouter-heavy-task-gate", "openrouter-model-advisor", "openrouter-flux2-pro", "openrouter-pdf-extract"],
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sync OpenRouter skill overrides to a tool runtime.")
    p.add_argument("--tool", choices=["claude", "codex"], required=True, help="Target runtime.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    runtime = Path.home() / f".{args.tool}"
    skills_dst = runtime / "skills"

    for skill in SKILLS[args.tool]:
        src = repo_root / "skills" / skill
        if not src.is_dir():
            print(f"ERROR: missing source skill: {src}", file=sys.stderr)
            return 1
        dst = skills_dst / skill
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"Synced {skill} -> {dst}")

    if args.tool == "claude":
        commands_src = repo_root / "claude" / "commands"
        commands_dst = runtime / "commands"
        commands_dst.mkdir(parents=True, exist_ok=True)
        for md in sorted(commands_src.glob("*.md")):
            shutil.copy2(md, commands_dst / md.name)
        print(f"Synced Claude commands -> {commands_dst}")

    print(f"{args.tool.capitalize()} OpenRouter custom skills are in sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
