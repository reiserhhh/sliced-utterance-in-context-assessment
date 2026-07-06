#!/usr/bin/env python
"""OP-22 LLM coder runner (blind coding v2).

Providers (4 model families — the same-family flaw of the v1 panel is retired):
  deepseek   : DeepSeek API (OpenAI-compatible; key/base from .env)
  qwen30     : qwen3:8b            @ 192.168.1.30 Ollama
  llama30    : llama3.1:8b         @ 192.168.1.30 Ollama
  mistral20  : persona-mistral-7b-q8 (UNTUNED base Mistral) @ 192.168.1.20 Ollama

Tasks: t1 (7-way label identification + salience 0-3), t2 (pair intensity).
Coders never see the key files. Temperature 0. <think> blocks stripped.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "results" / "suica_op22_item_bank_v2"
OUT_DIR = ROOT / "results" / "suica_op22_llm_coding_v2"

PROVIDERS = {
    "deepseek": {"kind": "openai", "model_env": "DEEPSEEK_LEADER_MODEL", "fallback_model": "deepseek-chat"},
    "qwen30": {"kind": "ollama", "host": "http://192.168.1.30:11434", "model": "qwen3:8b"},
    "llama30": {"kind": "ollama", "host": "http://192.168.1.30:11434", "model": "llama3.1:8b"},
    "mistral20": {"kind": "ollama", "host": "http://192.168.1.20:11434", "model": "persona-mistral-7b-q8:latest"},
}

T1_SYS = ("You are coding text excerpts for a psycholinguistics study. Choose which ONE of the "
          "seven descriptions (A-G) best characterizes what is DISTINCTIVE about the excerpt, then "
          "rate how salient that feature is: 0=absent, 1=weak, 2=clear, 3=dominant. "
          'Reply with ONLY a JSON object like {"choice":"C","salience":2} and nothing else.')
T2_SYS = ('You are coding text excerpts. Decide which text, A or B, shows MORE of the named feature. '
          'Reply with ONLY a JSON object like {"higher":"A"} and nothing else.')

THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
JSON_RE = re.compile(r"\{[^{}]*\}")


def load_env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def call_provider(cfg: dict, env: dict, system: str, user: str, *, retries: int = 2) -> str:
    for attempt in range(retries + 1):
        try:
            if cfg["kind"] == "openai":
                base = env.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
                model = env.get(cfg["model_env"]) or cfg["fallback_model"]
                r = requests.post(f"{base}/chat/completions",
                                  headers={"Authorization": f"Bearer {env['DEEPSEEK_API_KEY']}"},
                                  json={"model": model, "temperature": 0,
                                        "messages": [{"role": "system", "content": system},
                                                     {"role": "user", "content": user}]},
                                  timeout=90)
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
            r = requests.post(f"{cfg['host']}/api/chat",
                              json={"model": cfg["model"], "stream": False,
                                    "options": {"temperature": 0},
                                    "messages": [{"role": "system", "content": system},
                                                 {"role": "user", "content": user}]},
                              timeout=300)
            r.raise_for_status()
            return r.json()["message"]["content"]
        except Exception:
            if attempt >= retries:
                raise
            time.sleep(3 * (attempt + 1))
    return ""


def parse_json(raw: str) -> dict:
    raw = THINK_RE.sub("", raw or "")
    m = JSON_RE.search(raw)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}


def main() -> None:
    provider = sys.argv[sys.argv.index("--provider") + 1]
    task = sys.argv[sys.argv.index("--task") + 1]
    cfg = PROVIDERS[provider]
    env = load_env()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{provider}_{task}.csv"
    done_ids = set()
    if out_path.exists():
        done_ids = set(pd.read_csv(out_path)["id"].astype(str))
    rows = []
    if task == "t1":
        items = pd.read_csv(BANK / "t1_items.csv")
        for _, it in items.iterrows():
            if str(it["item_id"]) in done_ids:
                continue
            opts = "\n".join(f"{L}. {it[f'opt_{L}']}" for L in "ABCDEFG")
            user = f"EXCERPT:\n\"\"\"\n{it['text']}\n\"\"\"\n\nDESCRIPTIONS:\n{opts}"
            try:
                raw = call_provider(cfg, env, T1_SYS, user)
            except Exception as exc:
                raw = f"__ERROR__{exc}"
            parsed = parse_json(raw)
            choice = str(parsed.get("choice", "")).strip().upper()[:1]
            rows.append({"id": it["item_id"], "choice": choice if choice in "ABCDEFG" else "",
                         "salience": parsed.get("salience", ""), "raw": raw[:400]})
            if len(rows) % 25 == 0:
                pd.DataFrame(rows).to_csv(out_path, index=False) if not out_path.exists() else \
                    pd.concat([pd.read_csv(out_path), pd.DataFrame(rows)]).drop_duplicates("id").to_csv(out_path, index=False)
                print(f"{provider} {task}: {len(done_ids) + len(rows)} done", flush=True)
    else:
        pairs = pd.read_csv(BANK / "t2_pairs.csv")
        for _, pr in pairs.iterrows():
            if str(pr["pair_id"]) in done_ids:
                continue
            user = (f"FEATURE: {pr['construct_label']}\n\nTEXT A:\n\"\"\"\n{pr['text_A']}\n\"\"\"\n\n"
                    f"TEXT B:\n\"\"\"\n{pr['text_B']}\n\"\"\"")
            try:
                raw = call_provider(cfg, env, T2_SYS, user)
            except Exception as exc:
                raw = f"__ERROR__{exc}"
            parsed = parse_json(raw)
            higher = str(parsed.get("higher", "")).strip().upper()[:1]
            rows.append({"id": pr["pair_id"], "higher": higher if higher in "AB" else "", "raw": raw[:400]})
    if rows:
        new = pd.DataFrame(rows)
        merged = pd.concat([pd.read_csv(out_path), new]).drop_duplicates("id") if out_path.exists() else new
        merged.to_csv(out_path, index=False)
    print(f"{provider} {task}: complete, total {len(pd.read_csv(out_path))} rows")


if __name__ == "__main__":
    main()
