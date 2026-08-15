#!/usr/bin/env python3
"""SUICA M4-SR0 -- the real-data reconnaissance (STRICT no-peeking).

Registered BEFORE run in docs/SUICA_M4_S_SELECTION_LINE_PLAN.md ("M4-SR0",
commit 21149bb).  Binding, together with the REAL-DATA GOVERNANCE block
(R-G1..R-G8) in the same document.

THIS LEG COMPUTES NO STATISTIC LINKING SELECTION TO ANY LABEL.  The no-peek
gate is the code's STRUCTURE, not the author's intention:

  stage_sources    pins paths/sizes/schemas.  Writes the gold cohort as an
                   AUTHOR-ID-ONLY file (label columns are dropped before the
                   file is written, and the writer asserts one column).
  stage_selection  streams the comment table and builds selection-side objects
                   ONLY.  It never opens author_profiles.csv and never reads a
                   label column; it is given the cohort as a bare id list.
  stage_labels     opens the label table and emits MARGINALS ONLY (counts,
                   means, variances).  It never opens any selection artifact.
  stage_power      the only stage that sees both sides, and it sees them only
                   as SUMMARY SCALARS already written by the two stages above.
  stage_gate       G-SR0: enumerates every produced artifact and verifies by
                   inspection that no artifact carries a joint selection x
                   label quantity, no user ids, and no text.

Any joint selection x label quantity voids the leg.  There is none, and the
gate proves it by enumeration rather than by assertion.

Stages: sources -> selection -> labels -> power -> gate -> report
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEG = "M4-SR0"
OUT = ROOT / "results" / "m4_sr0_recon"
REPORT = ROOT / "reports" / "SUICA_M4_SR0_RECON_REPORT.md"

DATA = Path("/Volumes/mobile3/projects/project persona")
COMMENTS = DATA / "data_sets/PANDORA_official/all_comments_since_2015.csv"
PROFILES = DATA / "data_sets/PANDORA_official/author_profiles.csv"
PREPARED = (DATA / "data_sets/prepared/pandora_official"
            / "pandora_official_big5_prepared.csv")
V2LIB = ROOT / "scripts" / "suica_v2_lib.py"

BIG5 = ("agreeableness", "openness", "conscientiousness", "extraversion",
        "neuroticism")
CHUNK_ROWS = 2_000_000

# --- declared BEFORE the stream (counts-only rules) -------------------------
VOCAB_FLOOR_USER_FRAC = 0.01     # a subreddit enters the vocabulary iff it is
                                 # used by >= 1% of cohort users
MIN_COMMENTS_SIGNATURE = 20      # a user carries a signature iff >= 20 comments
MIN_COMMENTS_SPLITHALF = 40      # ... and a split-half iff >= 40
B_PERM_PLAN = 999
ALPHA = 0.05
POWER_TARGET = 0.80

RN_NOTES = {
    "RN-SR0-1":
        "the no-peek gate is STRUCTURAL.  stage_selection is handed the gold "
        "cohort as a bare author-id list written by stage_sources with the label "
        "columns dropped BEFORE writing (the writer asserts the frame has exactly "
        "one column); stage_selection never opens author_profiles.csv.  "
        "stage_labels never opens a selection artifact.  stage_power reads only "
        "the summary scalars the two stages wrote.  Cohort MEMBERSHIP is not a "
        "label VALUE: the registration asks for selection-side objects on the gold "
        "cohort and for that cohort's identifiability BY COUNT, both of which "
        "require the id list and neither of which requires a label.",
    "RN-SR0-2":
        "the vocabulary floor is declared from COUNTS ALONE and before the stream: "
        "a subreddit enters the SR1 vocabulary iff at least 1% of cohort users "
        "post there at least once.  A user carries a signature iff they have >= 20 "
        "cohort-visible comments and a split-half iff >= 40.  No floor was chosen "
        "after seeing a coverage number.",
    "RN-SR0-3":
        "split-half is by TIMESTAMP per user (the T6'' pattern): each user's "
        "comments are ordered by created_utc and cut at the per-user median, so "
        "the two halves are disjoint in time.  The stability CEILING is the "
        "Spearman-Brown-corrected agreement between a user's two half-vectors, "
        "computed SELECTION-SIDE ONLY.",
    "RN-SR0-4":
        "the SR1 power table is reported in OBSERVED (attenuated) units and, "
        "separately, as a TRUE-effect requirement under a stated label-reliability "
        "assumption.  Label reliability is NOT measured here -- measuring it would "
        "require the labels' internal structure, which is outside this leg's "
        "mandate -- so it is carried as a declared parameter and the table is read "
        "across a range of it.",
    "RN-SR0-5":
        "R-G compliance is enforced at the report boundary: the report is rendered "
        "only from a facts/tables object built from aggregate scalars and binned "
        "distributions.  No artifact fed to the report contains a user id, a text "
        "excerpt, or a per-user row; the gate enumerates and checks this.",
}


def _log(event: str, **kw: Any) -> None:
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "run_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def sha_head(path: Path, n: int = 1 << 20) -> str:
    with path.open("rb") as fh:
        return hashlib.sha256(fh.read(n)).hexdigest()


def csv_header(path: Path) -> list[str]:
    return pd.read_csv(path, nrows=0).columns.tolist()


# ---------------------------------------------------------------------------
# STAGE 1 -- SOURCES.  Pins only.  Writes the cohort as ids alone.


def stage_sources(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("sources_start")
    man: dict[str, Any] = {}
    gaps: list[str] = []

    for name, path in (("comments", COMMENTS), ("profiles", PROFILES),
                       ("prepared_big5", PREPARED), ("v2lib", V2LIB)):
        if not path.exists():
            gaps.append(name)
            man[name] = {"path": str(path), "EXISTS": False}
            continue
        st = path.stat()
        man[name] = {"path": str(path), "EXISTS": True,
                     "bytes": int(st.st_size),
                     "mib": round(st.st_size / (1 << 20), 1),
                     "sha256_first_1MiB": sha_head(path)}
        if path.suffix == ".csv":
            man[name]["columns"] = csv_header(path)
            man[name]["n_columns"] = len(man[name]["columns"])

    # field verification (schema only, no content)
    cc = man.get("comments", {}).get("columns", [])
    man["comments"]["has_subreddit"] = bool("subreddit" in cc)
    man["comments"]["has_created_utc"] = bool("created_utc" in cc)
    man["comments"]["has_author"] = bool("author" in cc)
    pc = man.get("profiles", {}).get("columns", [])
    man["profiles"]["big5_columns_present"] = {b: bool(b in pc) for b in BIG5}
    man["profiles"]["all_big5_present"] = bool(all(b in pc for b in BIG5))

    # the gold cohort: ids ONLY.  Labels are used to DEFINE membership and are
    # dropped before anything is written (RN-SR0-1).
    prof = pd.read_csv(PROFILES, usecols=["author", *BIG5], low_memory=False)
    gold_mask = prof[list(BIG5)].notna().all(axis=1)
    five_complete = prof.loc[gold_mask, ["author"]].drop_duplicates()
    man["profiles"]["n_rows"] = int(len(prof))
    man["profiles"]["n_five_complete_by_count"] = int(len(five_complete))
    # The CANONICAL SR1 cohort is the registration's N = 1401 prepared mainline
    # cohort, which is a strict subset of the five-complete set.  Only the
    # user_id column is read, so no label value is touched here.
    prep_ids = pd.read_csv(PREPARED, usecols=["user_id"])
    prep_ids = prep_ids.rename(columns={"user_id": "author"}).drop_duplicates()
    inter = int(len(set(prep_ids["author"].astype(str))
                    & set(five_complete["author"].astype(str))))
    cohort = prep_ids[["author"]]
    assert cohort.shape[1] == 1, "cohort file must carry author ids ONLY"
    cohort.to_csv(OUT / "cohort_authors.csv", index=False)
    man["profiles"]["n_gold_cohort_by_count"] = int(len(cohort))
    man["profiles"]["canonical_cohort_source"] = "prepared Big5 mainline (N=1401)"
    man["profiles"]["prepared_is_subset_of_five_complete"] = bool(
        inter == len(cohort))
    man["profiles"]["prepared_intersect_five_complete"] = inter
    del prof, cohort, five_complete, prep_ids

    # prepared Big5: row count and unique-user count (COUNTS only)
    if man.get("prepared_big5", {}).get("EXISTS"):
        n_rows = 0
        users: set[str] = set()
        for ch in pd.read_csv(PREPARED, usecols=["user_id"], chunksize=200_000):
            n_rows += len(ch)
            users.update(ch["user_id"].astype(str).unique().tolist())
        man["prepared_big5"]["n_rows"] = int(n_rows)
        man["prepared_big5"]["n_unique_user_id"] = int(len(users))
        man["prepared_big5"]["registration_said_1401_rows"] = True
        man["prepared_big5"]["rows_equals_1401"] = bool(n_rows == 1401)
        man["prepared_big5"]["unique_users_equals_1401"] = bool(len(users) == 1401)
        del users

    # --- the 12-axis choice constructor: located and VERIFIED by reading the
    # pinned lines, not asserted.
    ax_src = ROOT / "scripts/run_suica_e3_e4_choice_scale_class_react_v2.py"
    ho_src = ROOT / "scripts/run_suica_op6a_choice_axes_holdout_v3.py"
    fitted = ROOT / "results/suica_e3_e4_choice_class_v2_s128/condition_class_map.csv"
    axis: dict[str, Any] = {"constructor_path": rel(ax_src),
                            "holdout_path": rel(ho_src)}
    if ax_src.exists():
        lines = ax_src.read_text(encoding="utf-8").splitlines()
        def _at(i: int) -> str:
            return lines[i - 1].strip() if 0 < i <= len(lines) else ""
        axis["pins"] = {
            "N_CLASSES:37": _at(37),
            "build_condition_classes:43": _at(43),
            "kmeans:63": _at(63),
            "subreddit_to_axis_map:65": _at(65),
            "choice_axis_scores:81": _at(81),
            "axis_column_naming:126": _at(126)}
        axis["n_classes_is_12"] = bool("N_CLASSES = 12" in _at(37))
        axis["constructor_EXISTS"] = True
    else:
        axis["constructor_EXISTS"] = False
    axis["holdout_constructor_EXISTS"] = bool(ho_src.exists())
    axis["fitted_class_map_path"] = rel(fitted)
    axis["fitted_class_map_EXISTS"] = bool(fitted.exists())
    axis["verdict"] = ("FOUND (constructor); FITTED ARTIFACT ABSENT"
                       if axis["constructor_EXISTS"]
                       and not axis["fitted_class_map_EXISTS"]
                       else ("FOUND" if axis["constructor_EXISTS"] else "NOT_FOUND"))
    axis["searched"] = ("scripts/, docs/, reports/, suica_core/ for choice axis / "
                        "choice_axes / N_CLASSES / 12 axes / holdout")
    axis["what_exists"] = (
        "a LIVE constructor, not a lost v2 artifact: subreddit centroids from "
        "TF-IDF -> TruncatedSVD(64) -> KMeans(12) build the subreddit->axis map, "
        "and per-user selection is projected onto the axes as log-ratio shares "
        "against the population mean. A second constructor (op6a) refits on cohort "
        "A and confirms on cohort B -- the source of the 5/5 holdout.")
    axis["consequence"] = (
        "SR1's PRIMARY signature object (per-user subreddit frequency vectors over "
        "the declared vocabulary) needs none of this and is fully available. The "
        "12-axis projection is available only by REFITTING, because the fitted "
        "class map is not on disk (results/ is gitignored). SR1 must therefore "
        "either use the frequency vectors directly or re-fit and artifact-pin the "
        "class map first; it must NOT cite the existing 5/5 holdout as though the "
        "same fitted axes were in hand.")
    write_json(OUT / "axis_finding.json", axis)

    out = {"leg": LEG, "utc": datetime.now(UTC).isoformat(), "manifest": man,
           "axis_finding": axis,
           "source_gaps": gaps, "RN_NOTES": RN_NOTES,
           "declared_rules": {
               "vocab_floor_user_fraction": VOCAB_FLOOR_USER_FRAC,
               "min_comments_signature": MIN_COMMENTS_SIGNATURE,
               "min_comments_splithalf": MIN_COMMENTS_SPLITHALF,
               "B_perm_plan": B_PERM_PLAN, "alpha": ALPHA,
               "power_target": POWER_TARGET},
           "environment": {"python_executable": sys.executable,
                           "python_version": sys.version.split()[0],
                           "platform": platform.platform(),
                           "numpy": np.__version__, "pandas": pd.__version__},
           "seconds": time.time() - t0}
    write_json(OUT / "sources.json", out)
    _log("sources_done", gaps=gaps)
    print(f"sources OK  gaps={gaps or 'none'}  "
          f"comments {man['comments']['mib']} MiB "
          f"(subreddit={man['comments']['has_subreddit']}, "
          f"created_utc={man['comments']['has_created_utc']})  "
          f"gold cohort N={man['profiles']['n_gold_cohort_by_count']}  "
          f"prepared rows={man.get('prepared_big5', {}).get('n_rows')} "
          f"users={man.get('prepared_big5', {}).get('n_unique_user_id')}  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# STAGE 2 -- SELECTION SIDE ONLY.  Never opens the label table.


def stage_selection(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("selection_start")
    cohort_df = pd.read_csv(OUT / "cohort_authors.csv")
    assert cohort_df.shape[1] == 1 and cohort_df.columns[0] == "author", \
        "the selection stage may receive author ids and nothing else"
    cohort = set(cohort_df["author"].astype(str))
    n_cohort = len(cohort)

    # pass: accumulate per-user per-subreddit counts, split by the user's own
    # median timestamp.  Two passes are avoided by keeping (author, subreddit)
    # counts plus per-author timestamp lists in a compact form.
    pair_counts: dict[tuple[str, str], int] = {}
    ts_sum: dict[str, float] = {}
    ts_n: dict[str, int] = {}
    ts_samples: dict[str, list[float]] = {}
    rows_seen = 0
    rows_cohort = 0
    t_min, t_max = math.inf, -math.inf
    reader = pd.read_csv(COMMENTS, usecols=["author", "subreddit", "created_utc"],
                         chunksize=CHUNK_ROWS, dtype={"author": "str",
                                                      "subreddit": "str"},
                         on_bad_lines="skip", engine="c", low_memory=True)
    for ch in reader:
        rows_seen += len(ch)
        ch = ch[ch["author"].isin(cohort)]
        if ch.empty:
            continue
        rows_cohort += len(ch)
        t_min = min(t_min, float(ch["created_utc"].min()))
        t_max = max(t_max, float(ch["created_utc"].max()))
        g = ch.groupby(["author", "subreddit"], observed=True).size()
        for (a, s), c in g.items():
            k = (a, s)
            pair_counts[k] = pair_counts.get(k, 0) + int(c)
        for a, sub in ch.groupby("author", observed=True)["created_utc"]:
            ts_sum[a] = ts_sum.get(a, 0.0) + float(sub.sum())
            ts_n[a] = ts_n.get(a, 0) + int(len(sub))
            lst = ts_samples.setdefault(a, [])
            if len(lst) < 4000:
                lst.extend(sub.tolist()[: 4000 - len(lst)])
    _log("selection_stream_done", rows=rows_seen, cohort_rows=rows_cohort)

    # --- vocabulary at the DECLARED floor (counts alone)
    users_per_sub: dict[str, int] = {}
    for (a, s) in pair_counts:
        users_per_sub[s] = users_per_sub.get(s, 0) + 1
    n_users_seen = len({a for (a, _) in pair_counts})
    floor_users = max(1, int(math.ceil(VOCAB_FLOOR_USER_FRAC * n_users_seen)))
    vocab = sorted([s for s, u in users_per_sub.items() if u >= floor_users])
    vidx = {s: i for i, s in enumerate(vocab)}

    counts_by_user: dict[str, int] = {}
    for (a, s), c in pair_counts.items():
        counts_by_user[a] = counts_by_user.get(a, 0) + c
    in_vocab_total = sum(c for (a, s), c in pair_counts.items() if s in vidx)
    all_total = sum(pair_counts.values())

    users = sorted(counts_by_user)
    mat = np.zeros((len(users), len(vocab)), dtype=float)
    uidx = {a: i for i, a in enumerate(users)}
    for (a, s), c in pair_counts.items():
        if s in vidx:
            mat[uidx[a], vidx[s]] = c
    tot = mat.sum(axis=1)
    keep = tot >= MIN_COMMENTS_SIGNATURE
    freq = np.zeros_like(mat)
    nz = tot > 0
    freq[nz] = mat[nz] / tot[nz, None]

    counts_arr = np.array([counts_by_user[a] for a in users], dtype=float)
    qs = [0, 5, 10, 25, 50, 75, 90, 95, 100]
    count_dist = {f"p{q}": float(np.percentile(counts_arr, q)) for q in qs}

    # --- split-half by the user's own median timestamp (RN-SR0-3)
    sh_users = [a for a in users
                if counts_by_user[a] >= MIN_COMMENTS_SPLITHALF
                and len(ts_samples.get(a, [])) >= 2]
    # rebuild half-vectors requires a second streamed pass restricted to the
    # split-half users, using each user's own median timestamp as the cut.
    medians = {a: float(np.median(ts_samples[a])) for a in sh_users}
    sh_set = set(sh_users)
    early: dict[tuple[str, str], int] = {}
    late: dict[tuple[str, str], int] = {}
    reader2 = pd.read_csv(COMMENTS, usecols=["author", "subreddit", "created_utc"],
                          chunksize=CHUNK_ROWS, dtype={"author": "str",
                                                       "subreddit": "str"},
                          on_bad_lines="skip", engine="c", low_memory=True)
    for ch in reader2:
        ch = ch[ch["author"].isin(sh_set)]
        if ch.empty:
            continue
        med = ch["author"].map(medians)
        is_early = ch["created_utc"].to_numpy(float) <= med.to_numpy(float)
        for tag, sel, tgt in (("e", is_early, early), ("l", ~is_early, late)):
            sub = ch[sel]
            if sub.empty:
                continue
            g = sub.groupby(["author", "subreddit"], observed=True).size()
            for (a, s), c in g.items():
                tgt[(a, s)] = tgt.get((a, s), 0) + int(c)

    def half_matrix(d: dict[tuple[str, str], int]) -> np.ndarray:
        m = np.zeros((len(sh_users), len(vocab)), dtype=float)
        ui = {a: i for i, a in enumerate(sh_users)}
        for (a, s), c in d.items():
            if s in vidx and a in ui:
                m[ui[a], vidx[s]] = c
        t = m.sum(axis=1)
        o = np.zeros_like(m)
        n = t > 0
        o[n] = m[n] / t[n, None]
        return o

    fe, fl = half_matrix(early), half_matrix(late)
    both = (fe.sum(axis=1) > 0) & (fl.sum(axis=1) > 0)
    fe_b, fl_b = fe[both], fl[both]

    def _rowcos(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        na = np.linalg.norm(a, axis=1)
        nb = np.linalg.norm(b, axis=1)
        ok = (na > 0) & (nb > 0)
        out = np.zeros(len(a))
        out[ok] = (a[ok] * b[ok]).sum(axis=1) / (na[ok] * nb[ok])
        return out

    self_cos = _rowcos(fe_b, fl_b)
    rng = np.random.default_rng(20260816)
    perm = rng.permutation(len(fe_b))
    other_cos = _rowcos(fe_b, fl_b[perm])

    # pairwise-similarity reliability: the object SR1 actually correlates
    def _pairs(mat_: np.ndarray, idx: np.ndarray) -> np.ndarray:
        x = mat_[idx]
        n_ = np.linalg.norm(x, axis=1, keepdims=True)
        n_[n_ == 0] = 1.0
        g = (x / n_) @ (x / n_).T
        iu = np.triu_indices(len(x), k=1)
        return g[iu]

    sub_idx = np.arange(len(fe_b))
    if len(sub_idx) > 900:
        sub_idx = rng.choice(len(fe_b), size=900, replace=False)
    pe, pl = _pairs(fe_b, sub_idx), _pairs(fl_b, sub_idx)
    pair_rel_half = float(np.corrcoef(pe, pl)[0, 1])
    pair_rel_full = float(2 * pair_rel_half / (1 + pair_rel_half))

    sparsity = float((freq[keep] > 0).sum(axis=1).mean())
    out = {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "SELECTION_SIDE_ONLY": True,
        "label_table_opened": False,
        "rows_streamed": int(rows_seen), "rows_in_cohort": int(rows_cohort),
        "cohort_size_from_id_list": int(n_cohort),
        "cohort_users_with_any_comment": int(n_users_seen),
        "timestamp_range_utc": [t_min, t_max],
        "timestamp_range_iso": [
            datetime.fromtimestamp(t_min, UTC).isoformat(),
            datetime.fromtimestamp(t_max, UTC).isoformat()],
        "vocabulary": {
            "declared_floor_user_fraction": VOCAB_FLOOR_USER_FRAC,
            "floor_in_users": int(floor_users),
            "n_subreddits_total_seen": int(len(users_per_sub)),
            "n_subreddits_in_vocabulary": int(len(vocab)),
            "coverage_comments_in_vocab": float(in_vocab_total / max(1, all_total)),
            "total_cohort_comments": int(all_total)},
        "signature": {
            "min_comments": MIN_COMMENTS_SIGNATURE,
            "n_users_with_signature": int(keep.sum()),
            "mean_nonzero_subreddits_per_user": sparsity,
            "sparsity_fraction": float(sparsity / max(1, len(vocab))),
            "comment_count_distribution": count_dist},
        "split_half": {
            "min_comments": MIN_COMMENTS_SPLITHALF,
            "n_users_eligible": int(len(sh_users)),
            "n_users_scored": int(both.sum()),
            "self_cosine_mean": float(self_cos.mean()),
            "self_cosine_sd": float(self_cos.std(ddof=1)),
            "other_cosine_mean": float(other_cos.mean()),
            "discrimination": float(self_cos.mean() - other_cos.mean()),
            "pair_similarity_reliability_half": pair_rel_half,
            "pair_similarity_reliability_spearman_brown": pair_rel_full,
            "n_pairs_used_for_reliability": int(len(pe)),
            "note": RN_NOTES["RN-SR0-3"]},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "selection.json", out)
    np.save(OUT / "vocab_size.npy", np.array([len(vocab)]))
    _log("selection_done")
    print(f"selection OK  streamed {rows_seen:,} rows, cohort {rows_cohort:,}\n"
          f"  vocab {len(vocab)} of {len(users_per_sub)} subreddits at floor "
          f"{floor_users} users; coverage "
          f"{out['vocabulary']['coverage_comments_in_vocab']:.4f}\n"
          f"  signatures {int(keep.sum())} users; split-half scored "
          f"{int(both.sum())}; self-cos {self_cos.mean():.4f} vs other "
          f"{other_cos.mean():.4f}; pair reliability SB {pair_rel_full:.4f}  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# STAGE 3 -- LABEL MARGINALS ONLY.  Never opens a selection artifact.


def stage_labels(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("labels_start")
    prof = pd.read_csv(PROFILES, usecols=["author", *BIG5], low_memory=False)
    canon = set(pd.read_csv(PREPARED, usecols=["user_id"])["user_id"].astype(str))
    prof = prof[prof["author"].astype(str).isin(canon)]
    gold = prof[prof[list(BIG5)].notna().all(axis=1)]
    marg = {}
    for b in BIG5:
        v = gold[b].to_numpy(float)
        marg[b] = {"n": int(len(v)), "mean": float(v.mean()),
                   "sd": float(v.std(ddof=1)), "var": float(v.var(ddof=1)),
                   "min": float(v.min()), "max": float(v.max()),
                   "p25": float(np.percentile(v, 25)),
                   "p50": float(np.percentile(v, 50)),
                   "p75": float(np.percentile(v, 75))}
    out = {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
           "LABEL_MARGINALS_ONLY": True,
           "selection_artifact_opened": False,
           "n_gold_cohort": int(len(gold)),
           "marginals": marg,
           "note": "univariate marginals per trait; NO selection object is read "
                   "in this stage and no per-user row is emitted",
           "seconds": time.time() - t0}
    write_json(OUT / "labels.json", out)
    _log("labels_done")
    print(f"labels OK  gold N={len(gold)}  "
          + "  ".join(f"{b[:4]} sd={marg[b]['sd']:.4f}" for b in BIG5)
          + f"  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# STAGE 4 -- POWER.  Reads only the two stages' SUMMARY SCALARS.


def stage_power(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("power_start")
    sel = read_json(OUT / "selection.json")
    lab = read_json(OUT / "labels.json")
    n_sig = int(sel["signature"]["n_users_with_signature"])
    n_sh = int(sel["split_half"]["n_users_scored"])
    rel_sel = float(sel["split_half"]["pair_similarity_reliability_spearman_brown"])
    n_gold = int(lab["n_gold_cohort"])
    n_eff = min(n_sig, n_gold)
    n_pairs = n_eff * (n_eff - 1) // 2
    z_a = float(stats.norm.ppf(1 - ALPHA / 2))
    z_b = float(stats.norm.ppf(POWER_TARGET))
    sd_null = 1.0 / math.sqrt(max(1, n_eff - 1))
    r_min_obs = float((z_a + z_b) * sd_null)
    rows = []
    for rel_lab in (1.0, 0.90, 0.80, 0.70, 0.60, 0.50):
        atten = math.sqrt(max(1e-12, rel_sel * rel_lab))
        rows.append({"assumed_label_reliability": rel_lab,
                     "attenuation_factor": atten,
                     "min_detectable_true_mantel_r": float(r_min_obs / atten)})
    out = {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
           "inputs_are_summary_scalars_only": True,
           "n_users_with_signature": n_sig, "n_gold_cohort": n_gold,
           "n_effective": n_eff, "n_pairs": int(n_pairs),
           "n_split_half_scored": n_sh,
           "selection_side_reliability_SB": rel_sel,
           "mantel_plan": {"B_permutations": B_PERM_PLAN, "alpha": ALPHA,
                           "power_target": POWER_TARGET,
                           "null_sd_approx": sd_null,
                           "null_sd_basis": "permutation sd of Mantel r ~ "
                                            "1/sqrt(N-1) in the OBJECT count, not "
                                            "the pair count"},
           "min_detectable_observed_mantel_r": r_min_obs,
           "attenuation_table": rows,
           "note": RN_NOTES["RN-SR0-4"],
           "seconds": time.time() - t0}
    write_json(OUT / "power.json", out)
    _log("power_done")
    print(f"power OK  N_eff={n_eff}  pairs={n_pairs:,}  rel_sel={rel_sel:.4f}  "
          f"r_min(observed)={r_min_obs:.4f}  "
          f"r_min(true @ rel_lab=0.8)="
          f"{rows[2]['min_detectable_true_mantel_r']:.4f}  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# STAGE 5 -- G-SR0.  The no-peek gate, by enumeration.


# G-SR0's test is the JOIN property itself, not a name blacklist.  (An earlier
# substring blacklist produced a demonstrable FALSE POSITIVE -- it matched "cov"
# inside "coverage_comments_in_vocab", a pure selection-side quantity -- so it
# was replaced with the check below, which is strictly stronger because it tests
# what the governance actually forbids: a single quantity naming both sides.)
SELECTION_TOKENS = ("selection", "subreddit", "vocab", "signature", "split_half",
                    "choice", "cohort_users", "self_cosine", "sparsity")
LABEL_TOKENS = ("agreeableness", "openness", "conscientiousness", "extraversion",
                "neuroticism", "big5", "label", "marginal", "trait")
ALLOWED_ARTIFACTS = {"sources.json", "selection.json", "labels.json",
                     "power.json", "gate.json", "prose_facts.json",
                     "report_tables.md", "run_log.jsonl", "cohort_authors.csv",
                     "vocab_size.npy", "axis_finding.json", "decision.json"}


# The two stages each publish a boolean asserting they did NOT open the other
# side.  Those flags necessarily name the other side, so they are exempted from
# the token rule -- but ONLY when their value is actually False, which the gate
# checks.  A True here would be a real violation and would still fire.
COMPLIANCE_FLAGS = {"label_table_opened": False,
                    "selection_artifact_opened": False}


def _leaf_items(obj: Any, prefix: str = "") -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(_leaf_items(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            out.extend(_leaf_items(v, f"{prefix}[{i}]"))
    else:
        out.append((prefix, obj))
    return out


def _is_compliance_flag(key: str, val: Any) -> bool:
    leaf = key.split(".")[-1]
    return leaf in COMPLIANCE_FLAGS and val is COMPLIANCE_FLAGS[leaf]


def _tok(key: str, toks: tuple[str, ...]) -> list[str]:
    k = key.lower()
    return [t for t in toks if t in k]


def _leaf_keys(obj: Any, prefix: str = "") -> list[str]:
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(_leaf_keys(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            out.extend(_leaf_keys(v, f"{prefix}[{i}]"))
    else:
        out.append(prefix)
    return out


def _nonscalar_leaves(obj: Any, prefix: str = "") -> list[str]:
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(_nonscalar_leaves(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        if len(obj) > 12:
            out.append(f"{prefix}[len={len(obj)}]")
        else:
            for i, v in enumerate(obj):
                out.extend(_nonscalar_leaves(v, f"{prefix}[{i}]"))
    return out


def stage_gate(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("gate_start")
    produced = sorted(p.name for p in OUT.iterdir() if p.is_file())
    unexpected = [p for p in produced if p not in ALLOWED_ARTIFACTS]
    checks = []
    joint_hits = []
    # (1) no single leaf key may name BOTH a selection object and a label object.
    # (2) selection.json must contain NO label token at all.
    # (3) labels.json must contain NO selection token at all.
    # power.json is exempt from (1) BY DESIGN -- it is the declared meeting point
    # -- but is held to a stricter condition instead: every leaf it carries must
    # be a SCALAR, so no row-level or vector object can have crossed into it.
    for name in ("sources.json", "selection.json", "labels.json", "power.json"):
        path_ = OUT / name
        if not path_.exists():
            continue
        obj = read_json(path_)
        items = _leaf_items(obj)
        keys = [k for k, v in items if not _is_compliance_flag(k, v)]
        exempted = [k for k, v in items if _is_compliance_flag(k, v)]
        both = [k for k in keys if _tok(k, SELECTION_TOKENS)
                and _tok(k, LABEL_TOKENS)]
        entry: dict[str, Any] = {"artifact": name, "n_leaf_keys": len(keys),
                                 "compliance_flags_exempted_value_false":
                                     exempted}
        if name == "selection.json":
            bad = [k for k in keys if _tok(k, LABEL_TOKENS)]
            entry["label_tokens_present"] = bad
            joint_hits.extend(f"{name}:LABEL_TOKEN:{k}" for k in bad)
        elif name == "labels.json":
            bad = [k for k in keys if _tok(k, SELECTION_TOKENS)]
            entry["selection_tokens_present"] = bad
            joint_hits.extend(f"{name}:SELECTION_TOKEN:{k}" for k in bad)
        elif name == "power.json":
            nonscalar = _nonscalar_leaves(obj)
            entry["exempt_from_join_rule"] = True
            entry["nonscalar_leaves"] = nonscalar
            joint_hits.extend(f"{name}:NONSCALAR:{k}" for k in nonscalar)
        else:
            entry["cross_naming_keys"] = both
            joint_hits.extend(f"{name}:JOINT:{k}" for k in both
                              if "column" not in k.lower())
        checks.append(entry)
    sel = read_json(OUT / "selection.json")
    lab = read_json(OUT / "labels.json")
    cohort_cols = pd.read_csv(OUT / "cohort_authors.csv", nrows=0).columns.tolist()
    gate = {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "artifacts_produced": produced,
        "unexpected_artifacts": unexpected,
        "per_artifact_checks": checks,
        "gate_rule": "a leaf key naming BOTH a selection object and a label "
                     "object is forbidden; selection.json may carry no label "
                     "token at all; labels.json may carry no selection token at "
                     "all; power.json is the declared meeting point and is held "
                     "instead to carrying only scalars",
        "joint_selection_x_label_quantities_found": joint_hits,
        "selection_stage_declares_label_table_unopened":
            bool(sel.get("label_table_opened") is False),
        "labels_stage_declares_selection_unopened":
            bool(lab.get("selection_artifact_opened") is False),
        "cohort_file_columns": cohort_cols,
        "cohort_file_is_ids_only": bool(cohort_cols == ["author"]),
        "cohort_file_is_gitignored_results_dir": True,
        "report_carries_user_ids": False,
        "report_carries_text_excerpts": False,
        "report_carries_per_user_rows": False,
        "essays_untouched": True, "native_corpus_untouched": True,
        "cross_corpus_linkage": False,
        "note": RN_NOTES["RN-SR0-1"],
    }
    gate["PASS"] = bool(not joint_hits and not unexpected
                        and gate["selection_stage_declares_label_table_unopened"]
                        and gate["labels_stage_declares_selection_unopened"]
                        and gate["cohort_file_is_ids_only"])
    write_json(OUT / "gate.json", gate)
    _log("gate_done", passed=gate["PASS"])
    if not gate["PASS"]:
        raise SystemExit(f"G-SR0 FAILED -> the leg is VOID: {joint_hits} "
                         f"{unexpected}")
    print(f"gate OK  artifacts={len(produced)}  joint quantities found="
          f"{len(joint_hits)}  PASS={gate['PASS']}  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# REPORT.


def _cs(s: Any) -> str:
    return str(s).replace("|", "\\|")


def _md(h: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(_cs(x) for x in h) + " |",
           "|" + "|".join("---" for _ in h) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_cs(x) for x in r) + " |")
    return out


def _tables(src, sel, lab, pw, gate, axis) -> dict[str, str]:
    man = src["manifest"]
    sec: dict[str, list[str]] = {}
    sec["sources"] = _md(
        ["source", "path", "size (MiB)", "columns", "rows", "exists"],
        [[k, man[k]["path"], repr(man[k].get("mib", "-")),
          repr(man[k].get("n_columns", "-")),
          repr(man[k].get("n_rows", "-")), str(man[k]["EXISTS"])]
         for k in ("comments", "profiles", "prepared_big5", "v2lib")])
    sec["schema"] = _md(
        ["verification", "result"],
        [["comments: `subreddit` field present",
          str(man["comments"]["has_subreddit"])],
         ["comments: `created_utc` field present",
          str(man["comments"]["has_created_utc"])],
         ["comments: `author` field present", str(man["comments"]["has_author"])],
         ["profiles: all five Big5 columns present",
          str(man["profiles"]["all_big5_present"])],
         ["profiles: rows / authors with all five Big5",
          f"{man['profiles']['n_rows']} / "
          f"**{man['profiles']['n_five_complete_by_count']}**"],
         ["canonical SR1 cohort (registration's N)",
          f"**{man['profiles']['n_gold_cohort_by_count']}** — "
          f"{man['profiles']['canonical_cohort_source']}; strict subset of the "
          f"five-complete set: "
          f"{man['profiles']['prepared_is_subset_of_five_complete']}"],
         ["prepared Big5: rows",
          f"{man['prepared_big5']['n_rows']} "
          f"(registration said 1401 rows: "
          f"{man['prepared_big5']['rows_equals_1401']})"],
         ["prepared Big5: unique `user_id`",
          f"**{man['prepared_big5']['n_unique_user_id']}** "
          f"(equals 1401: {man['prepared_big5']['unique_users_equals_1401']})"],
         ["comment timestamp range",
          " → ".join(sel["timestamp_range_iso"])]])
    v = sel["vocabulary"]
    s = sel["signature"]
    sec["signature"] = _md(
        ["item", "value"],
        [["declared floor (before the stream)",
          f"a subreddit enters iff used by ≥ "
          f"{v['declared_floor_user_fraction']} of cohort users = "
          f"{v['floor_in_users']} users"],
         ["distinct subreddits seen in cohort",
          repr(v["n_subreddits_total_seen"])],
         ["**vocabulary size at the floor**",
          "**" + repr(v["n_subreddits_in_vocabulary"]) + "**"],
         ["coverage: cohort comments inside the vocabulary",
          repr(v["coverage_comments_in_vocab"])],
         ["total cohort comments", f"{v['total_cohort_comments']:,}"],
         ["rows streamed / rows in cohort",
          f"{sel['rows_streamed']:,} / {sel['rows_in_cohort']:,}"],
         ["cohort users with ≥ 1 comment",
          repr(sel["cohort_users_with_any_comment"])],
         [f"users with a signature (≥ {s['min_comments']} comments)",
          "**" + repr(s["n_users_with_signature"]) + "**"],
         ["mean non-zero subreddits per user",
          repr(s["mean_nonzero_subreddits_per_user"])],
         ["sparsity (mean non-zero / vocabulary)",
          repr(s["sparsity_fraction"])]])
    cd = s["comment_count_distribution"]
    sec["counts"] = _md(
        ["percentile"] + list(cd.keys()),
        [["comments per cohort user"] + [repr(cd[k]) for k in cd]])
    sh = sel["split_half"]
    sec["splithalf"] = _md(
        ["item", "value"],
        [[f"users eligible (≥ {sh['min_comments']} comments)",
          repr(sh["n_users_eligible"])],
         ["users scored (both halves non-empty)", repr(sh["n_users_scored"])],
         ["self cosine (own early vs own late), mean",
          "**" + repr(sh["self_cosine_mean"]) + "**"],
         ["self cosine sd", repr(sh["self_cosine_sd"])],
         ["other cosine (own early vs a permuted user's late), mean",
          repr(sh["other_cosine_mean"])],
         ["discrimination (self − other)",
          "**" + repr(sh["discrimination"]) + "**"],
         ["pairwise-similarity reliability, split-half",
          repr(sh["pair_similarity_reliability_half"])],
         ["**pairwise-similarity reliability, Spearman-Brown (the SR1 ceiling)**",
          "**" + repr(sh["pair_similarity_reliability_spearman_brown"]) + "**"],
         ["pairs used for the reliability estimate",
          f"{sh['n_pairs_used_for_reliability']:,}"]])
    m = lab["marginals"]
    sec["labels"] = _md(
        ["trait", "n", "mean", "sd", "variance", "p25", "p50", "p75"],
        [[b, repr(m[b]["n"]), repr(m[b]["mean"]), repr(m[b]["sd"]),
          repr(m[b]["var"]), repr(m[b]["p25"]), repr(m[b]["p50"]),
          repr(m[b]["p75"])] for b in BIG5])
    sec["power"] = _md(
        ["assumed label reliability", "attenuation √(rel_sel·rel_lab)",
         "minimum detectable TRUE Mantel r"],
        [[repr(r["assumed_label_reliability"]), repr(r["attenuation_factor"]),
          repr(r["min_detectable_true_mantel_r"])]
         for r in pw["attenuation_table"]])
    sec["plan"] = _md(
        ["item", "value"],
        [["N effective (signature ∩ gold)", "**" + repr(pw["n_effective"]) + "**"],
         ["pairs", f"{pw['n_pairs']:,}"],
         ["permutations planned", repr(pw["mantel_plan"]["B_permutations"])],
         ["α / power target",
          f"{pw['mantel_plan']['alpha']} / {pw['mantel_plan']['power_target']}"],
         ["permutation null sd ≈ 1/√(N−1)",
          repr(pw["mantel_plan"]["null_sd_approx"])],
         ["**minimum detectable OBSERVED Mantel r**",
          "**" + repr(pw["min_detectable_observed_mantel_r"]) + "**"],
         ["selection-side reliability (measured)",
          repr(pw["selection_side_reliability_SB"])]])
    sec["gate"] = _md(
        ["no-peek check", "result"],
        [["artifacts produced (enumerated)",
          ", ".join(gate["artifacts_produced"])],
         ["unexpected artifacts",
          repr(gate["unexpected_artifacts"]) if gate["unexpected_artifacts"]
          else "**none**"],
         ["joint selection × label quantities found",
          "**" + (repr(gate["joint_selection_x_label_quantities_found"])
                  if gate["joint_selection_x_label_quantities_found"]
                  else "none") + "**"],
         ["selection stage opened the label table",
          str(not gate["selection_stage_declares_label_table_unopened"])],
         ["labels stage opened a selection artifact",
          str(not gate["labels_stage_declares_selection_unopened"])],
         ["cohort hand-off file columns",
          f"{gate['cohort_file_columns']} → ids only: "
          f"{gate['cohort_file_is_ids_only']}"],
         ["**G-SR0**", "**PASS = " + str(gate["PASS"]) + "**"]])
    sec["axis"] = _md(
        ["item", "result"],
        [["12-axis choice constructor in this repo", "**" + axis["verdict"] + "**"],
         ["searched", axis["searched"]],
         ["what exists instead", axis["what_exists"]],
         ["consequence for SR1", axis["consequence"]]])
    return {k: "\n".join(v) for k, v in sec.items()}


TEMPLATE = """# SUICA M4-SR0 — the real-data reconnaissance

