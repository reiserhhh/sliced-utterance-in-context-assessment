#!/usr/bin/env python
"""Probe a non-axis geometric object in opportunity-conditioned text paths.

The probe represents each complete within-subreddit comment run as a
time-augmented, normalized path in residual text space and computes its truncated
path signature.  It asks whether ordered path geometry contains same-author
information beyond endpoints and a shuffled-order null.  It is a screening test,
not an individual-dynamics estimator: the PANDORA epoch x technical-replica audit
already establishes that this corpus cannot separate persistent state from a
stable author parameter at the registered resolution.
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
    crossfit_residuals,
    fit_representation,
    identity_diagnostics,
    prepare_units,
)
from scripts.run_suica_v6_residual_source_audit import (  # noqa: E402
    auc_from_stranger_distances,
    author_half_condition_sets,
    matched_stranger_distances,
    paired_metadata,
)
from suica_core.factor_discovery import stable_user_split  # noqa: E402
from suica_core.path_signature import piecewise_linear_signature, signature_dimension, time_augmented_shape_path  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / "data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/v6_factor_discovery_raw.json")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/v6_path_signature_probe")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/V6_PATH_SIGNATURE_PROBE.md")
    parser.add_argument("--evaluation-cohort", choices=("all", "confirmation"), default="all",
                        help="Evaluate all eligible authors or only author-disjoint confirmation users.")
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _shuffle_interior(path: np.ndarray, seed_key: str) -> np.ndarray:
    """Destroy order while preserving each run's endpoints and point cloud."""
    if len(path) <= 3:
        return path.copy()
    digest = hashlib.sha256(seed_key.encode()).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    output = path.copy()
    output[1:-1] = output[1:-1][rng.permutation(len(output) - 2)]
    return output


def signature_author_halves(
    units: pd.DataFrame,
    coordinates: np.ndarray,
    cfg: dict,
    *,
    shuffled: bool,
    depth: int = 3,
) -> pd.DataFrame:
    """Aggregate equal-weight whole-run signatures into user-half feature vectors."""
    work = units[["user_id", "half", "condition", "run_id", "run_pos", "created_utc", "order"]].copy()
    for j in range(coordinates.shape[1]):
        work[f"coord_{j}"] = coordinates[:, j]
    coord_cols = [f"coord_{j}" for j in range(coordinates.shape[1])]
    rows: list[dict[str, float | str]] = []
    for (user, half), group in work.groupby(["user_id", "half"], observed=True, sort=False):
        signatures: list[np.ndarray] = []
        scales: list[float] = []
        transitions = 0
        for run_id, run in group.groupby("run_id", observed=True, sort=False):
            run = run.sort_values("run_pos")
            positions = run["run_pos"].to_numpy(int)
            if len(run) < cfg["dynamic_min_run_length"] or not np.all(np.diff(positions) == 1):
                continue
            spatial = run[coord_cols].to_numpy(float)
            path, scale = time_augmented_shape_path(spatial, normalize_shape=True)
            if shuffled:
                path = _shuffle_interior(path, f"signature-null::{user}::{half}::{run_id}")
            signatures.append(piecewise_linear_signature(path, depth=depth))
            scales.append(scale)
            transitions += len(run) - 1
        if len(signatures) < cfg["dynamic_min_runs"] or transitions < cfg["dynamic_min_transitions"]:
            continue
        signature = np.mean(np.vstack(signatures), axis=0)
        row: dict[str, float | str] = {
            "user_id": str(user), "half": str(half), "dynamic_runs": len(signatures),
            "dynamic_transitions": transitions, "meta_comments": len(group),
            "meta_conditions": int(group["condition"].nunique()),
            "meta_log_path_scale": float(np.mean(np.log1p(scales))),
        }
        row.update({f"signature_{i:02d}": float(value) for i, value in enumerate(signature)})
        rows.append(row)
    return pd.DataFrame(rows)


