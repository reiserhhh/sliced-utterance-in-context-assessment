#!/usr/bin/env python
"""Run or package independent LLM coding for a SUICA blind-validation batch.

The script has two modes:

1. `dry_run`: writes the exact JSONL requests and a blank coder template. This
   is the default and does not require an API key.
2. `deepseek` / `openai`: sends blind text batches to a chat-completions
   compatible endpoint and writes an evaluator-compatible coder CSV.
3. `ollama`: sends blind text batches to a local or remote Ollama `/api/chat`
   endpoint without requiring an API key.

The generated ratings intentionally contain only blind item IDs, 0-3 construct
ratings, and notes. Factor names, poles, source families, author IDs, and SUICA
scores are never included in the prompt payload.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_suica_blind_construct_coding_v1 import DIMENSIONS as DEFAULT_DIMENSIONS  # noqa: E402


DIMENSIONS = list(DEFAULT_DIMENSIONS)


ITEMS_PATH = ROOT / "results" / "suica_independent_blind_validation_batch_v1" / "coder_A_items.csv"
OUT_DIR = ROOT / "results" / "suica_independent_llm_coding_v1" / "coder_A"
REPORT_PATH = ROOT / "reports" / "suica_independent_llm_coding_coder_A_v1.md"


PROVIDER_DEFAULTS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/chat/completions",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4.1-mini",
        "api_key_env": "OPENAI_API_KEY",
    },
    "ollama": {
        "base_url": "http://127.0.0.1:11434/api/chat",
        "model": "persona-mistral-7b:latest",
        "api_key_env": "",
    },
}


SYSTEM_PROMPT = """You are an independent blind construct coder for a text-behavior measurement study.

You will rate short text excerpts. Do not infer hidden factor names, source dataset, author identity, Big5, MBTI, or any personality label. Score only the visible text behavior.

For every item, return ratings from 0 to 3 for each dimension:
0 = absent/negligible, 1 = weak/implicit, 2 = clear/repeated, 3 = dominant/highly salient.

