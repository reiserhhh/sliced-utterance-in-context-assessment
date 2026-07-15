#!/usr/bin/env python
"""Audit static V6 residuals against increasingly rich opportunity matching.

The V6 raw-factor residualizer already adjusts individual-comment surface
features linearly.  This follow-up asks a narrower, different question: could
the remaining same-author retrieval be explained by *distributional* differences
in visible expression opportunity (format means, format dispersion, or sampling
cadence) that a linear event-level adjustment did not remove?

It uses no external labels and writes only aggregate metrics.  It does not turn
subreddit choice into a nuisance: community overlap is a matched-control
constraint, while selection itself remains part of the natural process.
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
    crossfit_residuals,
    fit_representation,
    opportunity_axis,
    prepare_units,
    stable_user_split,
)
from scripts.run_suica_v6_residual_source_audit import (  # noqa: E402
    auc_from_stranger_distances,
    family_matrices,
    matched_stranger_distances,
)
from suica_core.opportunity_profiles import (  # noqa: E402
    build_opportunity_profiles,
    paired_profile_matrices,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path,
        default=ROOT / "data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet",
        help="Local Tier-U PANDORA parquet; this file is intentionally not in the repository.",
    )
    parser.add_argument("--factor-config", type=Path,
                        default=ROOT / "configs/v6_factor_discovery_raw.json")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/v6_opportunity_profile_audit.json")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/v6_opportunity_profile_audit")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/V6_OPPORTUNITY_PROFILE_AUDIT.md")
    parser.add_argument("--quick", action="store_true",
                        help="Use fewer factor permutations and bootstrap draws for smoke testing only.")
    return parser.parse_args()


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return float(len(left & right) / len(union)) if union else 1.0


def _random_match_baseline(
    early_meta: np.ndarray,
    late_meta: np.ndarray,
    late_sets: list[set[str]],
    valid: np.ndarray,
    *,
    seed: int,
    n_draws: int,
) -> dict[str, float]:
    """Describe random-stranger profile distance for matching-quality QA only.

    This calculation is not a new endpoint or decision rule. It confirms that
    the frozen nearest-pool matcher obtains surface profiles closer than random
    non-self late-author pairings on the same eligible target rows.
    """
    valid_index = np.flatnonzero(valid)
    if len(valid_index) < 2:
        return {
            "random_numeric_opportunity_distance": float("nan"),
            "random_condition_jaccard": float("nan"),
        }
    joint = np.vstack([early_meta, late_meta])
    scale = np.nanstd(joint, axis=0, ddof=1)
    scale[~np.isfinite(scale) | (scale < 1e-8)] = 1.0
    normalized_late = late_meta / scale
    rng = np.random.default_rng(seed)
    random_numeric: list[float] = []
    random_jaccard: list[float] = []
    for index in valid_index:
        candidates = rng.integers(0, len(late_meta) - 1, size=n_draws)
        candidates += candidates >= index
        random_numeric.extend(
            np.sqrt(np.mean((normalized_late[index] - normalized_late[candidates]) ** 2, axis=1)).tolist()
        )
        random_jaccard.extend(_jaccard(late_sets[index], late_sets[candidate]) for candidate in candidates)
    return {
        "random_numeric_opportunity_distance": float(np.mean(random_numeric)),
        "random_condition_jaccard": float(np.mean(random_jaccard)),
    }


def _audit_rows(
    object_name: str,
    early: np.ndarray,
    late: np.ndarray,
    users: list[str],
    profiles: pd.DataFrame,
    condition_sets: dict[tuple[str, str], set[str]],
    spec: dict,
    *,
    seed: int,
) -> list[dict[str, object]]:
    """Generate frozen nested matching rows for one static representation."""
    own = np.linalg.norm(early - late, axis=1)
    early_sets = [condition_sets.get((user, "early"), set()) for user in users]
    late_sets = [condition_sets.get((user, "late"), set()) for user in users]
    rows: list[dict[str, object]] = []
    stages: list[tuple[str, str, float, float | None]] = [
        *( (layer, layer, 0.0, None) for layer in spec["profile_layers"] ),
        ("surface_time_plus_community", "surface_time", float(spec["community_weight"]), None),
        ("surface_time_plus_community_caliper", "surface_time", float(spec["community_weight"]),
         float(spec["strict_condition_jaccard"])),
    ]
    for stage_index, (stage, layer, community_weight, caliper) in enumerate(stages):
        early_meta, late_meta, columns = paired_profile_matrices(profiles, users, layer)
        strangers, balance = matched_stranger_distances(
            early,
            late,
            early_meta,
            late_meta,
            early_sets,
            late_sets,
            condition_weight=community_weight,
            minimum_condition_jaccard=caliper,
            candidate_pool=int(spec["candidate_pool"]),
            n_draws=int(spec["stranger_draws"]),
            seed=seed + 1009 * stage_index,
        )
        result = auc_from_stranger_distances(
            own,
            strangers,
            seed=seed + 1009 * stage_index + 431,
            bootstrap_iterations=int(spec["bootstrap_iterations"]),
        )
        valid = np.isfinite(strangers).all(axis=1)
        baseline = _random_match_baseline(
            early_meta,
            late_meta,
            late_sets,
            valid,
            seed=seed + 1009 * stage_index + 787,
            n_draws=int(spec["stranger_draws"]),
        )
        matched_distance = float(balance["matched_numeric_opportunity_distance"])
        random_distance = float(baseline["random_numeric_opportunity_distance"])
        matched_jaccard = float(balance["matched_condition_jaccard"])
        random_jaccard = float(baseline["random_condition_jaccard"])
        rows.append({
            "object": object_name,
            "stage": stage,
            "profile_layer": layer,
            "n_profile_features": len(columns),
            "profile_features": ";".join(columns),
            "community_weight": community_weight,
            "strict_condition_jaccard": caliper,
            "matched_to_random_profile_distance": (
                matched_distance / random_distance
                if np.isfinite(matched_distance) and np.isfinite(random_distance) and random_distance > 1e-12
                else float("nan")
            ),
            "matched_community_jaccard_lift": (
                matched_jaccard - random_jaccard
                if np.isfinite(matched_jaccard) and np.isfinite(random_jaccard) else float("nan")
            ),
            **balance,
            **baseline,
            **result,
        })
    return rows


def _decision(metrics: pd.DataFrame, spec: dict) -> tuple[str, str]:
    """Apply the preregistered classification to the primary strictest row."""
    row = metrics.loc[
        (metrics["object"] == str(spec["primary_object"]))
        & (metrics["stage"] == "surface_time_plus_community_caliper")
    ]
    if len(row) != 1:
        return "REFUSE_INTERNAL_MISSING_PRIMARY_ROW", "The preregistered primary row was not produced."
    value = row.iloc[0]
    coverage = float(value["condition_caliper_coverage"])
    lo, hi = float(value["matched_auc_ci_lo"]), float(value["matched_auc_ci_hi"])
    if coverage < float(spec["minimum_caliper_coverage"]):
        return (
            "REFUSE_INSUFFICIENT_MATCHED_SUPPORT",
            "The strict community caliper did not retain the preregistered minimum coverage.",
        )
    if lo > 0.5:
        return (
            "SURVIVES_OBSERVED_OPPORTUNITY_PROFILE_SCREEN",
            "The residual is still above chance after all observed profile and community controls.",
        )
    if hi < 0.5:
        return (
            "COMPATIBLE_WITH_OBSERVED_OPPORTUNITY_PROXY",
            "The residual no longer separates same authors after the frozen observed controls.",
        )
    return (
        "UNDECIDED_AFTER_OBSERVED_OPPORTUNITY_SCREEN",
        "The strict matched estimate overlaps chance; this does not prove a null or a causal source.",
    )


def _report(metrics: pd.DataFrame, decision: str, rationale: str, provenance: dict[str, object]) -> str:
    table_columns = [
        "object", "stage", "n_matched_users", "matched_auc", "matched_auc_ci_lo", "matched_auc_ci_hi",
        "condition_caliper_coverage", "matched_condition_jaccard",
        "matched_numeric_opportunity_distance", "matched_to_random_profile_distance",
        "matched_community_jaccard_lift", "n_profile_features",
    ]
    display = metrics.loc[:, table_columns].copy()
    return f"""# SUICA V6 Opportunity-Profile Source Audit

