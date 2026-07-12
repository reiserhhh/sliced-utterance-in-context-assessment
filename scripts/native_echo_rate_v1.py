#!/usr/bin/env python
"""Assistant-echo rate, reference implementation (native corpus PROTOCOL_V1 section 5).

echo(turn) = share of the participant turn's content 3-grams that appeared in ANY
prior interviewer turn of the same dialogue; participant block echo rate = mean over
that participant's turns. Ceiling is set at pilot (median + 2*MAD) and preregistered.

Input: JSONL records per PROTOCOL_V1 section 3 (block == "dialogue", "turns" list).
Usage: native_echo_rate_v1.py records.jsonl  ->  per-pid echo rates + summary (stdout).
Label-free; no anchors are read.
"""
from __future__ import annotations

import json
import re
import sys

TOKEN_RE = re.compile(r"\w+(?:['’-]\w+)?", re.UNICODE)
STOP_EN = set("the a an and or but if of to in on at for with is are was were be been "
              "i you he she it we they my your this that not no do does did have has".split())


def content_tokens(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text) if t.lower() not in STOP_EN]


def ngrams(tokens: list[str], n: int = 3) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def dialogue_echo(turns: list[dict]) -> float | None:
    seen: set[tuple[str, ...]] = set()
    rates = []
    for turn in turns:
        grams = ngrams(content_tokens(turn.get("text", "")))
        if turn.get("role") == "interviewer":
            seen |= grams
        elif turn.get("role") == "participant" and grams:
            rates.append(len(grams & seen) / len(grams))
    return sum(rates) / len(rates) if rates else None


def main(path: str) -> None:
    per_pid: dict[str, list[float]] = {}
    with open(path) as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("block") != "dialogue":
                continue
            e = dialogue_echo(rec.get("turns", []))
            if e is not None:
                per_pid.setdefault(rec["pid"], []).append(e)
    rates = sorted(sum(v) / len(v) for v in per_pid.values())
    for pid, v in per_pid.items():
        print(f"{pid}\t{sum(v)/len(v):.4f}")
    if rates:
        mid = rates[len(rates) // 2]
        mad = sorted(abs(r - mid) for r in rates)[len(rates) // 2]
        print(f"# n={len(rates)} median={mid:.4f} MAD={mad:.4f} "
              f"pilot-ceiling(median+2MAD)={mid + 2 * mad:.4f}")


if __name__ == "__main__":
    main(sys.argv[1])
