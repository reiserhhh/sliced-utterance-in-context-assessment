#!/usr/bin/env python
"""Extract Tier-U comment streams for SUICA v2 validation (plan section 3, Phase 2).

Two vectorized passes over the official PANDORA dump:
pass 1 counts comments per Tier-U user; pass 2 keeps an approximately uniform
temporal subsample (cap ~400/user) for a deterministic 5,000-user subset.
Label values are never read. Tier-L users are excluded entirely.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / "data_sets" / "PANDORA_official" / "all_comments_since_2015.csv"
TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
OUT_PATH = TIER_DIR / "tier_u_comments_deep.parquet"
USECOLS = ["author", "body", "created_utc", "subreddit", "lang"]
CHUNK = 400_000
USER_SAMPLE = 2000
CAP_PER_USER = 1200
SEED = 42


def stable_fraction(value: str) -> float:
    digest = hashlib.sha1(str(value).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16**12 - 1)


def main() -> None:
    tier_u = set(pd.read_csv(TIER_DIR / "tier_u_users.csv")["user_id"].astype(str))
    counts: dict[str, int] = {}
    for chunk in pd.read_csv(DUMP, usecols=["author"], chunksize=CHUNK):
        vc = chunk.loc[chunk["author"].astype(str).isin(tier_u), "author"].astype(str).value_counts()
        for user, n in vc.items():
            counts[user] = counts.get(user, 0) + int(n)
    print(f"pass1 done: users seen={len(counts)}, total comments={sum(counts.values())}")
    target = set(sorted(counts, key=lambda u: counts[u], reverse=True)[:USER_SAMPLE])
    counts = {u: n for u, n in counts.items() if u in target}
    print(f"deep target users: {len(target)}, min count: {min(counts.values())}")

    keep_p = {u: min(1.0, CAP_PER_USER / max(1, n)) for u, n in counts.items()}
    rng = np.random.default_rng(SEED)
    parts: list[pd.DataFrame] = []
    kept = 0
    for chunk in pd.read_csv(DUMP, usecols=USECOLS, chunksize=CHUNK):
        chunk["author"] = chunk["author"].astype(str)
        mask = chunk["author"].isin(target)
        if not mask.any():
            continue
        sub = chunk.loc[mask].copy()
        sub = sub.loc[sub["lang"].fillna("en").astype(str).eq("en")]
        body = sub["body"].fillna("").astype(str)
        sub = sub.loc[body.str.len().gt(0) & ~body.isin(["[deleted]", "[removed]"])]
        if sub.empty:
            continue
        p = sub["author"].map(keep_p).fillna(0.0).to_numpy(float)
        draw = rng.random(len(sub))
        sub = sub.loc[draw < p]
        if sub.empty:
            continue
        sub["body"] = sub["body"].astype(str).str.slice(0, 1500)
        sub = sub.drop(columns=["lang"])
        parts.append(sub)
        kept += len(sub)
    out = pd.concat(parts, ignore_index=True)
    out["created_utc"] = pd.to_numeric(out["created_utc"], errors="coerce")
    out = out.dropna(subset=["created_utc"]).sort_values(["author", "created_utc"]).reset_index(drop=True)
    out.to_parquet(OUT_PATH, index=False)
    manifest = {
        "users_targeted": len(target),
        "users_with_rows": int(out["author"].nunique()),
        "rows": int(len(out)),
        "cap_per_user": CAP_PER_USER,
        "seed": SEED,
        "median_rows_per_user": float(out.groupby("author").size().median()),
    }
    (TIER_DIR / "tier_u_comments_deep_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
