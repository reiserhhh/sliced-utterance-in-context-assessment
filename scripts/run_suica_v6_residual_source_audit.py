#!/usr/bin/env python
"""Audit whether V6 residual and motion identity survive matched strangers.

This is a label-free falsification step.  It contrasts each author's early
representation with late views from strangers matched on available expression
opportunity: text volume, condition support, dynamic path support, and the
set of observed subreddits.  A signal that survives cannot be explained solely
by these measured opportunity variables; it remains an *unidentified stable
author-path feature*, not a personality construct.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v6_factor_discovery_v2 import (  # noqa: E402
    build_objects,
    conditional_residual,
    crossfit_residuals,
    fit_representation,
    identity_diagnostics,
    paired_views,
    permutation_strata,
    prepare_units,
)
from suica_core.factor_discovery import (  # noqa: E402
    fit_stable_crossview,
    stable_user_split,
    transform_stable_crossview,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / "data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/v6_factor_discovery_raw.json")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/v6_residual_source_audit")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/V6_RESIDUAL_SOURCE_AUDIT.md")
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return float(len(left & right) / len(union)) if union else 1.0


def paired_metadata(frame: pd.DataFrame, users: list[str]) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Return aligned early/late opportunity metadata with median imputation."""
    columns = [c for c in frame if c.startswith("meta_") or c in {"dynamic_runs", "dynamic_transitions"}]
    if not columns:
        columns = ["__intercept__"]
        frame = frame.assign(__intercept__=1.0)
    early = frame.loc[frame["half"].eq("early")].set_index("user_id").reindex(users)[columns]
    late = frame.loc[frame["half"].eq("late")].set_index("user_id").reindex(users)[columns]
    all_values = np.vstack([early.to_numpy(float), late.to_numpy(float)])
    median = np.nanmedian(all_values, axis=0)
    return (
        np.where(np.isfinite(early.to_numpy(float)), early.to_numpy(float), median),
        np.where(np.isfinite(late.to_numpy(float)), late.to_numpy(float), median),
        columns,
    )


def author_half_condition_sets(units: pd.DataFrame) -> dict[tuple[str, str], set[str]]:
    """Build observed condition sets; absence is preserved as an empty set."""
    return {
        (str(user), str(half)): set(group["condition"].astype(str))
        for (user, half), group in units.groupby(["user_id", "half"], observed=True)
    }


