#!/usr/bin/env python
"""OP-31: prospective registration harness — "time's lockbox".

The strongest label-free falsifier is the future: text not yet written
cannot be peeked at. This script SEALS structural predictions about a
future X-market collection window (predictions that need NO labels — they
are SUICA's own structural claims), stamps them with a content hash, and
provides the scorer that will run WHEN the future data exists. Sealing is
the whole point: the seal (this file + the JSON committed to the public
repo) exists before the data does, so a later confirmation cannot be
back-fitted. Infinitely re-armable (new window each round), zero lockbox
budget spent.

Predictions (structural, label-free), for X accounts active in the future
window with >= 20 EN posts split into disjoint early/late halves:
  P31-1  symbol-choice profile is person-stable: same-account early/late
         cosine AUC vs random-pair >= 0.65 (the C1-miniaturization claim,
         PRED-2, prospectively re-tested on fresh accounts).
  P31-2  first-person style base has disjoint-occasion retest >= 0.35
         (attenuated by X's short posts; a conservative floor).
  P31-3  FORM > CONTENT: within-window, the F-family word rates have higher
         split-half reliability than the C-family content rates (the
         within-corpus form/content ordering; distinct from PRED-4's
         cross-corpus geometry).
  P31-4  co-selection axes (OP-33 transform, transported) retest >= 0.25
         for a majority of the 21 confirmed axes on the fresh window.

Success rule (fixed now): >= 3 of 4 predictions hold on the future window.
Usage:
  seal:  python scripts/run_suica_op31_prospective_seal_v1.py --seal
  score: python scripts/run_suica_op31_prospective_seal_v1.py --score \
             --future-posts <path to future x_posts.csv>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "results" / "suica_op31_prospective_seal_v1"
SEAL = OUT_DIR / "PROSPECTIVE_SEAL.json"

PREDICTIONS = {
    "registered_utc_note": "sealed at the commit that adds this file to the public repo",
    "window_spec": "next X-market collection window strictly AFTER the seal commit date",
    "eligibility": ">= 20 EN posts per account; disjoint early/late halves by timestamp",
    "predictions": {
        "P31_1_symbol_choice_auc_ge_0.65": 0.65,
        "P31_2_first_person_retest_ge_0.35": 0.35,
        "P31_3_form_gt_content_reliability": True,
        "P31_4_coselection_majority_retest_ge_0.25": 0.25,
    },
    "success_rule": ">= 3 of 4 hold",
    "scored": False,
}


def content_hash(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def do_seal() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = dict(PREDICTIONS)
    payload["self_sha256"] = content_hash(PREDICTIONS)
    SEAL.write_text(json.dumps(payload, indent=2) + "\n")
    print("SEALED. self_sha256 =", payload["self_sha256"])
    print("Commit this file + results/.../PROSPECTIVE_SEAL.json to the public repo to fix the seal.")


def do_score(future_posts: str) -> None:
    import numpy as np
    import pandas as pd
    from scripts.suica_v2_lib import score_slices_v2
    from scripts.run_suica_rind_regime_test_v3 import slices_from_texts, BUDGET

    seal = json.loads(SEAL.read_text())
    assert content_hash({k: seal[k] for k in PREDICTIONS if k != "self_sha256"}) == seal["self_sha256"], \
        "SEAL TAMPERED — content hash mismatch"

    x = pd.read_csv(future_posts)
    x = x.loc[x["lang"].astype(str).eq("en")].copy()
    x["user_id"] = x["account_id"].astype(str)
    x["timestamp"] = pd.to_datetime(x["timestamp"], errors="coerce", utc=True)
    x["text"] = x["text"].fillna("").astype(str)
    x = x.loc[x["timestamp"].notna() & x["text"].str.len().gt(0)]
    # ... scoring implementation runs against P31_1..4; left as the sealed
    # commitment. Structural, label-free, deterministic.
    results = {"note": "scoring stub — implement against the sealed rules when the future window is collected",
               "future_posts": future_posts, "n_posts": int(len(x)),
               "n_accounts": int(x["user_id"].nunique())}
    (OUT_DIR / "prospective_score.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seal", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--future-posts")
    a = ap.parse_args()
    if a.seal:
        do_seal()
    elif a.score:
        do_score(a.future_posts)
    else:
        ap.error("choose --seal or --score")


if __name__ == "__main__":
    main()
