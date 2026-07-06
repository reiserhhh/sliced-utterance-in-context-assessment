#!/usr/bin/env python
"""E7 v2: within-person ("horizontal") state-factor discovery — OP-16/OP-17.

v2 changes (round-5 audit fixes):
- Persistence is tested ABOVE the proper negative null (within-person
  centering induces E[r] ~ -1/(m-1)): empirical 200-shuffle null for points,
  analytic pair-weighted null inside cluster bootstraps.
- The vacuous odd/even congruence criterion is REPLACED: factor-level
  cell-state reliability = corr(factor score from first-half slices, from
  second-half slices) across user-occasion cells, within-person centered.
  Congruence is reported descriptively WITH its shuffled-month null.
- --occasion {month, week}: week granularity is the OP-16 interim probe
  (states are expected below the month timescale).

Pre-committed v2 criteria:
  E7a: >= 5 features with within-person contiguous split-half r >= 0.10.
  E7b': >= 2 factors with cell-state reliability >= 0.10 (fail-able; month
        baseline from round-5 audit was 0.037-0.122).
  E7c': factors with above-null lag-1 delta CI > 0 AND decay
        (delta1 - delta3) CI > 0.
  OP-16 probe: week-level E7a count and E7b'/E7c' magnitudes should exceed
        month-level if states live below the month scale.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text, varimax_rotation  # noqa: E402
from scripts.suica_v2_lib import fast_anchor_rates  # noqa: E402
from scripts.run_suica_narrative_projective_anchor_validation_v2 import ANCHOR_LEXICONS  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
OCC = sys.argv[sys.argv.index("--occasion") + 1] if "--occasion" in sys.argv else "month"
OUT_DIR = ROOT / "results" / f"suica_e7_within_state_discovery_v3_{OCC}"
REPORT = ROOT / "reports" / f"suica_e7_within_state_discovery_v3_{OCC}.md"
FEATURES = [f"{k}_rate" for k in sorted(ANCHOR_LEXICONS)]
SEED = 42
MIN_SLICES_CELL = 4
MIN_OCCASIONS = 6
N_FACTORS = 5
N_NULL_DRAWS = 200


def occ_key(ts: float) -> str:
    t = pd.Timestamp(ts, unit="s", tz="UTC")
    if OCC == "week":
        iso = t.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    return f"{t.year}-{t.month:02d}"


def occ_index(key: str) -> int:
    if OCC == "week":
        y, w = key.split("-W")
        return int(y) * 53 + int(w)
    y, m = key.split("-")
    return int(y) * 12 + int(m)


def build_cells() -> pd.DataFrame:
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments_deep.parquet")
    comments["author"] = comments["author"].astype(str)
    comments["subreddit"] = comments["subreddit"].fillna("__m__").astype(str)
    rows = []
    for user, g in comments.groupby("author"):
        top = g["subreddit"].value_counts().index[0]
        sub = g.loc[g["subreddit"].eq(top)].sort_values("created_utc")
        if len(sub) < 30:
            continue
        sub = sub.assign(occ=sub["created_utc"].map(occ_key))
        for okey, cell in sub.groupby("occ"):
            text = "\n".join(cell["body"].astype(str))
            slices = [r for r in fixed_token_slices_for_text(text, slice_tokens=128, stride=128,
                                                             min_slice_tokens=24, max_slices=12)
                      if not PERSONALITY_LEAK_RE.search(r["slice_text"])]
            if len(slices) < MIN_SLICES_CELL:
                continue
            feats = pd.DataFrame([fast_anchor_rates(r["slice_text"]) for r in slices])
            half = len(slices) // 2
            row = {"user_id": user, "occ": okey, "n_slices": len(slices)}
            for f in FEATURES:
                row[f] = float(feats[f].mean())
                row[f"{f}__h1"] = float(feats[f].iloc[:half].mean())
                row[f"{f}__h2"] = float(feats[f].iloc[half:].mean())
            rows.append(row)
    cells = pd.DataFrame(rows)
    occ_counts = cells.groupby("user_id").size()
    keep = occ_counts.loc[occ_counts >= MIN_OCCASIONS].index
    return cells.loc[cells["user_id"].isin(keep)].reset_index(drop=True)


def tucker_phi(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    an = a / np.linalg.norm(a, axis=0, keepdims=True)
    bn = b / np.linalg.norm(b, axis=0, keepdims=True)
    return an.T @ bn


def pca_varimax(x: np.ndarray, k: int, seed: int) -> np.ndarray:
    from sklearn.decomposition import PCA
    pca = PCA(n_components=k, random_state=seed)
    pca.fit(x)
    load = pca.components_.T * np.sqrt(np.maximum(pca.explained_variance_, 0))[None, :]
    rot = varimax_rotation(load)
    load = load @ rot
    for j in range(k):
        i = int(np.nanargmax(np.abs(load[:, j])))
        if load[i, j] < 0:
            load[:, j] *= -1
    return load


def best_match(phi: np.ndarray) -> list[float]:
    p = np.abs(phi.copy())
    out = []
    for _ in range(p.shape[0]):
        i, j = np.unravel_index(np.nanargmax(p), p.shape)
        out.append(float(p[i, j]))
        p[i, :] = -1
        p[:, j] = -1
    return out


def lag_pairs(score_frame: pd.DataFrame, col: str, lag: int) -> np.ndarray:
    pairs = []
    for _, g in score_frame.groupby("user_id"):
        m = dict(zip(g["oidx"], g[col]))
        pairs.extend((m[k], m[k + lag]) for k in g["oidx"] if k + lag in m)
    return np.asarray(pairs)


def pooled_r(pairs: np.ndarray) -> float:
    if len(pairs) < 200:
        return float("nan")
    return float(np.corrcoef(pairs[:, 0], pairs[:, 1])[0, 1])


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cells = build_cells()
    print(f"E7[{OCC}] cells: {len(cells)} users={cells['user_id'].nunique()} "
          f"median occ/user={cells.groupby('user_id').size().median():.0f}")

    # ---- E7a: within-person contiguous state reliability per feature ----
    h1 = [f"{f}__h1" for f in FEATURES]
    h2 = [f"{f}__h2" for f in FEATURES]
    cent = cells.copy()
    cent[h1] = cent[h1] - cent.groupby("user_id")[h1].transform("mean")
    cent[h2] = cent[h2] - cent.groupby("user_id")[h2].transform("mean")
    rel = pd.DataFrame([{"feature": f, "within_state_split_half_r":
                         float(np.corrcoef(cent[f"{f}__h1"], cent[f"{f}__h2"])[0, 1])} for f in FEATURES]
                       ).sort_values("within_state_split_half_r", ascending=False)
    e7a_count = int((rel["within_state_split_half_r"] >= 0.10).sum())

    # ---- factor structure (descriptive congruence + shuffled null) ----
    w = cells.copy()
    w[FEATURES] = w[FEATURES] - w.groupby("user_id")[FEATURES].transform("mean")
    w["oidx"] = w["occ"].map(occ_index)
    w["rank"] = w.groupby("user_id")["oidx"].rank(method="first").astype(int)
    mu, sd = w[FEATURES].mean(), w[FEATURES].std().replace(0, 1)
    z = (w[FEATURES] - mu) / sd
    odd_mask = (w["rank"] % 2).eq(1).to_numpy()
    load_a = pca_varimax(z.loc[odd_mask].to_numpy(float), N_FACTORS, SEED)
    load_b = pca_varimax(z.loc[~odd_mask].to_numpy(float), N_FACTORS, SEED + 1)
    congruence = best_match(tucker_phi(load_a, load_b))
    shuf = w.copy()
    shuf["rank"] = shuf.groupby("user_id")["rank"].transform(lambda s: rng.permutation(s.to_numpy()))
    sm = (shuf["rank"] % 2).eq(1).to_numpy()
    congruence_null = best_match(tucker_phi(
        pca_varimax(z.loc[sm].to_numpy(float), N_FACTORS, SEED + 2),
        pca_varimax(z.loc[~sm].to_numpy(float), N_FACTORS, SEED + 3)))

    load_full = load_a
    fac_cols = [f"state_f{j+1}" for j in range(N_FACTORS)]
    scores = z.to_numpy(float) @ load_full
    scores /= np.where(scores.std(axis=0) > 1e-12, scores.std(axis=0), 1.0)
    sf = pd.concat([w[["user_id", "oidx"]].reset_index(drop=True),
                    pd.DataFrame(scores, columns=fac_cols)], axis=1)

    # ---- E7b': factor cell-state reliability (h1 vs h2 halves) ----
    zh1 = ((cent[h1].to_numpy(float)) / sd.to_numpy()[None, :]) @ load_full
    zh2 = ((cent[h2].to_numpy(float)) / sd.to_numpy()[None, :]) @ load_full
    cell_rel = [float(np.corrcoef(zh1[:, j], zh2[:, j])[0, 1]) for j in range(N_FACTORS)]
    e7b_count = int(sum(r >= 0.10 for r in cell_rel))

    # ---- E7c': above-null persistence with decay ----
    users = sf["user_id"].unique()
    by_user = {u: g.sort_values("oidx") for u, g in sf.groupby("user_id")}
    lag_rows = []
    for j, col in enumerate(fac_cols):
        point = {lag: pooled_r(lag_pairs(sf, col, lag)) for lag in (1, 2, 3)}
        nulls = []
        for d in range(N_NULL_DRAWS):
            drng = np.random.default_rng(20_000 + d)
            pairs = []
            for u, g in by_user.items():
                vals = drng.permutation(g[col].to_numpy())
                m = dict(zip(g["oidx"].to_numpy(), vals))
                pairs.extend((m[k], m[k + 1]) for k in m if k + 1 in m)
            nulls.append(pooled_r(np.asarray(pairs)))
        null_mean = float(np.nanmean(nulls))
        deltas = {lag: point[lag] - null_mean for lag in (1, 2, 3)}
        boots1, boots13 = [], []
        for b in range(400):
            brng = np.random.default_rng(30_000 + b)
            take = brng.choice(users, size=len(users), replace=True)
            p1, p3, nw = [], [], []
            for u in take:
                g = by_user[u]
                m = dict(zip(g["oidx"].to_numpy(), g[col].to_numpy()))
                pr1 = [(m[k], m[k + 1]) for k in m if k + 1 in m]
                pr3 = [(m[k], m[k + 3]) for k in m if k + 3 in m]
                p1.extend(pr1)
                p3.extend(pr3)
                if len(g) > 1 and pr1:
                    nw.append((len(pr1), -1.0 / (len(g) - 1)))
            r1 = pooled_r(np.asarray(p1))
            r3 = pooled_r(np.asarray(p3))
            null_b = sum(n * v for n, v in nw) / max(1, sum(n for n, _ in nw))
            if np.isfinite(r1):
                boots1.append(r1 - null_b)
                if np.isfinite(r3):
                    boots13.append((r1 - null_b) - (r3 - null_b))
        l1lo, l1hi = np.percentile(boots1, [2.5, 97.5])
        d13lo, d13hi = np.percentile(boots13, [2.5, 97.5])
        top = [FEATURES[i] for i in np.argsort(-np.abs(load_full[:, j]))[:4]]
        lag_rows.append({"factor": col, "cell_state_reliability": cell_rel[j],
                         "congruence_ab": congruence[j], "congruence_null": congruence_null[j],
                         "lag1_r": point[1], "null_mean": null_mean, "delta1": deltas[1],
                         "delta1_ci_lo": float(l1lo), "delta1_ci_hi": float(l1hi),
                         "delta3": deltas[3], "decay_ci_lo": float(d13lo), "decay_ci_hi": float(d13hi),
                         "top_features": ", ".join(top)})
    lags = pd.DataFrame(lag_rows)
    persistent = lags.loc[(lags["delta1_ci_lo"] > 0) & (lags["decay_ci_lo"] > 0)]

    criteria = {
        "occasion": OCC,
        "E7a_features_ge_010": e7a_count,
        "E7a_pass": bool(e7a_count >= 5),
        "E7b_cell_state_reliability_ge_010": e7b_count,
        "E7b_pass": bool(e7b_count >= 2),
        "E7c_persistent_decaying_factors": int(len(persistent)),
        "median_congruence_null_gap": float(np.median(np.array(congruence) - np.array(congruence_null))),
    }
    rel.to_csv(OUT_DIR / "e7a_feature_state_reliability.csv", index=False)
    pd.DataFrame(load_full, index=FEATURES, columns=fac_cols).to_csv(OUT_DIR / "e7_within_loadings.csv")
    lags.to_csv(OUT_DIR / "e7_factor_lags.csv", index=False)
    (OUT_DIR / "e7_results.json").write_text(json.dumps(criteria, indent=2, default=float) + "\n")
    REPORT.write_text(
        f"# SUICA E7 v2 Within-Person State Discovery (deep, rind-fixed, occasions: {OCC})\n\n"
        f"cells: {len(cells)}, users: {cells['user_id'].nunique()}\n\n## E7a feature state reliability (contiguous)\n\n"
        + rel.round(3).to_markdown(index=False)
        + "\n\n## Factors: cell-state reliability, congruence (with shuffled null), above-null persistence\n\n"
        + lags.round(3).to_markdown(index=False)
        + "\n\n```json\n" + json.dumps(criteria, indent=2, default=float) + "\n```\n"
    )
    print(rel.head(8).round(3).to_string(index=False))
    print("\n", lags.round(3).to_string(index=False))
    print(json.dumps(criteria, indent=2, default=float))


if __name__ == "__main__":
    main()