def matched_stranger_distances(
    early: np.ndarray,
    late: np.ndarray,
    early_meta: np.ndarray,
    late_meta: np.ndarray,
    early_sets: list[set[str]],
    late_sets: list[set[str]],
    *,
    condition_weight: float,
    seed: int,
    n_draws: int = 20,
    candidate_pool: int = 25,
    minimum_condition_jaccard: float | None = None,
) -> tuple[np.ndarray, dict[str, float]]:
    """Sample metadata- and condition-matched stranger distances.

    Each late stranger is matched to the observed late target, not to the early
    anchor. The candidate score is standardized late-opportunity distance plus a
    weighted Jaccard distance between late condition sets. Sampling within the
    nearest candidate pool avoids presenting one deterministic nearest neighbor
    as if it were a population-level matched control.
    """
    if len(early) != len(late) or len(early) < 2:
        raise ValueError("matched strangers require at least two paired authors")
    joint = np.vstack([early_meta, late_meta])
    scale = np.nanstd(joint, axis=0, ddof=1)
    scale[~np.isfinite(scale) | (scale < 1e-8)] = 1.0
    e_meta = early_meta / scale
    l_meta = late_meta / scale
    # The opportunity counterfactual is "another author with a late text like
    # u's observed late text", so matching is target-late to candidate-late.
    numeric = np.sqrt(np.mean((l_meta[:, None, :] - l_meta[None, :, :]) ** 2, axis=2))
    jaccard = np.array([[_jaccard(a, b) for b in late_sets] for a in late_sets])
    cost = numeric + condition_weight * (1.0 - jaccard)
    np.fill_diagonal(cost, np.inf)
    pool_size = min(candidate_pool, len(early) - 1)
    rng = np.random.default_rng(seed)
    strangers = np.full((len(early), n_draws), np.nan, dtype=float)
    matched_jaccard = np.full((len(early), n_draws), np.nan, dtype=float)
    matched_numeric = np.full((len(early), n_draws), np.nan, dtype=float)
    for i in range(len(early)):
        eligible = np.flatnonzero(np.isfinite(cost[i]))
        if minimum_condition_jaccard is not None:
            eligible = eligible[jaccard[i, eligible] >= minimum_condition_jaccard]
        if not len(eligible):
            continue
        k = min(pool_size, len(eligible))
        pool = eligible[np.argpartition(cost[i, eligible], k - 1)[:k]]
        pool_cost = cost[i, pool]
        weights = np.exp(-(pool_cost - np.min(pool_cost)))
        weights /= weights.sum()
        picks = rng.choice(pool, size=n_draws, replace=True, p=weights)
        strangers[i] = np.linalg.norm(early[i] - late[picks], axis=1)
        matched_jaccard[i] = jaccard[i, picks]
        matched_numeric[i] = numeric[i, picks]
    valid = np.isfinite(strangers).all(axis=1)
    return strangers, {
        "matched_condition_jaccard": float(np.nanmean(matched_jaccard)) if valid.any() else float("nan"),
        "matched_numeric_opportunity_distance": float(np.nanmean(matched_numeric)) if valid.any() else float("nan"),
        "candidate_pool_max": int(pool_size),
        "minimum_condition_jaccard": minimum_condition_jaccard,
        "condition_caliper_coverage": float(np.mean(valid)),
        "condition_weight": float(condition_weight),
    }


def auc_from_stranger_distances(own: np.ndarray, strangers: np.ndarray, *, seed: int,
                                bootstrap_iterations: int = 200) -> dict[str, float]:
    """Author-bootstrap AUC for precomputed matched stranger distances."""
    from sklearn.metrics import roc_auc_score

    valid = np.isfinite(own) & np.isfinite(strangers).all(axis=1)
    own, strangers = own[valid], strangers[valid]
    if len(own) < 20:
        return {"matched_auc": float("nan"), "matched_auc_ci_lo": float("nan"),
                "matched_auc_ci_hi": float("nan"), "n_matched_users": int(len(own))}

    def score(indices: np.ndarray) -> float:
        positive = own[indices]
        negative = strangers[indices].reshape(-1)
        return float(roc_auc_score(np.r_[np.ones(len(positive)), np.zeros(len(negative))],
                                   -np.r_[positive, negative]))

    base = np.arange(len(own))
    auc = score(base)
    rng = np.random.default_rng(seed)
    bootstrap = np.array([score(rng.integers(0, len(base), len(base)))
                          for _ in range(bootstrap_iterations)])
    lo, hi = np.quantile(bootstrap, [0.025, 0.975])
    return {"matched_auc": auc, "matched_auc_ci_lo": float(lo), "matched_auc_ci_hi": float(hi),
            "n_matched_users": int(len(own))}