Return JSON only. Do not include markdown or explanations outside JSON."""


DIMENSION_GUIDE = {
    "agency": "active choice, control, goal pursuit, self-directed action",
    "communion": "warmth, care, affiliation, support, relationship orientation",
    "mentalization": "explicit mental-state language such as think, feel, know, want, understand",
    "temporal_integration": "past/future sequencing, life continuity, autobiographical linking",
    "directive_interpersonal": "direct advice, instruction, second-person guidance",
    "self_focus": "first-person self-reference and self-positioning",
    "other_focus": "focus on other people, groups, third-person social actors",
    "affect_tension": "negative affect, uncertainty, conflict, threat, distress",
    "redemption_growth": "improvement, learning, recovery, growth after difficulty",
    "social_evaluation": "comparison, judgment, status, norm, evaluation of people/society",
    "novelty_play": "play, exploration, novelty, creative or task engagement",
    "positive_affect": "positive emotional tone, enjoyment, optimism, enthusiasm, appreciation",
    "negative_affect": "negative emotional tone, distress, frustration, sadness, anger, fear",
    "affect_balance": "overall positive-vs-negative emotional balance and emotional orientation",
    "uncertainty": "uncertainty, doubt, ambiguity, possibility, lack of closure",
    "certainty": "certainty, confidence, closure, definite judgment or resolved stance",
    "conflict_threat": "conflict, danger, risk, threat, loss pressure, adversarial tension",
    "affective_stability": "stable, clear, regulated affect across the excerpt or excerpt bundle",
}
RATING_KEY_ALIASES = {
    "rating": "ratings",
    "scores": "ratings",
}
DIMENSION_ALIASES = {
    "agenacy": "agency",
    "agentic": "agency",
    "communication": "communion",
    "communality": "communion",
    "community": "communion",
    "directive": "directive_interpersonal",
    "interpersonal_directive": "directive_interpersonal",
    "self": "self_focus",
    "other": "other_focus",
    "affect": "affect_tension",
    "tension": "affect_tension",
    "redemption": "redemption_growth",
    "growth": "redemption_growth",
    "evaluation": "social_evaluation",
    "novelty": "novelty_play",
    "play": "novelty_play",
    "positive": "positive_affect",
    "negative": "negative_affect",
    "uncertain": "uncertainty",
    "certain": "certainty",
    "threat": "conflict_threat",
    "conflict": "conflict_threat",
    "stability": "affective_stability",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run/package SUICA independent LLM coder v1.")
    parser.add_argument("--items", default=str(ITEMS_PATH), help="Blind coder item CSV.")
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--coder-id", default="llm_coder_A")
    parser.add_argument("--provider", choices=["dry_run", "deepseek", "openai", "ollama"], default="dry_run")
    parser.add_argument("--model", default="", help="Override provider model.")
    parser.add_argument("--base-url", default="", help="Override chat-completions URL.")
    parser.add_argument("--api-key-env", default="", help="Override API key environment variable name.")
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--max-items", type=int, default=0, help="Limit item count for pilot runs. 0 = all.")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--request-timeout", type=int, default=120)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument(
        "--dimension",
        action="append",
        default=[],
        help="Override rating dimensions. Repeatable. Defaults to *_0_to_3 columns in --items, then legacy SUICA dimensions.",
    )
    return parser.parse_args()


def validate_items(items: pd.DataFrame) -> pd.DataFrame:
    required = {"blind_item_id", "text_excerpt"}
    missing = required.difference(items.columns)
    if missing:
        raise ValueError(f"missing required item columns: {sorted(missing)}")
    out = items.copy()
    out["blind_item_id"] = out["blind_item_id"].astype(str)
    out["text_excerpt"] = out["text_excerpt"].fillna("").astype(str)
    if out["blind_item_id"].duplicated().any():
        dupes = sorted(out.loc[out["blind_item_id"].duplicated(), "blind_item_id"].unique())
        raise ValueError(f"duplicate blind_item_id values: {dupes[:5]}")
    return out


def infer_dimensions(items: pd.DataFrame, explicit_dimensions: list[str]) -> list[str]:
    if explicit_dimensions:
        return list(dict.fromkeys(str(dim).strip() for dim in explicit_dimensions if str(dim).strip()))
    inferred = [col[: -len("_0_to_3")] for col in items.columns if col.endswith("_0_to_3")]
    if inferred:
        return list(dict.fromkeys(inferred))
    return list(DEFAULT_DIMENSIONS)


def load_dotenv_if_present(path: Path = ROOT / ".env") -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def chunk_frame(frame: pd.DataFrame, batch_size: int) -> list[pd.DataFrame]:
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    return [frame.iloc[start : start + batch_size].copy() for start in range(0, len(frame), batch_size)]


def build_user_prompt(batch: pd.DataFrame) -> str:
    dimension_lines = "\n".join(
        f"- {dimension}: {DIMENSION_GUIDE.get(dimension, 'rate the visible text behavior for this named dimension')}"
        for dimension in DIMENSIONS
    )
    item_payload = [
        {"blind_item_id": row.blind_item_id, "text_excerpt": row.text_excerpt}
        for row in batch[["blind_item_id", "text_excerpt"]].itertuples(index=False)
    ]
    schema = {
        "items": [
            {
                "blind_item_id": "SUICA-IB-0001",
                "ratings": {dimension: 0 for dimension in DIMENSIONS},
                "coder_notes": "optional short note",
            }
        ]
    }
    return (
        "Rate the following blind text excerpts.\n\n"
        "Dimensions:\n"
        f"{dimension_lines}\n\n"
        "Output schema. Use these exact keys: `items`, `blind_item_id`, `ratings`, every dimension key exactly as listed, and `coder_notes`.\n"
        "Do not rename `ratings` to `rating`. Do not rename dimensions.\n"
        f"{json.dumps(schema, ensure_ascii=False)}\n\n"
        "Items:\n"
        f"{json.dumps(item_payload, ensure_ascii=False, indent=2)}"
    )


def build_request_record(batch: pd.DataFrame, *, batch_index: int, coder_id: str, model: str, temperature: float) -> dict[str, Any]:
    return {
        "batch_index": batch_index,
        "coder_id": coder_id,
        "model": model,
        "blind_item_ids": batch["blind_item_id"].astype(str).tolist(),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(batch)},
        ],
        "temperature": temperature,
    }


def extract_json_payload(text: str) -> Any:
    """Extract JSON from a model response that should already be JSON-only."""

    stripped = str(text).strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped, flags=re.IGNORECASE).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", stripped, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(1))


def coerce_rating(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if numeric < 0:
        numeric = 0.0
    if numeric > 3:
        numeric = 3.0
    return numeric


def normalize_ratings_object(item: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    warnings: list[str] = []
    ratings = item.get("ratings")
    if not isinstance(ratings, dict):
        for alias, canonical in RATING_KEY_ALIASES.items():
            candidate = item.get(alias)
            if canonical == "ratings" and isinstance(candidate, dict):
                ratings = candidate
                warnings.append(f"rating_key_alias:{alias}->ratings")
                break
    if not isinstance(ratings, dict):
        return None, warnings
    normalized: dict[str, Any] = {}
    for key, value in ratings.items():
        normalized_key = str(key).strip()
        canonical_key = DIMENSION_ALIASES.get(normalized_key, normalized_key)
        if canonical_key != normalized_key:
            warnings.append(f"dimension_alias:{normalized_key}->{canonical_key}")
        normalized[canonical_key] = value
    return normalized, warnings


def parse_llm_ratings_response(response_text: str, *, expected_ids: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payload = extract_json_payload(response_text)
    if isinstance(payload, dict) and "items" in payload:
        items = payload["items"]
    elif isinstance(payload, list):
        items = payload
    else:
        raise ValueError("LLM response must be a list or an object with an items list")
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen: set[str] = set()
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append({"item_index": idx, "blind_item_id": "", "error": "item_not_object"})
            continue
        blind_id = str(item.get("blind_item_id", "")).strip()
        if blind_id not in expected_ids:
            errors.append({"item_index": idx, "blind_item_id": blind_id, "error": "unexpected_blind_item_id"})
            continue
        ratings, warnings = normalize_ratings_object(item)
        if not isinstance(ratings, dict):
            errors.append({"item_index": idx, "blind_item_id": blind_id, "error": "ratings_not_object"})
            continue
        row: dict[str, Any] = {"blind_item_id": blind_id}
        missing_dims: list[str] = []
        for dimension in DIMENSIONS:
            rating = coerce_rating(ratings.get(dimension))
            if rating is None:
                missing_dims.append(dimension)
            row[f"{dimension}_0_to_3"] = rating
        row["coder_notes"] = str(item.get("coder_notes", "") or "")
        rows.append(row)
        seen.add(blind_id)
        if warnings:
            errors.append(
                {
                    "item_index": idx,
                    "blind_item_id": blind_id,
                    "error": "schema_alias_normalized",
                    "detail": "; ".join(warnings),
                }
            )
        if missing_dims:
            errors.append(
                {
                    "item_index": idx,
                    "blind_item_id": blind_id,
                    "error": "missing_or_invalid_dimensions",
                    "detail": "; ".join(missing_dims),
                }
            )
    for missing_id in sorted(expected_ids.difference(seen)):
        errors.append({"item_index": -1, "blind_item_id": missing_id, "error": "missing_item_in_response"})
    return rows, errors


def call_chat_completion(
    request_record: dict[str, Any],
    *,
    provider: str,
    base_url: str,
    api_key: str,
    timeout: int,
    max_retries: int,
) -> dict[str, Any]:
    payload = {
        "model": request_record["model"],
        "messages": request_record["messages"],
        "temperature": request_record["temperature"],
        "response_format": {"type": "json_object"},
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "project-persona-suica-coder/1.0",
    }
    last_error = ""
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(base_url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                content = data["choices"][0]["message"]["content"]
                return {"ok": True, "provider": provider, "raw_response": data, "content": content, "attempt": attempt + 1}
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            if attempt < max_retries:
                time.sleep(min(2**attempt, 8))
    return {"ok": False, "provider": provider, "error": last_error, "content": "", "attempt": max_retries + 1}


def call_ollama_chat(
    request_record: dict[str, Any],
    *,
    base_url: str,
    timeout: int,
    max_retries: int,
) -> dict[str, Any]:
    rating_properties = {dimension: {"type": "number", "minimum": 0, "maximum": 3} for dimension in DIMENSIONS}
    response_schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "blind_item_id": {"type": "string"},
                        "ratings": {
                            "type": "object",
                            "properties": rating_properties,
                            "required": DIMENSIONS,
                            "additionalProperties": False,
                        },
                        "coder_notes": {"type": "string"},
                    },
                    "required": ["blind_item_id", "ratings"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["items"],
        "additionalProperties": False,
    }
    payload = {
        "model": request_record["model"],
        "messages": request_record["messages"],
        "stream": False,
        "format": response_schema,
        "options": {"temperature": request_record["temperature"]},
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "project-persona-suica-coder/1.0"}
    last_error = ""
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(base_url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                content = data.get("message", {}).get("content", "")
                return {"ok": bool(content), "provider": "ollama", "raw_response": data, "content": content, "attempt": attempt + 1}
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            if attempt < max_retries:
                time.sleep(min(2**attempt, 8))
    return {"ok": False, "provider": "ollama", "error": last_error, "content": "", "attempt": max_retries + 1}


def blank_coder_template(items: pd.DataFrame) -> pd.DataFrame:
    out = items[["blind_item_id", "text_excerpt"]].copy()
    for dimension in DIMENSIONS:
        out[f"{dimension}_0_to_3"] = ""
    out["coder_notes"] = ""
    return out


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_report(
    path: Path,
    *,
    provider: str,
    coder_id: str,
    item_count: int,
    batch_count: int,
    parsed_count: int,
    error_count: int,
    model: str,
    out_dir: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SUICA Independent LLM Coder Run v1",
        "",
        "## Purpose",
        "",
        "This artifact standardizes blind construct coding for SUICA. It produces evaluator-compatible coder ratings when an API provider is used, or an auditable request package in dry-run mode.",
        "",
        "## Run Summary",
        "",
        f"- provider: `{provider}`",
        f"- coder_id: `{coder_id}`",
        f"- model: `{model}`",
        f"- blind items: `{item_count}`",
        f"- request batches: `{batch_count}`",
        f"- parsed rated items: `{parsed_count}`",
        f"- parse/API errors: `{error_count}`",
        "",
        "## Evidence Status",
        "",
        "- `dry_run` is not construct evidence; it only proves the blind prompt package is ready.",
        "- API/provider runs are still weaker than human coding unless two isolated coders/models are run and evaluator agreement is acceptable.",
        "- The hidden key must not be given to this script; only coder-facing item files are valid inputs.",
        "",
        "## Artifacts",
        "",
        f"- `{out_dir / 'llm_coding_requests.jsonl'}`",
        f"- `{out_dir / 'coder_ratings.csv'}`",
        f"- `{out_dir / 'coder_ratings_template.csv'}`",
        f"- `{out_dir / 'llm_raw_responses.jsonl'}`",
        f"- `{out_dir / 'parser_errors.csv'}`",
        f"- `{out_dir / 'run_config.json'}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    items = validate_items(pd.read_csv(args.items))
    global DIMENSIONS
    DIMENSIONS = infer_dimensions(items, args.dimension)
    if args.max_items > 0:
        items = items.head(args.max_items).copy()

    provider_defaults = PROVIDER_DEFAULTS.get(args.provider, {})
    model = args.model or provider_defaults.get("model", "dry-run")
    base_url = args.base_url or provider_defaults.get("base_url", "")
    api_key_env = args.api_key_env or provider_defaults.get("api_key_env", "")

    requests = [
        build_request_record(batch, batch_index=idx, coder_id=args.coder_id, model=model, temperature=args.temperature)
        for idx, batch in enumerate(chunk_frame(items, args.batch_size), start=1)
    ]
    write_jsonl(out_dir / "llm_coding_requests.jsonl", requests)
    blank_coder_template(items).to_csv(out_dir / "coder_ratings_template.csv", index=False)

    raw_responses: list[dict[str, Any]] = []
    parsed_rows: list[dict[str, Any]] = []
    parser_errors: list[dict[str, Any]] = []

    if args.provider != "dry_run":
        load_dotenv_if_present()
        api_key = os.environ.get(api_key_env, "") if api_key_env else ""
        if args.provider in {"deepseek", "openai"} and not api_key:
            raise RuntimeError(f"Missing API key in environment variable {api_key_env}")
        for request_record in requests:
            if args.provider == "ollama":
                response = call_ollama_chat(
                    request_record,
                    base_url=base_url,
                    timeout=args.request_timeout,
                    max_retries=args.max_retries,
                )
            else:
                response = call_chat_completion(
                    request_record,
                    provider=args.provider,
                    base_url=base_url,
                    api_key=api_key,
                    timeout=args.request_timeout,
                    max_retries=args.max_retries,
                )
            raw_responses.append(
                {
                    "batch_index": request_record["batch_index"],
                    "blind_item_ids": request_record["blind_item_ids"],
                    "ok": response["ok"],
                    "attempt": response["attempt"],
                    "content": response.get("content", ""),
                    "error": response.get("error", ""),
                    "raw_response": response.get("raw_response", {}),
                }
            )
            if response["ok"]:
                rows, errors = parse_llm_ratings_response(
                    response["content"],
                    expected_ids=set(request_record["blind_item_ids"]),
                )
                parsed_rows.extend(rows)
                for error in errors:
                    error["batch_index"] = request_record["batch_index"]
                    parser_errors.append(error)
            else:
                for blind_id in request_record["blind_item_ids"]:
                    parser_errors.append(
                        {
                            "batch_index": request_record["batch_index"],
                            "blind_item_id": blind_id,
                            "error": "api_call_failed",
                            "detail": response.get("error", ""),
                        }
                    )
            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)

    write_jsonl(out_dir / "llm_raw_responses.jsonl", raw_responses)
    pd.DataFrame(parser_errors).to_csv(out_dir / "parser_errors.csv", index=False)
    if parsed_rows:
        ratings = pd.DataFrame(parsed_rows)
        ratings = ratings.drop_duplicates(subset=["blind_item_id"], keep="last")
        ordered = items[["blind_item_id"]].merge(ratings, on="blind_item_id", how="left")
        ordered.to_csv(out_dir / "coder_ratings.csv", index=False)
    else:
        pd.DataFrame(columns=["blind_item_id", *[f"{d}_0_to_3" for d in DIMENSIONS], "coder_notes"]).to_csv(
            out_dir / "coder_ratings.csv",
            index=False,
        )

    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "items": str(Path(args.items)),
                "provider": args.provider,
                "coder_id": args.coder_id,
                "model": model,
                "base_url": base_url,
                "api_key_env": api_key_env,
                "batch_size": args.batch_size,
                "max_items": args.max_items,
                "temperature": args.temperature,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(
        Path(args.report_path),
        provider=args.provider,
        coder_id=args.coder_id,
        item_count=len(items),
        batch_count=len(requests),
        parsed_count=len(parsed_rows),
        error_count=len(parser_errors),
        model=model,
        out_dir=out_dir,
    )
    print("SUICA independent LLM coder package complete.")
    print(f"provider={args.provider} items={len(items)} batches={len(requests)} parsed={len(parsed_rows)} errors={len(parser_errors)}")
    print(f"output_dir={out_dir}")


if __name__ == "__main__":
    main()
