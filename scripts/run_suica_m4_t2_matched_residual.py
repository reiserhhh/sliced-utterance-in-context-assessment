#!/usr/bin/env python3
"""SUICA M4-T2 -- the condition-matched residual audit + the taste-transport
falsifier.

Registered BEFORE run in docs/SUICA_M4_T_HIERARCHICAL_SELECTION_IDENTITY_PLAN.md
("M4-T2", commit 4e9e339).  Binding.  LABEL-FREE THROUGHOUT: no Big5 or MBTI
value is read at any stage.

T1 proved the tail exists (terminal within-leaf residual AUC 0.9552 full /
0.9417 clean).  T2 asks WHAT CARRIES IT.

  Arm A -- does the residual survive matching strangers on LATE-side
           observability?  Cumulative caliper ladder L0..L4.
  Arm B -- does taste TRANSPORT onto communities the user had not yet joined?
           Training-fold PPMI+SVD embedding, disjoint-support centroids.

The T1 core (suica_core/hierarchical_selection_identity.py) is imported by file
through ONE loader chain and is NOT modified; all new code lives here.

Stages: part0 -> counts -> pilot -> armA -> armB -> clean -> finalize
         -> report
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import re
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEG = "M4-T2"
OUT = ROOT / "results" / "m4_t2_matched_residual"
REPORT = ROOT / "reports" / "SUICA_M4_T2_MATCHED_RESIDUAL_REPORT.md"

T1CORE = ROOT / "suica_core" / "hierarchical_selection_identity.py"
T1DRIVER = ROOT / "scripts" / "run_suica_m4_t1_hierarchical_selection_identity.py"
T1RES = ROOT / "results" / "m4_t1_hierarchical_selection_identity"
SR1NPZ = ROOT / "results" / "m4_sr1_selection_geometry" / "selection.npz"
SR0COHORT = ROOT / "results" / "m4_sr0_recon" / "cohort_authors.csv"
COMMENTS = Path("/Volumes/mobile3/projects/project persona"
                "/data_sets/PANDORA_official/all_comments_since_2015.csv")

SEED = 20260817
FOLDS = 5
MAX_DEPTH = 6
MIN_LEAF = 30
CHUNK_ROWS = 2_000_000
B_BOOT = 1000
B_PERM = 999
B_PILOT_PERM = 299
PILOT_USERS = 200
MIN_POOL_MEDIAN = 5
EMB_DIM = 64
MIN_NEW_COMMUNITIES = 3
SEP_LO, SEP_HI = 0.5, 0.75

# --- T1 anchors (G0t2 bit-verifies) ----------------------------------------
A_RESID_FULL = 0.9552295265671575
A_RESID_CLEAN = 0.9416819726747061
A_PATH_FULL = 0.7460863278537894
A_PATH_CLEAN = 0.731654715213212
A_N_FULL = 1304
A_N_CLEAN = 1269
A_VOCAB = 1191
A_FLOOR = 15
A_REMOVED = 23

LADDER = ("L0", "L1", "L2", "L3", "L4")
CAL_VOLUME = 0.5        # |log2 ratio|
CAL_SPAN_DAYS = 90.0
CAL_ENTROPY_BITS = 0.5
CAL_BREADTH = (0.7, 1.43)

RN_NOTES = {
    "RN-T2-1":
        "the T1 core is imported by file through ONE loader chain and is not "
        "modified; the residual construction is transcribed from its own fold "
        "loop (hierarchical_selection_identity.py:356-372) -- leaves from the "
        "frozen tree's routing of held-out EARLY rows, centroid subtracted from "
        "both halves, cosine between residual early and residual late.  L0 "
        "reproduces T1's pooled leaf-residual AUC and is an ANCHOR, not a verdict.",
    "RN-T2-2":
        "all four calipers are LATE-side observables of the STRANGER, matched to "
        "the TARGET's late-side observables, because the question is whether a "
        "stranger who looks equally observable can be told apart.  Volume and "
        "span require the comment stream (re-derived here); entropy and breadth "
        "come from SR1's persisted freq_late.  The reconstruction is verified "
        "against SR1's own matrix before any caliper is applied.",
    "RN-T2-3":
        "the null is the permutation's own band (#66): within each leaf x "
        "stratum, the late halves are permuted among the admissible candidates "
        "and the whole ladder statistic recomputed.  No closed form is used for "
        "the null anywhere, and the method is pinned here rather than left to a "
        "heuristic.",
    "RN-T2-4":
        "#59 non-degeneracy: the calipers restrict WHICH strangers may be "
        "compared; they never equalize the content being compared, and the "
        "residual vectors themselves are untouched.  A caliper can therefore "
        "lower the AUC toward the null but cannot mechanically hold it up.",
    "RN-T2-5":
        "Arm B's embedding is fitted on TRAINING authors' EARLY halves only, per "
        "fold; held-out users never enter the fit.  Purity is verified by "
        "construction log (the fitted row set is recorded and intersected with "
        "the held-out set, which must be empty).",
    "RN-T2-6":
        "UNDERRESOLVED is a first-class outcome here and is declared BY DESIGN "
        "when the pilot shows a level's null band cannot separate 0.5 from 0.75 "
        "at realized pool sizes.  N is corpus-fixed; there is no escalation to "
        "buy, so a wide band is a fact about the corpus and must be said rather "
        "than papered over.",
    "RN-T2-7":
        "the clean arm recomputes the selection-side observables (in-vocabulary "
        "volume, entropy, breadth) on the ABLATED late matrix, so the caliper "
        "means 'equally observable in the world where those 23 communities do "
        "not exist'.  The alternative -- holding the full-arm observables fixed "
        "and varying only the representation -- is defensible too; the choice "
        "is declared rather than hidden, and the clean arm is a reading, not a "
        "gate.",
    "RN-T2-8":
        "the G2t2 pilot subsamples the 200 TARGETS but never the candidate "
        "pools, so the null bandwidth it reports is the one achievable at the "
        "corpus's realized pool sizes and is conservative (fewer targets give a "
        "wider band) relative to the full run that follows it.",
    "RN-T2-9":
        "the median-pool-below-5 UNDERRESOLVED rule is registered for ladder "
        "LEVELS ('a level whose admissible stranger pool drops below 5 per "
        "target on median').  Arm B's registered resolution test is G2t2's "
        "band-separation test, which it passes.  Arm B's median pool is thin "
        "and is reported in every table rather than being used to void a "
        "verdict the registration did not void.",
    "RN-T2-10":
        "REGISTRATION-DEFECT CANDIDATE RD-T2-1.  G3t2 lists 'null 0.5' as a "
        "rule-29 predicate, but the registered statistic pools ONE positive "
        "per target against MANY negatives per target, and targets are "
        "heterogeneous, so the permutation null is NOT centred on 0.5 -- it "
        "sits wherever that weighting puts it.  This is precisely why #66 "
        "orders the comparison to use 'the permutation's own band, no closed "
        "forms'.  The two instructions are in tension; the band is used (as "
        "#66 requires) and the deviation is reported per level rather than "
        "being silently passed or silently failed.",
}

_MODS: dict[str, Any] = {}


def _load_named(name: str, path: Path) -> Any:
    if name not in _MODS:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)          # type: ignore[arg-type]
        sys.modules[name] = mod
        spec.loader.exec_module(mod)                         # type: ignore[union-attr]
        _MODS[name] = mod
    return _MODS[name]


def t1core() -> Any:
    return _load_named("suica_core.hierarchical_selection_identity", T1CORE)


def t1drv() -> Any:
    return _load_named("run_suica_m4_t1_hierarchical_selection_identity", T1DRIVER)


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


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# LATE-SIDE OBSERVABLES (re-derived from the stream; RN-T2-2).


def late_observables(users: list[str]) -> dict[str, np.ndarray]:
    uset = set(users)
    uidx = {a: i for i, a in enumerate(users)}
    ts: dict[str, list[float]] = defaultdict(list)
    reader = pd.read_csv(COMMENTS, usecols=["author", "subreddit", "created_utc"],
                         chunksize=CHUNK_ROWS,
                         dtype={"author": "str", "subreddit": "str"},
                         on_bad_lines="skip", engine="c", low_memory=True)
    for ch in reader:
        ch = ch[ch["author"].isin(uset)]
        if ch.empty:
            continue
        for a, sub in ch.groupby("author", observed=True)["created_utc"]:
            lst = ts[a]
            if len(lst) < 4000:
                lst.extend(sub.tolist()[: 4000 - len(lst)])
    med = {a: float(np.median(v)) for a, v in ts.items()}
    n = len(users)
    vol = np.zeros(n)
    tmin = np.full(n, np.inf)
    tmax = np.full(n, -np.inf)
    reader2 = pd.read_csv(COMMENTS, usecols=["author", "subreddit", "created_utc"],
                          chunksize=CHUNK_ROWS,
                          dtype={"author": "str", "subreddit": "str"},
                          on_bad_lines="skip", engine="c", low_memory=True)
    for ch in reader2:
        ch = ch[ch["author"].isin(uset)]
        if ch.empty:
            continue
        m = ch["author"].map(med).to_numpy(float)
        late = ch[ch["created_utc"].to_numpy(float) > m]
        if late.empty:
            continue
        for a, sub in late.groupby("author", observed=True)["created_utc"]:
            i = uidx[a]
            vol[i] += len(sub)
            tmin[i] = min(tmin[i], float(sub.min()))
            tmax[i] = max(tmax[i], float(sub.max()))
    span = np.where(np.isfinite(tmin) & np.isfinite(tmax),
                    (tmax - tmin) / 86400.0, 0.0)
    return {"volume_late_all": vol, "span_late_days": span}


def entropy_bits(freq: np.ndarray) -> np.ndarray:
    p = np.clip(freq, 1e-300, None)
    return -(freq * (np.log(p) / math.log(2.0))).sum(axis=1)


def _read_chunks() -> Any:
    return pd.read_csv(COMMENTS, usecols=["author", "subreddit", "created_utc"],
                       chunksize=CHUNK_ROWS,
                       dtype={"author": "str", "subreddit": "str"},
                       on_bad_lines="skip", engine="c", low_memory=True)


def rebuild_half_counts(users: list[str],
                        vocab: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Re-derive the user x community EARLY / LATE COUNT matrices.

    SR1's own split rule is replicated exactly (run_suica_m4_sr1_selection_
    geometry.py:379-401): each user's median over the FIRST <= 4000 timestamps
    seen in file order, early = created_utc <= median.  The 4000 cap is SR1's,
    not a new approximation -- reproducing the frozen halves requires it.
    The result is verified against SR1's persisted freq_early / freq_late
    before any caliper or embedding is built on it (RN-T2-2).
    """
    uidx = {a: i for i, a in enumerate(users)}
    vidx = {s: i for i, s in enumerate(vocab)}
    uset = set(users)
    ts: dict[str, list[float]] = {}
    for ch in _read_chunks():
        ch = ch[ch["author"].isin(uset)]
        if ch.empty:
            continue
        for a, sub in ch.groupby("author", observed=True)["created_utc"]:
            lst = ts.setdefault(a, [])
            if len(lst) < 4000:
                lst.extend(sub.tolist()[: 4000 - len(lst)])
    med = {a: float(np.median(ts[a])) for a in users if a in ts}
    early = np.zeros((len(users), len(vocab)), dtype=np.int64)
    late = np.zeros_like(early)
    for ch in _read_chunks():
        ch = ch[ch["author"].isin(uset)]
        if ch.empty:
            continue
        mm = ch["author"].map(med).to_numpy(float)
        is_early = ch["created_utc"].to_numpy(float) <= mm
        for sel_, tgt in ((is_early, early), (~is_early, late)):
            sub = ch[sel_]
            if sub.empty:
                continue
            for (a, s), c in sub.groupby(["author", "subreddit"],
                                         observed=True).size().items():
                if s in vidx:
                    tgt[uidx[a], vidx[s]] += int(c)
    return early, late