def family_matrices(
    name: str,
    frame: pd.DataFrame,
    discovery_users: set[str],
    confirmation_users: set[str],
    cfg: dict,
    seed_offset: int,
) -> dict[str, tuple[np.ndarray, np.ndarray, list[str]]]:
    """Freeze a discovery factor projection and expose full/factor/residual views."""
    cols = [c for c in frame if c.startswith(f"{name}::")]
    de, dl, users_d = paired_views(frame, cols, discovery_users)
    ce, cl, users_c = paired_views(frame, cols, confirmation_users)
    fit = fit_stable_crossview(
        de, dl,
        n_permutations=50 if cfg.get("quick") else cfg["factor_permutations"],
        max_factors=cfg["factor_max_per_family"],
        min_stable_share=cfg["factor_min_stable_share"],
        strata=permutation_strata(frame, users_d),
        seed=cfg["seed"] + seed_offset,
    )
    center, scale = fit.center, fit.scale
    ce_z = (np.where(np.isfinite(ce), ce, center) - center) / scale
    cl_z = (np.where(np.isfinite(cl), cl, center) - center) / scale
    if fit.n_factors:
        factor_early = transform_stable_crossview(ce, fit)
        factor_late = transform_stable_crossview(cl, fit)
        projector = fit.rotated_directions @ np.linalg.pinv(fit.rotated_directions)
        residual_early = ce_z @ (np.eye(ce_z.shape[1]) - projector)
        residual_late = cl_z @ (np.eye(cl_z.shape[1]) - projector)
    else:
        factor_early = np.empty((len(ce_z), 0))
        factor_late = np.empty((len(cl_z), 0))
        residual_early, residual_late = ce_z, cl_z
    return {
        "full": (ce_z, cl_z, users_c),
        "factor": (factor_early, factor_late, users_c),
        "residual": (residual_early, residual_late, users_c),
    }


def audit_view(
    label: str,
    early: np.ndarray,
    late: np.ndarray,
    users: list[str],
    frame: pd.DataFrame,
    condition_sets: dict[tuple[str, str], set[str]],
    cfg: dict,
    seed: int,
) -> list[dict[str, float | str]]:
    """Run an unmatched reference and sensitivity curve of matched negatives."""
    if early.shape[1] == 0:
        return [{"object": label, "control": "not_available", "n_users": len(users)}]
    early_meta, late_meta, meta_cols = paired_metadata(frame, users)
    early_sets = [condition_sets.get((u, "early"), set()) for u in users]
    late_sets = [condition_sets.get((u, "late"), set()) for u in users]
    own = np.linalg.norm(early - late, axis=1)
    unmatched = identity_diagnostics(early, late, seed=seed)
    rows: list[dict[str, float | str]] = [{
        "object": label, "control": "unmatched_deranged", "n_users": len(users),
        "auc": unmatched["own_vs_stranger_auc"], "auc_ci_lo": unmatched["own_vs_stranger_auc_ci_lo"],
        "auc_ci_hi": unmatched["own_vs_stranger_auc_ci_hi"],
        "metadata": ";".join(meta_cols),
    }]
    for weight in (0.0, 0.5, 1.0, 2.0):
        strangers, balance = matched_stranger_distances(
            early, late, early_meta, late_meta, early_sets, late_sets,
            condition_weight=weight, seed=seed + int(weight * 1000) + 17,
        )
        result = auc_from_stranger_distances(own, strangers, seed=seed + int(weight * 1000) + 91)
        rows.append({
            "object": label, "control": f"matched_condition_weight_{weight:g}", "n_users": len(users),
            "auc": result["matched_auc"], "auc_ci_lo": result["matched_auc_ci_lo"],
            "auc_ci_hi": result["matched_auc_ci_hi"], "metadata": ";".join(meta_cols), **balance,
        })
    for caliper in (0.05, 0.10):
        strangers, balance = matched_stranger_distances(
            early, late, early_meta, late_meta, early_sets, late_sets,
            condition_weight=1.0, seed=seed + int(caliper * 10000) + 2017,
            minimum_condition_jaccard=caliper,
        )
        result = auc_from_stranger_distances(own, strangers, seed=seed + int(caliper * 10000) + 2091)
        rows.append({
            "object": label, "control": f"condition_caliper_{caliper:.2f}",
            "n_users": result["n_matched_users"], "auc": result["matched_auc"],
            "auc_ci_lo": result["matched_auc_ci_lo"], "auc_ci_hi": result["matched_auc_ci_hi"],
            "metadata": ";".join(meta_cols), **balance,
        })
    return rows


