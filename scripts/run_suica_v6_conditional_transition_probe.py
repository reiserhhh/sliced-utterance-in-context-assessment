#!/usr/bin/env python
"""Screen a nonlinear conditional transition object in SUICA V6 residual paths.

The estimator is deliberately narrower than an individual dynamics model.  A
pooled transition law is frozen from discovery authors; unseen confirmation
authors are represented by their equal-run-weighted residual kernel embeddings.
The primary null preserves each run's observations and endpoints while destroying
interior order.  This can screen for order-sensitive path information, but cannot
identify personality, persistent state, or a person-specific operator in PANDORA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v6_factor_discovery_v2 import (  # noqa: E402
    Q_COLS,
    crossfit_residuals,
    fit_representation,
    identity_diagnostics,
    prepare_units,
)
from scripts.run_suica_v6_path_signature_probe import paired_auc_delta  # noqa: E402
from scripts.run_suica_v6_residual_source_audit import (  # noqa: E402
    auc_from_stranger_distances,
    author_half_condition_sets,
    matched_stranger_distances,
    paired_metadata,
)
from suica_core.conditional_transition import fit_conditional_transition_model  # noqa: E402
from suica_core.factor_discovery import stable_user_split  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / "data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/v6_factor_discovery_raw.json")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/v6_conditional_transition_probe")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/V6_CONDITIONAL_TRANSITION_PROBE.md")
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _shuffle_indices(length: int, seed_key: str) -> np.ndarray:
    """Return an endpoint-preserving permutation for one complete text run."""
    indices = np.arange(length)
    if length <= 3:
        return indices
    digest = hashlib.sha256(seed_key.encode()).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    indices[1:-1] = indices[1:-1][rng.permutation(length - 2)]
    return indices


def build_transitions(
    units: pd.DataFrame,
    coordinates: np.ndarray,
    cfg: dict,
    *,
    shuffled: bool,
) -> pd.DataFrame:
    """Build valid within-run one-step transitions without bridging text gaps."""
    work = units[["user_id", "half", "condition", "run_id", "run_pos", "created_utc", "order", *Q_COLS]].copy()
    work["coord_0"] = coordinates[:, 0]
    work["coord_1"] = coordinates[:, 1]
    history_cols = ["coord_0", "coord_1", *Q_COLS]
    rows: list[dict[str, float | str]] = []
    for (user, half, run_id), run in work.groupby(["user_id", "half", "run_id"], observed=True, sort=False):
        run = run.sort_values("run_pos").reset_index(drop=True)
        position = run["run_pos"].to_numpy(int)
        if (len(run) < cfg["dynamic_min_run_length"] or not np.all(np.diff(position) == 1)):
            continue
        if shuffled:
            run = run.iloc[_shuffle_indices(len(run), f"ckte-null::{user}::{half}::{run_id}")].reset_index(drop=True)
        values = run[history_cols].to_numpy(float)
        for index in range(len(run) - 1):
            current, following = values[index], values[index + 1]
            history = np.r_[current, following[2:], index / max(1, len(run) - 1)]
            row: dict[str, float | str] = {
                "user_id": str(user),
                "half": str(half),
                "run_id": str(run_id),
                "condition": str(run.loc[index, "condition"]),
            }
            row.update({f"history_{j:02d}": float(value) for j, value in enumerate(history)})
            row.update({f"outcome_{j:02d}": float(value) for j, value in enumerate(following[:2])})
            rows.append(row)
    return pd.DataFrame(rows)


def aggregate_author_embeddings(
    transitions: pd.DataFrame,
    model,
    units: pd.DataFrame,
    cfg: dict,
    *,
    include_users: set[str],
) -> pd.DataFrame:
    """Estimate equal-run-weighted conditional-transition deviations per author half."""
    work = transitions.loc[transitions["user_id"].isin(include_users)].copy()
    if work.empty:
        return pd.DataFrame()
    history_cols = sorted(c for c in work if c.startswith("history_"))
    outcome_cols = sorted(c for c in work if c.startswith("outcome_"))
    embedding = model.residual_embedding(
        work[history_cols].to_numpy(float), work[outcome_cols].to_numpy(float)
    )
    for index in range(embedding.shape[1]):
        work[f"ckte_{index:03d}"] = embedding[:, index]
    ckte_cols = [c for c in work if c.startswith("ckte_")]
    run = work.groupby(["user_id", "half", "run_id"], observed=True)[ckte_cols].mean().reset_index()
    transitions_per_half = work.groupby(["user_id", "half"], observed=True).size().rename("dynamic_transitions")
    result = run.groupby(["user_id", "half"], observed=True)[ckte_cols].mean().reset_index()
    result = result.merge(
        run.groupby(["user_id", "half"], observed=True).size().rename("dynamic_runs").reset_index(),
        on=["user_id", "half"], how="left",
    ).merge(transitions_per_half.reset_index(), on=["user_id", "half"], how="left")
    result = result.loc[
        (result["dynamic_runs"] >= cfg["dynamic_min_runs"])
        & (result["dynamic_transitions"] >= cfg["dynamic_min_transitions"])
    ].copy()
    meta = (units.loc[units["user_id"].isin(include_users)]
            .groupby(["user_id", "half"], observed=True)
            .agg(meta_comments=("text", "size"), meta_conditions=("condition", "nunique"))
            .reset_index())
    return result.merge(meta, on=["user_id", "half"], how="left")


def paired_embeddings(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Align early and late author embeddings with a fixed embedding coordinate order."""
    cols = sorted(c for c in frame if c.startswith("ckte_"))
    early = frame.loc[frame["half"].eq("early")].set_index("user_id")
    late = frame.loc[frame["half"].eq("late")].set_index("user_id")
    users = sorted(set(early.index) & set(late.index))
    return early.loc[users, cols].to_numpy(float), late.loc[users, cols].to_numpy(float), users