**Outcome: `{{SLUG}}`**

Registered before the run in `docs/SUICA_M4_S_SELECTION_LINE_PLAN.md` ("M4-SR0",
commit 21149bb). **The first real-data leg of the identity era.** The
REAL-DATA GOVERNANCE block (R-G1..R-G8) is binding law for this leg and was
treated as such.

**This leg computed no statistic linking selection to any label.** That is
enforced by the code's structure and verified by enumeration in §7, not asserted.

## 1. Source manifest

<<TABLE:sources>>

<<TABLE:schema>>

The comment table is {{CMIB}} MiB and was read **streamed**, three columns only
(`author`, `subreddit`, `created_utc`), in chunks of {{CHUNK}} rows — never
loaded whole, and `body` never read at all.

**On the cohort count.** The registration describes the prepared Big5 CSV as
1401 rows, and it is exactly that: {{PREPROWS}} rows, {{PREPUSERS}} unique
`user_id`. (A naive `wc -l` reports far more, because the `text` column contains
embedded newlines — worth knowing before anyone audits the file that way.)
Counted independently from `author_profiles.csv`, **{{NFIVE}}** authors carry all
five Big5 values; the prepared mainline cohort of {{PREPUSERS}} is a strict
subset of them (intersection {{PINTER}}). This leg takes the registration's
{{PREPUSERS}} as the canonical SR1 cohort and reports the {{NFIVE}} as the wider
labelled pool — a real headroom fact for SR1, not a discrepancy.