def paired_features(frame: pd.DataFrame, *, depth: int) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Return paired signatures truncated at an explicitly requested degree."""
    n_features = signature_dimension(3, depth)
    cols = [f"signature_{index:02d}" for index in range(n_features)]
    early = frame.loc[frame["half"].eq("early")].set_index("user_id")
    late = frame.loc[frame["half"].eq("late")].set_index("user_id")
    users = sorted(set(early.index) & set(late.index))
    return early.loc[users, cols].to_numpy(float), late.loc[users, cols].to_numpy(float), users


def _auc(own: np.ndarray, stranger: np.ndarray, indices: np.ndarray) -> float:
    from sklearn.metrics import roc_auc_score

    positive = own[indices]
    negative = stranger[indices].reshape(-1)
    return float(roc_auc_score(np.r_[np.ones(len(positive)), np.zeros(len(negative))],
                               -np.r_[positive, negative]))


def paired_auc_delta(
    own_ordered: np.ndarray,
    stranger_ordered: np.ndarray,
    own_null: np.ndarray,
    stranger_null: np.ndarray,
    *,
    seed: int,
    iterations: int = 500,
) -> dict[str, float]:
    """Author-bootstrap increase in matched AUC caused by retaining path order."""
    valid = (np.isfinite(own_ordered) & np.isfinite(own_null)
             & np.isfinite(stranger_ordered).all(axis=1) & np.isfinite(stranger_null).all(axis=1))
    own_ordered, stranger_ordered = own_ordered[valid], stranger_ordered[valid]
    own_null, stranger_null = own_null[valid], stranger_null[valid]
    if len(own_ordered) < 20:
        return {"order_delta_auc": float("nan"), "order_delta_ci_lo": float("nan"),
                "order_delta_ci_hi": float("nan"), "n_users": int(len(own_ordered))}
    base = np.arange(len(own_ordered))
    delta = _auc(own_ordered, stranger_ordered, base) - _auc(own_null, stranger_null, base)
    rng = np.random.default_rng(seed)
    boot_values = []
    for _ in range(iterations):
        indices = rng.integers(0, len(base), len(base))
        boot_values.append(_auc(own_ordered, stranger_ordered, indices)
                           - _auc(own_null, stranger_null, indices))
    boot = np.asarray(boot_values)
    lo, hi = np.quantile(boot, [0.025, 0.975])
    return {"order_delta_auc": float(delta), "order_delta_ci_lo": float(lo),
            "order_delta_ci_hi": float(hi), "n_users": int(len(base))}


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
    residual, _ = crossfit_residuals(units, representation, discovery_users, cfg)
    from sklearn.decomposition import PCA
    discovery_mask = units["user_id"].isin(discovery_users).to_numpy()
    pca = PCA(n_components=2, random_state=cfg["seed"]).fit(residual[discovery_mask])
    coordinates = pca.transform(residual)

    ordered = signature_author_halves(units, coordinates, cfg, shuffled=False)
    shuffled = signature_author_halves(units, coordinates, cfg, shuffled=True)
    if args.evaluation_cohort == "confirmation":
        ordered = ordered.loc[ordered["user_id"].isin(confirmation_users)].copy()
        shuffled = shuffled.loc[shuffled["user_id"].isin(confirmation_users)].copy()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    ordered.to_csv(args.output_dir / "ordered_signatures.csv", index=False)
    shuffled.to_csv(args.output_dir / "shuffled_signatures.csv", index=False)
    condition_sets = author_half_condition_sets(units)
    depth_results: dict[str, dict] = {}
    summary_rows: list[dict[str, float | str | int]] = []
    metadata_columns: list[str] = []
    n_paired_authors = 0
    for depth in (1, 2, 3):
        early, late, paired_users = paired_features(ordered, depth=depth)
        null_early, null_late, null_users = paired_features(shuffled, depth=depth)
        if paired_users != null_users:
            raise RuntimeError("ordered and shuffled path eligibility must agree")
        early_meta, late_meta, meta_cols = paired_metadata(ordered, paired_users)
        early_sets = [condition_sets.get((user, "early"), set()) for user in paired_users]
        late_sets = [condition_sets.get((user, "late"), set()) for user in paired_users]
        own = np.linalg.norm(early - late, axis=1)
        null_own = np.linalg.norm(null_early - null_late, axis=1)
        unmatched = identity_diagnostics(early, late, seed=cfg["seed"] + 701)
        null_unmatched = identity_diagnostics(null_early, null_late, seed=cfg["seed"] + 701)
        strangers, balance = matched_stranger_distances(
            early, late, early_meta, late_meta, early_sets, late_sets,
            condition_weight=2.0, seed=cfg["seed"] + 703,
        )
        null_strangers, _ = matched_stranger_distances(
            null_early, null_late, early_meta, late_meta, early_sets, late_sets,
            condition_weight=2.0, seed=cfg["seed"] + 703,
        )
        matched = auc_from_stranger_distances(own, strangers, seed=cfg["seed"] + 709)
        null_matched = auc_from_stranger_distances(null_own, null_strangers, seed=cfg["seed"] + 709)
        order_delta = paired_auc_delta(own, strangers, null_own, null_strangers,
                                       seed=cfg["seed"] + 719)
        depth_results[f"depth_{depth}"] = {
            "signature_dimension": signature_dimension(3, depth),
            "ordered_unmatched": unmatched,
            "shuffled_unmatched": null_unmatched,
            "ordered_matched": {**matched, **balance},
            "shuffled_matched": null_matched,
            "order_effect": order_delta,
        }
        for variant, control, metric in (
            ("ordered_signature", "unmatched", unmatched),
            ("ordered_signature", "opportunity_matched", matched),
            ("shuffled_order_null", "unmatched", null_unmatched),
            ("shuffled_order_null", "opportunity_matched", null_matched),
            ("ordered_minus_shuffled", "opportunity_matched", order_delta),
        ):
            if variant == "ordered_minus_shuffled":
                key, lo_key, hi_key = "order_delta_auc", "order_delta_ci_lo", "order_delta_ci_hi"
            elif control == "opportunity_matched":
                key, lo_key, hi_key = "matched_auc", "matched_auc_ci_lo", "matched_auc_ci_hi"
            else:
                key, lo_key, hi_key = (
                    "own_vs_stranger_auc",
                    "own_vs_stranger_auc_ci_lo",
                    "own_vs_stranger_auc_ci_hi",
                )
            summary_rows.append({
                "signature_depth": depth,
                "signature_dimension": signature_dimension(3, depth),
                "variant": variant,
                "control": control,
                "auc": metric[key],
                "ci_lo": metric[lo_key],
                "ci_hi": metric[hi_key],
            })
        metadata_columns = meta_cols
        n_paired_authors = len(paired_users)
    summary = pd.DataFrame(summary_rows)
    result = {
        "run": "SUICA_V6_PATH_SIGNATURE_PROBE_V2",
        "n_comments": int(len(comments)), "n_sampled_comments": int(len(units)),
        "n_discovery_authors": int(len(discovery_users)),
        "n_confirmation_authors": int(len(confirmation_users)),
        "evaluation_cohort": args.evaluation_cohort,
        "n_paired_authors": int(n_paired_authors), "signature_depths": [1, 2, 3],
        "pca_dimensions": 2, "pca_explained_variance": pca.explained_variance_ratio_.tolist(),
        "metadata": metadata_columns, "by_depth": depth_results,
        "labels_used": False,
        "interpretation": (
            "A positive order delta only shows that the chosen truncated path geometry "
            "contains same-author information beyond an endpoint-preserving shuffle. "
            "It does not identify a personality trait or separate stable author dynamics "
            "from persistent state in this corpus."
        ),
    }
    (args.output_dir / "path_signature_probe.json").write_text(json.dumps(result, indent=2) + "\n")
    summary.to_csv(args.output_dir / "path_signature_summary.csv", index=False)
    math_formula = r"""\[
S_{\le3}(X)=\left(\int dX,\ \int_{t_1<t_2}dX_{t_1}\otimes dX_{t_2},
\int_{t_1<t_2<t_3}dX_{t_1}\otimes dX_{t_2}\otimes dX_{t_3}\right).
\]"""
    args.report.write_text(rf"""# SUICA V6 Path-Signature Geometry Probe