def evaluate_order_effect(
    ordered: pd.DataFrame,
    shuffled: pd.DataFrame,
    units: pd.DataFrame,
    cfg: dict,
    *,
    bootstrap_iterations: int,
) -> tuple[dict, pd.DataFrame]:
    """Compare true transition embeddings to the endpoint-preserving order null."""
    early, late, users = paired_embeddings(ordered)
    null_early, null_late, null_users = paired_embeddings(shuffled)
    if users != null_users:
        raise RuntimeError("ordered and shuffled transition eligibility must agree")
    condition_sets = author_half_condition_sets(units)
    early_meta, late_meta, metadata = paired_metadata(ordered, users)
    early_sets = [condition_sets.get((user, "early"), set()) for user in users]
    late_sets = [condition_sets.get((user, "late"), set()) for user in users]
    own = np.linalg.norm(early - late, axis=1)
    null_own = np.linalg.norm(null_early - null_late, axis=1)
    unmatched = identity_diagnostics(early, late, seed=cfg["seed"] + 1301)
    null_unmatched = identity_diagnostics(null_early, null_late, seed=cfg["seed"] + 1301)
    matching_specs = [
        ("weighted_opportunity", 2.0, None),
        ("condition_caliper_0.05", 1.0, 0.05),
        ("condition_caliper_0.10", 1.0, 0.10),
    ]
    matching_results: dict[str, dict] = {}
    summary_rows: list[dict[str, float | str]] = []
    for index, (name, weight, minimum_jaccard) in enumerate(matching_specs):
        strangers, balance = matched_stranger_distances(
            early, late, early_meta, late_meta, early_sets, late_sets,
            condition_weight=weight, seed=cfg["seed"] + 1303 + index,
            minimum_condition_jaccard=minimum_jaccard,
        )
        null_strangers, _ = matched_stranger_distances(
            null_early, null_late, early_meta, late_meta, early_sets, late_sets,
            condition_weight=weight, seed=cfg["seed"] + 1303 + index,
            minimum_condition_jaccard=minimum_jaccard,
        )
        matched = auc_from_stranger_distances(
            own, strangers, seed=cfg["seed"] + 1307 + index,
            bootstrap_iterations=bootstrap_iterations,
        )
        null_matched = auc_from_stranger_distances(
            null_own, null_strangers, seed=cfg["seed"] + 1307 + index,
            bootstrap_iterations=bootstrap_iterations,
        )
        order_delta = paired_auc_delta(
            own, strangers, null_own, null_strangers,
            seed=cfg["seed"] + 1311 + index, iterations=bootstrap_iterations,
        )
        matching_results[name] = {
            "ordered_matched": {**matched, **balance},
            "shuffled_matched": null_matched,
            "order_effect": order_delta,
        }
        for variant, metric in (
            ("conditional_transition_embedding", matched),
            ("endpoint_preserving_order_shuffle", null_matched),
            ("ordered_minus_shuffled", order_delta),
        ):
            if variant == "ordered_minus_shuffled":
                key, lo_key, hi_key = "order_delta_auc", "order_delta_ci_lo", "order_delta_ci_hi"
            else:
                key, lo_key, hi_key = "matched_auc", "matched_auc_ci_lo", "matched_auc_ci_hi"
            summary_rows.append({"variant": variant, "control": name,
                                 "auc": metric[key], "ci_lo": metric[lo_key], "ci_hi": metric[hi_key]})
    primary = matching_results["weighted_opportunity"]
    summary = pd.DataFrame([
        {"variant": "conditional_transition_embedding", "control": "unmatched",
         "auc": unmatched["own_vs_stranger_auc"], "ci_lo": unmatched["own_vs_stranger_auc_ci_lo"],
         "ci_hi": unmatched["own_vs_stranger_auc_ci_hi"]},
        {"variant": "endpoint_preserving_order_shuffle", "control": "unmatched",
         "auc": null_unmatched["own_vs_stranger_auc"], "ci_lo": null_unmatched["own_vs_stranger_auc_ci_lo"],
         "ci_hi": null_unmatched["own_vs_stranger_auc_ci_hi"]},
        *summary_rows,
    ])
    return {
        "n_paired_confirmation_authors": len(users),
        "metadata": metadata,
        "ordered_unmatched": unmatched,
        "shuffled_unmatched": null_unmatched,
        "ordered_matched": primary["ordered_matched"],
        "shuffled_matched": primary["shuffled_matched"],
        "order_effect": primary["order_effect"],
        "matching_sensitivity": matching_results,
    }, summary