def main() -> None:
    args = parse_args()
    cfg = json.loads(args.config.read_text())
    cfg["quick"] = args.quick
    comments = pd.read_parquet(args.input, columns=["author", "body", "created_utc", "subreddit"])
    units = prepare_units(comments, cfg)
    users = sorted(units["user_id"].unique())
    discovery_users = {u for u in users if stable_user_split(u) == "discovery"}
    confirmation_users = set(users) - discovery_users
    _, _, representation = fit_representation(units, discovery_users, cfg)
    residual, supported_conditions = crossfit_residuals(units, representation, discovery_users, cfg)
    # The current source audit intentionally holds the opportunity coordinate
    # fixed to the registered surface-profile version from factor discovery.
    from scripts.run_suica_v6_factor_discovery_v2 import opportunity_axis
    z_map, _ = opportunity_axis(units, discovery_users, supported_conditions)
    static, response, dynamic_raw, _ = build_objects(units, residual, z_map, cfg)
    response = conditional_residual(response, [static], "hybrid::", discovery_users)
    dynamic = conditional_residual(dynamic_raw, [static] + ([response] if len(response) else []),
                                   "dynamic::", discovery_users)
    dynamic = dynamic.merge(
        dynamic_raw[["user_id", "half", "dynamic_runs", "dynamic_transitions"]],
        on=["user_id", "half"], how="left",
    )
    condition_sets = author_half_condition_sets(units)

    rows: list[dict[str, float | str]] = []
    for offset, (family, frame) in enumerate((("static", static), ("dynamic", dynamic))):
        matrices = family_matrices(family, frame, discovery_users, confirmation_users, cfg, 1000 * offset)
        for view, (early, late, paired_users) in matrices.items():
            rows.extend(audit_view(f"{family}_{view}", early, late, paired_users, frame,
                                   condition_sets, cfg, cfg["seed"] + 5000 + offset * 100 + len(rows)))
    out = pd.DataFrame(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output_dir / "matched_stranger_audit.csv", index=False)
    supported = out.loc[(out["control"] == "condition_caliper_0.10") &
                        (out["condition_caliper_coverage"] >= 0.80) &
                        (out["auc_ci_lo"] > 0.5), "object"].tolist()
    undecided = out.loc[(out["control"] == "condition_caliper_0.10") &
                        (out["auc_ci_lo"] <= 0.5) & (out["auc_ci_hi"] >= 0.5), "object"].tolist()
    args.report.write_text(f"""# SUICA V6 Residual Source Audit

## Registered question

Can same-author signal survive stranger controls matched on measured opportunity
and community exposure? This audit uses no personality labels. It holds the raw
factor-discovery representation and author split fixed, then compares early text
objects with late stranger objects matched on available metadata and subreddit-set
overlap.

## Result table

{out.to_markdown(index=False, floatfmt='.3f')}

## Decision rule

The `condition_caliper_*` rows match the observed late target to strangers whose
late subreddit set has at least the stated Jaccard overlap. They are sensitivity
analyses, not causal adjustment: coverage and actual overlap are reported. The
weighted nearest-neighbour rows are a screening control. Neither analysis alone
licenses an author-level or personality claim, because the current corpus lacks
within-occasion technical replicates and fixed discovery-calibrated calipers.

The immediate inference is narrower: a signal that collapses under metadata
matching is compatible with an expression-opportunity proxy. A signal that
survives is an **unidentified stable author-path feature** requiring the next,
epoch-and-replicate audit; it is not personality.

### Current classifications

- Survives strongest matching: {', '.join(supported) if supported else 'none'}.
- Undecided after strongest matching: {', '.join(undecided) if undecided else 'none'}.
- This is not a causal adjustment: unmeasured topic semantics, social role,
  identity, and latent opportunity may still explain any surviving signal.

## Dynamic-variable interpretation

Dynamic descriptors represent a candidate unknown variable only if their signal
survives matched strangers. It should then be described mechanically (stable
trajectory configuration, persistence, roughness, variance, or change-point
pattern) until a preregistered repeated-condition human study establishes its
psychological meaning. The audit cannot name it; it can rule out a class of
opportunity explanations.
""")
    print(out.to_string(index=False))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
