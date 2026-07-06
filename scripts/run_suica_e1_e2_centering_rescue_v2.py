#!/usr/bin/env python
"""E1/E2: can the condition-centering mechanism be rescued? (exploration phase)

Rescue hypotheses, with decision rules committed BEFORE running:

R1 (two-way fixed-effects centering): the v1 operationalization subtracted raw
condition means = true condition effect + person composition of that
condition's authors. The theory only licenses subtracting the former. Estimate
condition effects with person effects explicitly modeled (alternating
demeaning / two-way FE), subtract only c_hat.
  Decision: delta_FE_vs_raw CI > +0.02 -> centering rescued;
            CI inside (-0.02, +0.02) -> FE centering harmless, adoptable as
            principled default but adds nothing;
            CI < -0.02 -> centering retired for that score family.

R2 (partial centering): sweep lambda in {0, .25, .5, .75, 1} on the naive
LOO-centered branch. Decision: report argmax lambda per construct; argmax at 0
confirms retirement; interior argmax with CI-supported gain revives partial
correction.

Both tested on (a) the 5 lexicon constructs and (b) 24-node occupancy shares
(linear-share arms so all reference choices are on the same scale), using the
same disjoint condition-set A/B stability design as audited P2.
Also reruns P1 (temporal retest) with the FE arm for the style family.
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

from scripts.suica_v2_lib import V2_CONSTRUCTS, loo_condition_center  # noqa: E402
from scripts.run_suica_p2_condition_centering_v2 import assign_condition_sets, corr_cols  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "s128"
EPS = 1e-4
LAMBDAS = [0.0, 0.25, 0.5, 0.75, 1.0]
N_BOOT = 500
SEED = 42


def twoway_fe_condition_effects(frame: pd.DataFrame, value_col: str, *, iters: int = 12) -> pd.Series:
    """Alternating-demeaning two-way FE: returns condition effects purged of person mix."""
    y = frame[value_col].to_numpy(float)
    users = frame["user_id"].to_numpy()
    conds = frame["condition"].to_numpy()
    b = pd.Series(0.0, index=pd.unique(users))
    c = pd.Series(0.0, index=pd.unique(conds))
    for _ in range(iters):
        resid_for_c = pd.Series(y - b.reindex(users).to_numpy(), index=conds)
        c_new = resid_for_c.groupby(level=0).mean()
        resid_for_b = pd.Series(y - c_new.reindex(conds).to_numpy(), index=users)
        b_new = resid_for_b.groupby(level=0).mean()
        if float(np.max(np.abs(c_new.reindex(c.index).fillna(0) - c))) < 1e-10:
            b, c = b_new, c_new
            break
        b, c = b_new, c_new
    c = c - float(np.average(c.reindex(conds).to_numpy()))  # identify: slice-weighted mean 0
    return c


def set_bases(work: pd.DataFrame, score_col: str) -> pd.DataFrame:
    cell = work.groupby(["user_id", "cset", "condition"], as_index=False)[score_col].mean()
    return cell.groupby(["user_id", "cset"])[score_col].mean().unstack("cset").dropna()


def ab_r(base: pd.DataFrame) -> float:
    return float(np.corrcoef(base["A"].to_numpy(float), base["B"].to_numpy(float))[0, 1])


def boot_delta(base_x: pd.DataFrame, base_y: pd.DataFrame, rng: np.random.Generator, n_boot: int = N_BOOT) -> tuple[float, float, float]:
    joined = base_x.join(base_y, lsuffix="_x", rsuffix="_y").dropna()
    ax, bx = joined["A_x"].to_numpy(float), joined["B_x"].to_numpy(float)
    ay, by = joined["A_y"].to_numpy(float), joined["B_y"].to_numpy(float)
    point = float(np.corrcoef(ax, bx)[0, 1] - np.corrcoef(ay, by)[0, 1])
    idx = np.arange(len(joined))
    draws = np.empty(n_boot)
    for i in range(n_boot):
        t = rng.choice(idx, size=len(idx), replace=True)
        draws[i] = np.corrcoef(ax[t], bx[t])[0, 1] - np.corrcoef(ay[t], by[t])[0, 1]
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return point, float(lo), float(hi)


def main() -> None:
    rng = np.random.default_rng(SEED)
    out_dir = ROOT / "results" / f"suica_e1_e2_centering_rescue_v2_{TAG}"
    out_dir.mkdir(parents=True, exist_ok=True)

    frame = pd.read_parquet(TIER_DIR / f"phase2_passB_scored_{TAG}.parquet")
    users_per_cond = frame.groupby("condition")["user_id"].nunique()
    frame = frame.loc[frame["condition"].map(users_per_cond).ge(3)]

    class _A:  # reuse audited P2 split rule
        min_conditions, min_slices_per_condition = 4, 3
    sets = assign_condition_sets(frame, _A)
    work = frame.merge(sets, on=["user_id", "condition"]).reset_index(drop=True)
    print(f"E1/E2 users={work['user_id'].nunique()} slices={len(work)}")

    # ----- E1/E2 on lexicon constructs -----
    rows = []
    lam_rows = []
    for construct in V2_CONSTRUCTS:
        w = work[["user_id", "condition", "cset", construct]].copy()
        w["_naive"] = loo_condition_center(w, construct, group_cols=("condition",))
        c_fe = twoway_fe_condition_effects(w, construct)
        w["_fe"] = w[construct] - c_fe.reindex(w["condition"]).to_numpy()
        base_raw = set_bases(w, construct)
        base_naive = set_bases(w, "_naive")
        base_fe = set_bases(w, "_fe")
        d_fe, lo_fe, hi_fe = boot_delta(base_fe, base_raw, rng)
        d_nv, lo_nv, hi_nv = boot_delta(base_naive, base_raw, rng)
        rows.append({
            "construct": construct, "n_users": int(len(base_raw)),
            "r_raw": ab_r(base_raw), "r_naive": ab_r(base_naive), "r_fe": ab_r(base_fe),
            "delta_fe_vs_raw": d_fe, "fe_ci_lo": lo_fe, "fe_ci_hi": hi_fe,
            "delta_naive_vs_raw": d_nv, "naive_ci_lo": lo_nv, "naive_ci_hi": hi_nv,
        })
        for lam in LAMBDAS:
            w["_lam"] = w[construct] - lam * (w[construct] - w["_naive"])
            lam_rows.append({"construct": construct, "lam": lam, "r": ab_r(set_bases(w, "_lam"))})
    e1_lex = pd.DataFrame(rows)
    e2 = pd.DataFrame(lam_rows)

    # ----- E1 on node-occupancy (linear shares; raw/naive/fe references) -----
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler
    from suica_core.suica import controlled_slice_text

    texts_frame = pd.read_parquet(TIER_DIR / f"phase2_passB_slicetext_{TAG}.parquet").merge(sets, on=["user_id", "condition"]).reset_index(drop=True)
    texts = texts_frame["slice_text"].fillna("").map(lambda t: controlled_slice_text(t, "method_stripped"))
    vec = TfidfVectorizer(lowercase=True, strip_accents="unicode", analyzer="word", ngram_range=(1, 2),
                          max_features=22000, min_df=3, sublinear_tf=True)
    dense = StandardScaler().fit_transform(
        TruncatedSVD(n_components=64, random_state=SEED).fit_transform(vec.fit_transform(texts)))
    K = 24
    labels = MiniBatchKMeans(n_clusters=K, random_state=SEED, batch_size=4096, n_init=5, max_iter=120).fit_predict(dense)
    texts_frame["node"] = labels
    onehot = np.zeros((len(texts_frame), K))
    onehot[np.arange(len(texts_frame)), labels] = 1.0
    pop_global = onehot.mean(axis=0)
    cond_index = texts_frame["condition"]
    pop_by_cond = pd.DataFrame(onehot).groupby(cond_index.values).mean()
    # two-way FE per node dimension
    fe_by_cond = np.zeros((len(pop_by_cond), K))
    cond_order = list(pop_by_cond.index)
    tmp = texts_frame[["user_id", "condition"]].copy()
    for k in range(K):
        tmp["_y"] = onehot[:, k]
        c_fe = twoway_fe_condition_effects(tmp, "_y")
        fe_by_cond[:, k] = c_fe.reindex(cond_order).fillna(0.0).to_numpy() + float(onehot[:, k].mean())
    fe_by_cond = pd.DataFrame(fe_by_cond, index=cond_order)

    def set_matrices(ref: str) -> dict[str, np.ndarray]:
        mats = {}
        for cset, sub in texts_frame.groupby("cset"):
            users_b = sorted(texts_frame["user_id"].unique())
            upos = {u: i for i, u in enumerate(users_b)}
            m = np.full((len(users_b), K), np.nan)
            for user, usub in sub.groupby("user_id"):
                oh = np.zeros((len(usub), K))
                oh[np.arange(len(usub)), usub["node"].to_numpy(int)] = 1.0
                if ref == "raw":
                    m[upos[user]] = oh.mean(axis=0) - pop_global
                elif ref == "naive":
                    m[upos[user]] = (oh - pop_by_cond.reindex(usub["condition"]).to_numpy()).mean(axis=0)
                else:
                    m[upos[user]] = (oh - fe_by_cond.reindex(usub["condition"]).to_numpy()).mean(axis=0)
            mats[cset] = m
        return mats

    occ = {}
    for ref in ("raw", "naive", "fe"):
        mats = set_matrices(ref)
        ok = ~(np.isnan(mats["A"]).any(axis=1) | np.isnan(mats["B"]).any(axis=1))
        occ[ref] = (mats["A"][ok], mats["B"][ok])
    n_ok = occ["raw"][0].shape[0]
    occ_point = {ref: float(np.nanmean(corr_cols(a, b))) for ref, (a, b) in occ.items()}
    idx = np.arange(n_ok)
    draws = {"fe": np.empty(N_BOOT), "naive": np.empty(N_BOOT)}
    for i in range(N_BOOT):
        t = rng.choice(idx, size=n_ok, replace=True)
        base = np.nanmean(corr_cols(occ["raw"][0][t], occ["raw"][1][t]))
        draws["fe"][i] = np.nanmean(corr_cols(occ["fe"][0][t], occ["fe"][1][t])) - base
        draws["naive"][i] = np.nanmean(corr_cols(occ["naive"][0][t], occ["naive"][1][t])) - base
    occ_summary = {
        "n_users": int(n_ok),
        "mean_node_r": occ_point,
        "delta_fe_vs_raw": occ_point["fe"] - occ_point["raw"],
        "fe_ci": [float(v) for v in np.percentile(draws["fe"], [2.5, 97.5])],
        "delta_naive_vs_raw": occ_point["naive"] - occ_point["raw"],
        "naive_ci": [float(v) for v in np.percentile(draws["naive"], [2.5, 97.5])],
    }

    # ----- P1 temporal retest with FE arm (style family) -----
    passa = pd.read_parquet(TIER_DIR / f"phase2_passA_scored_{TAG}.parquet")
    upc = passa.groupby("condition")["user_id"].nunique()
    passa = passa.loc[passa["condition"].map(upc).ge(3)]
    cc = passa.groupby(["user_id", "condition", "half"]).size().unstack("half").fillna(0)
    sh = cc.loc[(cc.get("early", 0) >= 2) & (cc.get("late", 0) >= 2)].reset_index()[["user_id", "condition"]]
    pu = sh.groupby("user_id").size()
    sh = sh.loc[sh["user_id"].isin(pu.loc[pu >= 2].index)]
    aw = passa.merge(sh.drop_duplicates(), on=["user_id", "condition"])
    p1_rows = []
    for construct in V2_CONSTRUCTS:
        halves = {}
        for arm in ("raw", "fe"):
            cols = {}
            for half in ("early", "late"):
                sub = aw.loc[aw["half"].eq(half)].copy()
                if arm == "fe":
                    c_fe = twoway_fe_condition_effects(sub, construct)
                    sub["_v"] = sub[construct] - c_fe.reindex(sub["condition"]).to_numpy()
                else:
                    sub["_v"] = sub[construct]
                cell = sub.groupby(["user_id", "condition"])["_v"].mean()
                cols[half] = cell.groupby("user_id").mean()
            joined = pd.concat(cols, axis=1).dropna()
            halves[arm] = float(joined["early"].corr(joined["late"]))
        p1_rows.append({"construct": construct, "p1_r_raw": halves["raw"], "p1_r_fe": halves["fe"]})
    p1_fe = pd.DataFrame(p1_rows)

    e1_lex.to_csv(out_dir / "e1_lexicon_arms.csv", index=False)
    e2.to_csv(out_dir / "e2_lambda_curve.csv", index=False)
    p1_fe.to_csv(out_dir / "p1_fe_vs_raw.csv", index=False)
    summary = {"occupancy": occ_summary}
    (out_dir / "e1_e2_results.json").write_text(json.dumps(summary, indent=2, default=float) + "\n")
    report = ROOT / "reports" / f"suica_e1_e2_centering_rescue_v2_{TAG}.md"
    report.write_text(
        "# SUICA E1/E2 Centering Rescue (exploration)\n\n## E1 lexicon arms\n\n"
        + e1_lex.round(4).to_markdown(index=False)
        + "\n\n## E2 lambda curve\n\n" + e2.pivot(index="construct", columns="lam", values="r").round(4).to_markdown()
        + "\n\n## E1 occupancy arms\n\n```json\n" + json.dumps(occ_summary, indent=2, default=float)
        + "\n```\n\n## P1 temporal retest, FE vs raw\n\n" + p1_fe.round(4).to_markdown(index=False) + "\n"
    )
    print(e1_lex.round(4).to_string(index=False))
    print("\nlambda curve:\n", e2.pivot(index="construct", columns="lam", values="r").round(4).to_string())
    print("\noccupancy:", json.dumps(occ_summary, indent=2, default=float))
    print("\nP1 FE vs raw:\n", p1_fe.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