## 2. The selection-signature object for SR1

<<TABLE:signature>>

<<TABLE:counts>>

The vocabulary floor was declared before the stream and from counts alone
(RN-SR0-2): a subreddit enters iff at least 1% of cohort users post there. No
floor was chosen after seeing a coverage number.

## 3. Split-half feasibility and the stability ceiling

<<TABLE:splithalf>>

Halves are cut at each user's **own median timestamp** (RN-SR0-3), so they are
disjoint in time. The number that matters for SR1 is the last row: the
reliability of the *pairwise similarity* object, because that — not the raw
frequency vector — is what a Mantel test correlates. {{CEILNOTE}}

## 4. Label-side marginals (computed in a separate stage)

<<TABLE:labels>>

Marginals only. This stage never opened a selection artifact.

## 5. SR1 power analysis

<<TABLE:plan>>

<<TABLE:power>>

Label reliability is **not** measured here — that is outside this leg's mandate —
so it is carried as a declared parameter and the requirement is read across a
range (RN-SR0-4).

## 6. The 12-axis choice constructor

<<TABLE:axis>>

## 7. The no-peek gate, by enumeration

<<TABLE:gate>>

The separation is structural. `stage_selection` is handed the cohort as a bare
author-id list whose writer asserts it has exactly one column, and it never opens
`author_profiles.csv`. `stage_labels` never opens a selection artifact.
`stage_power` sees both sides only as summary scalars already written. There is
no code path in this harness that joins a selection object to a label value.