## Question

The raw V6 static residualizer already models individual-comment surface features
linearly. This frozen follow-up asks whether its residual same-author signal
survives stranger matching on progressively richer **observable opportunity
profiles**: text amount, format means, format dispersion, sampling cadence, and
finally observed-community overlap. It is a label-free source audit, not a
personality, causal, or denoising result.

## Data and boundaries

- technical raw units after the existing explicit personality-report guard: `{provenance['n_units']:,}`
- confirmation authors represented in the static object: `{provenance['n_confirmation_authors']:,}`
- external labels read: `False`
- raw text, author identifiers, embeddings, and profile rows persisted: `False`
- source path is local and is not included in this release.

Subreddit selection is not subtracted as nuisance. It appears only as a late-target
matched-control constraint, because selection is part of an author's natural text
process. The audit cannot control exact topic semantics, social role, identity,
editing behavior, or unrecorded opportunity.

## Frozen nested controls

1. `coarse`: selected comment count and selected condition count.
2. `surface_mean`: coarse controls plus the mean of ten observed format variables.
3. `surface_distribution`: mean controls plus within-view format dispersion.
4. `surface_time`: distribution controls plus span, median/max gap, and long-run support.
5. `surface_time_plus_community`: the preceding numeric profile plus soft community-set matching.
6. `surface_time_plus_community_caliper`: the same, requiring subreddit-set Jaccard
   `>= {provenance['strict_condition_jaccard']:.2f}`. This is the primary row.

