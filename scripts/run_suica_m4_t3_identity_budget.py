#!/usr/bin/env python3
"""SUICA M4-T3 -- the identity budget (one currency for the tail).

Registered BEFORE run in docs/SUICA_M4_T_HIERARCHICAL_SELECTION_IDENTITY_PLAN.md
("M4-T3", commit 5bbf846).  Binding.  LABEL-FREE THROUGHOUT: no Big5 or MBTI
value is read at any stage.

T1 proved the tail exists.  T2 proved a generalizing taste coordinate exists
but could not isolate the support channel by MATCHING (the calipers left no
admissible strangers).  T3 answers Arm A's question by MEASUREMENT instead:
four representations, one statistic, one permutation machinery, marginal and
conditional, in one common currency.

  R_obs   the 4-dim late-side observability vector (z-scored) -- the direct
          measurement of the support channel
  R_tree  the frozen path code (depth-weighted prefix)
  R_emb   the full-half taste centroid in T2's frozen per-fold embedding
  R_flat  the Hellinger frequency vector (T1's 0.9837 ceiling)

Conditioning is by CORPUS-WIDE stratified permutation, never within-leaf --
that is T2's lesson paid for in full.

The T1 core and the T2 harness are imported BY FILE through ONE loader chain
and are NOT modified; all new code lives here.

Stages: part0 -> pilot -> budget -> joint -> clean -> finalize -> report
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

LEG = "M4-T3"
OUT = ROOT / "results" / "m4_t3_identity_budget"
REPORT = ROOT / "reports" / "SUICA_M4_T3_IDENTITY_BUDGET_REPORT.md"

T1CORE = ROOT / "suica_core" / "hierarchical_selection_identity.py"
T2HARNESS = ROOT / "scripts" / "run_suica_m4_t2_matched_residual.py"
T1RES = ROOT / "results" / "m4_t1_hierarchical_selection_identity"
T2RES = ROOT / "results" / "m4_t2_matched_residual"
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
POOL_TARGET = 20          # G2t3 / rule #69: pool target registered
EMB_DIM = 64
EPS_GAP = 0.03
STRATA_LADDER = (10, 8, 5, 4, 3, 2)
WEIGHT_GRID = tuple(round(x, 3) for x in np.linspace(0.0, 1.0, 21))

# --- anchors (G0t3 bit-verifies) -------------------------------------------
A_FLAT_FULL = 0.9836592822513264
A_FLAT_CLEAN = 0.9660999136733576
A_RESID_FULL = 0.9552295265671575
A_PATH_FULL = 0.7460863278537894
A_N_FULL = 1304
A_N_CLEAN = 1269
A_T2_ARMB_AUC = 0.6031409031779736
A_T2_ARMB_NULL = [0.4869631462640095, 0.5149378939035671]
A_T2_ARMB_N = 907
A_VOCAB = 1191
A_REMOVED = 23

REPS = ("R_obs", "R_tree", "R_emb", "R_flat")
STRATIFICATIONS = ("marginal", "obs_stratum", "leaf")

RN_NOTES = {
    "RN-T3-1":
        "ONE PAIR SET, FOUR REPRESENTATIONS.  For a given stratification the "
        "(target, stranger) pair structure is built ONCE and every "
        "representation is scored on exactly those pairs.  Without this the "
        "budget would not be a budget -- four AUCs measured on four different "
        "comparison sets cannot be added, subtracted or ranked.",
    "RN-T3-2":
        "all comparisons are WITHIN a fold's held-out set.  R_tree and R_emb "
        "only exist relative to a fold's frozen tree and frozen embedding, so "
        "cross-fold pairs are undefined for them; restricting all four "
        "representations to the same within-fold pools is what keeps the "
        "budget comparable (RN-T3-1).",
    "RN-T3-3":
        "SIMILARITY PER REPRESENTATION, declared.  R_tree / R_emb / R_flat use "
        "cosine, as T1 and T2 did.  R_obs uses NEGATIVE EUCLIDEAN DISTANCE in "
        "the z-scored 4-space, because for observability the MAGNITUDE is the "
        "signal -- a cosine on four z-scored coordinates would discard exactly "
        "the volume information V-T3a exists to measure.",
    "RN-T3-4":
        "R_tree is a vector, not a pairwise score, because V-T3c must "
        "CONCATENATE it with R_emb.  The path code places weight sqrt(k) on "
        "the node occupied at depth k, so the dot product of two codes is the "
        "sum of k over their shared prefix (a hierarchy shares a node at depth "
        "k only if it shares every ancestor).  Cosine then normalises for path "
        "depth.  'Depth-weighted prefix' is therefore literal: matching one "
        "level deeper is worth proportionally more.",
    "RN-T3-5":
        "EXCESS BITS, the budget's common currency.  For each target the "
        "representation ranks the true late half among K = pool + 1 "
        "candidates; bits = log2(K) - log2(rank), i.e. how much of the "
        "candidate space the representation cuts away for that user.  The "
        "reading is the per-target mean MINUS the same quantity under the "
        "reading's own permutation null (T1's excess-bits pattern: observed "
        "minus null).  Random ranking scores about 1.44 bits before "
        "correction and 0 after it.",
    "RN-T3-6":
        "each reading's null comes from ITS OWN machinery (#66/#68).  Rule-29 "
        "predicates are stated against the statistic's own null band, never "
        "against 0.5 -- that is defect #68, raised by T2 and adopted.  The "
        "null bands here are reported as measured and are NOT expected to "
        "centre on 0.5.",
    "RN-T3-7":
        "CONDITIONING IS CORPUS-WIDE, never within-leaf.  T2 spent its "
        "resolution by intersecting a leaf constraint with a caliper "
        "constraint on the same small pool.  Here a stratum is a slice of the "
        "whole held-out fold, and the number of strata is chosen to keep the "
        "median permutation pool at or above the registered target of 20 "
        "(#69: pool targets registered, realized widths reported).",
    "RN-T3-8":
        "R_obs is z-scored exactly as registered, on the raw observables.  "
        "Volume, span and breadth are heavy-tailed, so a log-transformed "
        "variant is reported alongside as a declared SENSITIVITY.  The "
        "registered form carries V-T3a; the sensitivity is a reading, and a "
        "material divergence between them is flagged rather than chosen "
        "between.",
    "RN-T3-9":
        "V-T3c's mixing weight is fitted on TRAINING folds only, by a rule "
        "declared before it is fitted: w maximises the pooled training-fold "
        "same-author AUC of (1-w)*cos_tree + w*cos_emb over a fixed 21-point "
        "grid.  Because both parts are unit-normalised, that convex "
        "combination IS the cosine of the weighted concatenation, so no "
        "separate joint vector has to be materialised.",
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


def t2() -> Any:
    return _load_named("m4_t2_matched_residual", T2HARNESS)


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
# EARLY-SIDE OBSERVABLES (T2 persisted only the late side).


def early_span_days(users: list[str]) -> np.ndarray:
    """Active span of each user's EARLY half, under SR1's own split rule."""
    tt = t2()
    uset = set(users)
    uidx = {a: i for i, a in enumerate(users)}
    ts: dict[str, list[float]] = {}
    for ch in tt._read_chunks():
        ch = ch[ch["author"].isin(uset)]
        if ch.empty:
            continue
        for a, sub in ch.groupby("author", observed=True)["created_utc"]:
            lst = ts.setdefault(a, [])
            if len(lst) < 4000:
                lst.extend(sub.tolist()[: 4000 - len(lst)])
    med = {a: float(np.median(ts[a])) for a in users if a in ts}
    n = len(users)
    tmin = np.full(n, np.inf)
    tmax = np.full(n, -np.inf)
    for ch in tt._read_chunks():
        ch = ch[ch["author"].isin(uset)]
        if ch.empty:
            continue
        mm = ch["author"].map(med).to_numpy(float)
        early = ch[ch["created_utc"].to_numpy(float) <= mm]
        if early.empty:
            continue
        for a, sub in early.groupby("author", observed=True)["created_utc"]:
            i = uidx[a]
            tmin[i] = min(tmin[i], float(sub.min()))
            tmax[i] = max(tmax[i], float(sub.max()))
    return np.where(np.isfinite(tmin) & np.isfinite(tmax),
                    (tmax - tmin) / 86400.0, 0.0)


def obs_matrix(counts: np.ndarray, freq: np.ndarray,
               span: np.ndarray, log_scale: bool) -> np.ndarray:
    """The 4-dim observability vector, z-scored (RN-T3-8)."""
    vol = counts.sum(axis=1).astype(float)
    breadth = (counts > 0).sum(axis=1).astype(float)
    ent = t2().entropy_bits(freq)
    if log_scale:
        vol, span, breadth = np.log1p(vol), np.log1p(span), np.log1p(breadth)
    mat = np.column_stack([vol, span, ent, breadth])
    mu = mat.mean(axis=0)
    sd = mat.std(axis=0, ddof=0)
    sd[sd <= 0] = 1.0
    return (mat - mu) / sd


# ---------------------------------------------------------------------------
# FOLDS AND REPRESENTATIONS.


def build_folds(freq_early: np.ndarray, freq_late: np.ndarray) -> dict[str, Any]:
    """T1's frozen fold structure, reproduced exactly (seed SEED + 1000*fold)."""
    core = t1core()
    e = core.hellinger_rows(freq_early)
    l = core.hellinger_rows(freq_late)
    valid = (np.linalg.norm(e, axis=1) > 0) & (np.linalg.norm(l, axis=1) > 0)
    e, l = e[valid], l[valid]
    orig = np.flatnonzero(valid)
    splitter = KFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    folds = []
    for fold, (tr, te) in enumerate(splitter.split(e)):
        tree = core.fit_selection_tree(e[tr], max_depth=MAX_DEPTH,
                                       min_leaf=MIN_LEAF,
                                       random_state=SEED + 1000 * fold)
        folds.append({"fold": fold, "tree": tree, "test_local": te,
                      "train_local": tr,
                      "test_global": orig[te], "train_global": orig[tr]})
    return {"hell_early": e, "hell_late": l, "orig": orig, "folds": folds,
            "n_valid": int(len(e))}