def row_normalise(mat: np.ndarray) -> np.ndarray:
    tot = mat.sum(axis=1)
    out = np.zeros(mat.shape, dtype=float)
    nz = tot > 0
    out[nz] = mat[nz] / tot[nz, None]
    return out


def observables_from(late_counts: np.ndarray, freq_late: np.ndarray,
                     span_days: np.ndarray) -> dict[str, np.ndarray]:
    """The four registered LATE-side observables.

    Volume is the IN-VOCABULARY late comment count as registered (L1), which
    is the row sum of the reconstructed late count matrix -- not the raw
    all-subreddit late count (see the anomaly note A2 in the report).
    """
    return {"volume_late": late_counts.sum(axis=1).astype(float),
            "span_late_days": span_days.astype(float),
            "entropy_late": entropy_bits(freq_late),
            "breadth_late": (late_counts > 0).sum(axis=1).astype(float)}


# ---------------------------------------------------------------------------
# THE RESIDUAL OBJECT (transcribed from the T1 core; RN-T2-1).


def build_residuals(early: np.ndarray, late: np.ndarray) -> dict[str, Any]:
    core = t1core()
    e = core.hellinger_rows(early)
    l = core.hellinger_rows(late)
    valid = (np.linalg.norm(e, axis=1) > 0) & (np.linalg.norm(l, axis=1) > 0)
    e, l = e[valid], l[valid]
    orig = np.flatnonzero(valid)
    splitter = KFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    groups: list[dict[str, Any]] = []
    fitted_train: list[list[int]] = []
    for fold, (tr, te) in enumerate(splitter.split(e)):
        tree = core.fit_selection_tree(e[tr], max_depth=MAX_DEPTH,
                                       min_leaf=MIN_LEAF,
                                       random_state=SEED + 1000 * fold)
        fitted_train.append([int(orig[i]) for i in tr])
        paths = tree.route_many(e[te])
        leaves = np.array([p[-1] for p in paths], dtype=int)
        for leaf_id in np.unique(leaves):
            local = np.flatnonzero(leaves == leaf_id)
            if len(local) < 2:
                continue
            c = tree.nodes[int(leaf_id)].centroid
            re_ = e[te[local]] - c
            rl_ = l[te[local]] - c
            groups.append({
                "fold": int(fold), "leaf": int(leaf_id),
                "members": [int(orig[te[i]]) for i in local],
                "scores": core._cosine_matrix(re_, rl_),
                "train_rows": [int(orig[i]) for i in tr],
                "tree": tree})
    return {"groups": groups, "valid_original_indices": orig.tolist(),
            "n_valid": int(len(e)), "fitted_train": fitted_train}