## Mathematical object

For each complete same-condition run, let \(X=(x_0,\ldots,x_n)\) be the
time-augmented, within-run normalized residual path in \(\mathbb{{R}}^3\): time
plus two discovery-only residual PCA coordinates. Its degree-three signature is

{math_formula}

Whole-run signatures are averaged within author-half. This is a geometric path
object, not a rotated factor catalog. Degree one is endpoint displacement only;
degree two adds ordered pair interactions (including signed area / cross-coordinate
coupling); degree three adds ordered triple interactions (turning and sequence
asymmetry). The endpoint-preserving shuffle is therefore expected to leave degree
one unchanged and can only be beaten by higher-order ordered geometry.

## Results

{summary.to_markdown(index=False, floatfmt='.3f')}

## Boundary

The full time-augmented signature has strong path-uniqueness properties under
bounded variation; these finite truncations do not. No materiality threshold was
preregistered for this exploratory screen. A future confirmation should freeze one
degree and require a matched `ordered_minus_shuffled` lower confidence bound above
zero, a predeclared practical margin, leave-one-community-out survival, and formal
familywise control. The PANDORA epoch x technical-replica feasibility audit leaves
stable-author dynamics versus persistent state unidentifiable, so no personality or
author-parameter claim is made.
""")
    print(json.dumps(result, indent=2))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
