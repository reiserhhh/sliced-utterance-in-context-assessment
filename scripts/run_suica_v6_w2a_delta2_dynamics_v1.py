"""W2a — leverage-free gust dynamics via second differences (F12.1, registered commit da07462). Label-free.

Preregistered execution script for the SUICA W2a experiment.

For each corpus (Essays primary, PANDORA secondary) and for two m-range arms
(primary 5<=m<=12, sensitivity 4<=m<=12), this script:

  1. Restricts to texts whose window count m falls inside the arm's range,
     excludes m>12 texts (subsampled / j-gapped), and reports how many texts
     were excluded at each boundary.
  2. Standardizes every one of the 19 construct columns by that corpus's
     pooled window standard deviation (guarding sd>0). The pooled sd is
     computed once per corpus over the FULL corpus (all m values, before
     any arm-level restriction) and applied identically to both arms, so
     the sensitivity arm isolates the m-inclusion-range choice alone rather
     than also confounding it with a shifted standardization reference.
  3. Builds, per text, ordered (by j) series for each of the 19 raw
     constructs plus 2 gust-axis projection series (gust1_E, taken from the
     Essays C_motion gust; gust1_P, recomputed deterministically from the
     PANDORA m==3 second-difference correlation structure).
  4. Computes within-text second differences d_k = x_{k+1} - 2*x_k + x_{k-1},
     centers them within-text, and pools the lag-1 (d_k, d_{k+1}) pairs
     across texts to obtain rho1.
  5. Builds a 2000-replicate iid-standard-normal simulation null (identical
     pipeline, shape-matched to the real per-text window counts) to obtain a
     null distribution for rho1. This null depends only on corpus+arm (the
     multiset of text window-counts), not on which series is tested, so it
     is computed once per corpus+arm and reused across all 21 series.
  6. Derives a bias-adjusted theta-hat per series from the exact rho1(theta)
     identity via bisection.

Only the two parquet window caches and the Essays C_motion JSON are read.
No CSV files and no label columns are read anywhere in this script.

Seed: 20260712.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

SEED = 20260712
N_REPLICATES = 2000

REPO_ROOT = Path("/Volumes/mobile3/projects/project persona")

ESSAYS_PARQUET = REPO_ROOT / "results/suica_v6_e2_essays_motion/cache_essays_windows_scored19.parquet"
PANDORA_PARQUET = REPO_ROOT / "results/suica_tgeo_p8_functionalization/cache_windows_scored19.parquet"
ESSAYS_MOTION_JSON = REPO_ROOT / "results/suica_v6_e2_essays_motion/V6_E2_ESSAYS_MOTION.json"

OUTPUT_DIR = REPO_ROOT / "results/suica_v6_w2a_delta2_dynamics"
OUTPUT_JSON = OUTPUT_DIR / "V6_W2A_DELTA2_DYNAMICS.json"
OUTPUT_MD = OUTPUT_DIR / "V6_W2A_DELTA2_DYNAMICS.md"

NON_CONSTRUCT_COLS = ("eid", "cid", "user_id", "j", "m", "t", "tau", "delta")

# Primary arm first, sensitivity arm second (report order below follows this).
ARMS: dict = {
    "primary_m5_12": (5, 12),
    "sensitivity_m4_12": (4, 12),
}


# --------------------------------------------------------------------------
# Small numeric helpers
# --------------------------------------------------------------------------

def get_construct_cols(df: pd.DataFrame) -> list:
    return [c for c in df.columns if c not in NON_CONSTRUCT_COLS]


def corr_guarded(x: np.ndarray) -> np.ndarray:
    """z-score columns (guard sd>0), C = Z.T@Z/(n-1), fill diagonal with 1.0."""
    mu = x.mean(axis=0)
    sd = x.std(axis=0)
    sd_g = np.where(sd > 0, sd, 1.0)
    z = (x - mu) / sd_g
    n = x.shape[0]
    c = (z.T @ z) / (n - 1)
    np.fill_diagonal(c, 1.0)
    return c


def rho1_theta_model(theta: float) -> float:
    return -(4.0 * (1.0 + theta ** 2) + 7.0 * theta) / (6.0 * (1.0 + theta ** 2) + 8.0 * theta)


def solve_theta(observed: float, null_mean: float) -> float:
    adj = observed - (null_mean - (-2.0 / 3.0))
    if adj >= -2.0 / 3.0:
        return 0.0
    f_hi = rho1_theta_model(1.0)
    if adj <= f_hi:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f_mid = rho1_theta_model(mid)
        if f_mid > adj:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12:
            break
    return 0.5 * (lo + hi)


def pooled_pearson_from_sums(n, sa, sb, saa, sbb, sab) -> float:
    if n < 2:
        return float("nan")
    num = n * sab - sa * sb
    den = np.sqrt((n * saa - sa ** 2) * (n * sbb - sb ** 2))
    if den <= 0:
        return float("nan")
    return float(num / den)


# --------------------------------------------------------------------------
# Axis construction
# --------------------------------------------------------------------------

def load_gust1_e(cols: list) -> np.ndarray:
    with open(ESSAYS_MOTION_JSON) as f:
        obj = json.load(f)
    assert obj["constructs"] == cols, "gust1_E: JSON constructs order does not match parquet cols order"
    vec = np.asarray(obj["C_motion"]["gusts"][0]["vector"], dtype=float)
    assert vec.shape == (len(cols),), f"gust1_E: expected {len(cols)} floats, got {vec.shape}"
    return vec


def compute_gust1_p(pandora: pd.DataFrame, cols: list):
    pm3 = pandora[pandora["m"] == 3]
    sizes = pm3.groupby("cid").size()
    valid_cids = sizes[sizes == 3].index
    pm3 = pm3[pm3["cid"].isin(valid_cids)].sort_values(["cid", "j"])

    n_cols = len(cols)
    raw = pm3[cols].to_numpy(dtype=float)
    w = raw.reshape(-1, 3, n_cols)

    sd = raw.std(axis=0)
    sd_g = np.where(sd > 0, sd, 1.0)

    q = ((w[:, 0] - 2 * w[:, 1] + w[:, 2]) / np.sqrt(6.0)) / sd_g

    c = corr_guarded(q)
    eigvals, eigvecs = np.linalg.eigh(c)
    gust1_p = eigvecs[:, -1]
    return gust1_p, float(eigvals[-1]), int(q.shape[0])


def compute_pooled_sd(df: pd.DataFrame, cols: list):
    """Corpus-pooled window sd, computed over the FULL corpus (all m values).
    Shared across both arms so the sensitivity arm isolates the m-range
    choice alone. Returns (raw_sd, guarded_sd)."""
    sd = df[cols].to_numpy(dtype=float).std(axis=0)
    sd_g = np.where(sd > 0, sd, 1.0)
    return sd, sd_g


# --------------------------------------------------------------------------
# Per corpus+arm preparation
# --------------------------------------------------------------------------

def prepare_corpus_arm(df: pd.DataFrame, id_col: str, cols: list, m_lo: int, m_hi: int, pooled_sd_g: np.ndarray) -> dict:
    assert m_hi == 12, "arm upper bound expected to be 12 per spec (m>12 texts are subsampled/gapped)"

    total_texts = int(df[id_col].nunique())

    m_nunique = df.groupby(id_col)["m"].nunique()
    assert (m_nunique == 1).all(), f"{id_col}: m not constant within some text ids"

    m_by_id = df.groupby(id_col)["m"].first()
    sizes_by_id = df.groupby(id_col).size()

    n_gt12 = int((m_by_id > 12).sum())
    n_below_range = int((m_by_id < m_lo).sum())

    in_range_ids = m_by_id[(m_by_id >= m_lo) & (m_by_id <= m_hi)].index

    sizes_sub = sizes_by_id.reindex(in_range_ids)
    m_sub = m_by_id.reindex(in_range_ids)
    mismatch_mask = sizes_sub.to_numpy() != m_sub.to_numpy()
    bad = sizes_sub.index[mismatch_mask].tolist()
    assert not bad, f"{id_col}: {len(bad)} in-range texts have row count != m (unexpected gap): {bad[:5]}"

    sub = df[df[id_col].isin(in_range_ids)].sort_values([id_col, "j"]).reset_index(drop=True)

    std_matrix = sub[cols].to_numpy(dtype=float) / pooled_sd_g

    n_included = len(in_range_ids)
    assert n_included + n_gt12 + n_below_range == total_texts, (
        f"{id_col}: exclusion accounting mismatch: "
        f"{n_included}+{n_gt12}+{n_below_range} != {total_texts}"
    )

    return {
        "sub": sub,
        "std_matrix": std_matrix,
        "n_total_texts": total_texts,
        "n_included_texts": n_included,
        "n_excluded_m_gt_12": n_gt12,
        "n_excluded_m_below_range": n_below_range,
    }


def build_m_groups(sub: pd.DataFrame, id_col: str):
    """Return [(m_value, row_mask, n_texts_m), ...], validating id/j block structure."""
    m_arr = sub["m"].to_numpy()
    id_arr = sub[id_col].to_numpy()
    j_arr = sub["j"].to_numpy()

    groups = []
    for m_value in sorted(pd.unique(m_arr).tolist()):
        mask = m_arr == m_value
        n_rows = int(mask.sum())
        assert n_rows % m_value == 0, f"m={m_value}: row count {n_rows} not divisible by m"
        n_texts_m = n_rows // m_value

        ids_block = id_arr[mask].reshape(n_texts_m, m_value)
        j_block = j_arr[mask].reshape(n_texts_m, m_value)
        assert np.all(ids_block == ids_block[:, [0]]), f"m={m_value}: id not constant within a text block"
        assert np.all(np.diff(j_block, axis=1) > 0), f"m={m_value}: j not strictly increasing within a text block"

        groups.append((int(m_value), mask, n_texts_m))
    return groups


# --------------------------------------------------------------------------
# Observed pooled rho1 for one series
# --------------------------------------------------------------------------

def observed_rho1(series_col: np.ndarray, groups) -> tuple:
    sa = sb = saa = sbb = sab = 0.0
    n_pairs = 0
    for m_value, mask, n_texts_m in groups:
        if m_value < 4 or n_texts_m == 0:
            continue
        x = series_col[mask].reshape(n_texts_m, m_value)
        d2 = x[:, 2:] - 2 * x[:, 1:-1] + x[:, :-2]
        d2 = d2 - d2.mean(axis=1, keepdims=True)
        a = d2[:, :-1]
        b = d2[:, 1:]
        sa += float(a.sum())
        sb += float(b.sum())
        saa += float((a * a).sum())
        sbb += float((b * b).sum())
        sab += float((a * b).sum())
        n_pairs += a.size
    rho1 = pooled_pearson_from_sums(n_pairs, sa, sb, saa, sbb, sab)
    return rho1, n_pairs


# --------------------------------------------------------------------------
# Vectorized iid-normal simulation null (per corpus+arm, shared across series)
# --------------------------------------------------------------------------

def simulate_null(groups, n_replicates: int, rng: np.random.Generator):
    sa = np.zeros(n_replicates)
    sb = np.zeros(n_replicates)
    saa = np.zeros(n_replicates)
    sbb = np.zeros(n_replicates)
    sab = np.zeros(n_replicates)
    n_pairs_total = 0

    for m_value, _mask, n_texts_m in groups:
        if m_value < 4 or n_texts_m == 0:
            continue
        x = rng.standard_normal(size=(n_replicates, n_texts_m, m_value))
        d2 = x[:, :, 2:] - 2 * x[:, :, 1:-1] + x[:, :, :-2]
        d2 = d2 - d2.mean(axis=2, keepdims=True)
        a = d2[:, :, :-1]
        b = d2[:, :, 1:]
        sa += a.sum(axis=(1, 2))
        sb += b.sum(axis=(1, 2))
        saa += (a * a).sum(axis=(1, 2))
        sbb += (b * b).sum(axis=(1, 2))
        sab += (a * b).sum(axis=(1, 2))
        n_pairs_total += n_texts_m * (m_value - 3)

    num = n_pairs_total * sab - sa * sb
    den = np.sqrt((n_pairs_total * saa - sa ** 2) * (n_pairs_total * sbb - sb ** 2))
    with np.errstate(divide="ignore", invalid="ignore"):
        null_rho1 = np.where(den > 0, num / den, np.nan)
    return null_rho1, n_pairs_total


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    essays = pd.read_parquet(ESSAYS_PARQUET)
    pandora = pd.read_parquet(PANDORA_PARQUET)

    cols_e = get_construct_cols(essays)
    cols_p = get_construct_cols(pandora)
    assert cols_e == cols_p, "construct column lists differ between Essays and PANDORA"
    cols = cols_e
    assert len(cols) == 19, f"expected 19 construct columns, got {len(cols)}: {cols}"

    gust1_e_raw = load_gust1_e(cols)
    gust1_e = gust1_e_raw / np.linalg.norm(gust1_e_raw)

    gust1_p_raw, gust1_p_eigval, gust1_p_n = compute_gust1_p(pandora, cols)
    gust1_p = gust1_p_raw / np.linalg.norm(gust1_p_raw)

    print(f"gust1_E (normalized, from {ESSAYS_MOTION_JSON.name}): {np.round(gust1_e, 4).tolist()}")
    print(f"gust1_P (normalized, recomputed from {gust1_p_n} PANDORA m==3 texts): "
          f"{np.round(gust1_p, 4).tolist()}  [top eigenvalue={gust1_p_eigval:.4f}]")
    print()

    corpora = {
        "essays": {"df": essays, "id_col": "eid"},
        "pandora": {"df": pandora, "id_col": "cid"},
    }

    json_out: dict = {"essays": {}, "pandora": {}}
    exclusions: dict = {"essays": {}, "pandora": {}}
    pooled_sd_report: dict = {}

    for corpus_name, info in corpora.items():
        df = info["df"]
        id_col = info["id_col"]

        pooled_sd_raw, pooled_sd_g = compute_pooled_sd(df, cols)
        pooled_sd_report[corpus_name] = pooled_sd_raw.tolist()
        print(f"[{corpus_name}] full-corpus pooled sd (n_windows={len(df)}): "
              f"{np.round(pooled_sd_raw, 4).tolist()}")

        for arm_name, (m_lo, m_hi) in ARMS.items():
            prep = prepare_corpus_arm(df, id_col, cols, m_lo, m_hi, pooled_sd_g)
            sub = prep["sub"]
            std_matrix = prep["std_matrix"]

            proj_e = std_matrix @ gust1_e
            proj_p = std_matrix @ gust1_p
            series_matrix = np.concatenate([proj_e[:, None], proj_p[:, None], std_matrix], axis=1)
            series_names = ["gust1_E", "gust1_P"] + cols
            assert series_matrix.shape == (len(sub), 21)

            groups = build_m_groups(sub, id_col)

            null_dist, null_n_pairs = simulate_null(groups, N_REPLICATES, rng)
            null_mean = float(np.nanmean(null_dist))
            null_lo = float(np.nanpercentile(null_dist, 2.5))
            null_hi = float(np.nanpercentile(null_dist, 97.5))

            print(f"=== {corpus_name} / {arm_name} (m in [{m_lo},{m_hi}]) "
                  f"n_texts={prep['n_included_texts']} excluded_m_gt_12={prep['n_excluded_m_gt_12']} "
                  f"excluded_below_range={prep['n_excluded_m_below_range']} total={prep['n_total_texts']} ===")
            print(f"    null: mean={null_mean:+.4f} lo2.5={null_lo:+.4f} hi97.5={null_hi:+.4f} "
                  f"n_pairs={null_n_pairs} reps={N_REPLICATES}")

            arm_json = {}
            for k, name in enumerate(series_names):
                rho1, n_pairs = observed_rho1(series_matrix[:, k], groups)
                assert n_pairs == null_n_pairs, (
                    f"{corpus_name}/{arm_name}/{name}: observed n_pairs {n_pairs} != null n_pairs {null_n_pairs}"
                )
                p = float(np.nanmean(null_dist <= rho1))
                theta = solve_theta(rho1, null_mean)

                arm_json[name] = {
                    "rho1": rho1,
                    "null_mean": null_mean,
                    "null_lo": null_lo,
                    "null_hi": null_hi,
                    "p": p,
                    "theta": theta,
                    "n_texts": int(prep["n_included_texts"]),
                    "n_pairs": int(n_pairs),
                }

                print(f"[{corpus_name} {name}] rho1={rho1:+.4f} null_mean={null_mean:+.4f} "
                      f"p={p:.4f} theta={theta:.3f} n_pairs={n_pairs}")

            json_out[corpus_name][arm_name] = arm_json
            exclusions[corpus_name][arm_name] = {
                "m_lo": m_lo,
                "m_hi": m_hi,
                "n_total_texts": prep["n_total_texts"],
                "n_included_texts": prep["n_included_texts"],
                "n_excluded_m_gt_12": prep["n_excluded_m_gt_12"],
                "n_excluded_m_below_range": prep["n_excluded_m_below_range"],
            }
            print()

    elapsed = time.time() - t_start
    print(f"total runtime: {elapsed:.1f}s")

    meta = {
        "seed": SEED,
        "n_replicates": N_REPLICATES,
        "construct_cols": cols,
        "arms": {name: {"m_lo": lo, "m_hi": hi} for name, (lo, hi) in ARMS.items()},
        "exclusions": exclusions,
        "gust1_E_normalized": gust1_e.tolist(),
        "gust1_P_normalized": gust1_p.tolist(),
        "gust1_P_top_eigenvalue": gust1_p_eigval,
        "gust1_P_n_source_texts": gust1_p_n,
        "pooled_sd_by_corpus": pooled_sd_report,
        "runtime_seconds": elapsed,
        "docstring": (
            "W2a — leverage-free gust dynamics via second differences "
            "(F12.1, registered commit da07462). Label-free."
        ),
        "standardization_note": (
            "Step-2 pooled sd is computed once per corpus over the FULL "
            "corpus (all texts, all m values, before any arm-level "
            "m-restriction) and applied identically to both the primary "
            "and sensitivity arms, so the sensitivity arm isolates the "
            "m-inclusion-range choice alone. This choice is provably "
            "inconsequential for the 19 raw construct series (pooled "
            "Pearson rho1 is invariant to any positive per-series rescale), "
            "and only marginally affects the 2 axis-projection series via "
            "relative inter-column weighting."
        ),
    }

    final_json = {"meta": meta, **json_out}

    with open(OUTPUT_JSON, "w") as f:
        json.dump(final_json, f, indent=2)

    write_markdown(final_json)

    print(f"wrote {OUTPUT_JSON}")
    print(f"wrote {OUTPUT_MD}")


def write_markdown(final_json: dict) -> None:
    lines = []
    lines.append("# V6 W2a — Delta-2 Gust Dynamics")
    lines.append("")
    lines.append(
        "W2a — leverage-free gust dynamics via second differences "
        "(F12.1, registered commit da07462). Label-free."
    )
    lines.append("")
    meta = final_json["meta"]
    lines.append(f"- seed: {meta['seed']}")
    lines.append(f"- null replicates: {meta['n_replicates']}")
    lines.append(f"- runtime: {meta['runtime_seconds']:.1f}s")
    lines.append("")

    axis_names = ["gust1_E", "gust1_P"]

    for corpus_name in ("essays", "pandora"):
        arm_name = "primary_m5_12"
        arm = final_json[corpus_name][arm_name]
        excl = meta["exclusions"][corpus_name][arm_name]
        lines.append(f"## {corpus_name} (primary arm, m in [{excl['m_lo']},{excl['m_hi']}])")
        lines.append("")
        lines.append(
            f"n_texts={excl['n_included_texts']} of {excl['n_total_texts']} "
            f"(excluded m>12: {excl['n_excluded_m_gt_12']}, "
            f"excluded below range: {excl['n_excluded_m_below_range']})"
        )
        lines.append("")
        lines.append("| series | rho1 | null_mean | null_lo | null_hi | p | theta | n_pairs |")
        lines.append("|---|---|---|---|---|---|---|---|")

        def fmt_row(name):
            row = arm[name]
            return (
                f"| {name} | {row['rho1']:+.4f} | {row['null_mean']:+.4f} | {row['null_lo']:+.4f} | "
                f"{row['null_hi']:+.4f} | {row['p']:.4f} | {row['theta']:.3f} | {row['n_pairs']} |"
            )

        for name in axis_names:
            lines.append(fmt_row(name))

        construct_names = [n for n in arm.keys() if n not in axis_names]
        sorted_constructs = sorted(construct_names, key=lambda n: arm[n]["rho1"])
        most_negative = sorted_constructs[:5]
        least_negative = sorted_constructs[-5:]

        lines.append("| _5 most negative_ | | | | | | | |")
        for name in most_negative:
            lines.append(fmt_row(name))
        lines.append("| _5 least negative_ | | | | | | | |")
        for name in least_negative:
            lines.append(fmt_row(name))
        lines.append("")

    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