## Results

{display.to_markdown(index=False, floatfmt='.3f')}

## Registered decision

**{decision}** — {rationale}

The decision applies only to `{provenance['primary_object']}`. It is accepted only
when the strict caliper retains at least `{provenance['minimum_caliper_coverage']:.0%}`
of the eligible confirmation authors and its bootstrap lower bound exceeds `.50`.
It does not establish that the remaining signal is a trait, a psychological
construct, a causal response parameter, or an independent occasion effect.

## Post-run matching-quality QA

`matched_to_random_profile_distance` and
`matched_community_jaccard_lift` are post-run quality diagnostics added after
the primary endpoint was fixed. They do not change the decision rule. A profile
distance ratio below `1` means that the nearest-pool procedure found surface
profiles closer than random non-self late-author pairings; a positive Jaccard
lift means it also increased community overlap relative to random pairings.

## Interpretation rule

- A collapse is compatible with an **observed opportunity proxy**; it is not proof
  that one profile variable caused the earlier signal.
- Survival is an **unknown stable author configuration after this observed screen**;
  it remains confounded with unmeasured topic, role, identity, and long-term writing
  habit.
- Dynamic objects are deliberately absent: the current PANDORA corpus cannot meet
  the registered epoch-by-technical-replica design needed to attribute dynamic
  differences to an author parameter rather than persistent state.
"""


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise FileNotFoundError(
            f"Missing local Tier-U input: {args.input}. Pass --input with a locally prepared PANDORA file; do not copy data into the repository."
        )
    cfg = json.loads(args.factor_config.read_text())
    cfg["quick"] = bool(args.quick)
    spec = json.loads(args.config.read_text())
    if args.quick:
        spec = {**spec, "bootstrap_iterations": 99}

    comments = pd.read_parquet(args.input, columns=["author", "body", "created_utc", "subreddit"])
    units = prepare_units(comments, cfg)
    users = sorted(units["user_id"].unique())
    discovery_users = {user for user in users if stable_user_split(user) == "discovery"}
    confirmation_users = set(users) - discovery_users
    _, _, representation = fit_representation(units, discovery_users, cfg)
    residual, supported_conditions = crossfit_residuals(units, representation, discovery_users, cfg)
    z_map, _ = opportunity_axis(units, discovery_users, supported_conditions)
    static, _, _, _ = build_objects(units, residual, z_map, cfg)
    profiles, condition_sets = build_opportunity_profiles(units)

    rows: list[dict[str, object]] = []
    for index, (view, early, late, aligned_users) in enumerate(
        (name, *values) for name, values in family_matrices(
            "static", static, discovery_users, confirmation_users, cfg, 17000
        ).items()
    ):
        rows.extend(_audit_rows(
            f"static_{view}", early, late, aligned_users, profiles, condition_sets, spec,
            seed=int(spec["seed"]) + index * 5000,
        ))
    metrics = pd.DataFrame(rows)
    decision, rationale = _decision(metrics, spec)
    provenance = {
        "n_units": int(len(units)),
        "n_confirmation_authors": int(len(confirmation_users)),
        "primary_object": str(spec["primary_object"]),
        "strict_condition_jaccard": float(spec["strict_condition_jaccard"]),
        "minimum_caliper_coverage": float(spec["minimum_caliper_coverage"]),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "opportunity_profile_metrics.csv", index=False)
    (args.output_dir / "manifest.json").write_text(json.dumps({
        "spec": spec,
        "factor_config": cfg,
        "provenance": provenance,
        "decision": decision,
        "decision_rationale": rationale,
        "external_labels_read": False,
        "raw_text_persisted": False,
        "author_ids_persisted": False,
    }, indent=2, sort_keys=True) + "\n")
    args.report.write_text(_report(metrics, decision, rationale, provenance))
    print(metrics.to_string(index=False))
    print(f"decision={decision}")
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
