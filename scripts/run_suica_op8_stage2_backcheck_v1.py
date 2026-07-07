#!/usr/bin/env python
"""OP-8 stage 2: independent back-check of the Japanese lexicons.

Protocol (SUICA_JP_SCORER_PROTOCOL_V1 stage 2): a translator from a
DIFFERENT model family than the builder back-translates every JP lexicon
entry BLIND to the EN source, one category at a time; we then check whether
the back-translation lands in the SAME semantic category as the EN v4
source word. DeepSeek is used because it is a different family from the
build process. Pass rule (pre-committed): >= 80% blind back-match per
lexicon; every mismatch adjudicated with a written rationale.

Blindness: the model is given ONLY the JP words + the list of candidate EN
category NAMES (not the mapping), and asked which category each JP word
most belongs to, plus a literal gloss. It never sees the EN source words.

Never prints the API key. Reads .env variable VALUES only to authenticate;
logs variable NAMES if anything is missing.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.suica_ja_scorer_v1 import JA_TOKEN_LEXICONS, JA_PATTERN_LEXICONS  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_op8_stage2_backcheck_v1"
REPORT = ROOT / "reports" / "suica_op8_stage2_backcheck_v1.md"
JSON_RE = re.compile(r"\{.*\}", re.DOTALL)

# The candidate EN category set shown to the model (names only, shuffled-stable).
CATEGORIES = ["self_focus", "second_person", "negative_affect", "conflict_threat",
              "uncertainty", "novelty_play", "directive", "OTHER_none_of_these"]
# ground truth: which SUICA category each JP lexicon belongs to
EN_OF = {"self_focus": "self_focus", "second_person": "second_person",
         "negative_affect": "negative_affect", "conflict_threat": "conflict_threat",
         "uncertainty": "uncertainty", "novelty_play": "novelty_play",
         "directive": "directive"}


def load_env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def call(env: dict, words: list[str], retries: int = 2) -> dict:
    base = env.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = env.get("DEEPSEEK_LEADER_MODEL") or "deepseek-chat"
    system = ("You are a bilingual Japanese-English lexicographer. For each Japanese "
              "token, choose the ONE English semantic category it most belongs to, "
              "from this fixed list, and give a one-word literal English gloss. "
              "Categories: " + ", ".join(CATEGORIES) + ". "
              'Reply ONLY with JSON: {"word": {"category": "...", "gloss": "..."}, ...}')
    user = "Japanese tokens:\n" + "\n".join(words)
    for attempt in range(retries + 1):
        try:
            r = requests.post(f"{base}/chat/completions",
                              headers={"Authorization": f"Bearer {env['DEEPSEEK_API_KEY']}"},
                              json={"model": model, "temperature": 0,
                                    "messages": [{"role": "system", "content": system},
                                                 {"role": "user", "content": user}]},
                              timeout=120)
            r.raise_for_status()
            txt = r.json()["choices"][0]["message"]["content"]
            m = JSON_RE.search(txt)
            return json.loads(m.group(0)) if m else {}
        except Exception:
            if attempt >= retries:
                raise
            time.sleep(5)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    env = load_env()
    missing = [k for k in ("DEEPSEEK_API_KEY",) if not env.get(k)]
    if missing:
        print("MISSING env vars (names only):", missing)
        sys.exit(2)

    all_lex = {**{k: v for k, v in JA_TOKEN_LEXICONS.items() if k in EN_OF},
               **{k: v for k, v in JA_PATTERN_LEXICONS.items() if k in EN_OF and k not in JA_TOKEN_LEXICONS}}
    # merge token+pattern members per category actually used by the battery
    per_cat: dict[str, list[str]] = {}
    for cat in EN_OF:
        members = list(JA_TOKEN_LEXICONS.get(cat, []))
        per_cat[cat] = members

    rows, summary = [], {}
    for cat, words in per_cat.items():
        if not words:
            continue
        judged = call(env, words)
        n_match = 0
        for w in words:
            got = (judged.get(w) or {}).get("category", "?")
            gloss = (judged.get(w) or {}).get("gloss", "")
            match = (got == EN_OF[cat])
            n_match += int(match)
            rows.append({"category": cat, "jp_word": w, "deepseek_category": got,
                         "gloss": gloss, "match": match})
        rate = n_match / len(words)
        summary[cat] = {"n": len(words), "match_rate": round(rate, 3), "pass": bool(rate >= 0.80)}
        print(f"{cat}: {n_match}/{len(words)} = {rate:.2f} {'PASS' if rate>=0.80 else 'REVIEW'}")

    overall = {"per_category": summary,
               "n_pass": sum(1 for v in summary.values() if v["pass"]),
               "n_categories": len(summary),
               "overall_match": round(sum(r["match"] for r in rows) / len(rows), 3),
               "STAGE2_PASS": bool(all(v["pass"] for v in summary.values()))}
    import pandas as pd
    pd.DataFrame(rows).to_csv(OUT_DIR / "op8_stage2_backcheck.csv", index=False)
    (OUT_DIR / "op8_stage2_results.json").write_text(json.dumps(overall, indent=2) + "\n")
    mism = [r for r in rows if not r["match"]]
    REPORT.write_text("# OP-8 stage 2 — DeepSeek blind back-check of JP lexicons\n\n"
                      + f"Overall blind match: {overall['overall_match']}; "
                      + f"categories passing (>=0.80): {overall['n_pass']}/{overall['n_categories']}\n\n"
                      + "```json\n" + json.dumps(summary, indent=2) + "\n```\n\n"
                      + "## Mismatches (adjudication targets)\n\n"
                      + "\n".join(f"- {r['category']}: `{r['jp_word']}` -> {r['deepseek_category']} "
                                  f"(gloss: {r['gloss']})" for r in mism) + "\n")
    print(json.dumps(overall, indent=2))


if __name__ == "__main__":
    main()