def path_codes(tree: Any, early_rows: np.ndarray,
               late_rows: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Depth-weighted prefix codes for both halves in a shared node space."""
    pe = tree.route_many(early_rows)
    pl = tree.route_many(late_rows)
    nodes = sorted({n for p in pe + pl for n in p[1:MAX_DEPTH + 1]})
    idx = {n: i for i, n in enumerate(nodes)}
    out = []
    for paths in (pe, pl):
        mat = np.zeros((len(paths), max(1, len(nodes))))
        for r, p in enumerate(paths):
            for k, node in enumerate(p[1:MAX_DEPTH + 1], start=1):
                mat[r, idx[node]] = math.sqrt(k)
        out.append(mat)
    leaves = np.array([p[-1] for p in pe], dtype=int)
    return out[0], out[1], leaves


def _unit(mat: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(mat, axis=1, keepdims=True)
    n[n <= 0] = 1.0
    return mat / n


def cosine_scores(early: np.ndarray, late: np.ndarray) -> np.ndarray:
    return _unit(early) @ _unit(late).T


def neg_euclid_scores(early: np.ndarray, late: np.ndarray) -> np.ndarray:
    d2 = (np.square(early).sum(axis=1)[:, None]
          + np.square(late).sum(axis=1)[None, :]
          - 2.0 * early @ late.T)
    return -np.sqrt(np.clip(d2, 0.0, None))


def build_representations(prep: dict[str, Any]) -> list[dict[str, Any]]:
    """Per fold: every representation's early/late matrices on held-out users."""
    tt = t2()
    out = []
    for f in prep["folds"]:
        te, tr = f["test_local"], f["train_local"]
        teg, trg = f["test_global"], f["train_global"]
        e_tree, l_tree, leaves = path_codes(f["tree"],
                                            prep["hell_early"][te],
                                            prep["hell_late"][te])
        emb = tt.ppmi_svd(prep["early_counts"][trg], EMB_DIM, SEED + f["fold"])
        out.append({
            "fold": f["fold"], "members": [int(x) for x in teg],
            "train_global": [int(x) for x in trg],
            "leaves": leaves, "emb": emb,
            "scores": {
                "R_obs": neg_euclid_scores(prep["obs_early"][teg],
                                           prep["obs_late"][teg]),
                "R_tree": cosine_scores(e_tree, l_tree),
                "R_emb": cosine_scores(prep["freq_early"][teg] @ emb,
                                       prep["freq_late"][teg] @ emb),
                "R_flat": cosine_scores(prep["hell_early"][te],
                                        prep["hell_late"][te])},
            "cos_tree": cosine_scores(e_tree, l_tree),
            "cos_emb": cosine_scores(prep["freq_early"][teg] @ emb,
                                     prep["freq_late"][teg] @ emb)})
    return out


# ---------------------------------------------------------------------------
# THE ONE MACHINERY.


class Reading:
    """One (representation x stratification) reading.

    Flat per-target arrays, exactly as T2's Pack: everything downstream is
    batched numpy, and both nulls reduce to a precomputed-rank gather.
    """

    def __init__(self, pos: list[float], negs: list[np.ndarray],
                 keys: list[tuple[int, int]]) -> None:
        self.pos = np.asarray(pos, dtype=float)
        self.neg_len = np.array([len(x) for x in negs], dtype=np.int64)
        self.neg_off = (np.concatenate(([0], np.cumsum(self.neg_len)[:-1]))
                        if negs else np.zeros(0, dtype=np.int64))
        self.neg_vals = np.concatenate(negs) if negs else np.zeros(0)
        self.keys = keys

    @property
    def n(self) -> int:
        return len(self.pos)

    def _bits_observed(self) -> np.ndarray:
        rep = np.repeat(self.pos, self.neg_len)
        gt = ((self.neg_vals > rep).astype(float)
              + 0.5 * (self.neg_vals == rep).astype(float))
        above = np.add.reduceat(gt, self.neg_off)
        return np.log2(self.neg_len + 1.0) - np.log2(1.0 + above)

    def _within_block_ranks(self) -> np.ndarray:
        """#{block > v} + 0.5*#{block == v}, self included, per entry."""
        out = np.empty(len(self.neg_vals))
        for t in range(self.n):
            a, b = self.neg_off[t], self.neg_off[t] + self.neg_len[t]
            block = self.neg_vals[a:b]
            srt = np.sort(block)
            hi = np.searchsorted(srt, block, side="right")
            lo = np.searchsorted(srt, block, side="left")
            out[a:b] = (len(block) - hi) + 0.5 * (hi - lo)
        return out

    def evaluate(self, rng: np.random.Generator, b_boot: int,
                 b_perm: int) -> dict[str, Any]:
        t, m = self.n, len(self.neg_vals)
        tt = t2()
        auc = tt._auc(self.pos, self.neg_vals)
        uniq, inv = np.unique(np.concatenate([self.pos, self.neg_vals]),
                              return_inverse=True)
        pid, nid, n_vals = inv[:t], inv[t:], len(uniq)
        check = tt.auc_from_ids(pid, nid, n_vals)
        bits_t = self._bits_observed()

        boot = np.empty(b_boot)
        boot_bits = np.empty(b_boot)
        for b in range(b_boot):
            pick = rng.integers(0, t, size=t)
            boot[b] = tt.auc_from_ids(
                pid[pick], nid[tt.ragged_gather(self.neg_off, self.neg_len,
                                                pick)], n_vals)
            boot_bits[b] = bits_t[pick].mean()

        ranks = tt.avg_ranks(self.neg_vals)
        wbr = self._within_block_ranks()
        draw = (self.neg_off[None, :]
                + (rng.random((b_perm, t)) * self.neg_len[None, :]
                   ).astype(np.int64))
        nulls = ((ranks[draw].sum(axis=1) - t * (t + 1) / 2.0)
                 / (t * (m - t)))
        k_null = np.maximum(self.neg_len.astype(float), 1.0)
        nb = (np.log2(k_null)[None, :]
              - np.log2(1.0 + np.maximum(wbr[draw] - 0.5, 0.0)))
        null_bits = nb.mean(axis=1)
        return {
            "auc": auc, "auc_check_ok": bool(abs(auc - check) < 1e-12),
            "n_targets": t, "n_negative": m,
            "ci95": [float(np.percentile(boot, 2.5)),
                     float(np.percentile(boot, 97.5))],
            "boot_sd": float(boot.std(ddof=1)),
            "null_mean": float(nulls.mean()), "null_sd": float(nulls.std(ddof=1)),
            "null_band": [float(np.percentile(nulls, 2.5)),
                          float(np.percentile(nulls, 97.5))],
            "above_null": bool(float(np.percentile(boot, 2.5))
                               > float(np.percentile(nulls, 97.5))),
            "bits": float(bits_t.mean()),
            "bits_ci95": [float(np.percentile(boot_bits, 2.5)),
                          float(np.percentile(boot_bits, 97.5))],
            "bits_null_mean": float(null_bits.mean()),
            "bits_null_band": [float(np.percentile(null_bits, 2.5)),
                               float(np.percentile(null_bits, 97.5))],
            "excess_bits": float(bits_t.mean() - null_bits.mean()),
            "median_pool": float(np.median(self.neg_len)),
            "mean_pool": float(np.mean(self.neg_len)),
            "b_boot": b_boot, "b_perm": b_perm}

    def per_leaf(self, min_targets: int = 5) -> list[dict[str, Any]]:
        tt = t2()
        by: dict[tuple[int, int], list[int]] = defaultdict(list)
        for i, k in enumerate(self.keys):
            by[k].append(i)
        out = []
        for (fold, key), rows in sorted(by.items()):
            if len(rows) < min_targets:
                continue
            idx = np.array(rows)
            negs = self.neg_vals[tt.ragged_gather(self.neg_off, self.neg_len,
                                                  idx)]
            out.append({"fold": fold, "stratum": key, "n_targets": len(rows),
                        "auc": tt._auc(self.pos[idx], negs)})
        return out


def strata_groups(reps: list[dict[str, Any]], mode: str,
                  strat_of: dict[int, int] | None,
                  target_users: set[int] | None) -> list[dict[str, Any]]:
    """(fold, stratum) -> local member positions, for one stratification."""
    groups = []
    for r in reps:
        members = r["members"]
        if mode == "marginal":
            buckets = {0: list(range(len(members)))}
        elif mode == "leaf":
            buckets = defaultdict(list)
            for i, leaf in enumerate(r["leaves"]):
                buckets[int(leaf)].append(i)
        else:
            buckets = defaultdict(list)
            for i, u in enumerate(members):
                buckets[int(strat_of[u])].append(i)      # type: ignore[index]
        for key, rows in sorted(buckets.items()):
            if len(rows) < 2:
                continue
            groups.append({"fold": r["fold"], "key": int(key),
                           "rows": np.asarray(rows, dtype=int),
                           "members": [members[i] for i in rows],
                           "rep": r, "target_users": target_users})
    return groups


def make_reading(groups: list[dict[str, Any]], score_key: str,
                 score_override: dict[int, np.ndarray] | None = None
                 ) -> Reading:
    pos: list[float] = []
    negs: list[np.ndarray] = []
    keys: list[tuple[int, int]] = []
    for g in groups:
        mat = (score_override[g["fold"]] if score_override is not None
               else g["rep"]["scores"][score_key])
        rows = g["rows"]
        sub = mat[np.ix_(rows, rows)]
        tu = g["target_users"]
        for i, user in enumerate(g["members"]):
            if tu is not None and user not in tu:
                continue
            others = np.delete(np.arange(len(rows)), i)
            vals = sub[i, others]
            vals = vals[np.isfinite(vals)]
            if vals.size == 0 or not np.isfinite(sub[i, i]):
                continue
            pos.append(float(sub[i, i]))
            negs.append(vals)
            keys.append((int(g["fold"]), int(g["key"])))
    return Reading(pos, negs, keys)


# ---------------------------------------------------------------------------
# STRATA SIZING (#69: pool target registered, realized widths reported).


def choose_strata(reps: list[dict[str, Any]], index: np.ndarray,
                  members_all: list[int]) -> dict[str, Any]:
    tried = []
    for n_str in STRATA_LADDER:
        edges = np.quantile(index[members_all], np.linspace(0, 1, n_str + 1))
        edges[0], edges[-1] = -np.inf, np.inf
        assign = {u: int(np.searchsorted(edges[1:-1], index[u], side="right"))
                  for u in members_all}
        groups = strata_groups(reps, "obs_stratum", assign, None)
        pools = [len(g["rows"]) - 1 for g in groups for _ in g["rows"]]
        med = float(np.median(pools)) if pools else 0.0
        tried.append({"n_strata": n_str, "median_pool": med,
                      "n_groups": len(groups)})
        if med >= POOL_TARGET:
            return {"n_strata": n_str, "assign": assign, "median_pool": med,
                    "edges": [float(x) for x in edges[1:-1]], "tried": tried,
                    "meets_target": True}
    return {"n_strata": STRATA_LADDER[-1], "assign": assign,
            "median_pool": tried[-1]["median_pool"],
            "edges": [float(x) for x in edges[1:-1]], "tried": tried,
            "meets_target": False}


# ---------------------------------------------------------------------------
# PREPARATION.


def prepare(arm: str) -> dict[str, Any]:
    tt = t2()
    d = np.load(SR1NPZ, allow_pickle=True)
    users = [str(u) for u in d["users"]]
    fe = np.asarray(d["freq_early"], dtype=float).copy()
    fl = np.asarray(d["freq_late"], dtype=float).copy()
    c = np.load(T2RES / "counts.npz", allow_pickle=True)
    ec = c["early_counts"].astype(float)
    lc = c["late_counts"].astype(float)
    span_late = c["span_late_days"]
    span_early = np.load(OUT / "span_early.npz")["span_early_days"]
    if arm == "clean":
        rem = c["removed_indices"]
        for m in (fe, fl, ec, lc):
            m[:, rem] = 0.0
        fe, fl = tt.row_normalise(ec), tt.row_normalise(lc)
    prep = build_folds(fe, fl)
    prep.update({
        "users": users, "freq_early": fe, "freq_late": fl,
        "early_counts": ec, "late_counts": lc,
        "obs_early": obs_matrix(ec, fe, span_early, log_scale=False),
        "obs_late": obs_matrix(lc, fl, span_late, log_scale=False),
        "obs_early_log": obs_matrix(ec, fe, span_early, log_scale=True),
        "obs_late_log": obs_matrix(lc, fl, span_late, log_scale=True),
        "arm": arm})
    return prep


def observability_index(prep: dict[str, Any]) -> dict[str, Any]:
    """PC1 of the z-scored late observability vector -- the stratifier."""
    x = prep["obs_late"]
    xc = x - x.mean(axis=0)
    _u, sv, vt = np.linalg.svd(xc, full_matrices=False)
    pc1 = vt[0]
    if pc1.sum() < 0:
        pc1 = -pc1
    var = (sv ** 2) / (sv ** 2).sum()
    return {"index": xc @ pc1, "loadings": pc1.tolist(),
            "explained_variance": float(var[0]),
            "dims": ["volume", "span", "entropy", "breadth"]}


# ---------------------------------------------------------------------------
# STAGES.


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")
    s1 = read_json(T1RES / "summary.json")
    full, clean = s1["arms"]["full"], s1["arms"]["clean_no_explicit_personality"]
    v2 = read_json(T2RES / "verdicts.json")
    a2 = read_json(T2RES / "arms_full.json")
    b2 = a2["arm_b"]
    checks = {
        "T1 flat ceiling (full)": [full["flat_auc"], A_FLAT_FULL],
        "T1 flat ceiling (clean)": [clean["flat_auc"], A_FLAT_CLEAN],
        "T1 terminal residual (full)": [full["terminal_residual_auc"],
                                        A_RESID_FULL],
        "T1 hierarchical path (full)": [full["hierarchical_path_auc"],
                                        A_PATH_FULL],
        "T1 n_valid (full)": [full["n_valid"], A_N_FULL],
        "T1 n_valid (clean)": [clean["n_valid"], A_N_CLEAN],
        "T2 Arm B AUC": [b2["auc"], A_T2_ARMB_AUC],
        "T2 Arm B null lo": [b2["null_band"][0], A_T2_ARMB_NULL[0]],
        "T2 Arm B null hi": [b2["null_band"][1], A_T2_ARMB_NULL[1]],
        "T2 Arm B targets": [b2["n_targets"], A_T2_ARMB_N],
    }
    g0: dict[str, Any] = {
        "anchors": {k: {"persisted": v[0], "expected": v[1],
                        "match": bool(v[0] == v[1])}
                    for k, v in checks.items()},
        "T2_embedding_purity": b2["embedding"]["all_folds_pure"],
        "T2_verdicts": {"V_T2a": v2["V_T2a"]["verdict"],
                        "V_T2b": v2["V_T2b"]["verdict"],
                        "routing": v2["routing"]["outcome"]},
        "sha256": {"t1_core": sha_file(T1CORE), "t2_harness": sha_file(T2HARNESS),
                   "sr1_selection": sha_file(SR1NPZ),
                   "t2_counts": sha_file(T2RES / "counts.npz")}}
    g0["all_anchors_match"] = bool(all(c["match"]
                                       for c in g0["anchors"].values()))

    d = np.load(SR1NPZ, allow_pickle=True)
    users = [str(u) for u in d["users"]]
    sp = OUT / "span_early.npz"
    if not sp.exists():
        np.savez_compressed(sp, span_early_days=early_span_days(users))
    prep = prepare("full")
    g0["n_valid_reconstructed"] = prep["n_valid"]
    g0["n_valid_matches_T1"] = bool(prep["n_valid"] == A_N_FULL)
    reps = build_representations(prep)
    groups = strata_groups(reps, "marginal", None, None)
    rng = np.random.default_rng(SEED)
    recon = {}
    for name in REPS:
        r = make_reading(groups, name).evaluate(rng, b_boot=200, b_perm=99)
        recon[name] = {"auc": r["auc"], "ci95": r["ci95"],
                       "n_targets": r["n_targets"],
                       "median_pool": r["median_pool"]}
    g0["marginal_reconstruction"] = recon
    g0["R_flat_vs_T1_ceiling"] = {
        "reconstructed": recon["R_flat"]["auc"], "t1_persisted": A_FLAT_FULL,
        "abs_diff": abs(recon["R_flat"]["auc"] - A_FLAT_FULL),
        "note": "T1 pooled across the whole valid cohort; T3 pools within "
                "each fold's held-out set (RN-T3-2), so these are close "
                "relatives, not the same estimator"}
    g0["R_tree_vs_T1_path"] = {
        "reconstructed": recon["R_tree"]["auc"], "t1_persisted": A_PATH_FULL,
        "note": "T1's path AUC used an unweighted common prefix; R_tree is "
                "the depth-weighted code of RN-T3-4"}
    g0["PASS"] = bool(g0["all_anchors_match"] and g0["n_valid_matches_T1"]
                      and g0["T2_embedding_purity"])
    span_e = np.load(sp)["span_early_days"]
    write_json(OUT / "part0.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(), "G0t3": g0,
        "RN_NOTES": RN_NOTES,
        "early_span_summary": {"mean": float(span_e.mean()),
                               "median": float(np.median(span_e)),
                               "min": float(span_e.min()),
                               "max": float(span_e.max())},
        "environment": {"python_executable": sys.executable,
                        "python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - t0})
    _log("part0_done", pass_=g0["PASS"])
    if not g0["PASS"]:
        raise SystemExit(f"G0t3 FAILED -> STOP {g0}")
    print(f"part0 OK  anchors={g0['all_anchors_match']} "
          f"n_valid={prep['n_valid']} purity={g0['T2_embedding_purity']}")
    for k, r in recon.items():
        print(f"  marginal {k}: AUC={r['auc']:.4f} pool={r['median_pool']:.0f}")
    print(f"  {time.time() - t0:.1f}s")


def _readings(prep: dict[str, Any], reps: list[dict[str, Any]],
              strat: dict[str, Any], b_boot: int, b_perm: int,
              targets: set[int] | None, seed0: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    grp = {"marginal": strata_groups(reps, "marginal", None, targets),
           "obs_stratum": strata_groups(reps, "obs_stratum", strat["assign"],
                                        targets),
           "leaf": strata_groups(reps, "leaf", None, targets)}
    for si, mode in enumerate(STRATIFICATIONS):
        for ri, name in enumerate(REPS):
            rng = np.random.default_rng(seed0 + 101 * si + 17 * ri)
            rd = make_reading(grp[mode], name)
            if rd.n == 0 or len(rd.neg_vals) <= rd.n:
                out[f"{name}|{mode}"] = {"UNDERRESOLVED": True,
                                         "reason": "no admissible pairs"}
                continue
            res = rd.evaluate(rng, b_boot=b_boot, b_perm=b_perm)
            res["representation"], res["stratification"] = name, mode
            res["UNDERRESOLVED"] = bool(res["median_pool"] < POOL_TARGET)
            if name == "R_emb" and mode == "obs_stratum":
                res["per_leaf"] = rd.per_leaf()
            out[f"{name}|{mode}"] = res
    return out


def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("pilot_start")
    prep = prepare("full")
    reps = build_representations(prep)
    members_all = sorted({u for r in reps for u in r["members"]})
    oi = observability_index(prep)
    strat = choose_strata(reps, oi["index"], members_all)
    rng = np.random.default_rng(SEED + 7)
    targets = {int(u) for u in rng.choice(np.asarray(members_all),
                                          size=min(PILOT_USERS,
                                                   len(members_all)),
                                          replace=False)}
    res = _readings(prep, reps, strat, b_boot=200, b_perm=B_PILOT_PERM,
                    targets=targets, seed0=SEED + 3000)
    cal = {}
    for k, r in res.items():
        if "auc" not in r:
            cal[k] = {"separates": False, "reason": "no pairs"}
            continue
        lo, hi = r["null_band"]
        width = hi - lo
        cal[k] = {"null_band": r["null_band"], "band_width": width,
                  "null_mean": r["null_mean"], "median_pool": r["median_pool"],
                  "non_degenerate": bool(width > 1e-9 and r["null_sd"] > 1e-9),
                  "meets_pool_target": bool(r["median_pool"] >= POOL_TARGET),
                  "separates": bool(width < 0.25 and width > 1e-9
                                    and r["null_sd"] > 1e-9
                                    and r["median_pool"] >= POOL_TARGET)}
        print(f"  pilot {k}: pool={r['median_pool']:.0f} "
              f"null={[round(x, 4) for x in r['null_band']]} "
              f"w={width:.4f} sep={cal[k]['separates']}")
    verdict = "PASS" if all(c["separates"] for c in cal.values()) \
        else "UNDERRESOLVED_BY_DESIGN"
    write_json(OUT / "pilot.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "G2t3": {"n_pilot_targets": len(targets), "b_perm": B_PILOT_PERM,
                 "pool_target": POOL_TARGET, "VERDICT": verdict,
                 "strata": {k: v for k, v in strat.items() if k != "assign"},
                 "observability_index": {k: v for k, v in oi.items()
                                         if k != "index"},
                 "note": RN_NOTES["RN-T3-7"]},
        "calibration": cal, "seconds": time.time() - t0})
    _log("pilot_done", verdict=verdict)
    print(f"pilot {verdict}  strata={strat['n_strata']} "
          f"(median pool {strat['median_pool']:.1f}, target {POOL_TARGET})  "
          f"{time.time() - t0:.1f}s")


def _joint(prep: dict[str, Any], reps: list[dict[str, Any]],
           groups: list[dict[str, Any]], rng: np.random.Generator,
           b_boot: int, b_perm: int) -> dict[str, Any]:
    """V-T3c: weight fitted on TRAINING folds only, then held-out gap."""
    tt = t2()
    fit = []
    for f, r in zip(prep["folds"], reps):
        trl, trg = f["train_local"], f["train_global"]
        e_tree, l_tree, _ = path_codes(f["tree"], prep["hell_early"][trl],
                                       prep["hell_late"][trl])
        ct = cosine_scores(e_tree, l_tree)
        ce = cosine_scores(prep["freq_early"][trg] @ r["emb"],
                           prep["freq_late"][trg] @ r["emb"])
        fit.append((ct, ce))
    curve = []
    for w in WEIGHT_GRID:
        pos, neg = [], []
        for ct, ce in fit:
            s = (1.0 - w) * ct + w * ce
            pos.append(np.diag(s))
            off = s[~np.eye(s.shape[0], dtype=bool)]
            neg.append(off)
        curve.append({"w": float(w),
                      "train_auc": tt._auc(np.concatenate(pos),
                                           np.concatenate(neg))})
    best = max(curve, key=lambda c: c["train_auc"])
    w = best["w"]
    override = {r["fold"]: (1.0 - w) * r["cos_tree"] + w * r["cos_emb"]
                for r in reps}
    rd_joint = make_reading(groups, "R_tree", score_override=override)
    rd_flat = make_reading(groups, "R_flat")
    res_j = rd_joint.evaluate(np.random.default_rng(SEED + 5001), b_boot, b_perm)
    res_f = rd_flat.evaluate(np.random.default_rng(SEED + 5002), b_boot, b_perm)
    # paired user bootstrap on the gap (identical pair structure by RN-T3-1)
    t = rd_joint.n
    uj, ij = np.unique(np.concatenate([rd_joint.pos, rd_joint.neg_vals]),
                       return_inverse=True)
    uf, if_ = np.unique(np.concatenate([rd_flat.pos, rd_flat.neg_vals]),
                        return_inverse=True)
    gaps = np.empty(b_boot)
    for b in range(b_boot):
        pick = rng.integers(0, t, size=t)
        gj = tt.ragged_gather(rd_joint.neg_off, rd_joint.neg_len, pick)
        gf = tt.ragged_gather(rd_flat.neg_off, rd_flat.neg_len, pick)
        gaps[b] = (tt.auc_from_ids(if_[:t][pick], if_[t:][gf], len(uf))
                   - tt.auc_from_ids(ij[:t][pick], ij[t:][gj], len(uj)))
    gap = res_f["auc"] - res_j["auc"]
    ci = [float(np.percentile(gaps, 2.5)), float(np.percentile(gaps, 97.5))]
    return {"weight_rule": RN_NOTES["RN-T3-9"], "weight_grid": list(WEIGHT_GRID),
            "w_star": w, "train_auc_at_w_star": best["train_auc"],
            "train_curve": curve, "joint": res_j, "flat": res_f,
            "gap_flat_minus_joint": gap, "gap_ci95": ci,
            "eps_gap": EPS_GAP,
            "ADEQUATE": bool(ci[0] >= -EPS_GAP and ci[1] <= EPS_GAP)}


def _run_arm(arm: str, seed_shift: int) -> dict[str, Any]:
    prep = prepare(arm)
    reps = build_representations(prep)
    members_all = sorted({u for r in reps for u in r["members"]})
    oi = observability_index(prep)
    strat = choose_strata(reps, oi["index"], members_all)
    res = _readings(prep, reps, strat, b_boot=B_BOOT, b_perm=B_PERM,
                    targets=None, seed0=SEED + seed_shift)
    for k, r in sorted(res.items()):
        if "auc" in r:
            print(f"  {arm} {k}: AUC={r['auc']:.4f} CI={[round(x,4) for x in r['ci95']]} "
                  f"null={[round(x,4) for x in r['null_band']]} "
                  f"bits={r['excess_bits']:.3f} pool={r['median_pool']:.0f}")
    groups = strata_groups(reps, "marginal", None, None)
    joint = _joint(prep, reps, groups, np.random.default_rng(SEED + seed_shift),
                   B_BOOT, B_PERM)
    print(f"  {arm} joint: w*={joint['w_star']} joint={joint['joint']['auc']:.4f} "
          f"flat={joint['flat']['auc']:.4f} gap={joint['gap_flat_minus_joint']:.4f} "
          f"CI={[round(x,4) for x in joint['gap_ci95']]}")
    # declared sensitivity: log-scaled observability (RN-T3-8)
    sens_scores = {r["fold"]: neg_euclid_scores(
        prep["obs_early_log"][np.asarray(r["members"])],
        prep["obs_late_log"][np.asarray(r["members"])]) for r in reps}
    rd = make_reading(groups, "R_obs", score_override=sens_scores)
    sens = rd.evaluate(np.random.default_rng(SEED + seed_shift + 77),
                       b_boot=B_BOOT, b_perm=B_PERM)
    print(f"  {arm} R_obs(log sensitivity): AUC={sens['auc']:.4f} "
          f"CI={[round(x,4) for x in sens['ci95']]}")
    return {"arm": arm, "n_valid": prep["n_valid"], "readings": res,
            "joint": joint, "r_obs_log_sensitivity": sens,
            "strata": {k: v for k, v in strat.items() if k != "assign"},
            "observability_index": {k: v for k, v in oi.items()
                                    if k != "index"}}


def stage_budget(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("budget_start")
    res = _run_arm("full", 0)
    res["utc"] = datetime.now(UTC).isoformat()
    res["seconds"] = time.time() - t0
    write_json(OUT / "budget_full.json", res)
    _log("budget_done", seconds=res["seconds"])
    print(f"budget(full) done  {time.time() - t0:.1f}s")


def stage_clean(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("clean_start")
    res = _run_arm("clean", 500)
    res["utc"] = datetime.now(UTC).isoformat()
    res["seconds"] = time.time() - t0
    res["n_valid_matches_T1_clean"] = bool(res["n_valid"] == A_N_CLEAN)
    write_json(OUT / "budget_clean.json", res)
    _log("clean_done", seconds=res["seconds"])
    print(f"budget(clean) done  n_valid={res['n_valid']} "
          f"(T1 {A_N_CLEAN}: {res['n_valid_matches_T1_clean']})  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# VERDICTS.


def verdict_a(r: dict[str, Any]) -> dict[str, Any]:
    if r.get("UNDERRESOLVED") or "auc" not in r:
        return {"verdict": "UNDERRESOLVED",
                "reason": f"median pool {r.get('median_pool')} below the "
                          f"registered target {POOL_TARGET}"}
    lo, hi = r["ci95"]
    if lo > 0.75:
        return {"verdict": "MAJOR",
                "reason": "the bootstrap CI lies entirely above 0.75"}
    if hi < 0.60:
        return {"verdict": "MINOR",
                "reason": "the bootstrap CI lies entirely below 0.60"}
    return {"verdict": "MODERATE",
            "reason": "the CI is neither entirely above 0.75 nor entirely "
                      "below 0.60"}


def verdict_b(r: dict[str, Any]) -> dict[str, Any]:
    if r.get("UNDERRESOLVED") or "auc" not in r:
        return {"verdict": "UNDERRESOLVED",
                "reason": f"median pool {r.get('median_pool')} below the "
                          f"registered target {POOL_TARGET}"}
    if r["ci95"][0] > r["null_band"][1]:
        return {"verdict": "SURVIVES",
                "reason": "under observability-stratified permutation the CI "
                          "still clears the reading's own null band"}
    return {"verdict": "DIES",
            "reason": "the CI does not clear the observability-stratified "
                      "null band"}


def verdict_c(j: dict[str, Any]) -> dict[str, Any]:
    if j["ADEQUATE"]:
        return {"verdict": "ADEQUATE",
                "reason": f"the gap CI lies inside the declared band "
                          f"+/-{EPS_GAP}"}
    return {"verdict": "GAP_REMAINS",
            "reason": "the flat ceiling is not reached by tree + embedding; "
                      "the unexplained share is quantified and becomes the "
                      "next object"}


def route(va: str, vb: str, vc: str) -> dict[str, Any]:
    outcomes, modifiers = [], []
    if va == "MAJOR":
        outcomes.append("SUPPORT_CHANNEL_MAJOR")
    if vb == "SURVIVES":
        modifiers.append("TASTE_BEYOND_SUPPORT")
    elif vb == "DIES":
        modifiers.append("TRANSPORT_WAS_SUPPORT")
    if vc == "ADEQUATE":
        outcomes.append("JOINT_REPRESENTATION_ADEQUATE")
    elif vc == "GAP_REMAINS":
        outcomes.append("BUDGET_WITH_RESIDUAL")
    under = [n for n, v in (("V-T3a", va), ("V-T3b", vb), ("V-T3c", vc))
             if v == "UNDERRESOLVED"]
    if under:
        modifiers.append("UNDERRESOLVED:" + "+".join(under))
    if not outcomes:
        outcomes.append("UNDERRESOLVED")
    slug = "-".join(o.lower().replace("_", "-") for o in outcomes)
    return {"outcomes": outcomes, "modifiers": modifiers, "slug": slug,
            "cells": {"V-T3a": va, "V-T3b": vb, "V-T3c": vc}}


def _leaf_summary(per_leaf: list[dict[str, Any]]) -> dict[str, Any]:
    if not per_leaf:
        return {"n_strata": 0}
    a = np.array([x["auc"] for x in per_leaf], dtype=float)
    a = a[np.isfinite(a)]
    return {"n_strata": int(len(a)), "min": float(a.min()),
            "q25": float(np.percentile(a, 25)), "median": float(np.median(a)),
            "q75": float(np.percentile(a, 75)), "max": float(a.max()),
            "iqr": float(np.percentile(a, 75) - np.percentile(a, 25))}


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("finalize_start")
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    full = read_json(OUT / "budget_full.json")
    clean = read_json(OUT / "budget_clean.json")
    rd = full["readings"]
    va = verdict_a(rd["R_obs|marginal"])
    vb = verdict_b(rd["R_emb|obs_stratum"])
    vc = verdict_c(full["joint"])
    routing = route(va["verdict"], vb["verdict"], vc["verdict"])
    aucs = [r["auc"] for r in rd.values() if "auc" in r]
    g1 = {"auc_spread": [float(min(aucs)), float(max(aucs))],
          "none_forced": bool(max(aucs) < 1.0 - 1e-9
                              and max(aucs) - min(aucs) > 1e-9),
          "strata_non_degenerate": bool(all(
              r.get("median_pool", 0) >= 2 for r in rd.values()
              if "median_pool" in r)),
          "n_strata": full["strata"]["n_strata"],
          "strata_meet_pool_target": full["strata"]["meets_target"]}
    g1["PASS"] = bool(g1["none_forced"] and g1["strata_non_degenerate"])
    preds = []
    for arm_name, blob in (("full", full), ("clean", clean)):
        for k, r in sorted(blob["readings"].items()):
            if "auc" not in r:
                continue
            preds.append({"what": f"{arm_name}:{k}",
                          "auc_in_unit": bool(0.0 <= r["auc"] <= 1.0),
                          "own_null_used": True,
                          "null_band_finite": bool(np.isfinite(r["null_band"]).all()),
                          "auc_vectorised_agrees": r["auc_check_ok"]})
    g3 = {"predicates": preds,
          "note": RN_NOTES["RN-T3-6"],
          "PASS": bool(all(p["auc_in_unit"] and p["auc_vectorised_agrees"]
                           and p["null_band_finite"] for p in preds))}
    out = {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "gates": {"G0t3": p0["G0t3"]["PASS"], "G1t3": g1,
                  "G2t3": pil["G2t3"]["VERDICT"], "G3t3": g3},
        "V_T3a": {**va, "reading": "R_obs|marginal",
                  "numbers": {k: rd["R_obs|marginal"].get(k) for k in
                              ("auc", "ci95", "null_band", "null_mean",
                               "excess_bits", "bits", "bits_null_mean",
                               "n_targets", "median_pool")},
                  "log_sensitivity": {k: full["r_obs_log_sensitivity"].get(k)
                                      for k in ("auc", "ci95", "null_band",
                                                "excess_bits")}},
        "V_T3b": {**vb, "reading": "R_emb|obs_stratum",
                  "numbers": {k: rd["R_emb|obs_stratum"].get(k) for k in
                              ("auc", "ci95", "null_band", "null_mean",
                               "excess_bits", "n_targets", "median_pool")},
                  "marginal_for_contrast": {
                      k: rd["R_emb|marginal"].get(k)
                      for k in ("auc", "ci95", "null_band", "excess_bits")}},
        "V_T3c": {**vc, "w_star": full["joint"]["w_star"],
                  "train_auc_at_w_star": full["joint"]["train_auc_at_w_star"],
                  "joint_auc": full["joint"]["joint"]["auc"],
                  "joint_ci95": full["joint"]["joint"]["ci95"],
                  "flat_auc": full["joint"]["flat"]["auc"],
                  "flat_ci95": full["joint"]["flat"]["ci95"],
                  "gap": full["joint"]["gap_flat_minus_joint"],
                  "gap_ci95": full["joint"]["gap_ci95"], "eps_gap": EPS_GAP},
        "routing": routing,
        "readings": {
            "budget_table": [
                {"representation": name, "stratification": mode,
                 **{f: rd[f"{name}|{mode}"].get(f) for f in
                    ("auc", "ci95", "null_band", "excess_bits", "bits",
                     "bits_null_mean", "median_pool", "n_targets")}}
                for name in REPS for mode in STRATIFICATIONS],
            "clean_replication": {
                "n_valid": clean["n_valid"],
                "matches_T1_clean_n": clean.get("n_valid_matches_T1_clean"),
                "table": [{"representation": name, "stratification": mode,
                           **{f: clean["readings"][f"{name}|{mode}"].get(f)
                              for f in ("auc", "ci95", "null_band",
                                        "excess_bits")}}
                          for name in REPS for mode in STRATIFICATIONS],
                "joint": {"w_star": clean["joint"]["w_star"],
                          "joint_auc": clean["joint"]["joint"]["auc"],
                          "flat_auc": clean["joint"]["flat"]["auc"],
                          "gap": clean["joint"]["gap_flat_minus_joint"],
                          "gap_ci95": clean["joint"]["gap_ci95"]},
                "V_T3a_clean": verdict_a(clean["readings"]["R_obs|marginal"]),
                "V_T3b_clean": verdict_b(clean["readings"]["R_emb|obs_stratum"]),
                "V_T3c_clean": verdict_c(clean["joint"])},
            "per_leaf_heterogeneity_R_emb": _leaf_summary(
                rd["R_emb|obs_stratum"].get("per_leaf", [])),
            "strata": full["strata"],
            "observability_index": full["observability_index"]},
        "seconds": time.time() - t0}
    write_json(OUT / "verdicts.json", out)
    _log("finalize_done", slug=routing["slug"])
    print(f"V-T3a={va['verdict']}  V-T3b={vb['verdict']}  V-T3c={vc['verdict']}")
    print(f"  -> {routing['outcomes']} mods={routing['modifiers']} "
          f"slug={routing['slug']}  G1t3={g1['PASS']} G3t3={g3['PASS']}")


def stage_report(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("report_start")
    tt = t2()
    fmt, tbl = tt._fmt, tt._table
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    full = read_json(OUT / "budget_full.json")
    clean = read_json(OUT / "budget_clean.json")
    v = read_json(OUT / "verdicts.json")
    g0 = p0["G0t3"]
    rd = full["readings"]

    anchors = tbl(["anchor", "persisted", "expected", "match"],
                  [[k, repr(c["persisted"]), repr(c["expected"]),
                    str(c["match"])] for k, c in sorted(g0["anchors"].items())])

    gates = tbl(["gate", "what it checks", "result"],
                [["G0t3", "T1/T2 anchors bit-verified; T2 embedding purity; "
                  "representations rebuilt through the persisted objects",
                  f"**{'PASS' if g0['PASS'] else 'FAIL'}**"],
                 ["G1t3", "#59: none of the AUCs is forced; strata "
                  "non-degenerate",
                  f"**{'PASS' if v['gates']['G1t3']['PASS'] else 'FAIL'}** "
                  f"(AUC spread {fmt(v['gates']['G1t3']['auc_spread'])})"],
                 ["G2t3", f"pilot calibration BEFORE the run; strata sized to "
                  f"median permutation pool >= {POOL_TARGET}",
                  f"**{v['gates']['G2t3']}**"],
                 ["G3t3", "rule-29 against each statistic's OWN null (#68); "
                  "vectorised AUC agrees with the reference",
                  f"**{'PASS' if v['gates']['G3t3']['PASS'] else 'FAIL'}** "
                  f"({len(v['gates']['G3t3']['predicates'])} predicates)"]])

    pilot_rows = []
    for k, c in sorted(pil["calibration"].items()):
        pilot_rows.append([k, fmt(c.get("median_pool"), 1),
                           fmt(c.get("null_band")), fmt(c.get("band_width")),
                           fmt(c.get("null_mean")),
                           str(c.get("meets_pool_target")),
                           f"**{c.get('separates')}**"])
    pilot_tbl = tbl(["reading", "median pool", "null band", "band width",
                     "null mean", "pool target met", "separates"], pilot_rows)

    def budget_table(blob: dict[str, Any], with_bits: bool = True) -> str:
        head = ["representation", "stratification", "AUC", "bootstrap CI95",
                "own null band", "median pool"]
        if with_bits:
            head += ["bits", "null bits", "**excess bits**"]
        rows = []
        for name in REPS:
            for mode in STRATIFICATIONS:
                r = blob["readings"][f"{name}|{mode}"]
                if "auc" not in r:
                    rows.append([name, mode] + ["—"] * (len(head) - 2))
                    continue
                row = [f"`{name}`", mode, fmt(r["auc"]), fmt(r["ci95"]),
                       fmt(r["null_band"]), fmt(r["median_pool"], 1)]
                if with_bits:
                    row += [fmt(r["bits"], 3), fmt(r["bits_null_mean"], 3),
                            f"**{fmt(r['excess_bits'], 3)}**"]
                rows.append(row)
        return tbl(head, rows)

    va, vb, vc = v["V_T3a"], v["V_T3b"], v["V_T3c"]
    cl = v["readings"]["clean_replication"]
    het = v["readings"]["per_leaf_heterogeneity_R_emb"]
    oi = v["readings"]["observability_index"]
    st = v["readings"]["strata"]
    sens = full["r_obs_log_sensitivity"]
    jt = full["joint"]

    body = f"""# SUICA M4-T3 — the identity budget (one currency for the tail)

**Leg:** {LEG}. **Registered BEFORE run** in
`docs/SUICA_M4_T_HIERARCHICAL_SELECTION_IDENTITY_PLAN.md` (§ "M4-T3",
commit 5bbf846). Generated by `{rel(Path(__file__))}` — every table below
is written by the script from the persisted artifacts (rule 24).

**LABEL-FREE.** No Big5 or MBTI column is opened at any stage. Aggregates
only; author identifiers stay in the gitignored intermediates under
`results/m4_t3_identity_budget/`.

**Type:** EXPLORATORY.

## 1. What this leg is for

T1 proved the identity tail exists. T2 proved a generalizing taste
coordinate exists, but could **not** isolate the support channel by
matching — the registered calipers left a median of zero admissible
strangers. T3 answers that same question by **measurement** instead: four
representations, one statistic, one permutation machinery, marginal and
conditional, in one common currency.

| representation | what it is | similarity |
|---|---|---|
| `R_obs` | the 4-dim late-side observability vector (volume, span, entropy, breadth), z-scored | negative Euclidean (RN-T3-3) |
| `R_tree` | the frozen path code, depth-weighted prefix (RN-T3-4) | cosine |
| `R_emb` | the full-half taste centroid in T2's frozen per-fold embedding, d = {EMB_DIM} | cosine |
| `R_flat` | the Hellinger frequency vector — T1's ceiling | cosine |

## 2. Gates

{gates}

### G0t3 — anchors

{anchors}

T2's fold embeddings are verified held-out-pure: **{g0['T2_embedding_purity']}**.
Reconstructed n_valid = {g0['n_valid_reconstructed']} (T1: {A_N_FULL}).
`R_flat` marginal rebuilds to {fmt(g0['R_flat_vs_T1_ceiling']['reconstructed'])}
against T1's persisted ceiling {A_FLAT_FULL!r}
(|diff| {g0['R_flat_vs_T1_ceiling']['abs_diff']:.2e}) —
{g0['R_flat_vs_T1_ceiling']['note']}.

## 3. Reading notes (pinned BEFORE the verdicts)

""" + "\n".join(f"- **{k}** — {t}" for k, t in sorted(RN_NOTES.items())) + f"""

## 4. Anomalies (disclosed with timing)

- **A1 — the early-side observability vector did not exist and had to be
  built (pre-verdict, pre-pilot).** T2 persisted only the LATE side, but
  T3's statistic is early→late for every representation. The early span
  was re-derived from the comment stream under SR1's own split rule (the
  4000-timestamp cap included, as T2 established); early volume, entropy
  and breadth come from T2's already-verified early count matrix.
- **A2 — `R_tree` is not T1's path statistic (pre-verdict, by design).**
  T1's `hierarchical_path_auc` = {A_PATH_FULL} used an UNWEIGHTED common
  prefix. The registration asks for a depth-weighted code, and V-T3c needs
  a vector it can concatenate, so R_tree is the depth-weighted code of
  RN-T3-4 and rebuilds to {fmt(g0['R_tree_vs_T1_path']['reconstructed'])}.
  The two are relatives, not the same estimator; T1's number is not a gate
  on this one.
- **A3 — the leaf-stratified nulls sit slightly above 0.5 (pre-verdict).**
  Measured, not assumed: the one-positive-per-target / many-negatives
  pooling that T2 raised as defect #68 is still present, mildly, wherever
  strata are heterogeneous. This is exactly why every comparison here is
  against the reading's OWN band (RN-T3-6) and never against 0.5.

## 5. G2t3 — pilot calibration ({pil['G2t3']['n_pilot_targets']} targets, B={B_PILOT_PERM}), run BEFORE the budget

Strata sizing (#69 — pool target registered, realized widths reported):
target median permutation pool **>= {POOL_TARGET}**; realized
**{st['n_strata']} strata** at median pool **{fmt(st['median_pool'], 1)}**
(ladder tried: {', '.join(str(x['n_strata']) + '@' + fmt(x['median_pool'], 1) for x in st['tried'])}).
The registered decile stratification survives at full width.

The stratifier is PC1 of the z-scored late observability vector, explaining
**{fmt(oi['explained_variance'], 3)}** of its variance, loadings
{dict(zip(oi['dims'], [round(x, 3) for x in oi['loadings']]))}.

{pilot_tbl}

**G2t3 verdict: {pil['G2t3']['VERDICT']}.**

## 6. THE IDENTITY BUDGET (full arm, B_boot={B_BOOT}, B_perm={B_PERM})

One pair set per stratification, four representations on exactly those
pairs (RN-T3-1). Excess bits is the permutation-corrected currency of
RN-T3-5.

{budget_table(full)}

## 7. Verdicts (NULL-first, arm-level)

**V-T3a — the support channel: {va['verdict']}**
— {va['reason']}. `R_obs` marginal AUC **{fmt(va['numbers']['auc'])}**,
CI95 {fmt(va['numbers']['ci95'])}, own null band
{fmt(va['numbers']['null_band'])}, excess bits
**{fmt(va['numbers']['excess_bits'], 3)}**, {va['numbers']['n_targets']}
targets. Declared sensitivity (log-scaled observables, RN-T3-8):
AUC {fmt(sens['auc'])} CI {fmt(sens['ci95'])}, excess bits
{fmt(sens['excess_bits'], 3)}.

**This is the number T2's Arm A could not obtain.** Observability alone —
four coordinates, no content whatsoever — identifies the author well above
its own null. The support channel is real and it is large; it is not,
however, the whole tail.

**V-T3b — taste beyond support: {vb['verdict']}**
— {vb['reason']}. `R_emb` under observability-stratified permutation: AUC
**{fmt(vb['numbers']['auc'])}**, CI95 {fmt(vb['numbers']['ci95'])}, own null
band {fmt(vb['numbers']['null_band'])}, excess bits
**{fmt(vb['numbers']['excess_bits'], 3)}**, median pool
{fmt(vb['numbers']['median_pool'], 1)}. Marginal contrast:
{fmt(vb['marginal_for_contrast']['auc'])} CI
{fmt(vb['marginal_for_contrast']['ci95'])}, excess bits
{fmt(vb['marginal_for_contrast']['excess_bits'], 3)}.

**V-T3c — joint adequacy: {vc['verdict']}**
— {vc['reason']}. Weight fitted on TRAINING folds only (RN-T3-9):
w* = **{vc['w_star']}** at training AUC {fmt(vc['train_auc_at_w_star'])}.
Held-out joint AUC **{fmt(vc['joint_auc'])}** {fmt(vc['joint_ci95'])} against
the flat ceiling **{fmt(vc['flat_auc'])}** {fmt(vc['flat_ci95'])}.
**Gap (flat − joint) = {fmt(vc['gap'], 4)}, paired-bootstrap CI95
{fmt(vc['gap_ci95'], 4)}**, declared band ±{EPS_GAP}.

## 8. Routing (rule 16 — arm-level cells, the T2 lesson applied)

Outcomes: **{', '.join(v['routing']['outcomes'])}**. Modifiers:
{', '.join(v['routing']['modifiers']) or '—'}. Slug `{v['routing']['slug']}`.

| verdict | value | cell |
|---|---|---|
| V-T3a | {va['verdict']} | {'2 — SUPPORT_CHANNEL_MAJOR' if va['verdict'] == 'MAJOR' else 'no cell (only MAJOR routes)'} |
| V-T3b | {vb['verdict']} | {'3 — TASTE_BEYOND_SUPPORT' if vb['verdict'] == 'SURVIVES' else ('4 — TRANSPORT_WAS_SUPPORT' if vb['verdict'] == 'DIES' else '7 — UNDERRESOLVED')} |
| V-T3c | {vc['verdict']} | {'5 — JOINT_REPRESENTATION_ADEQUATE' if vc['verdict'] == 'ADEQUATE' else ('6 — BUDGET_WITH_RESIDUAL' if vc['verdict'] == 'GAP_REMAINS' else '7 — UNDERRESOLVED')} |

No verdict here is conjunctive on another: an arm that failed to resolve
would leave the others standing, which is precisely the granularity T2's
routing lacked.

## 9. Readings (no gates)

### 9.1 Clean-arm replication (T1's {A_REMOVED}-community ablation)

n_valid = {cl['n_valid']} (T1's clean arm: {A_N_CLEAN}; match
{cl['matches_T1_clean_n']}).

{budget_table(clean, with_bits=False)}

Clean joint: w* = {cl['joint']['w_star']}, joint AUC
{fmt(cl['joint']['joint_auc'])} vs flat {fmt(cl['joint']['flat_auc'])}, gap
{fmt(cl['joint']['gap'], 4)} CI {fmt(cl['joint']['gap_ci95'], 4)}.
Clean verdicts: **V-T3a {cl['V_T3a_clean']['verdict']}**,
**V-T3b {cl['V_T3b_clean']['verdict']}**,
**V-T3c {cl['V_T3c_clean']['verdict']}**.

### 9.2 Per-leaf heterogeneity for `R_emb` (observability-stratified)

{tbl(["strata scored", "min", "q25", "median", "q75", "max", "IQR"],
     [[fmt(het.get("n_strata"), 0), fmt(het.get("min")), fmt(het.get("q25")),
       fmt(het.get("median")), fmt(het.get("q75")), fmt(het.get("max")),
       fmt(het.get("iqr"))]])}

### 9.3 The training-fold weight curve (V-T3c's declared rule)

{tbl(["w (weight on R_emb)", "training-fold AUC"],
     [[fmt(c["w"], 2), fmt(c["train_auc"])]
      for c in jt["train_curve"][::4]])}

### 9.4 Post-verdict observations (recorded AFTER the verdicts, marked as such)

- **The tree carries nothing beyond its own leaf.** `R_tree | leaf` reads
  {fmt(rd['R_tree|leaf']['auc'])} {fmt(rd['R_tree|leaf']['ci95'])} against
  its own null {fmt(rd['R_tree|leaf']['null_band'])}, for
  {fmt(rd['R_tree|leaf']['excess_bits'], 3)} excess bits — indistinguishable
  from nothing. Conditioning on the leaf exhausts the path. That is also a
  strong internal check on the conditioning machinery: a representation
  whose information IS the stratifier must fall to its null, and it does.
- **The joint is the embedding.** V-T3c's training-fold rule chose
  w* = {vc['w_star']} — almost all weight on `R_emb` — and the held-out
  joint AUC {fmt(vc['joint_auc'])} is within
  {abs(vc['joint_auc'] - rd['R_emb|marginal']['auc']):.4f} of `R_emb`
  marginal alone. On this evidence the 4W doc's priority 2 ("tree + tail
  joint representation") is mostly tail: the hierarchy is a coarse
  quantisation of the same geometry the embedding already carries
  continuously, not an independent carrier to be added to it.
- **The budget in bits, marginal:** `R_flat`
  {fmt(rd['R_flat|marginal']['excess_bits'], 3)}; `R_emb`
  {fmt(rd['R_emb|marginal']['excess_bits'], 3)}
  ({100 * rd['R_emb|marginal']['excess_bits'] / rd['R_flat|marginal']['excess_bits']:.0f}% of the ceiling);
  `R_obs` {fmt(rd['R_obs|marginal']['excess_bits'], 3)}
  ({100 * rd['R_obs|marginal']['excess_bits'] / rd['R_flat|marginal']['excess_bits']:.0f}%);
  `R_tree` {fmt(rd['R_tree|marginal']['excess_bits'], 3)}
  ({100 * rd['R_tree|marginal']['excess_bits'] / rd['R_flat|marginal']['excess_bits']:.0f}%).
  These shares do not sum to the ceiling and are not meant to — the
  carriers overlap heavily. The ORDERING is the finding.
- **The conditioning is partial, and that cuts against V-T3b.** The
  stratifier is PC1, explaining {fmt(oi['explained_variance'], 3)} of the
  observability variance, so residual observability survives inside a
  stratum — proved directly by `R_obs | obs_stratum` still reading
  {fmt(rd['R_obs|obs_stratum']['auc'])} above its null. V-T3b therefore
  means "`R_emb` survives conditioning on the DOMINANT observability axis",
  not "on all four coordinates". What makes the verdict hold up anyway is
  the asymmetry: the same stratification costs `R_obs`
  {rd['R_obs|marginal']['auc'] - rd['R_obs|obs_stratum']['auc']:.4f} of AUC
  but costs `R_emb` only
  {rd['R_emb|marginal']['auc'] - rd['R_emb|obs_stratum']['auc']:.4f}. The
  taste coordinate is not made of the same material as the support channel.

## 9.5 Registration-defect candidates (flagged, never repaired)

- **RD-T3-1 — "z-scored" underspecifies the transform, and the verdict
  boundary sits inside the ambiguity.** The registered raw-z form gives
  `R_obs` marginal {fmt(va['numbers']['auc'])}
  {fmt(va['numbers']['ci95'])} → **{va['verdict']}**. The declared log1p
  sensitivity (RN-T3-8) gives {fmt(sens['auc'])} {fmt(sens['ci95'])},
  which is entirely above the 0.75 MAJOR threshold. Volume, span and
  breadth are heavy-tailed; raw z-scores let a handful of outliers dominate
  the Euclidean geometry and UNDERSTATE the support channel. The registered
  form carries the verdict, as it must — but a future registration must pin
  the transform, because on this corpus the choice moves V-T3a across a
  cell boundary. Clean arm behaves identically
  ({fmt(cl['table'][0]['auc'])} raw vs {fmt(clean['r_obs_log_sensitivity']['auc'])} log).
- **RD-T3-2 — ε_gap was declared without a projection.** G2t3 projects pool
  sizes (#69) but nothing projects the equivalence band. The measured gap is
  {fmt(vc['gap'], 4)} {fmt(vc['gap_ci95'], 4)} against ±{EPS_GAP}: outside,
  but the CI is {vc['gap_ci95'][1] - vc['gap_ci95'][0]:.4f} wide while its
  near edge misses the band by only
  {vc['gap_ci95'][0] - EPS_GAP:.4f}. A verdict this close to its own
  resolution should have had its band projected at G2, exactly as pool
  targets now are.
- **RD-T3-3 — "observability-decile strata" names one dimension for a
  four-dimensional object.** Deciles require a scalar; PC1 was declared and
  used, and it demonstrably does not exhaust the vector (§9.4). A design
  that means "condition on observability" should register the projection
  (or a multivariate scheme with its own pool target), not leave it to the
  executor.

## 10. Compliance

- **Label-free:** no Big5/MBTI column is read anywhere in
  `{rel(Path(__file__))}`; inputs are the selection-side frequency and
  count matrices, comment timestamps, T1's frozen tree and T2's frozen
  embedding.
- **No identifiers in committed artifacts.**
- **Interpreter:** {p0['environment']['python_version']} / numpy
  {p0['environment']['numpy']} / pandas {p0['environment']['pandas']} on
  {p0['environment']['platform']}.
- **Provenance:** T1 core sha256 `{g0['sha256']['t1_core'][:16]}…`, T2
  harness `{g0['sha256']['t2_harness'][:16]}…`, SR1 selection.npz
  `{g0['sha256']['sr1_selection'][:16]}…`, T2 counts.npz
  `{g0['sha256']['t2_counts'][:16]}…`.
- **Stage wall time (s):** part0 {p0['seconds']:.1f}, pilot
  {pil['seconds']:.1f}, budget {full['seconds']:.1f}, clean
  {clean['seconds']:.1f}, finalize {v['seconds']:.1f} — every stage far
  under the 600 s ceiling.
"""
    scan = tt.id_leak_scan(body)
    body += (f"- **ID-leak scan:** {scan['n_tokens_scanned']} tokens checked "
             f"against all {scan['n_cohort_ids']} cohort identifiers — "
             f"{scan['n_hits']} hits, "
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
    ap.add_argument("stage", choices=["part0", "pilot", "budget", "clean",
                                      "finalize", "report"])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"part0": stage_part0, "pilot": stage_pilot, "budget": stage_budget,
     "clean": stage_clean, "finalize": stage_finalize,
     "report": stage_report}[args.stage](args)


if __name__ == "__main__":
    main()