def _auc(pos: np.ndarray, neg: np.ndarray) -> float:
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    order = np.argsort(allv, kind="mergesort")
    ranks = np.empty(len(allv), dtype=float)
    ranks[order] = np.arange(1, len(allv) + 1)
    # average ranks for ties
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.zeros(len(cnt))
    np.add.at(sums, inv, ranks)
    ranks = (sums / cnt)[inv]
    r_pos = ranks[: len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


# ---------------------------------------------------------------------------
# THE CALIPER LADDER.


def admissible_mask(obs: dict[str, np.ndarray], members: list[int],
                    level: str, scale: float = 1.0) -> np.ndarray:
    """(m x m) boolean: is stranger j admissible for target i at this level?

    ``scale`` widens every caliper by a common factor.  It is 1.0 -- the
    registered widths -- everywhere a verdict is computed; the only caller
    that moves it is the UNREGISTERED width diagnostic in section 10.4 of
    the report, which exists to name a redesign, not to claim a result.
    """
    m = len(members)
    idx = np.array(members, dtype=int)
    ok = np.ones((m, m), dtype=bool)
    np.fill_diagonal(ok, False)
    if level == "L0":
        return ok
    v = np.clip(obs["volume_late"][idx], 1.0, None)
    ok &= np.abs(np.log2(v[:, None] / v[None, :])) <= CAL_VOLUME * scale
    if level == "L1":
        return ok
    sp = obs["span_late_days"][idx]
    ok &= np.abs(sp[:, None] - sp[None, :]) <= CAL_SPAN_DAYS * scale
    if level == "L2":
        return ok
    h = obs["entropy_late"][idx]
    ok &= np.abs(h[:, None] - h[None, :]) <= CAL_ENTROPY_BITS * scale
    if level == "L3":
        return ok
    b = np.clip(obs["breadth_late"][idx], 1.0, None)
    lo = 1.0 - (1.0 - CAL_BREADTH[0]) * scale
    hi = 1.0 + (CAL_BREADTH[1] - 1.0) * scale
    ratio = b[:, None] / b[None, :]
    ok &= (ratio >= max(lo, 1e-6)) & (ratio <= hi)
    return ok


def avg_ranks(values: np.ndarray) -> np.ndarray:
    """Tie-averaged ranks, matching ``_auc``'s own rank convention."""
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.arange(1, len(values) + 1)
    _, inv, cnt = np.unique(values, return_inverse=True, return_counts=True)
    sums = np.zeros(len(cnt))
    np.add.at(sums, inv, ranks)
    return (sums / cnt)[inv]


def ragged_gather(off: np.ndarray, length: np.ndarray,
                  pick: np.ndarray) -> np.ndarray:
    """Indices of the concatenated per-target negative blocks for ``pick``."""
    lens = length[pick]
    total = int(lens.sum())
    if total == 0:
        return np.zeros(0, dtype=np.int64)
    csum = np.concatenate(([0], np.cumsum(lens)[:-1]))
    return np.repeat(off[pick] - csum, lens) + np.arange(total)


def auc_from_ids(pos_ids: np.ndarray, neg_ids: np.ndarray, n_vals: int) -> float:
    """Mann-Whitney AUC with tie correction, computed over value ids."""
    cn = np.bincount(neg_ids, minlength=n_vals)
    lower = np.cumsum(cn) - cn
    stat = float((lower[pos_ids] + 0.5 * cn[pos_ids]).sum())
    return stat / (len(pos_ids) * len(neg_ids))


class Pack:
    """Flat per-target arrays for one comparison set (a ladder level or Arm B).

    ``pos[t]`` is the same-author score; ``neg_vals[off[t]:off[t]+len[t]]`` are
    that target's admissible strangers.  Everything downstream (bootstrap,
    permutation null, per-leaf split) is batched numpy over these arrays --
    no per-user Python loop ever runs inside a replicate.
    """

    def __init__(self, pos: list[float], negs: list[np.ndarray],
                 keys: list[tuple[int, int]], pools: list[int]) -> None:
        self.pos = np.asarray(pos, dtype=float)
        self.neg_len = np.array([len(x) for x in negs], dtype=np.int64)
        self.neg_off = (np.concatenate(([0], np.cumsum(self.neg_len)[:-1]))
                        if len(negs) else np.zeros(0, dtype=np.int64))
        self.neg_vals = (np.concatenate(negs) if negs
                         else np.zeros(0, dtype=float))
        self.keys = keys
        self.pools = np.asarray(pools, dtype=float)

    @property
    def n_targets(self) -> int:
        return len(self.pos)

    def evaluate(self, rng: np.random.Generator, b_boot: int,
                 b_perm: int) -> dict[str, Any]:
        t, m = self.n_targets, len(self.neg_vals)
        auc = _auc(self.pos, self.neg_vals)
        uniq, inv = np.unique(np.concatenate([self.pos, self.neg_vals]),
                              return_inverse=True)
        pid, nid = inv[:t], inv[t:]
        n_vals = len(uniq)
        # the vectorised AUC must agree with the reference implementation
        check = auc_from_ids(pid, nid, n_vals)
        boot = np.empty(b_boot)
        for b in range(b_boot):
            pick = rng.integers(0, t, size=t)
            boot[b] = auc_from_ids(pid[pick],
                                   nid[ragged_gather(self.neg_off,
                                                     self.neg_len, pick)],
                                   n_vals)
        # within-leaf x within-stratum permutation null: one admissible
        # stranger's late half is promoted per target, the rest stay negative.
        # The combined multiset is therefore ALWAYS neg_vals, so its
        # tie-averaged ranks are precomputed once and every replicate is a
        # gather -- exactly the loop's statistic, without the loop.
        ranks = avg_ranks(self.neg_vals)
        draw = (self.neg_off[None, :]
                + (rng.random((b_perm, t)) * self.neg_len[None, :]
                   ).astype(np.int64))
        rsum = ranks[draw].sum(axis=1)
        nulls = (rsum - t * (t + 1) / 2.0) / (t * (m - t))
        return {
            "auc": auc, "auc_vectorised_check": check,
            "auc_check_ok": bool(abs(auc - check) < 1e-12),
            "n_targets": t, "n_negative": m,
            "ci95": [float(np.percentile(boot, 2.5)),
                     float(np.percentile(boot, 97.5))],
            "boot_sd": float(boot.std(ddof=1)),
            "null_mean": float(nulls.mean()), "null_sd": float(nulls.std(ddof=1)),
            "null_band": [float(np.percentile(nulls, 2.5)),
                          float(np.percentile(nulls, 97.5))],
            "median_pool": float(np.median(self.pools)) if len(self.pools) else 0.0,
            "mean_pool": float(np.mean(self.pools)) if len(self.pools) else 0.0,
            "b_boot": b_boot, "b_perm": b_perm,
        }

    def per_leaf(self, min_targets: int = 5) -> list[dict[str, Any]]:
        by: dict[tuple[int, int], list[int]] = defaultdict(list)
        for i, k in enumerate(self.keys):
            by[k].append(i)
        out = []
        for (fold, leaf), rows in sorted(by.items()):
            if len(rows) < min_targets:
                continue
            idx = np.array(rows)
            negs = self.neg_vals[ragged_gather(self.neg_off, self.neg_len, idx)]
            out.append({"fold": fold, "leaf": leaf, "n_targets": len(rows),
                        "auc": _auc(self.pos[idx], negs)})
        return out


def build_pack(groups: list[dict[str, Any]], obs: dict[str, np.ndarray],
               level: str,
               target_users: set[int] | None = None) -> Pack:
    pos: list[float] = []
    negs: list[np.ndarray] = []
    keys: list[tuple[int, int]] = []
    pools: list[int] = []
    for g in groups:
        members = g["members"]
        scores = g["scores"]
        ok = admissible_mask(obs, members, level)
        for i, user in enumerate(members):
            cand = np.flatnonzero(ok[i])
            if target_users is not None and user not in target_users:
                continue
            pools.append(int(len(cand)))
            if len(cand) == 0 or not np.isfinite(scores[i, i]):
                continue
            row = scores[i, cand]
            row = row[np.isfinite(row)]
            if row.size == 0:
                continue
            pos.append(float(scores[i, i]))
            negs.append(row)
            keys.append((int(g["fold"]), int(g["leaf"])))
    return Pack(pos, negs, keys, pools)


def ladder_level(groups: list[dict[str, Any]], obs: dict[str, np.ndarray],
                 level: str, b_perm: int, seed: int,
                 b_boot: int = B_BOOT,
                 target_users: set[int] | None = None) -> dict[str, Any]:
    """One rung of the cumulative caliper ladder (RN-T2-2, RN-T2-3)."""
    rng = np.random.default_rng(seed)
    pack = build_pack(groups, obs, level, target_users)
    if pack.n_targets == 0 or len(pack.neg_vals) <= pack.n_targets:
        return {"level": level, "UNDERRESOLVED": True,
                "reason": "no admissible pairs", "median_pool": 0.0,
                "n_targets": int(pack.n_targets),
                "mean_pool": float(np.mean(pack.pools)) if len(pack.pools) else 0.0}
    out = pack.evaluate(rng, b_boot=b_boot, b_perm=b_perm)
    out["level"] = level
    out["UNDERRESOLVED"] = bool(out["median_pool"] < MIN_POOL_MEDIAN)
    out["above_null"] = bool(out["ci95"][0] > out["null_band"][1])
    out["per_leaf"] = pack.per_leaf()
    return out


# ---------------------------------------------------------------------------
# ARM B -- PPMI + SVD transport.


def ppmi_svd(counts: np.ndarray, dim: int, seed: int) -> np.ndarray:
    """Community vectors from PPMI + truncated SVD of a sqrt-count matrix."""
    x = np.sqrt(np.clip(counts, 0, None))
    total = x.sum()
    if total <= 0:
        return np.zeros((counts.shape[1], dim))
    p = x / total
    pr = p.sum(axis=1, keepdims=True)
    pc = p.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(np.where(p > 0, p / np.clip(pr * pc, 1e-300, None), 1.0))
    ppmi = np.clip(np.nan_to_num(pmi), 0.0, None)
    _u, sv, vt = np.linalg.svd(ppmi, full_matrices=False)
    d = min(dim, vt.shape[0])
    return vt[:d].T * sv[:d]          # (n_communities x d)


def arm_b(early_counts: np.ndarray, late_counts: np.ndarray,
          groups: list[dict[str, Any]], obs: dict[str, np.ndarray],
          b_perm: int, seed: int, b_boot: int = B_BOOT,
          target_users: set[int] | None = None) -> dict[str, Any]:
    """Taste transport onto disjoint support (RN-T2-5).

    centroid_E is the count-weighted embedding centroid of the FULL early
    half; centroid_Lnew is the centroid of LATE communities ABSENT from that
    user's early half.  The embedding is fitted on TRAINING rows' early
    counts only, per fold, and the fitted row set is intersected with the
    held-out set (which must be empty) as the construction log.
    """
    rng = np.random.default_rng(seed)
    train_by_fold: dict[int, list[int]] = {}
    heldout_by_fold: dict[int, set[int]] = defaultdict(set)
    for g in groups:
        train_by_fold.setdefault(int(g["fold"]), list(g["train_rows"]))
        heldout_by_fold[int(g["fold"])].update(int(u) for u in g["members"])
    emb_by_fold: dict[int, np.ndarray] = {}
    purity: list[dict[str, Any]] = []
    for fold, tr_list in sorted(train_by_fold.items()):
        tr = np.asarray(tr_list, dtype=int)
        emb_by_fold[fold] = ppmi_svd(early_counts[tr], EMB_DIM, seed + fold)
        overlap = set(tr.tolist()) & heldout_by_fold[fold]
        purity.append({"fold": fold, "n_train_rows": int(len(tr)),
                       "n_heldout_rows": int(len(heldout_by_fold[fold])),
                       "train_x_heldout_overlap": int(len(overlap)),
                       "pure": bool(not overlap)})
    cent_e: dict[int, np.ndarray] = {}
    cent_ln: dict[int, np.ndarray] = {}
    n_new: dict[int, int] = {}
    for g in groups:
        emb = emb_by_fold[int(g["fold"])]
        for u in g["members"]:
            u = int(u)
            if u in n_new:
                continue
            ec, lc = early_counts[u], late_counts[u]
            new = np.flatnonzero((lc > 0) & (ec == 0))
            n_new[u] = int(len(new))
            if ec.sum() <= 0 or len(new) < MIN_NEW_COMMUNITIES:
                continue
            cent_e[u] = (ec / ec.sum()) @ emb
            cent_ln[u] = (lc[new] / lc[new].sum()) @ emb[new]
    keep = set(cent_e) & set(cent_ln)
    bgroups: list[dict[str, Any]] = []
    for g in groups:
        mem = [int(u) for u in g["members"] if int(u) in keep]
        if len(mem) < 2:
            continue
        left = np.stack([cent_e[u] for u in mem])
        right = np.stack([cent_ln[u] for u in mem])
        scores = t1core()._cosine_matrix(left, right)
        bgroups.append({"fold": int(g["fold"]), "leaf": int(g["leaf"]),
                        "members": mem, "scores": scores})
    all_new = np.array(list(n_new.values()), dtype=float)
    attrition = {
        "n_considered": int(len(n_new)),
        "n_with_ge_min_new_communities": int(np.sum(all_new
                                                    >= MIN_NEW_COMMUNITIES)),
        "min_new_communities_required": MIN_NEW_COMMUNITIES,
        "median_new_communities": float(np.median(all_new)),
        "n_retained": int(len(keep)),
        "retained_fraction": float(len(keep) / max(1, len(n_new))),
        "n_leaves_usable": int(len(bgroups))}
    embedding = {"dim": EMB_DIM, "folds": purity,
                 "all_folds_pure": bool(all(p["pure"] for p in purity)),
                 "fit_on": "TRAINING rows' EARLY sqrt-count matrix only",
                 "construction": (f"{rel(Path(__file__))}:ppmi_svd + arm_b "
                                  "fold loop"),
                 "note": RN_NOTES["RN-T2-5"]}
    pack = build_pack(bgroups, obs, "L1", target_users)
    if pack.n_targets == 0 or len(pack.neg_vals) <= pack.n_targets:
        return {"UNDERRESOLVED": True, "reason": "no admissible pairs",
                "attrition": attrition, "embedding": embedding,
                "n_targets": int(pack.n_targets), "median_pool": 0.0}
    out = pack.evaluate(rng, b_boot=b_boot, b_perm=b_perm)
    # RN-T2-9: the median-pool rule is registered for ladder LEVELS.  Arm B's
    # registered resolution test is its BAND (G2t2), so its pool is reported
    # prominently and flagged, not used to auto-void the verdict.
    out["thin_pool"] = bool(out["median_pool"] < MIN_POOL_MEDIAN)
    out["UNDERRESOLVED"] = bool(not _separates(out)["separates"])
    out["above_null"] = bool(out["ci95"][0] > out["null_band"][1])
    out["band_calibration"] = _separates(out)
    out["attrition"] = attrition
    out["embedding"] = embedding
    out["per_leaf"] = pack.per_leaf()
    out["stranger_matching"] = "leaf + L1 (in-vocabulary late volume caliper)"
    return out


def _load_inputs() -> dict[str, Any]:
    d = np.load(SR1NPZ, allow_pickle=True)
    users = [str(u) for u in d["users"]]
    return {"users": users, "freq_early": d["freq_early"],
            "freq_late": d["freq_late"], "counts": d["counts"]}


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")
    s = read_json(T1RES / "summary.json")
    full, clean = s["arms"]["full"], s["arms"]["clean_no_explicit_personality"]
    abl = s["ablation"]
    checks = {
        "terminal_residual_auc_full": [full["terminal_residual_auc"], A_RESID_FULL],
        "terminal_residual_auc_clean": [clean["terminal_residual_auc"],
                                        A_RESID_CLEAN],
        "path_auc_full": [full["hierarchical_path_auc"], A_PATH_FULL],
        "path_auc_clean": [clean["hierarchical_path_auc"], A_PATH_CLEAN],
        "n_valid_full": [full["n_valid"], A_N_FULL],
        "n_valid_clean": [clean["n_valid"], A_N_CLEAN],
        "vocabulary": [abl["vocabulary_size"], A_VOCAB],
        "floor_users": [abl["floor_users"], A_FLOOR],
        "n_removed": [abl["n_removed"], A_REMOVED],
    }
    g0 = {"t1_checks": {k: {"persisted": v[0], "expected": v[1],
                            "match": bool(v[0] == v[1])}
                        for k, v in checks.items()},
          "t1_core_sha256": sha_file(T1CORE),
          "t1_driver_sha256": sha_file(T1DRIVER),
          "sr1_npz_sha256": sha_file(SR1NPZ)}
    g0["all_t1_match"] = bool(all(c["match"] for c in g0["t1_checks"].values()))

    inp = _load_inputs()
    vocab, vinfo = t1drv().reconstruct_vocabulary(COMMENTS, SR0COHORT)
    g0["vocab_rebuilt"] = {"size": len(vocab), "floor": vinfo["floor_users"],
                           "matches_1191": bool(len(vocab) == A_VOCAB),
                           "matches_floor": bool(vinfo["floor_users"] == A_FLOOR)}
    obs_raw = late_observables(inp["users"])
    fl = inp["freq_late"]
    breadth = (fl > 0).sum(axis=1).astype(float)
    ent = entropy_bits(fl)
    # late in-vocab volume: total late comments scaled to in-vocab share
    obs = {"volume_late": obs_raw["volume_late_all"],
           "span_late_days": obs_raw["span_late_days"],
           "entropy_late": ent, "breadth_late": breadth}
    np.savez_compressed(OUT / "observables.npz", **obs)

    resid = build_residuals(inp["freq_early"], inp["freq_late"])
    g0["n_valid_reconstructed"] = resid["n_valid"]
    g0["n_valid_matches_t1"] = bool(resid["n_valid"] == A_N_FULL)
    l0 = ladder_level(resid["groups"], obs, "L0", b_perm=99, seed=SEED)
    g0["L0_anchor"] = {"auc": l0["auc"], "t1_auc": A_RESID_FULL,
                       "abs_diff": abs(l0["auc"] - A_RESID_FULL),
                       "ci95": l0["ci95"],
                       "reproduces_within_bootstrap": bool(
                           l0["ci95"][0] <= A_RESID_FULL <= l0["ci95"][1])}
    g0["PASS"] = bool(g0["all_t1_match"] and g0["vocab_rebuilt"]["matches_1191"]
                      and g0["n_valid_matches_t1"]
                      and g0["L0_anchor"]["reproduces_within_bootstrap"])
    write_json(OUT / "part0.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(), "G0t2": g0,
        "RN_NOTES": RN_NOTES,
        "observables_summary": {k: {"mean": float(np.mean(v)),
                                    "median": float(np.median(v)),
                                    "min": float(np.min(v)),
                                    "max": float(np.max(v))}
                                for k, v in obs.items()},
        "environment": {"python_executable": sys.executable,
                        "python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - t0})
    _log("part0_done", pass_=g0["PASS"])
    if not g0["PASS"]:
        raise SystemExit(f"G0t2 FAILED -> STOP  {g0}")
    print(f"part0 OK  T1 anchors all match={g0['all_t1_match']}  vocab="
          f"{len(vocab)}  n_valid={resid['n_valid']}\n"
          f"  L0 anchor AUC={l0['auc']!r} vs T1 {A_RESID_FULL!r} "
          f"(|diff| {g0['L0_anchor']['abs_diff']:.6f}, reproduces="
          f"{g0['L0_anchor']['reproduces_within_bootstrap']})  "
          f"{time.time() - t0:.1f}s")


def stage_counts(args: argparse.Namespace) -> None:
    """Reconstruct the half-split COUNT matrices Arm B needs and the
    registration-compliant in-vocabulary volume caliper Arm A needs."""
    t0 = time.time()
    _log("counts_start")
    inp = _load_inputs()
    users = inp["users"]
    vocab, vinfo = t1drv().reconstruct_vocabulary(COMMENTS, SR0COHORT)
    vocab = list(vocab)
    if len(vocab) != inp["freq_early"].shape[1]:
        raise SystemExit("vocabulary width mismatch -> STOP")
    early, late = rebuild_half_counts(users, vocab)
    fe_hat, fl_hat = row_normalise(early), row_normalise(late)
    d_e = float(np.abs(fe_hat - inp["freq_early"]).max())
    d_l = float(np.abs(fl_hat - inp["freq_late"]).max())
    support_e = bool(np.array_equal(fe_hat > 0, inp["freq_early"] > 0))
    support_l = bool(np.array_equal(fl_hat > 0, inp["freq_late"] > 0))
    ok = bool(d_e < 1e-12 and d_l < 1e-12 and support_e and support_l)
    removed = [i for i, n in enumerate(vocab)
               if t1drv().is_explicit_personality_community(n)]
    obs0 = dict(np.load(OUT / "observables.npz"))
    obs = observables_from(late, inp["freq_late"], obs0["span_late_days"])
    np.savez_compressed(OUT / "counts.npz", early_counts=early, late_counts=late,
                        removed_indices=np.array(removed, dtype=int),
                        vocab=np.array(vocab, dtype=object), **obs)
    rec = {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "reconstruction_vs_sr1": {
            "max_abs_freq_early_diff": d_e, "max_abs_freq_late_diff": d_l,
            "support_pattern_early_identical": support_e,
            "support_pattern_late_identical": support_l, "PASS": ok},
        "vocabulary": {"size": len(vocab), "floor_users": vinfo["floor_users"],
                       "n_explicit_personality_removed": len(removed),
                       "matches_t1_ablation": bool(len(removed) == A_REMOVED)},
        "totals": {"early_comments": int(early.sum()),
                   "late_comments": int(late.sum())},
        "volume_caliper_repair": {
            "registered": "in-vocabulary late comment volume",
            "part0_persisted": "all-subreddit late comment volume",
            "median_invocab": float(np.median(obs["volume_late"])),
            "median_all": float(np.median(obs0["volume_late"])),
            "spearman_like_ratio_median": float(np.median(
                obs["volume_late"] / np.clip(obs0["volume_late"], 1, None)))},
        "observables_summary": {k: {"mean": float(np.mean(v)),
                                    "median": float(np.median(v)),
                                    "min": float(np.min(v)),
                                    "max": float(np.max(v))}
                                for k, v in obs.items()},
        "seconds": time.time() - t0}
    write_json(OUT / "counts.json", rec)
    _log("counts_done", pass_=ok)
    if not ok:
        raise SystemExit(f"count reconstruction does not match SR1 -> STOP {rec}")
    print(f"counts OK  early={early.sum()} late={late.sum()}  "
          f"max|dfreq| early={d_e:.3e} late={d_l:.3e}  removed={len(removed)}  "
          f"median in-vocab late volume={np.median(obs['volume_late'])} "
          f"(all-subreddit was {np.median(obs0['volume_late'])})  "
          f"{time.time() - t0:.1f}s")


def _load_counts() -> dict[str, Any]:
    d = np.load(OUT / "counts.npz", allow_pickle=True)
    return {"early_counts": d["early_counts"].astype(float),
            "late_counts": d["late_counts"].astype(float),
            "removed_indices": d["removed_indices"],
            "obs": {k: d[k] for k in ("volume_late", "span_late_days",
                                      "entropy_late", "breadth_late")}}


def prepare(arm: str) -> dict[str, Any]:
    """Build the residual groups, observables and counts for one arm.

    ``clean`` reproduces T1's ablation exactly (the 23 explicit-personality
    columns zeroed in BOTH halves before the Hellinger map) and recomputes the
    selection-side observables on the ablated matrices -- see RN-T2-7.
    """
    inp = _load_inputs()
    c = _load_counts()
    fe = np.asarray(inp["freq_early"], dtype=float).copy()
    fl = np.asarray(inp["freq_late"], dtype=float).copy()
    ec, lc = c["early_counts"].copy(), c["late_counts"].copy()
    if arm == "clean":
        rem = c["removed_indices"]
        for m in (fe, fl, ec, lc):
            m[:, rem] = 0.0
        obs = observables_from(lc, row_normalise(lc), c["obs"]["span_late_days"])
    else:
        obs = c["obs"]
    resid = build_residuals(fe, fl)
    members = sorted({int(u) for g in resid["groups"] for u in g["members"]})
    return {"groups": resid["groups"], "obs": obs, "early_counts": ec,
            "late_counts": lc, "n_valid": resid["n_valid"], "members": members}


def _pilot_targets(members: list[int]) -> set[int]:
    rng = np.random.default_rng(SEED + 7)
    n = min(PILOT_USERS, len(members))
    pick = rng.choice(np.asarray(members), size=n, replace=False)
    return {int(u) for u in pick}


def _separates(res: dict[str, Any]) -> dict[str, Any]:
    """G2t2: can this level's null band tell 0.5 from 0.75?

    Three things must hold, and the third is the one the corpus breaks.
    (i) the band's upper edge must fall below 0.75, so a true 0.75 would
    read as signal; (ii) the band must be narrower than the 0.25 gap it is
    asked to resolve; (iii) the band must be NON-DEGENERATE.  A level whose
    admissible pools have collapsed to one or two candidates produces a
    band of literally zero width sitting nowhere near 0.5 -- it would pass
    a naive "upper edge below 0.75" test while resolving nothing at all.
    """
    if res.get("null_band") is None:
        return {"separates": False, "reason": "no null band"}
    lo, hi = float(res["null_band"][0]), float(res["null_band"][1])
    width = hi - lo
    non_degenerate = bool(width > 1e-9 and float(res.get("null_sd", 0.0)) > 1e-9)
    return {"null_band_hi": hi, "null_mean": float(res["null_mean"]),
            "null_sd": float(res["null_sd"]), "band_width": width,
            "n_negative": res.get("n_negative"),
            "median_pool": res.get("median_pool"),
            "upper_edge_below_0.75": bool(hi < SEP_HI),
            "narrower_than_the_gap": bool(width < SEP_HI - SEP_LO),
            "non_degenerate": non_degenerate,
            "null_centred_on_0.5": bool(abs(res["null_mean"] - SEP_LO) < 0.05),
            "separates": bool(hi < SEP_HI and width < SEP_HI - SEP_LO
                              and non_degenerate)}


def stage_pilot(args: argparse.Namespace) -> None:
    """G2t2 -- projection BEFORE the full run, on a 200-user subsample.

    The subsample restricts the TARGETS, never the candidate pools: the null
    bandwidth measured here is therefore the one achievable at the corpus's
    REALIZED pool sizes, and is conservative (fewer targets => wider band)
    relative to the full run.
    """
    t0 = time.time()
    _log("pilot_start")
    prep = prepare("full")
    targets = _pilot_targets(prep["members"])
    levels: dict[str, Any] = {}
    for i, level in enumerate(LADDER):
        r = ladder_level(prep["groups"], prep["obs"], level,
                         b_perm=B_PILOT_PERM, seed=SEED + 31 * i,
                         b_boot=200, target_users=targets)
        r.pop("per_leaf", None)
        r["calibration"] = _separates(r)
        levels[level] = r
        print(f"  pilot {level}: targets={r.get('n_targets')} "
              f"median_pool={r.get('median_pool')} "
              f"null={r.get('null_band')} sep={r['calibration']['separates']}")
    b = arm_b(prep["early_counts"], prep["late_counts"], prep["groups"],
              prep["obs"], b_perm=B_PILOT_PERM, seed=SEED + 991, b_boot=200,
              target_users=targets)
    b.pop("per_leaf", None)
    b["calibration"] = _separates(b)
    print(f"  pilot armB: targets={b.get('n_targets')} "
          f"median_pool={b.get('median_pool')} null={b.get('null_band')} "
          f"sep={b['calibration']['separates']}")
    l4_ok = bool(levels["L4"]["calibration"]["separates"])
    b_ok = bool(b["calibration"]["separates"])
    verdict = "PASS" if (l4_ok and b_ok) else "UNDERRESOLVED_BY_DESIGN"
    write_json(OUT / "pilot.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "G2t2": {"n_pilot_targets": len(targets), "b_perm": B_PILOT_PERM,
                 "separation_test": {"lo": SEP_LO, "hi": SEP_HI},
                 "L4_separates": l4_ok, "armB_separates": b_ok,
                 "VERDICT": verdict,
                 "note": RN_NOTES["RN-T2-6"]},
        "levels": levels, "arm_b": b, "seconds": time.time() - t0})
    _log("pilot_done", verdict=verdict)
    print(f"pilot {verdict}  L4 sep={l4_ok}  armB sep={b_ok}  "
          f"{time.time() - t0:.1f}s")
    if verdict != "PASS":
        print("  G2t2 fired BEFORE the full run: V-T2a is UNDERRESOLVED "
              "BY DESIGN and no survival/collapse claim may be made at L4. "
              "The full ladder still runs, because routing cell 5 obliges "
              "this leg to REPORT the attrition and the realized pool sizes "
              "that produced the finding -- not to buy resolution it cannot "
              "have.")


def _run_arms(arm: str, seed_shift: int) -> dict[str, Any]:
    prep = prepare(arm)
    levels: dict[str, Any] = {}
    for i, level in enumerate(LADDER):
        r = ladder_level(prep["groups"], prep["obs"], level, b_perm=B_PERM,
                         seed=SEED + seed_shift + 31 * i)
        levels[level] = r
        print(f"  {arm} {level}: AUC={r.get('auc')} CI={r.get('ci95')} "
              f"null={r.get('null_band')} pool_med={r.get('median_pool')} "
              f"n={r.get('n_targets')}")
    b = arm_b(prep["early_counts"], prep["late_counts"], prep["groups"],
              prep["obs"], b_perm=B_PERM, seed=SEED + seed_shift + 991)
    print(f"  {arm} armB: AUC={b.get('auc')} CI={b.get('ci95')} "
          f"null={b.get('null_band')} n={b.get('n_targets')}")
    return {"arm": arm, "n_valid": prep["n_valid"], "levels": levels,
            "arm_b": b}


def caliper_width_diagnostic(groups: list[dict[str, Any]],
                             obs: dict[str, np.ndarray]) -> dict[str, Any]:
    """UNREGISTERED DIAGNOSTIC -- names a redesign, claims nothing.

    How much wider would every caliper have to be for L4's admissible pool
    to reach the registered floor of 5?  No AUC is computed here and no
    verdict depends on it.
    """
    rows = []
    for scale in (1.0, 2.0, 4.0, 8.0, 16.0):
        entry: dict[str, Any] = {"scale": scale}
        for level in LADDER:
            pools = []
            for g in groups:
                ok = admissible_mask(obs, g["members"], level, scale=scale)
                pools.extend(ok.sum(axis=1).tolist())
            entry[level] = float(np.median(pools))
        rows.append(entry)
    reach = next((r["scale"] for r in rows if r["L4"] >= MIN_POOL_MEDIAN), None)
    return {"UNREGISTERED": True, "rows": rows,
            "scale_reaching_pool_floor_at_L4": reach,
            "pool_floor": MIN_POOL_MEDIAN}


def stage_arms(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("arms_start")
    res = _run_arms("full", 0)
    prep = prepare("full")
    res["caliper_width_diagnostic"] = caliper_width_diagnostic(prep["groups"],
                                                               prep["obs"])
    res["utc"] = datetime.now(UTC).isoformat()
    res["seconds"] = time.time() - t0
    write_json(OUT / "arms_full.json", res)
    _log("arms_done", seconds=res["seconds"])
    print(f"arms(full) done  {time.time() - t0:.1f}s")


def stage_clean(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("clean_start")
    res = _run_arms("clean", 500)
    res["utc"] = datetime.now(UTC).isoformat()
    res["seconds"] = time.time() - t0
    res["n_valid_matches_t1_clean"] = bool(res["n_valid"] == A_N_CLEAN)
    write_json(OUT / "arms_clean.json", res)
    _log("clean_done", seconds=res["seconds"])
    print(f"arms(clean) done  n_valid={res['n_valid']} "
          f"(T1 clean {A_N_CLEAN}: {res['n_valid_matches_t1_clean']})  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# VERDICTS (NULL-first, rule 22).


def _inside_band(res: dict[str, Any]) -> bool:
    lo, hi = res["null_band"]
    sd = res["null_sd"]
    return bool(res["ci95"][0] >= lo - sd and res["ci95"][1] <= hi + sd)


def verdict_a(res: dict[str, Any]) -> dict[str, Any]:
    if res.get("UNDERRESOLVED") or "auc" not in res:
        return {"verdict": "UNDERRESOLVED",
                "reason": f"median admissible pool {res.get('median_pool')} "
                          f"< {MIN_POOL_MEDIAN}" if res.get("median_pool") is
                          not None else "no admissible pairs"}
    above = bool(res["ci95"][0] > res["null_band"][1])
    if _inside_band(res) and not above:
        return {"verdict": "COLLAPSED",
                "reason": "the bootstrap CI lies inside the permutation null "
                          "band widened by its own spread (equivalence first)"}
    if above and res["auc"] >= 0.90:
        return {"verdict": "STRONG_SURVIVAL",
                "reason": "CI entirely above the null band and point AUC >= 0.90"}
    if above:
        return {"verdict": "PARTIAL",
                "reason": "CI entirely above the null band, point AUC < 0.90"}
    return {"verdict": "UNDERRESOLVED",
            "reason": "the CI neither sits inside the widened null band nor "
                      "clears it entirely"}


def verdict_b(res: dict[str, Any]) -> dict[str, Any]:
    if res.get("UNDERRESOLVED") or "auc" not in res:
        return {"verdict": "UNDERRESOLVED",
                "reason": f"median admissible pool {res.get('median_pool')} "
                          f"< {MIN_POOL_MEDIAN}"}
    if res["ci95"][0] > res["null_band"][1]:
        return {"verdict": "TRANSPORTS",
                "reason": "CI entirely above the null band -- the early-half "
                          "taste centroid predicts communities the user had "
                          "not yet joined"}
    if _inside_band(res):
        return {"verdict": "LOYALTY_ONLY",
                "reason": "CI inside the widened null band -- no transport "
                          "onto disjoint support"}
    return {"verdict": "UNDERRESOLVED",
            "reason": "the CI neither sits inside the widened null band nor "
                      "clears it entirely"}


def route(va: str, vb: str, g0_ok: bool) -> dict[str, str]:
    if not g0_ok:
        return {"cell": "1", "outcome": "STOP", "slug": "stop"}
    if va == "COLLAPSED":
        return {"cell": "2", "outcome": "SUPPORT_ARTIFACT_MAJOR",
                "slug": "support-artifact-major"}
    survives = va in {"STRONG_SURVIVAL", "PARTIAL"}
    if survives and vb == "TRANSPORTS":
        return {"cell": "3", "outcome": "CONTINUOUS_TASTE_COORDINATE",
                "slug": "continuous-taste-coordinate"}
    if survives and vb == "LOYALTY_ONLY":
        return {"cell": "4", "outcome": "HISTORY_IDENTITY",
                "slug": "history-identity"}
    return {"cell": "5", "outcome": "UNDERRESOLVED", "slug": "underresolved"}


def _leaf_summary(per_leaf: list[dict[str, Any]]) -> dict[str, Any]:
    if not per_leaf:
        return {"n_leaves": 0}
    a = np.array([x["auc"] for x in per_leaf], dtype=float)
    a = a[np.isfinite(a)]
    return {"n_leaves": int(len(a)), "min": float(a.min()),
            "q25": float(np.percentile(a, 25)), "median": float(np.median(a)),
            "q75": float(np.percentile(a, 75)), "max": float(a.max()),
            "iqr": float(np.percentile(a, 75) - np.percentile(a, 25)),
            "n_below_0.6": int(np.sum(a < 0.6))}


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("finalize_start")
    p0 = read_json(OUT / "part0.json")
    cnt = read_json(OUT / "counts.json")
    pil = read_json(OUT / "pilot.json")
    full = read_json(OUT / "arms_full.json")
    clean = read_json(OUT / "arms_clean.json")
    g0_ok = bool(p0["G0t2"]["PASS"]
                 and cnt["reconstruction_vs_sr1"]["PASS"])
    l4 = full["levels"]["L4"]
    g2 = pil["G2t2"]["VERDICT"]
    if g2 != "PASS":
        # G2t2 fired BEFORE the full run.  The L4 verdict was therefore
        # already spent: no survival and no collapse may be claimed there,
        # whatever the number turned out to be.
        va = {"verdict": "UNDERRESOLVED",
              "reason": "declared UNDERRESOLVED BY DESIGN at G2t2, before the "
                        "full run -- the L4 permutation band is degenerate at "
                        "the corpus's realized pool sizes, so neither survival "
                        "nor collapse is decidable there",
              "declared_by": "G2t2 (pre-run)"}
    else:
        va = verdict_a(l4)
    va_posthoc = verdict_a(l4)
    vb = verdict_b(full["arm_b"])
    routing = route(va["verdict"], vb["verdict"], g0_ok)
    # G1t2 -- #59 non-degeneracy
    aucs = [full["levels"][k].get("auc") for k in LADDER
            if full["levels"][k].get("auc") is not None]
    g1 = {"calipers_restrict_not_equalize": {
              "auc_moves_across_ladder": bool(max(aucs) - min(aucs) > 1e-9),
              "auc_range": [float(min(aucs)), float(max(aucs))],
              "note": RN_NOTES["RN-T2-4"]},
          "centroid_Lnew_nonempty": bool(
              full["arm_b"].get("attrition", {}).get("n_retained", 0) > 0),
          "embedding_heldout_purity": bool(
              full["arm_b"].get("embedding", {}).get("all_folds_pure", False)),
          "PASS": True}
    g1["PASS"] = bool(g1["calipers_restrict_not_equalize"]
                      ["auc_moves_across_ladder"]
                      and g1["centroid_Lnew_nonempty"]
                      and g1["embedding_heldout_purity"])
    # G3t2 -- rule-29 predicates
    checks = []
    for arm_name, blob in (("full", full), ("clean", clean)):
        for k in LADDER:
            r = blob["levels"][k]
            if "auc" not in r:
                continue
            checks.append({"what": f"{arm_name}:{k}",
                           "auc_in_unit": bool(0.0 <= r["auc"] <= 1.0),
                           "null_at_half": bool(abs(r["null_mean"] - 0.5) < 0.05),
                           "auc_vectorised_agrees": bool(r["auc_check_ok"])})
        rb = blob["arm_b"]
        if "auc" in rb:
            checks.append({"what": f"{arm_name}:armB",
                           "auc_in_unit": bool(0.0 <= rb["auc"] <= 1.0),
                           "null_at_half": bool(abs(rb["null_mean"] - 0.5) < 0.05),
                           "auc_vectorised_agrees": bool(rb["auc_check_ok"])})
    # RD-T2-1: "null 0.5" is reported, not enforced -- see RN-T2-10.
    g3 = {"predicates": checks,
          "required": {"auc_in_unit": bool(all(c["auc_in_unit"] for c in checks)),
                       "auc_vectorised_agrees": bool(
                           all(c["auc_vectorised_agrees"] for c in checks))},
          "reported_not_enforced": {
              "null_at_half": {"n_pass": int(sum(c["null_at_half"]
                                                 for c in checks)),
                               "n_total": len(checks),
                               "flag": "RD-T2-1", "note": RN_NOTES["RN-T2-10"]}},
          "PASS": bool(all(c["auc_in_unit"] and c["auc_vectorised_agrees"]
                           for c in checks))}
    out = {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "gates": {"G0t2": g0_ok, "G1t2": g1, "G2t2": pil["G2t2"]["VERDICT"],
                  "G3t2": g3},
        "V_T2a_posthoc_if_gate_had_passed": va_posthoc,
        "V_T2a": {**va, "level": "L4", "numbers": {
            k: l4.get(k) for k in ("auc", "ci95", "null_mean", "null_sd",
                                   "null_band", "n_targets", "n_negative",
                                   "median_pool", "mean_pool", "boot_sd")}},
        "V_T2b": {**vb, "numbers": {
            k: full["arm_b"].get(k) for k in
            ("auc", "ci95", "null_mean", "null_sd", "null_band", "n_targets",
             "n_negative", "median_pool", "boot_sd")},
            "attrition": full["arm_b"].get("attrition"),
            "embedding": full["arm_b"].get("embedding")},
        "routing": routing,
        "readings": {
            "ladder_curve": [{"level": k, **{f: full["levels"][k].get(f)
                                             for f in ("auc", "ci95",
                                                       "null_band",
                                                       "median_pool",
                                                       "mean_pool",
                                                       "n_targets")}}
                             for k in LADDER],
            "clean_replication": {
                "n_valid": clean["n_valid"],
                "matches_t1_clean_n": clean.get("n_valid_matches_t1_clean"),
                "levels": [{"level": k, **{f: clean["levels"][k].get(f)
                                           for f in ("auc", "ci95",
                                                     "null_band",
                                                     "median_pool")}}
                           for k in LADDER],
                "arm_b": {f: clean["arm_b"].get(f) for f in
                          ("auc", "ci95", "null_band", "n_targets",
                           "median_pool")},
                "V_T2a_clean": verdict_a(clean["levels"]["L4"]),
                "V_T2b_clean": verdict_b(clean["arm_b"])},
            "caliper_width_diagnostic": full.get("caliper_width_diagnostic"),
            "per_leaf_heterogeneity": {
                "full_L0": _leaf_summary(full["levels"]["L0"].get("per_leaf", [])),
                "full_L4": _leaf_summary(full["levels"]["L4"].get("per_leaf", [])),
                "full_armB": _leaf_summary(full["arm_b"].get("per_leaf", []))}},
        "seconds": time.time() - t0}
    write_json(OUT / "verdicts.json", out)
    _log("finalize_done", outcome=routing["outcome"])
    print(f"V-T2a={va['verdict']}  V-T2b={vb['verdict']}  -> "
          f"{routing['outcome']} (cell {routing['cell']}, slug "
          f"{routing['slug']})  G1t2={g1['PASS']} G3t2={g3['PASS']}")


def _fmt(v: Any, nd: int = 4) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_fmt(x, nd) for x in v) + "]"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def _table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def id_leak_scan(text: str) -> dict[str, Any]:
    authors = set(pd.read_csv(SR0COHORT)["author"].astype(str))
    tokens = set(re.findall(r"[A-Za-z0-9_\-]{3,}", text))
    hits = sorted(tokens & authors)
    return {"n_cohort_ids": len(authors), "n_tokens_scanned": len(tokens),
            "n_hits": len(hits), "PASS": bool(not hits)}


def stage_report(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("report_start")
    p0 = read_json(OUT / "part0.json")
    cnt = read_json(OUT / "counts.json")
    pil = read_json(OUT / "pilot.json")
    full = read_json(OUT / "arms_full.json")
    clean = read_json(OUT / "arms_clean.json")
    v = read_json(OUT / "verdicts.json")
    g0 = p0["G0t2"]

    gates = _table(
        ["gate", "what it checks", "result"],
        [["G0t2", "T1 anchors bit-exact; vocabulary/floor at source; "
          "n_valid; L0 anchor within bootstrap error",
          f"**{'PASS' if g0['PASS'] else 'FAIL'}**"],
         ["G0t2 (recon)", "half-split count matrices re-derived and compared "
          "to SR1's own freq matrices",
          f"**{'PASS' if cnt['reconstruction_vs_sr1']['PASS'] else 'FAIL'}** "
          f"(max |Δfreq| early {cnt['reconstruction_vs_sr1']['max_abs_freq_early_diff']:.1e}, "
          f"late {cnt['reconstruction_vs_sr1']['max_abs_freq_late_diff']:.1e})"],
         ["G1t2", "#59 non-degeneracy: calipers restrict but do not equalize; "
          "centroid_Lnew nonempty; embedding held-out purity",
          f"**{'PASS' if v['gates']['G1t2']['PASS'] else 'FAIL'}**"],
         ["G2t2", "pilot permutation calibration BEFORE the full run "
          "(200 targets, realized pools)",
          f"**{v['gates']['G2t2']}**"],
         ["G3t2", "rule-29 predicates (AUC ∈ [0,1], null at 0.5, vectorised "
          "AUC agrees with the reference implementation)",
          f"**{'PASS' if v['gates']['G3t2']['PASS'] else 'FAIL'}** "
          f"({len(v['gates']['G3t2']['predicates'])} predicates)"]])

    anchors = _table(
        ["T1 quantity", "persisted", "adjudication-cited", "match"],
        [[k, repr(c["persisted"]), repr(c["expected"]), str(c["match"])]
         for k, c in sorted(g0["t1_checks"].items())])

    pilot_rows = []
    for k in LADDER:
        r = pil["levels"][k]
        c = r["calibration"]
        pilot_rows.append([k, _fmt(r.get("n_targets"), 0),
                           _fmt(r.get("median_pool"), 1),
                           _fmt(r.get("auc")), _fmt(c.get("null_mean")),
                           _fmt(r.get("null_band")),
                           _fmt(c.get("band_width")),
                           str(c.get("upper_edge_below_0.75")),
                           str(c.get("non_degenerate")),
                           f"**{c.get('separates')}**"])
    rb = pil["arm_b"]
    rbc = rb["calibration"]
    pilot_rows.append(["Arm B", _fmt(rb.get("n_targets"), 0),
                       _fmt(rb.get("median_pool"), 1), _fmt(rb.get("auc")),
                       _fmt(rb.get("null_mean")), _fmt(rb.get("null_band")),
                       _fmt(rbc.get("band_width")),
                       str(rbc.get("upper_edge_below_0.75")),
                       str(rbc.get("non_degenerate")),
                       f"**{rbc.get('separates')}**"])
    pilot_tbl = _table(["level", "targets", "median pool", "AUC",
                        "null mean", "null band (2.5–97.5%)", "band width",
                        "edge < 0.75", "non-degenerate",
                        "separates 0.5/0.75"], pilot_rows)

    def ladder_table(blob: dict[str, Any]) -> str:
        rows = []
        for k in LADDER:
            r = blob["levels"][k]
            if "auc" not in r:
                rows.append([k, "—", "—", "—", "—", "—", "—",
                             "**UNDERRESOLVED**"])
                continue
            lv = verdict_a(r)["verdict"] if k == "L4" else (
                "above null" if r["above_null"] else "not above null")
            if r["UNDERRESOLVED"]:
                lv = "**UNDERRESOLVED** (pool)"
            rows.append([k, _fmt(r["n_targets"], 0), _fmt(r["median_pool"], 1),
                         _fmt(r["mean_pool"], 1), _fmt(r["auc"]),
                         _fmt(r["ci95"]), _fmt(r["null_band"]), lv])
        return _table(["level", "targets", "median pool", "mean pool", "AUC",
                       "bootstrap CI95", "null band", "per-level verdict"], rows)

    def armb_table(blob: dict[str, Any]) -> str:
        r = blob["arm_b"]
        if "auc" not in r:
            return "Arm B produced no admissible pairs — **UNDERRESOLVED**."
        return _table(["quantity", "value"],
                      [["AUC (same-author vs leaf+L1-matched strangers)",
                        _fmt(r["auc"])],
                       ["bootstrap CI95 (B=1000, user resample)", _fmt(r["ci95"])],
                       ["permutation null band (B=999)", _fmt(r["null_band"])],
                       ["null mean ± sd",
                        f"{_fmt(r['null_mean'])} ± {_fmt(r['null_sd'])}"],
                       ["targets retained", _fmt(r["n_targets"], 0)],
                       ["negative comparisons", _fmt(r["n_negative"], 0)],
                       ["median admissible pool", _fmt(r["median_pool"], 1)]])

    att = full["arm_b"].get("attrition", {})
    att_tbl = _table(["attrition step", "value"],
                     [["users entering Arm B", _fmt(att.get("n_considered"), 0)],
                      [f"users with ≥ {MIN_NEW_COMMUNITIES} late communities "
                       "absent from their early half",
                       _fmt(att.get("n_with_ge_min_new_communities"), 0)],
                      ["median count of such new communities",
                       _fmt(att.get("median_new_communities"), 1)],
                      ["retained (both centroids defined)",
                       _fmt(att.get("n_retained"), 0)],
                      ["retained fraction",
                       _fmt(att.get("retained_fraction"), 3)],
                      ["leaves usable", _fmt(att.get("n_leaves_usable"), 0)]])
    emb = full["arm_b"].get("embedding", {})
    pur_tbl = _table(["fold", "training rows fitted", "held-out rows",
                      "train × held-out overlap", "pure"],
                     [[str(x["fold"]), str(x["n_train_rows"]),
                       str(x["n_heldout_rows"]),
                       str(x["train_x_heldout_overlap"]), str(x["pure"])]
                      for x in emb.get("folds", [])])

    het = v["readings"]["per_leaf_heterogeneity"]
    het_tbl = _table(["comparison set", "leaves", "min", "q25", "median",
                      "q75", "max", "IQR", "leaves < 0.60"],
                     [[name, _fmt(d.get("n_leaves"), 0), _fmt(d.get("min")),
                       _fmt(d.get("q25")), _fmt(d.get("median")),
                       _fmt(d.get("q75")), _fmt(d.get("max")),
                       _fmt(d.get("iqr")), _fmt(d.get("n_below_0.6"), 0)]
                      for name, d in het.items()])

    va, vb, rt = v["V_T2a"], v["V_T2b"], v["routing"]
    cl = v["readings"]["clean_replication"]

    body = f"""# SUICA M4-T2 — the condition-matched residual audit, and the taste-transport falsifier

**Leg:** {LEG}. **Registered BEFORE run** in
`docs/SUICA_M4_T_HIERARCHICAL_SELECTION_IDENTITY_PLAN.md` (§ "M4-T2",
commit 4e9e339). This report is generated by
`{rel(Path(__file__))}` (rule 24 — every table below is written by the
script from the persisted artifacts).

**LABEL-FREE.** No Big5 or MBTI column is opened at any stage. Only
aggregates appear here; author identifiers stay in the gitignored
intermediates under `results/m4_t2_matched_residual/`.

**Type:** EXPLORATORY. T1's tail is an established measurement; T2 asks
what carries it, and both of its arms are falsifiers pointed at T1's own
headline.

## 1. The question

T1 measured a terminal within-leaf residual AUC of {A_RESID_FULL:.4f} (full)
and {A_RESID_CLEAN:.4f} (clean): inside a frozen selection leaf, a user's late
half still identifies them from their early half. T2 asks WHAT CARRIES IT.

- **Arm A** — is it merely *observability*? Strangers are progressively
  restricted to those who look equally observable on the late side
  (volume, span, entropy, breadth). If the residual is a support
  artifact, the AUC falls into the permutation null once matching bites.
- **Arm B** — is it merely *loyalty* to specific communities? The
  early-half taste centroid is asked to identify the user through
  communities they had **not yet joined**. If identity is only history,
  transport fails.

## 2. Gates

{gates}

### G0t2 — T1 anchors (bit-exact)

{anchors}

The L0 anchor reproduces T1's pooled leaf-residual AUC exactly:
**{g0['L0_anchor']['auc']!r}** vs T1's **{A_RESID_FULL!r}**
(|diff| = {g0['L0_anchor']['abs_diff']:.1e}; bootstrap CI
{_fmt(g0['L0_anchor']['ci95'])}). The reconstructed vocabulary is
{g0['vocab_rebuilt']['size']} at floor {g0['vocab_rebuilt']['floor']}, and
n_valid = {g0['n_valid_reconstructed']} matches T1's {A_N_FULL}.

The half-split **count** matrices (which SR1 never persisted — it kept
row-normalised frequencies and a per-user total only) were re-derived from
the comment stream under SR1's own split rule and verified against SR1's
frequency matrices: max |Δfreq| =
{cnt['reconstruction_vs_sr1']['max_abs_freq_early_diff']:.1e} (early) and
{cnt['reconstruction_vs_sr1']['max_abs_freq_late_diff']:.1e} (late), with
support patterns identical in both halves. {cnt['totals']['early_comments']}
early and {cnt['totals']['late_comments']} late in-vocabulary comments.

## 3. Reading notes (pinned BEFORE the verdicts)

""" + "\n".join(f"- **{k}** — {vtxt}" for k, vtxt in sorted(RN_NOTES.items())) + f"""

## 4. Anomalies (disclosed with timing)

- **A1 — the T1 per-fold seed (pre-verdict, pre-Part-0).** T1's fold seed
  is `SEED + 1000 * fold`, not `SEED + fold`. The wrong reading returns
  0.9536 instead of the bit-exact {A_RESID_FULL!r}. Fixed before Part 0
  was accepted; the L0 anchor above is the proof.
- **A2 — the volume caliper was measured on the wrong population
  (pre-verdict, found and repaired before the pilot).** Part 0 persisted
  `volume_late` as the user's **all-subreddit** late comment count, while
  the registration pins L1 to **in-vocabulary** comment volume. The two
  differ materially (median {cnt['volume_caliper_repair']['median_invocab']}
  in-vocabulary vs {cnt['volume_caliper_repair']['median_all']}
  all-subreddit). The ladder below uses the registered in-vocabulary
  volume, obtained as the row sum of the verified late count matrix. The
  defect is reported rather than silently corrected; no verdict was
  computed under the wrong caliper.
- **A3 — the permutation null was vectorised (pre-verdict, method
  preserved exactly).** The registered null permutes late halves among
  admissible candidates within each leaf × stratum. Its combined value
  multiset is therefore *always* the flat pool of admissible stranger
  scores, so the tie-averaged ranks are precomputed once and each
  replicate is a single batched gather. This is the same statistic as the
  per-user loop, not an approximation; the vectorised AUC is checked
  against the reference implementation at every level (G3t2).
- **A4 — SR1's 4000-timestamp cap is inherited, not introduced
  (pre-verdict).** SR1 computes each user's median split time from at most
  the first 4000 timestamps in file order. Reproducing the frozen halves
  requires reproducing that cap, so this leg does; it is a property of the
  frozen upstream object, and it is named here because it is invisible in
  SR1's own report.

## 5. G2t2 — pilot calibration (200 targets, realized pools, B={B_PILOT_PERM})

Run BEFORE the full ladder, as registered. The subsample restricts the
targets and never the candidate pools (RN-T2-8), so these bands are
conservative relative to the full run.

{pilot_tbl}

**G2t2 verdict: {pil['G2t2']['VERDICT']}** — L4 separates:
{pil['G2t2']['L4_separates']}; Arm B separates:
{pil['G2t2']['armB_separates']}. A level "separates" when three things hold
at the pool sizes this corpus actually provides: the band's upper edge falls
below {SEP_HI} (so a true {SEP_HI} would read as signal), the band is
narrower than the {SEP_HI - SEP_LO:.2f} gap it must resolve, and the band is
non-degenerate. L3 and L4 fail the third condition outright — their
admissible pools have collapsed to one or two candidates, which yields a
band of literally zero width sitting nowhere near {SEP_LO}. A naive
"upper edge below {SEP_HI}" test would have passed those levels while they
resolved nothing whatsoever; that is the trap this gate exists to catch.

## 6. Arm A — the cumulative caliper ladder (full arm, B_boot={B_BOOT}, B_perm={B_PERM})

Calipers, cumulative: L1 in-vocabulary late volume |log2 ratio| ≤
{CAL_VOLUME}; L2 + active span |Δ| ≤ {CAL_SPAN_DAYS:.0f} d; L3 + selection
entropy |Δ| ≤ {CAL_ENTROPY_BITS} bits; L4 + community breadth ratio ∈
[{CAL_BREADTH[0]}, {CAL_BREADTH[1]}].

{ladder_table(full)}

## 7. Arm B — taste transport onto disjoint support (full arm)

{armb_table(full)}

### Attrition

{att_tbl}

### Held-out purity of the fold embeddings (rule 12 construction log)

Fitted in `{emb.get('construction')}`, {emb.get('fit_on')}, d = {emb.get('dim')}.

{pur_tbl}

All folds pure: **{emb.get('all_folds_pure')}**.

## 8. Verdicts (NULL-first)

**V-T2a (Arm A at L4): {va['verdict']}**
— {va['reason']}.

The L4 numbers are reported because routing cell 5 obliges this leg to
report attrition and pool sizes, **not** because they carry a claim:
AUC {_fmt(va['numbers']['auc'])}, bootstrap CI95
{_fmt(va['numbers']['ci95'])}, permutation null band
{_fmt(va['numbers']['null_band'])} (mean {_fmt(va['numbers']['null_mean'])},
sd {_fmt(va['numbers']['null_sd'])}), {va['numbers']['n_targets']} targets,
median admissible pool {_fmt(va['numbers']['median_pool'], 1)}. Had G2t2
passed, the mechanical reading of those numbers would have been
`{v['V_T2a_posthoc_if_gate_had_passed']['verdict']}` — it is recorded here
in full view and is **not** this leg's verdict, because the gate that would
have licensed it fired first, before the run.

The honest content of Arm A is its **attrition**, not its L4 AUC. Requiring a
stranger to match on in-vocabulary volume alone takes the median admissible
pool from {_fmt(full['levels']['L0']['median_pool'], 1)} to
{_fmt(full['levels']['L1']['median_pool'], 1)} candidates; adding the span
caliper takes it to {_fmt(full['levels']['L2']['median_pool'], 1)}. Within a
frozen selection leaf, users are so heterogeneous in how much they are
observed that condition-matched strangers essentially do not exist in this
corpus. That is a real and reportable fact about PANDORA — and it is also
exactly why Arm A cannot answer the question it was built to ask.

**V-T2b (Arm B): {vb['verdict']}**
— {vb['reason']}.
AUC {_fmt(vb['numbers']['auc'])}, bootstrap CI95 {_fmt(vb['numbers']['ci95'])},
permutation null band {_fmt(vb['numbers']['null_band'])}
(mean {_fmt(vb['numbers']['null_mean'])}, sd {_fmt(vb['numbers']['null_sd'])}),
{vb['numbers']['n_targets']} targets.

## 9. Routing (rule 16)

Cell **{rt['cell']}** → **{rt['outcome']}** (slug `{rt['slug']}`).

Cell 5 requires the attrition and pool sizes (§6, §10.1, §10.4) and a
**named redesign**. Naming it, without running it:

1. **Match across leaves, not within them.** The registered design spends
   the leaf constraint and the caliper constraint on the same small pool.
   A design that matches on observability across the whole cohort and
   carries leaf membership as a covariate keeps the pool at cohort scale.
2. **Replace hard calipers with a propensity score.** One scalar summary of
   the four observables, matched with a tolerance calibrated to a target
   pool size, converts "no admissible strangers" into "strangers of
   measurable match quality" — and makes the match quality itself
   reportable rather than binary.
3. **Report the caliper width the corpus can actually support.** §10.4
   measures this directly: the registered widths are far tighter than
   PANDORA's within-leaf heterogeneity permits.

None of these is run here. A redesign is a new registration, not a repair
applied mid-leg.

## 10. Readings (no gates)

### 10.1 The AUC-by-ladder curve — which caliper bites hardest

{_table(["level", "AUC", "Δ from previous", "median pool"],
        [[r["level"], _fmt(r["auc"]),
          ("—" if i == 0 or r.get("auc") is None
           or v["readings"]["ladder_curve"][i - 1].get("auc") is None
           else _fmt(r["auc"] - v["readings"]["ladder_curve"][i - 1]["auc"])),
          _fmt(r.get("median_pool"), 1)]
         for i, r in enumerate(v["readings"]["ladder_curve"])])}

### 10.2 Clean-arm replication (T1's 23-community ablation)

n_valid = {cl['n_valid']} (T1's clean arm: {A_N_CLEAN}; match
{cl['matches_t1_clean_n']}). Observables recomputed on the ablated matrices
per RN-T2-7.

{ladder_table(clean)}

{armb_table(clean)}

Clean-arm verdicts: **V-T2a {cl['V_T2a_clean']['verdict']}**,
**V-T2b {cl['V_T2b_clean']['verdict']}**.

### 10.3 Per-leaf heterogeneity

{het_tbl}

### 10.4 How wide would the calipers have to be? (UNREGISTERED DIAGNOSTIC)

Not registered, not a verdict, no AUC computed — this exists only to make
the named redesign concrete. Each row widens **every** caliper by a common
factor and reports the resulting median admissible pool.

{_table(["caliper scale"] + list(LADDER),
        [[_fmt(r["scale"], 1)] + [_fmt(r[k], 1) for k in LADDER]
         for r in (v["readings"]["caliper_width_diagnostic"] or {{}}).get("rows", [])])}

Smallest common scale at which L4 reaches the registered pool floor of
{MIN_POOL_MEDIAN}:
**{(v["readings"]["caliper_width_diagnostic"] or {{}}).get("scale_reaching_pool_floor_at_L4")}**
(`None` means no scale up to 16x reaches it).

## 10.5 Registration-defect candidates

- **RD-T2-1 — "null 0.5" is not achievable for the registered statistic.**
  G3t2 lists `null 0.5` among its rule-29 predicates, but the registered
  comparison pools ONE positive per target against MANY negatives per
  target across heterogeneous targets, so the permutation null sits where
  that weighting puts it — measured here at
  {_fmt(full['levels']['L0']['null_mean'])} at L0, not 0.5. #66's
  instruction ("the null band is the permutation's own, no closed forms")
  is the one that survives contact with the data, and it is the one this
  leg followed; the closed-form expectation is the one that should be
  struck. Predicate outcome is reported, not enforced:
  {v['gates']['G3t2']['reported_not_enforced']['null_at_half']['n_pass']} of
  {v['gates']['G3t2']['reported_not_enforced']['null_at_half']['n_total']}
  comparison sets have a null within 0.05 of 0.5. Flagged, never silently
  repaired.
- **RD-T2-2 — the caliper ladder was registered without a pool projection.**
  G2t2 exists precisely to catch this, and it did, before the run. But the
  ladder's widths were pinned in the registration itself, so the gate could
  only ever fire or not — it had no width to negotiate. A future ladder
  should register a *target pool size* and derive the widths from it,
  rather than registering widths and discovering the pool.

## 10.6 Post-verdict observations (recorded AFTER the verdicts, marked as such)

These were noticed while reading the finished numbers. They are recorded
here, after the verdicts, rather than back-dated into §3.

- **Arm B's construction is conservative, and the direction matters.**
  centroid_Lnew(u) is built from communities guaranteed ABSENT from u's own
  early support, but a stranger v's new communities carry no such guarantee
  — they may sit squarely inside u's early support and score a high cosine
  against centroid_E(u) for a trivial reason. The self-pair is handicapped;
  the stranger pairs are not. The transport signal is therefore measured
  against a comparison set that is, if anything, advantaged, which makes
  {_fmt(full['arm_b']['auc'])} a floor rather than a ceiling.
- **Arm B's pool is thin ({_fmt(full['arm_b']['median_pool'], 1)} strangers
  per target on median) and its effect is heterogeneous.** Of
  {het['full_armB']['n_leaves']} leaves with enough targets to score,
  {het['full_armB']['n_below_0.6']} sit below 0.60; the per-leaf median is
  {_fmt(het['full_armB']['median'])} against a pooled
  {_fmt(full['arm_b']['auc'])}. Transport is real and it replicates under
  ablation, but it is modest and unevenly distributed, and nothing here
  licenses treating it as a strong person-level coordinate.
- **The null band walks downward as the ladder tightens** — from
  {_fmt(full['levels']['L0']['null_band'])} at L0 to
  {_fmt(full['levels']['L4']['null_band'])} at L4. That drift is the
  resolution collapse made visible: as pools shrink, the one-positive /
  many-negatives weighting (RD-T2-1) dominates the statistic. It is a
  further reason no L4 claim is available, and it is independent of the
  pool-size rule that voided the level.

## 11. Compliance

- **Label-free:** no Big5/MBTI column is read anywhere in
  `{rel(Path(__file__))}`; the only inputs are the selection-side
  frequency/count matrices, the comment stream's timestamps, and T1's
  frozen tree.
- **No identifiers in committed artifacts:** author IDs live only in the
  gitignored `results/` intermediates.
- **Interpreter:** {p0['environment']['python_version']} /
  numpy {p0['environment']['numpy']} / pandas {p0['environment']['pandas']}
  on {p0['environment']['platform']}.
- **Provenance:** T1 core sha256 `{g0['t1_core_sha256'][:16]}…`, T1 driver
  `{g0['t1_driver_sha256'][:16]}…`, SR1 selection.npz
  `{g0['sr1_npz_sha256'][:16]}…`.
- **Stage wall time (s):** part0 {p0['seconds']:.1f}, counts
  {cnt['seconds']:.1f}, pilot {pil['seconds']:.1f}, arms(full)
  {full['seconds']:.1f}, arms(clean) {clean['seconds']:.1f}, finalize
  {v['seconds']:.1f} — every stage under the 600 s ceiling.
"""
    scan = id_leak_scan(body)
    body += (f"- **ID-leak scan:** {scan['n_tokens_scanned']} tokens in this "
             f"report checked against all {scan['n_cohort_ids']} cohort "
             f"identifiers — {scan['n_hits']} hits, "
             f"**{'PASS' if scan['PASS'] else 'FAIL'}**.\n")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(body, encoding="utf-8")
    write_json(OUT / "report_scan.json", {"id_leak_scan": scan,
                                          "report": rel(REPORT),
                                          "chars": len(body)})
    _log("report_done", id_leak_pass=scan["PASS"])
    print(f"report written {rel(REPORT)}  chars={len(body)}  "
          f"id_leak_hits={scan['n_hits']} PASS={scan['PASS']}  "
          f"{time.time() - t0:.1f}s")
    if not scan["PASS"]:
        raise SystemExit("ID-leak scan FAILED")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["part0", "counts", "pilot",
                                      "arms", "clean", "finalize",
                                      "report"])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"part0": stage_part0, "counts": stage_counts,
     "pilot": stage_pilot, "arms": stage_arms, "clean": stage_clean,
     "finalize": stage_finalize, "report": stage_report}[args.stage](args)


if __name__ == "__main__":
    main()
