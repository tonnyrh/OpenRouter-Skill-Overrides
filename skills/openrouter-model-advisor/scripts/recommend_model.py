#!/usr/bin/env python3
"""Recommend an OpenRouter model from live model data and local preference notes."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


MODELS_URL = "https://openrouter.ai/api/v1/models"
SKILL_DIR = Path(__file__).resolve().parents[1]
PROJECT_PREFS_PATH = SKILL_DIR / "references" / "project-preferences.json"
MODEL_NOTES_PATH = SKILL_DIR / "references" / "model-notes.json"


TASK_KEYWORDS = {
    "image": ["image", "bilde", "asset", "sprite", "icon", "logo", "background", "texture", "illustration", "photo", "grafikk"],
    "image-edit": ["edit image", "image edit", "reference image", "endre bilde", "rediger bilde", "consistent style"],
    "vision": ["vision", "screenshot", "analyze image", "se pa bildet", "bildeanalyse"],
    "coding": ["code", "kode", "repo", "bug", "refactor", "test", "ci", "architecture", "migrate", "implementer"],
    "long-context": ["long context", "large repo", "stor kodebase", "mange filer", "repository analysis"],
    "reasoning": ["reasoning", "plan", "analyse", "second pass", "review", "vurder"],
}

PREMIUM_HINTS = ["best", "beste", "highest quality", "final", "production", "presis", "precise", "quality", "kvalitet"]
COST_HINTS = ["cheap", "cheapest", "low cost", "lav kost", "billig", "prototype", "draft", "test", "utforsk"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recommend an OpenRouter model for a task.")
    parser.add_argument("--task", required=True, help="Task description.")
    parser.add_argument("--project", default=None, help="Optional project name, e.g. NumberQuest.")
    parser.add_argument("--current-model", default=None, help="Known current model for this project/task.")
    parser.add_argument("--mode", choices=["auto", "text", "coding", "image", "image-edit", "vision", "long-context", "reasoning"], default="auto")
    parser.add_argument("--priority", choices=["auto", "cost", "balanced", "quality"], default="auto")
    parser.add_argument("--limit", type=int, default=3, help="Number of alternatives to include.")
    parser.add_argument("--allow-premium-without-confirmation", action="store_true")
    parser.add_argument("--models-json", default=None, help="Use a saved OpenRouter models JSON file instead of fetching live data.")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_models(models_json: str | None) -> tuple[list[dict], dict]:
    if models_json:
        path = Path(models_json).expanduser().resolve()
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("data", data), {"type": "saved_openrouter_models", "path": str(path)}

    request = urllib.request.Request(MODELS_URL, headers={"User-Agent": "Codex OpenRouter Model Advisor"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenRouter HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"OpenRouter request failed: {exc}") from exc
    return data.get("data", []), {
        "type": "live_openrouter_models_api",
        "url": MODELS_URL,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


def infer_mode(task: str, explicit_mode: str) -> str:
    if explicit_mode != "auto":
        return explicit_mode
    lowered = task.lower()
    for mode in ["image-edit", "image", "vision", "long-context", "coding", "reasoning"]:
        if any(keyword in lowered for keyword in TASK_KEYWORDS[mode]):
            return mode
    return "text"


def infer_priority(task: str, explicit_priority: str) -> str:
    if explicit_priority != "auto":
        return explicit_priority
    lowered = task.lower()
    if any(keyword in lowered for keyword in COST_HINTS):
        return "cost"
    if any(keyword in lowered for keyword in PREMIUM_HINTS):
        return "quality"
    return "balanced"


def modalities(model: dict) -> tuple[set[str], set[str]]:
    architecture = model.get("architecture") or {}
    return set(architecture.get("input_modalities") or []), set(architecture.get("output_modalities") or [])


def price_per_million(model: dict) -> dict[str, float]:
    pricing = model.get("pricing") or {}
    result: dict[str, float] = {}
    for key, value in pricing.items():
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if number >= 0:
            result[key] = number * 1_000_000
    return result


def blended_cost(model: dict, mode: str) -> float:
    prices = price_per_million(model)
    if not prices:
        return 0.0
    if mode in {"image", "image-edit", "vision"}:
        if "image" in prices and prices["image"] > 0:
            return prices["image"]
        prompt = prices.get("prompt", 0.0)
        completion = prices.get("completion", 0.0)
        return prompt * 1000 + completion * 1000
    return prices.get("prompt", 0.0) + prices.get("completion", 0.0) * 2


def supports_mode(model: dict, mode: str) -> bool:
    inputs, outputs = modalities(model)
    if model.get("expiration_date"):
        return False
    if mode in {"image", "image-edit"}:
        return "image" in outputs and (mode == "image" or "image" in inputs)
    if mode == "vision":
        return "image" in inputs
    if mode in {"coding", "long-context", "reasoning"}:
        return "text" in inputs and (not outputs or outputs == {"text"})
    return "text" in inputs and ("text" in outputs or not outputs)


def project_preference(project_prefs: dict, project: str | None, mode: str) -> dict | None:
    if not project:
        return None
    projects = project_prefs.get("projects") or {}
    project_data = projects.get(project) or projects.get(project.lower()) or {}
    for note in project_data.get("notes", []):
        task_family = note.get("task_family")
        if task_family == mode or (task_family == "image" and mode in {"image", "image-edit"}):
            return note
    return None


def note_for_model(model_notes: dict, model_id: str) -> dict:
    return (model_notes.get("models") or {}).get(model_id, {})


def quality_bonus(model: dict, mode: str, model_notes: dict, pref: dict | None) -> float:
    model_id = model.get("id", "")
    note = note_for_model(model_notes, model_id)
    bonus = 0.0
    if mode in note.get("task_strengths", []):
        bonus += 12.0
    if note.get("quality_tier") == "premium":
        bonus += 8.0
    name = f"{model.get('id', '')} {model.get('name', '')}".lower()
    if mode in {"coding", "long-context"} and any(s in name for s in ["glm", "claude", "gpt", "gemini"]):
        bonus += 4.0
    if mode in {"image", "image-edit"} and any(s in name for s in ["gpt-5-image", "flux.2", "gemini", "recraft", "grok"]):
        bonus += 4.0
    if pref and pref.get("preferred_model") == model_id:
        bonus += 30.0
    return bonus


def score_model(model: dict, mode: str, priority: str, model_notes: dict, pref: dict | None, max_cost: float) -> float:
    cost = blended_cost(model, mode)
    normalized_cost = (cost / max_cost) if max_cost > 0 else 0.0
    context = min(float(model.get("context_length") or 0) / 1_000_000, 1.0)
    params = set(model.get("supported_parameters") or [])
    param_bonus = 0.0
    if mode in {"coding", "reasoning", "long-context"} and "reasoning" in params:
        param_bonus += 5.0
    if mode == "coding" and "tools" in params:
        param_bonus += 3.0
    if mode in {"image", "image-edit"} and "seed" in params:
        param_bonus += 2.0

    quality = quality_bonus(model, mode, model_notes, pref) + context * 4 + param_bonus
    if priority == "cost":
        return quality * 0.35 - normalized_cost * 60
    if priority == "quality":
        return quality * 1.4 - normalized_cost * 15
    return quality - normalized_cost * 30


def format_price(model: dict, mode: str) -> dict:
    return {
        "blended_cost_metric": round(blended_cost(model, mode), 6),
        "per_million": {k: round(v, 6) for k, v in price_per_million(model).items()},
    }


def compact_model(model: dict, mode: str, model_notes: dict) -> dict:
    inputs, outputs = modalities(model)
    return {
        "id": model.get("id"),
        "name": model.get("name"),
        "context_length": model.get("context_length"),
        "modalities": {"input": sorted(inputs), "output": sorted(outputs)},
        "supported_parameters": model.get("supported_parameters") or [],
        "pricing": format_price(model, mode),
        "quality_tier": note_for_model(model_notes, model.get("id", "")).get("quality_tier", "unknown"),
    }


def build_sources(live_source: dict, model_notes: dict, pref: dict | None) -> list[dict]:
    sources = [live_source]
    sources.append({"type": "local_model_notes", "path": str(MODEL_NOTES_PATH)})
    if pref:
        sources.append({"type": pref.get("evidence_type", "local_project_preference"), "source": pref.get("source"), "summary": pref.get("summary")})
    return sources


def main() -> int:
    args = parse_args()
    mode = infer_mode(args.task, args.mode)
    priority = infer_priority(args.task, args.priority)
    project_prefs = load_json(PROJECT_PREFS_PATH)
    model_notes = load_json(MODEL_NOTES_PATH)
    pref = project_preference(project_prefs, args.project, mode)
    models, live_source = fetch_models(args.models_json)

    candidates = [model for model in models if supports_mode(model, mode)]
    if not candidates:
        raise SystemExit(f"No OpenRouter models matched mode={mode}.")

    max_cost = max(blended_cost(model, mode) for model in candidates) or 1.0
    ranked = sorted(
        candidates,
        key=lambda model: score_model(model, mode, priority, model_notes, pref, max_cost),
        reverse=True,
    )

    recommended = ranked[0]
    cheaper = [model for model in ranked if blended_cost(model, mode) < blended_cost(recommended, mode) and model.get("id") != recommended.get("id")]
    alternatives = [compact_model(model, mode, model_notes) for model in (cheaper[:2] + ranked[1 : max(args.limit, 1)])]
    seen: set[str] = set()
    alternatives = [alt for alt in alternatives if not (alt["id"] in seen or seen.add(alt["id"]))][: args.limit]

    current_switch = bool(args.current_model and args.current_model != recommended.get("id"))
    premium = note_for_model(model_notes, recommended.get("id", "")).get("quality_tier") == "premium"
    cheaper_exists = any(blended_cost(model, mode) < blended_cost(recommended, mode) for model in candidates)
    explicit_quality = priority == "quality"

    requires_confirmation = False
    reasons: list[str] = []
    if current_switch:
        requires_confirmation = True
        reasons.append(f"project model switch from {args.current_model} to {recommended.get('id')}")
    if premium and cheaper_exists and not explicit_quality and not args.allow_premium_without_confirmation:
        requires_confirmation = True
        reasons.append("premium model selected while cheaper plausible alternatives exist")
    if priority == "balanced" and cheaper_exists and premium and not pref:
        requires_confirmation = True
        reasons.append("balanced task has multiple plausible cost-quality choices")

    decision_notes = []
    if pref and pref.get("preferred_model") == recommended.get("id"):
        decision_notes.append(f"Local {args.project} preference favors {recommended.get('id')} for {mode}: {pref.get('summary')}")
    if priority == "cost":
        decision_notes.append("Priority is cost, so ranking penalized price strongly.")
    elif priority == "quality":
        decision_notes.append("Priority is quality, so ranking favored documented strengths and local observations.")
    else:
        decision_notes.append("Priority is balanced, so ranking used both capability fit and current OpenRouter price.")

    result = {
        "task": args.task,
        "project": args.project,
        "mode": mode,
        "priority": priority,
        "recommended_model": compact_model(recommended, mode, model_notes),
        "requires_confirmation": requires_confirmation,
        "confirmation_reason": "; ".join(reasons) if reasons else None,
        "current_model": args.current_model,
        "alternatives": alternatives,
        "decision_notes": decision_notes,
        "sources": build_sources(live_source, model_notes, pref),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