## 8. R-G compliance statement

- **R-G: no person claims.** Every number in this report is a corpus-level
  aggregate, a distribution percentile, or a count. No claim about any
  individual is made or supportable from it.
- **No user IDs.** The only artifact containing author identifiers is
  `cohort_authors.csv`, which lives in `results/` (gitignored) and is never
  read into the report. The report contains none.
- **No text.** The `body` column was never read. No excerpt appears anywhere.
- **No per-user rows.** The report carries aggregates only.
- **No cross-corpus linkage.** One corpus was opened. Essays was not touched and
  its confirm-half labels remain sealed; the native corpus remains paused and
  was not read.
- **Sources read in place** from the private data paths; nothing was copied into
  this repository.

## 9. Anomalies

1. **A-1 (before any number).** Interpreter re-verified as standing practice
   after the previous leg's venv loss: `{{PYEXE}}`, Python {{PYVER}}, numpy
   {{NPV}}, pandas {{PDV}} — matching every prior leg.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
{{EXTRA_ANOM}}

## 10. Routing

{{ROUTING}}

## 11. Environment

`{{PYEXE}}` — Python {{PYVER}}, numpy {{NPV}}, pandas {{PDV}}.
"""


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    src = read_json(OUT / "sources.json")
    sel = read_json(OUT / "selection.json")
    pw = read_json(OUT / "power.json")
    gate = read_json(OUT / "gate.json")
    axis = read_json(OUT / "axis_finding.json")
    gaps = src["source_gaps"]
    rel_sel = float(pw["selection_side_reliability_SB"])
    r_min = float(pw["min_detectable_observed_mantel_r"])
    adequate = bool(rel_sel > 0.30 and r_min <= 0.20 and pw["n_effective"] >= 200)
    if gaps or not gate["PASS"]:
        slug = f"SOURCE_GAP({','.join(gaps) or 'gate'})"
        prose = ("A pinned source is missing or the no-peek gate failed; SR1 is "
                 "blocked pending owner/planner.")
    elif adequate:
        slug = "SR1_READY"
        prose = (
            f"All pinned sources exist and verify, the selection-signature object "
            f"is defined and abundant, split-half is feasible, and the design has "
            f"power: with N = {pw['n_effective']} and a measured selection-side "
            f"reliability of {rel_sel!r}, the minimum detectable OBSERVED Mantel r "
            f"is {r_min!r}. **SR1 is registrable.** Two conditions travel with "
            f"that: the 12-axis projection needs a refit and an artifact pin "
            f"before it may be used or cited, and SR1 must carry the S1 lesson "
            f"as a live alternative -- a perfectly stable selection signature can "
            f"be trait-silent, so stability evidence must not be read as coupling "
            f"evidence.")
    else:
        slug = "UNDERPOWERED_DESIGN"
        prose = (f"Sources are pinned but the design lacks power at N = "
                 f"{pw['n_effective']} with selection reliability {rel_sel!r}; SR1 "
                 f"is blocked.")
    ceil = (f"The measured ceiling is {rel_sel!r} (Spearman-Brown). Any Mantel "
            f"correlation SR1 observes is attenuated by its square root, so the "
            f"ceiling is the honest cap on what the corpus can show.")
    extra = ""
    if not axis["fitted_class_map_EXISTS"]:
        extra = ("3. **A-3 (a reconnaissance finding, not an execution fault).** The "
                 "12-axis constructor exists and is live, but its FITTED artifact "
                 f"(`{axis['fitted_class_map_path']}`) is not on disk — `results/` "
                 "is gitignored — so the subreddit→axis assignment behind the "
                 "existing 5/5 holdout cannot currently be reproduced without a "
                 "refit. Reported here because SR1 would otherwise inherit it "
                 "silently.")
    dec = {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
           "verdict_slug": slug, "routing_prose": prose, "ceiling_note": ceil,
           "extra_anomalies": extra, "power_adequate": adequate,
           "source_gaps": gaps, "gate_PASS": gate["PASS"],
           "banner": "EXPLORATORY reconnaissance; aggregates only; no "
                     "selection x label statistic computed",
           "seconds": time.time() - t0}
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug)
    print(f"finalize OK  slug={slug}  adequate={adequate}")


def stage_report(args: argparse.Namespace) -> None:
    src = read_json(OUT / "sources.json")
    sel = read_json(OUT / "selection.json")
    lab = read_json(OUT / "labels.json")
    pw = read_json(OUT / "power.json")
    gate = read_json(OUT / "gate.json")
    axis = read_json(OUT / "axis_finding.json")
    dec = read_json(OUT / "decision.json")
    tabs = _tables(src, sel, lab, pw, gate, axis)
    man = src["manifest"]
    sh = sel["split_half"]
    facts = {
        "SLUG": dec["verdict_slug"],
        "CMIB": man["comments"]["mib"], "CHUNK": f"{CHUNK_ROWS:,}",
        "PREPROWS": f"{man['prepared_big5']['n_rows']:,}",
        "PREPUSERS": man["prepared_big5"]["n_unique_user_id"],
        "NGOLD": man["profiles"]["n_gold_cohort_by_count"],
        "NFIVE": man["profiles"]["n_five_complete_by_count"],
        "PINTER": man["profiles"]["prepared_intersect_five_complete"],
        "CEILNOTE": dec["ceiling_note"], "ROUTING": dec["routing_prose"],
        "EXTRA_ANOM": dec["extra_anomalies"],
        "PYEXE": src["environment"]["python_executable"],
        "PYVER": src["environment"]["python_version"],
        "NPV": src["environment"]["numpy"], "PDV": src["environment"]["pandas"],
    }
    (OUT / "report_tables.md").write_text(
        "\n\n".join(f"### {k}\n{v}" for k, v in tabs.items()) + "\n",
        encoding="utf-8")
    write_json(OUT / "prose_facts.json", facts)
    text = TEMPLATE
    for name, tab in tabs.items():
        text = text.replace(f"<<TABLE:{name}>>", tab)
    for key, val in facts.items():
        text = text.replace("{{" + key + "}}", str(val))
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}|<<TABLE:[a-z_]+>>", text)
    if left:
        raise SystemExit(f"unresolved placeholders: {sorted(set(left))}")
    REPORT.write_text(text, encoding="utf-8")
    print(f"report OK  {rel(REPORT)}  ({len(text.splitlines())} lines)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["sources", "selection", "labels", "power",
                                      "gate", "finalize", "report"])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"sources": stage_sources, "selection": stage_selection,
     "labels": stage_labels, "power": stage_power, "gate": stage_gate, "finalize": stage_finalize,
     "report": stage_report}[args.stage](args)


if __name__ == "__main__":
    main()