def main() -> None:
    args = parse_args()
    cfg = json.loads(args.config.read_text())
    cfg["quick"] = args.quick
    bootstrap_iterations = 199 if args.quick else 999
    input_features = 48 if args.quick else 128
    output_features = 32 if args.quick else 64
    comments = pd.read_parquet(args.input, columns=["author", "body", "created_utc", "subreddit"])
    units = prepare_units(comments, cfg)
    users = sorted(units["user_id"].unique())
    discovery_users = {user for user in users if stable_user_split(user) == "discovery"}
    confirmation_users = set(users) - discovery_users
    _, _, representation = fit_representation(units, discovery_users, cfg)
    residual, _ = crossfit_residuals(units, representation, discovery_users, cfg)
    from sklearn.decomposition import PCA

    discovery_mask = units["user_id"].isin(discovery_users).to_numpy()
    pca = PCA(n_components=2, random_state=cfg["seed"]).fit(residual[discovery_mask])
    coordinates = pca.transform(residual)
    ordered_transitions = build_transitions(units, coordinates, cfg, shuffled=False)
    shuffled_transitions = build_transitions(units, coordinates, cfg, shuffled=True)
    history_cols = sorted(c for c in ordered_transitions if c.startswith("history_"))
    outcome_cols = sorted(c for c in ordered_transitions if c.startswith("outcome_"))
    discovery_transition_mask = ordered_transitions["user_id"].isin(discovery_users).to_numpy()
    model = fit_conditional_transition_model(
        ordered_transitions.loc[discovery_transition_mask, history_cols].to_numpy(float),
        ordered_transitions.loc[discovery_transition_mask, outcome_cols].to_numpy(float),
        input_features=input_features,
        output_features=output_features,
        ridge_alpha=10.0,
        seed=cfg["seed"] + 1201,
    )
    ordered = aggregate_author_embeddings(
        ordered_transitions, model, units, cfg, include_users=confirmation_users,
    )
    shuffled = aggregate_author_embeddings(
        shuffled_transitions, model, units, cfg, include_users=confirmation_users,
    )
    results, summary = evaluate_order_effect(
        ordered, shuffled, units, cfg, bootstrap_iterations=bootstrap_iterations,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    ordered.to_csv(args.output_dir / "ordered_confirmation_embeddings.csv", index=False)
    shuffled.to_csv(args.output_dir / "shuffled_confirmation_embeddings.csv", index=False)
    ordered_transitions.loc[ordered_transitions["user_id"].isin(confirmation_users)].to_parquet(
        args.output_dir / "ordered_confirmation_transitions.parquet", index=False,
    )
    summary.to_csv(args.output_dir / "conditional_transition_summary.csv", index=False)
    result = {
        "run": "SUICA_V6_CONDITIONAL_TRANSITION_PROBE_V1",
        "labels_used": False,
        "n_comments": int(len(comments)),
        "n_sampled_comments": int(len(units)),
        "n_discovery_authors": int(len(discovery_users)),
        "n_confirmation_authors": int(len(confirmation_users)),
        "n_discovery_transitions": int(discovery_transition_mask.sum()),
        "n_confirmation_transitions": int((~discovery_transition_mask).sum()),
        "history_order": 1,
        "history_components": [
            "residual_coordinate_t",
            "surface_opportunity_t_and_t_plus_1",
            "within_run_progress",
            "condition_conditioned_in_upstream_residualization",
        ],
        "input_rff_features": input_features,
        "output_rff_features": output_features,
        "ridge_alpha": 10.0,
        "input_bandwidth": model.input_map.bandwidth,
        "output_bandwidth": model.output_map.bandwidth,
        "pca_explained_variance": pca.explained_variance_ratio_.tolist(),
        "bootstrap_iterations": bootstrap_iterations,
        **results,
        "interpretation": (
            "This is a confirmation-author screen for order-sensitive deviations from a pooled "
            "conditional transition distribution. It is not an estimated person-specific "
            "transition operator and cannot distinguish personality from persistent state, "
            "unobserved opportunity, social role, or scorer error in PANDORA."
        ),
    }
    (args.output_dir / "conditional_transition_probe.json").write_text(json.dumps(result, indent=2) + "\n")
    delta = results["order_effect"]
    verdict = (
        "The exploratory order-sensitive screen is positive, but not a construct claim."
        if delta["order_delta_ci_lo"] > 0
        else "The exploratory order-sensitive screen is not supported by this PANDORA split."
    )
    args.report.write_text(f"""# SUICA V6 Conditional Kernel Transition Probe

## Frozen mathematical object

Let `X` be the two-dimensional, discovery-fitted opportunity-conditioned residual
path and let `H_t = (X_t, Q_t, Q_(t+1), progress_t)`. A Gaussian output kernel
embeds the conditional next-state law:

\\[
\\mu_0(h)=\\mathbb{{E}}[\\ell(X_{{t+1}},\\cdot)\\mid H_t=h].
\\]

The pooled approximation `mu_0` is trained only on discovery authors. For an
unseen confirmation author-half, the measured object is the equal-run-weighted
conditional residual embedding:

\\[
\\widehat G_{{u,h}}=
\\frac{{1}}{{|R_{{u,h}}|}}\\sum_{{r\\in R_{{u,h}}}}
\\frac{{1}}{{m_r-1}}\\sum_{{t=1}}^{{m_r-1}}
\\left[\\phi(X_{{t+1}})-\\widehat\\mu_0(H_t)\\right].
\\]

Because the Gaussian kernel is characteristic in its infinite-dimensional limit,
this object is sensitive in principle to conditional mean, variance, skewness,
multimodality, and nonlinear switching. The present `output_rff_features={output_features}`
implementation is a finite, regularized approximation.

## Frozen evaluation protocol

- Representation, nuisance residualization, PCA, and pooled transition law fit:
  discovery authors only.
- Identity evaluation: held-out confirmation authors only.
- Runs are complete consecutive same-subreddit sequences; no transition crosses a
  run, condition, or sampling gap.
- Null: shuffle each run's interior observations jointly while preserving endpoints,
  run membership, and observation multiset.
- No Big Five, MBTI, other questionnaire labels, or author identifiers enter model fitting.

## Results

{summary.to_markdown(index=False, floatfmt='.3f')}

## Result status

{verdict}

The matched order delta is `{delta['order_delta_auc']:.4f}` with bootstrap interval
`[{delta['order_delta_ci_lo']:.4f}, {delta['order_delta_ci_hi']:.4f}]` across
`{results['n_paired_confirmation_authors']}` paired confirmation authors.

## Limits that remain non-negotiable

This does **not** identify a stable author operator `G_u`. PANDORA lacks the
registered `epoch x independent technical replica` structure: a stable author
parameter and a persistent state can generate the same observed transition law.
The matched-stranger procedure is a sensitivity analysis, not causal adjustment.
The current bootstrap is an exploratory uncertainty estimate, not the 1,999
stratified permutation/max-T confirmation protocol required before selecting among
kernel families, history lengths, or hyperparameters.
""")
    print(json.dumps(result, indent=2))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
