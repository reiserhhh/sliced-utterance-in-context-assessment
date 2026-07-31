#!/usr/bin/env python3
"""Run the opened-panel nested information-budget mechanism experiment."""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from itertools import combinations
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v8_event_set_composition_knockout import (  # noqa: E402
    build_event_tensor,
)
from suica_core.v8_exchangeable_background_audit import (  # noqa: E402
    exchangeable_set_reallocation,
)
from suica_core.v8_marginal_background_quotient import (  # noqa: E402
    FrozenMarginalBackground,
    MarginalQuotientSpec,
    fit_marginal_background,
    quotient_blocks,
    quotient_views,
    tensor_feature_blocks,
)
from suica_core.v8_nested_information_budget import (  # noqa: E402
    NestedInformationBudgetSpec,
    nested_event_indices,
    simultaneous_intervals,
    summarize_nested_budget_panel,
    synchronized_null_components,
)
from suica_core.v8_nuisance_filtration import (  # noqa: E402
    FrozenNuisanceResidualizer,
    build_nuisance_profiles,
    fit_nuisance_residualizer,
)
from suica_core.v8_realtext_relation_field import (  # noqa: E402
    RealTextRelationSpec,
    frozen_random_directions,
    stable_bucket,
)
from suica_core.v8_residual_geometry_correspondence import (  # noqa: E402
    ResidualGeometrySpec,
    _alignment,
    frozen_bandwidth,
    relational_matrices,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_nested_information_budget.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_nested_information_budget"
    / "opened_development_20260730"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_NESTED_INFORMATION_BUDGET.md"


@dataclass(frozen=True)
class FrozenBudgetOperator:
    """One context's D0-fitted feature-to-relation operator."""

    background: FrozenMarginalBackground
    residualizer: FrozenNuisanceResidualizer
    bandwidth: float
    profile_columns: tuple[str, ...]
    expected_events: int


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _load_pandora_source(config: dict[str, Any]) -> pd.DataFrame:
    raw = pd.read_parquet(
        _resolve(config["path"]),
        columns=["author", "body", "created_utc", "subreddit"],
    )
    raw["author"] = raw["author"].astype(str)
    raw["body"] = raw["body"].fillna("").astype(str)
    raw["subreddit"] = raw["subreddit"].fillna("<missing>").astype(str)
    raw = raw.loc[
        raw["body"].str.len().ge(int(config["minimum_text_characters"]))
    ].copy()
    excluded = {
        str(value).casefold()
        for value in config.get("excluded_contexts", [])
    }
    return raw.loc[
        ~raw["subreddit"].str.casefold().isin(excluded)
    ].copy()


def _spread_exact(group: pd.DataFrame, count: int) -> pd.DataFrame:
    indices = np.unique(
        np.linspace(0, len(group) - 1, num=count, dtype=int)
    )
    if len(indices) != count:
        return group.iloc[:0]
    return group.iloc[indices]


def _fixed_event_pool(
    raw: pd.DataFrame,
    context_a: str,
    context_b: str,
    *,
    event_count: int,
) -> tuple[pd.Index, dict[str, pd.DataFrame]]:
    selected = raw.loc[
        raw["subreddit"].isin([context_a, context_b])
    ].copy()
    counts = (
        selected.groupby(["author", "subreddit"], observed=True)
        .size()
        .unstack()
    )
    for context in (context_a, context_b):
        if context not in counts:
            return pd.Index([]), {}
    authors = counts.index[
        counts[[context_a, context_b]].ge(event_count).all(axis=1)
    ]
    selected = selected.loc[selected["author"].isin(authors)]
    result: dict[str, pd.DataFrame] = {}
    for context in (context_a, context_b):
        rows: list[dict[str, Any]] = []
        context_rows = selected.loc[
            selected["subreddit"].eq(context)
        ].sort_values(["author", "created_utc"], kind="stable")
        for author, group in context_rows.groupby(
            "author",
            observed=True,
            sort=False,
        ):
            sampled = _spread_exact(group, event_count)
            for order, row in enumerate(sampled.itertuples(index=False)):
                rows.append(
                    {
                        "author_id": str(author),
                        "context": context,
                        "order": order,
                        "source_order": order,
                        "text": str(row.body),
                        "timestamp": row.created_utc,
                    }
                )
        result[context] = pd.DataFrame(rows)
    return authors, result


def _nested_subset(
    pool: pd.DataFrame,
    source_indices: tuple[int, ...],
) -> pd.DataFrame:
    selected = pool.loc[pool["source_order"].isin(source_indices)].copy()
    selected = selected.sort_values(
        ["author_id", "source_order"],
        kind="stable",
    )
    selected["order"] = selected.groupby(
        "author_id",
        observed=True,
    ).cumcount()
    expected = len(source_indices)
    counts = selected.groupby("author_id", observed=True).size()
    if not len(counts) or not counts.eq(expected).all():
        raise RuntimeError("Nested event selection lost author observations.")
    return selected


def _fit_operator(
    events: pd.DataFrame,
    *,
    corpus: str,
    feature_spec: RealTextRelationSpec,
    directions: np.ndarray,
    background_spec: MarginalQuotientSpec,
    nuisance_config: dict[str, Any],
    declared_groups: list[str],
    expected_events: int,
    seed: int,
) -> tuple[FrozenBudgetOperator, dict[str, Any]]:
    tensor = build_event_tensor(
        events,
        corpus=corpus,
        feature_spec=feature_spec,
        expected_events=expected_events,
    )
    profiles = build_nuisance_profiles(
        events,
        tensor,
        feature_spec=feature_spec,
        content_directions=int(nuisance_config["content_directions"]),
    )
    selected_columns = sorted(
        {
            column
            for group in declared_groups
            for column in profiles.groups[group]
        }
    )
    background, background_diagnostics = fit_marginal_background(
        tensor,
        marginal_directions=directions,
        spec=background_spec,
        rng=np.random.default_rng(seed),
        reallocator=exchangeable_set_reallocation,
    )
    blocks = tensor_feature_blocks(
        tensor.vectors,
        marginal_directions=directions,
    )
    quotient = quotient_blocks(
        blocks,
        tensor.metadata["context"].astype(str).to_numpy(),
        background,
    )
    raw = quotient_views(
        quotient,
        marginal_directions=directions,
    )["M_all"]
    d0 = tensor.metadata["split"].eq("D0").to_numpy()
    residualizer = fit_nuisance_residualizer(
        raw,
        profiles.values,
        d0,
        columns=selected_columns,
        ridge_ratio=float(nuisance_config["ridge_ratio"]),
    )
    residual = residualizer.transform(raw, profiles.values)
    nuisance = (
        profiles.values[..., residualizer.active_columns]
        - residualizer.center
    ) / residualizer.scale
    operator = FrozenBudgetOperator(
        background=background,
        residualizer=residualizer,
        bandwidth=frozen_bandwidth(residual, tensor.metadata),
        profile_columns=profiles.columns,
        expected_events=expected_events,
    )
    panel = {
        "metadata": tensor.metadata.reset_index(drop=True),
        "values": residual,
        "nuisance": nuisance,
        "background_fixed_points": int(
            background_diagnostics["same_author"].sum()
        ),
        "background_assignments": int(
            background_diagnostics["total_assignments"].sum()
        ),
    }
    return operator, panel


def _apply_operator(
    events: pd.DataFrame,
    *,
    corpus: str,
    feature_spec: RealTextRelationSpec,
    directions: np.ndarray,
    nuisance_config: dict[str, Any],
    operator: FrozenBudgetOperator,
    expected_events: int,
) -> dict[str, Any]:
    tensor = build_event_tensor(
        events,
        corpus=corpus,
        feature_spec=feature_spec,
        expected_events=expected_events,
    )
    profiles = build_nuisance_profiles(
        events,
        tensor,
        feature_spec=feature_spec,
        content_directions=int(nuisance_config["content_directions"]),
    )
    if profiles.columns != operator.profile_columns:
        raise RuntimeError("Nuisance profile schema drifted across budgets.")
    blocks = tensor_feature_blocks(
        tensor.vectors,
        marginal_directions=directions,
    )
    quotient = quotient_blocks(
        blocks,
        tensor.metadata["context"].astype(str).to_numpy(),
        operator.background,
    )
    raw = quotient_views(
        quotient,
        marginal_directions=directions,
    )["M_all"]
    residual = operator.residualizer.transform(raw, profiles.values)
    nuisance = (
        profiles.values[..., operator.residualizer.active_columns]
        - operator.residualizer.center
    ) / operator.residualizer.scale
    return {
        "metadata": tensor.metadata.reset_index(drop=True),
        "values": residual,
        "nuisance": nuisance,
        "background_fixed_points": float("nan"),
        "background_assignments": float("nan"),
    }


def _align_context_panels(
    left: dict[str, Any],
    right: dict[str, Any],
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    left_meta = left["metadata"].copy()
    right_meta = right["metadata"].copy()
    author_order = left_meta["author_id"].astype(str)
    if set(author_order) != set(right_meta["author_id"].astype(str)):
        raise ValueError("Context panels do not contain the same authors.")
    right_indices = (
        right_meta.reset_index()
        .set_index("author_id")
        .loc[author_order, "index"]
        .to_numpy()
    )
    right_meta = right_meta.iloc[right_indices].reset_index(drop=True)
    if not left_meta["split"].reset_index(drop=True).equals(
        right_meta["split"]
    ):
        raise ValueError("Context panels do not share split assignments.")
    return (
        left_meta.reset_index(drop=True),
        left["values"],
        right["values"][right_indices],
        left["nuisance"],
        right["nuisance"][right_indices],
    )


def _relation_matrices_by_split(
    metadata: pd.DataFrame,
    values_a: np.ndarray,
    values_b: np.ndarray,
    nuisance_a: np.ndarray,
    nuisance_b: np.ndarray,
    *,
    bandwidth_a: float,
    bandwidth_b: float,
    budget_spec: NestedInformationBudgetSpec,
    transport_spec: dict[str, Any],
) -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    relation_spec = ResidualGeometrySpec(
        d0_null_draws=99,
        test_null_draws=99,
        bootstrap_draws=99,
        bandwidth_multipliers=(budget_spec.rbf_scale,),
        neighborhood_fractions=(0.10,),
        nuisance_kernel_ridge=float(
            transport_spec["nuisance_kernel_ridge"]
        ),
        minimum_context_authors=8,
        seed=budget_spec.seed,
    )
    metric = f"rbf_krc_{budget_spec.rbf_scale:g}"
    result = {}
    for split in ("D0", "D1", "D2"):
        mask = metadata["split"].eq(split).to_numpy()
        count = int(mask.sum())
        if count < 8:
            continue
        labels_a = np.repeat("context_a", count)
        labels_b = np.repeat("context_b", count)
        a0, a1 = relational_matrices(
            values_a[mask],
            nuisance_a[mask],
            labels_a,
            bandwidth=bandwidth_a,
            spec=relation_spec,
        )[metric]
        b0, b1 = relational_matrices(
            values_b[mask],
            nuisance_b[mask],
            labels_b,
            bandwidth=bandwidth_b,
            spec=relation_spec,
        )[metric]
        result[split] = (a0, a1, b0, b1)
    return result


def _build_report(
    *,
    decision: dict[str, Any],
    design: pd.DataFrame,
    curve: pd.DataFrame,
    deltas: pd.DataFrame,
    schedule_summary: pd.DataFrame,
    operators: pd.DataFrame,
    claim_boundary: str,
) -> str:
    held_curve = curve.loc[curve["split"].isin(["D1", "D2"])]
    return (
        "# V8 Nested Information-Budget Experiment\n\n"
        f"Status: `{decision['overall_status']}`\n\n"
        "This opened-panel mechanism experiment keeps the author cohort and "
        "12-event source pool fixed, then reveals literal nested subsets at "
        "4/6/8/10/12 events per context. The primary 12-minus-8 contrast "
        "separates a 12-event-frozen operator arm from a budget-specific "
        "refit arm.\n\n"
        "## Decision\n\n"
        f"```json\n{json.dumps(decision, ensure_ascii=False, indent=2)}\n"
        "```\n\n"
        "## Nested design audit\n\n"
        f"{design.to_markdown(index=False)}\n\n"
        "## Primary paired deltas\n\n"
        "Positive W means relation excess increased. Positive Q means "
        "technical disagreement decreased. W and Q reuse the same relation "
        "matrices, so they are complementary diagnostics rather than "
        "independent evidence.\n\n"
        f"{deltas.to_markdown(index=False)}\n\n"
        "## Eight-event content-sampling sensitivity\n\n"
        "All 15 ways to reveal four of the six event pairs were scored with "
        "the same frozen twelve-event operator. These rows are dependent "
        "design sensitivities, not 15 replications.\n\n"
        f"{schedule_summary.to_markdown(index=False)}\n\n"
        "Detailed cells are saved as `schedule_sensitivity.csv`.\n\n"
        "## Held-panel budget curve\n\n"
        f"{held_curve.to_markdown(index=False)}\n\n"
        "## Operator diagnostics\n\n"
        f"{operators.to_markdown(index=False)}\n\n"
        "## Interpretation boundary\n\n"
        f"{claim_boundary}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    config = _json(args.config)
    base = _json(_resolve(config["base_config"]))
    nuisance_config = _json(_resolve(config["nuisance_config"]))
    feature_spec = RealTextRelationSpec(**base["spec"])
    budget_spec = NestedInformationBudgetSpec(
        budgets=tuple(config["budgets"]),
        primary_low_budget=int(config["primary_low_budget"]),
        primary_high_budget=int(config["primary_high_budget"]),
        null_draws=int(config["null_draws"]),
        bootstrap_draws=int(config["bootstrap_draws"]),
        rbf_scale=float(config["rbf_scale"]),
        material_delta_reference=float(
            config["material_delta_reference"]
        ),
        seed=int(config["seed"]),
    )
    background_draws = int(config["background_draws"])
    if args.quick:
        budget_spec = replace(
            budget_spec,
            null_draws=99,
            bootstrap_draws=99,
        )
        background_draws = 49
    background_spec = MarginalQuotientSpec(
        background_draws=background_draws,
        null_draws=99,
        diagnostic_null_draws=49,
        bootstrap_draws=99,
        bootstrap_reference_worlds=8,
        local_length_block=int(nuisance_config["local_length_block"]),
        seed=budget_spec.seed,
    )
    directions = frozen_random_directions(
        event_dimensions=2 * feature_spec.hash_dimensions,
        count=feature_spec.random_directions,
        seed=feature_spec.seed + 17,
    )[0]
    declared_groups = nuisance_config["tiers"][
        nuisance_config["primary_tier"]
    ]
    event_count = max(budget_spec.budgets)
    pair_reveal_order = tuple(map(int, config["pair_reveal_order"]))
    nested_indices = nested_event_indices(
        event_count=event_count,
        budgets=budget_spec.budgets,
        pair_reveal_order=pair_reveal_order,
    )
    context_a, context_b = map(str, config["pandora_context_pair"])
    raw = _load_pandora_source(base["data"]["pandora"])
    authors, pools = _fixed_event_pool(
        raw,
        context_a,
        context_b,
        event_count=event_count,
    )
    if len(authors) < 24:
        raise RuntimeError("The fixed event pool has insufficient authors.")

    events_by_budget = {
        budget: {
            context: _nested_subset(pools[context], indices)
            for context in (context_a, context_b)
        }
        for budget, indices in nested_indices.items()
    }
    design_rows = []
    previous: dict[str, set[tuple[str, int]]] | None = None
    for budget in budget_spec.budgets:
        current: dict[str, set[tuple[str, int]]] = {}
        for context in (context_a, context_b):
            events = events_by_budget[budget][context]
            keys = set(
                zip(
                    events["author_id"].astype(str),
                    events["source_order"].astype(int),
                    strict=True,
                )
            )
            current[context] = keys
            subset_violations = (
                0
                if previous is None
                else len(previous[context] - keys)
            )
            design_rows.append(
                {
                    "budget": budget,
                    "context": context,
                    "authors": int(events["author_id"].nunique()),
                    "events": int(len(events)),
                    "events_per_replicate": budget // 2,
                    "subset_violations_from_previous": subset_violations,
                    "source_indices": ",".join(
                        map(str, nested_indices[budget])
                    ),
                }
            )
        previous = current
    design = pd.DataFrame(design_rows)
    if design["subset_violations_from_previous"].sum() != 0:
        raise RuntimeError("Nested design audit failed.")

    panels: dict[
        str,
        dict[int, dict[str, tuple[np.ndarray, ...]]],
    ] = {"fixed_12_operator": {}, "budget_refit": {}}
    operator_rows: list[dict[str, Any]] = []
    fixed_operators: dict[str, FrozenBudgetOperator] = {}
    fixed_high_panels: dict[str, dict[str, Any]] = {}
    high = budget_spec.primary_high_budget
    for context in (context_a, context_b):
        seed = (
            budget_spec.seed
            + stable_bucket(
                f"fixed-{context}-{high}",
                salt="v8-nested-budget-operator",
                modulus=2**31 - 1,
            )
        )
        operator, panel = _fit_operator(
            events_by_budget[high][context],
            corpus="pandora",
            feature_spec=feature_spec,
            directions=directions,
            background_spec=background_spec,
            nuisance_config=nuisance_config,
            declared_groups=declared_groups,
            expected_events=high,
            seed=seed,
        )
        fixed_operators[context] = operator
        fixed_high_panels[context] = panel
        operator_rows.append(
            {
                "arm": "fixed_12_operator",
                "fit_budget": high,
                "application_budget": high,
                "context": context,
                "bandwidth": operator.bandwidth,
                "active_nuisance_columns": int(
                    len(operator.residualizer.active_columns)
                ),
                "background_coverage": operator.background.coverage,
                "background_fixed_point_rate": (
                    panel["background_fixed_points"]
                    / max(panel["background_assignments"], 1)
                ),
            }
        )

    for budget in budget_spec.budgets:
        fixed_context_panels = {}
        refit_context_panels = {}
        refit_operators = {}
        for context in (context_a, context_b):
            if budget == high:
                fixed_panel = fixed_high_panels[context]
            else:
                fixed_panel = _apply_operator(
                    events_by_budget[budget][context],
                    corpus="pandora",
                    feature_spec=feature_spec,
                    directions=directions,
                    nuisance_config=nuisance_config,
                    operator=fixed_operators[context],
                    expected_events=budget,
                )
            fixed_context_panels[context] = fixed_panel
            if budget == high:
                refit_operator = fixed_operators[context]
                refit_panel = fixed_high_panels[context]
            else:
                seed = (
                    budget_spec.seed
                    + stable_bucket(
                        f"refit-{context}-{budget}",
                        salt="v8-nested-budget-operator",
                        modulus=2**31 - 1,
                    )
                )
                refit_operator, refit_panel = _fit_operator(
                    events_by_budget[budget][context],
                    corpus="pandora",
                    feature_spec=feature_spec,
                    directions=directions,
                    background_spec=background_spec,
                    nuisance_config=nuisance_config,
                    declared_groups=declared_groups,
                    expected_events=budget,
                    seed=seed,
                )
                operator_rows.append(
                    {
                        "arm": "budget_refit",
                        "fit_budget": budget,
                        "application_budget": budget,
                        "context": context,
                        "bandwidth": refit_operator.bandwidth,
                        "active_nuisance_columns": int(
                            len(refit_operator.residualizer.active_columns)
                        ),
                        "background_coverage": (
                            refit_operator.background.coverage
                        ),
                        "background_fixed_point_rate": (
                            refit_panel["background_fixed_points"]
                            / max(
                                refit_panel["background_assignments"],
                                1,
                            )
                        ),
                    }
                )
            refit_operators[context] = refit_operator
            refit_context_panels[context] = refit_panel
        if budget == high:
            for context in (context_a, context_b):
                operator_rows.append(
                    {
                        "arm": "budget_refit",
                        "fit_budget": budget,
                        "application_budget": budget,
                        "context": context,
                        "bandwidth": fixed_operators[context].bandwidth,
                        "active_nuisance_columns": int(
                            len(
                                fixed_operators[
                                    context
                                ].residualizer.active_columns
                            )
                        ),
                        "background_coverage": (
                            fixed_operators[context].background.coverage
                        ),
                        "background_fixed_point_rate": (
                            fixed_high_panels[context][
                                "background_fixed_points"
                            ]
                            / max(
                                fixed_high_panels[context][
                                    "background_assignments"
                                ],
                                1,
                            )
                        ),
                    }
                )

        for arm, context_panels, operators in (
            (
                "fixed_12_operator",
                fixed_context_panels,
                fixed_operators,
            ),
            ("budget_refit", refit_context_panels, refit_operators),
        ):
            aligned = _align_context_panels(
                context_panels[context_a],
                context_panels[context_b],
            )
            matrices = _relation_matrices_by_split(
                *aligned,
                bandwidth_a=operators[context_a].bandwidth,
                bandwidth_b=operators[context_b].bandwidth,
                budget_spec=budget_spec,
                transport_spec=config["transport_spec"],
            )
            for split, values in matrices.items():
                panels[arm].setdefault(budget, {})[split] = values

    curve_parts = []
    arm_summaries: dict[str, dict[str, dict[str, object]]] = {}
    for arm in ("fixed_12_operator", "budget_refit"):
        arm_summaries[arm] = {}
        for split in ("D0", "D1", "D2"):
            matrices_by_budget = {
                budget: panels[arm][budget][split]
                for budget in budget_spec.budgets
                if split in panels[arm][budget]
            }
            summary = summarize_nested_budget_panel(
                matrices_by_budget,
                split=split,
                arm=arm,
                spec=budget_spec,
                seed=(
                    budget_spec.seed
                    + stable_bucket(
                        f"{arm}-{split}",
                        salt="v8-nested-budget-inference",
                        modulus=2**31 - 1,
                    )
                ),
            )
            arm_summaries[arm][split] = summary
            curve_parts.append(summary["curve"])
    curve = pd.concat(curve_parts, ignore_index=True)

    schedule_rows: list[dict[str, Any]] = []
    all_pairs = tuple(range(event_count // 2))
    low_pairs = budget_spec.primary_low_budget // 2
    high_matrices = {
        split: panels["fixed_12_operator"][high][split]
        for split in ("D1", "D2")
    }
    schedule_null_draws = int(config["schedule_sensitivity_null_draws"])
    if args.quick:
        schedule_null_draws = 99
    primary_source_indices = nested_indices[
        budget_spec.primary_low_budget
    ]
    for schedule_index, selected_pairs in enumerate(
        combinations(all_pairs, low_pairs)
    ):
        source_indices = tuple(
            sorted(
                index
                for pair in selected_pairs
                for index in (2 * pair, 2 * pair + 1)
            )
        )
        context_panels = {
            context: _apply_operator(
                _nested_subset(pools[context], source_indices),
                corpus="pandora",
                feature_spec=feature_spec,
                directions=directions,
                nuisance_config=nuisance_config,
                operator=fixed_operators[context],
                expected_events=budget_spec.primary_low_budget,
            )
            for context in (context_a, context_b)
        }
        aligned = _align_context_panels(
            context_panels[context_a],
            context_panels[context_b],
        )
        low_matrices = _relation_matrices_by_split(
            *aligned,
            bandwidth_a=fixed_operators[context_a].bandwidth,
            bandwidth_b=fixed_operators[context_b].bandwidth,
            budget_spec=budget_spec,
            transport_spec=config["transport_spec"],
        )
        schedule_id = "-".join(map(str, selected_pairs))
        for split in ("D1", "D2"):
            matrix_pair = {
                budget_spec.primary_low_budget: low_matrices[split],
                budget_spec.primary_high_budget: high_matrices[split],
            }
            null = synchronized_null_components(
                matrix_pair,
                draws=schedule_null_draws,
                rng=np.random.default_rng(
                    budget_spec.seed
                    + stable_bucket(
                        f"schedule-{schedule_id}-{split}",
                        salt="v8-nested-budget-schedule",
                        modulus=2**31 - 1,
                    )
                ),
            )

            def observed(
                matrices: tuple[np.ndarray, ...],
            ) -> dict[str, float]:
                a0, a1, b0, b1 = matrices
                return {
                    "within_a": _alignment(a0, a1),
                    "within_b": _alignment(b0, b1),
                    "cross": 0.5
                    * (_alignment(a0, b1) + _alignment(a1, b0)),
                }

            low_observed = observed(
                matrix_pair[budget_spec.primary_low_budget]
            )
            high_observed = observed(
                matrix_pair[budget_spec.primary_high_budget]
            )
            for component in ("within_a", "within_b", "cross"):
                low_excess = float(
                    low_observed[component]
                    - np.mean(
                        null[
                            budget_spec.primary_low_budget
                        ][component]
                    )
                )
                high_excess = float(
                    high_observed[component]
                    - np.mean(
                        null[
                            budget_spec.primary_high_budget
                        ][component]
                    )
                )
                schedule_rows.append(
                    {
                        "schedule_index": schedule_index,
                        "schedule_id": schedule_id,
                        "source_indices": ",".join(
                            map(str, source_indices)
                        ),
                        "is_primary_schedule": bool(
                            source_indices == primary_source_indices
                        ),
                        "split": split,
                        "component": component,
                        "low_budget_excess": low_excess,
                        "high_budget_excess": high_excess,
                        "delta_high_minus_low": (
                            high_excess - low_excess
                        ),
                    }
                )
    schedule_sensitivity = pd.DataFrame(schedule_rows)
    schedule_summary = (
        schedule_sensitivity.groupby(
            ["split", "component"],
            observed=True,
        )["delta_high_minus_low"]
        .agg(
            schedules="size",
            positive_fraction=lambda values: float(
                np.mean(np.asarray(values) > 0)
            ),
            median_delta="median",
            minimum_delta="min",
            maximum_delta="max",
        )
        .reset_index()
    )

    delta_parts = []
    for arm in ("fixed_12_operator", "budget_refit"):
        for metric_key, metric_name in (
            ("w", "delta_relation_excess_w"),
            ("q", "reduction_technical_disagreement_q"),
        ):
            points: dict[str, float] = {}
            samples: dict[str, np.ndarray] = {}
            for split in ("D1", "D2"):
                summary = arm_summaries[arm][split]
                points.update(summary[f"{metric_key}_points"])
                samples.update(summary[f"{metric_key}_samples"])
            intervals = simultaneous_intervals(points, samples)
            intervals["arm"] = arm
            intervals["metric"] = metric_name
            intervals["all_simultaneous_positive"] = bool(
                intervals["simultaneous_lcb"].gt(0).all()
            )
            intervals["material_reference"] = (
                budget_spec.material_delta_reference
                if metric_key == "w"
                else float("nan")
            )
            delta_parts.append(intervals)
    deltas = pd.concat(delta_parts, ignore_index=True)

    fixed_w = deltas.loc[
        deltas["arm"].eq("fixed_12_operator")
        & deltas["metric"].eq("delta_relation_excess_w")
    ]
    fixed_q = deltas.loc[
        deltas["arm"].eq("fixed_12_operator")
        & deltas["metric"].eq(
            "reduction_technical_disagreement_q"
        )
    ]
    refit_w = deltas.loc[
        deltas["arm"].eq("budget_refit")
        & deltas["metric"].eq("delta_relation_excess_w")
    ]
    fixed_w_simultaneous = bool(
        len(fixed_w) and fixed_w["simultaneous_lcb"].gt(0).all()
    )
    fixed_q_simultaneous = bool(
        len(fixed_q) and fixed_q["simultaneous_lcb"].gt(0).all()
    )
    refit_w_simultaneous = bool(
        len(refit_w) and refit_w["simultaneous_lcb"].gt(0).all()
    )
    if fixed_w_simultaneous and fixed_q_simultaneous:
        overall = "OPENED_INPUT_INFORMATION_GAIN_RESOLVED"
    elif refit_w_simultaneous and not fixed_w_simultaneous:
        overall = "ESTIMATOR_ADAPTATION_ONLY_ON_OPENED_PANEL"
    elif (
        fixed_w["point"].gt(0).all()
        or fixed_q["point"].gt(0).all()
    ):
        overall = "PARTIAL_OPENED_INFORMATION_BUDGET_SIGNAL"
    else:
        overall = "INFORMATION_BUDGET_EFFECT_UNDERRESOLVED"
    decision = {
        "status": "NESTED_INFORMATION_BUDGET_COMPLETED",
        "overall_status": overall,
        "pair_id": f"pandora::{context_a}::{context_b}",
        "authors": int(len(authors)),
        "budgets": list(budget_spec.budgets),
        "primary_contrast": (
            f"{budget_spec.primary_high_budget}-"
            f"{budget_spec.primary_low_budget}"
        ),
        "fixed_w_all_positive": bool(fixed_w["point"].gt(0).all()),
        "fixed_w_simultaneous_all_positive": fixed_w_simultaneous,
        "fixed_q_all_positive": bool(fixed_q["point"].gt(0).all()),
        "fixed_q_simultaneous_all_positive": fixed_q_simultaneous,
        "refit_w_simultaneous_all_positive": refit_w_simultaneous,
        "fixed_w_cells_at_material_reference": int(
            fixed_w["point"]
            .ge(budget_spec.material_delta_reference)
            .sum()
        ),
        "fixed_w_cells": int(len(fixed_w)),
        "nested_subset_violations": int(
            design["subset_violations_from_previous"].sum()
        ),
        "schedule_sensitivity_designs": int(
            schedule_sensitivity["schedule_id"].nunique()
        ),
        "schedule_positive_fraction_min": float(
            schedule_summary["positive_fraction"].min()
        ),
        "schedule_positive_fraction_max": float(
            schedule_summary["positive_fraction"].max()
        ),
        "fresh_confirmation_status": "NOT_FRESH_D3",
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_boundary": config["claim_boundary"],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    design.to_csv(args.output_dir / "nested_design_audit.csv", index=False)
    curve.to_csv(args.output_dir / "budget_curve.csv", index=False)
    deltas.to_csv(args.output_dir / "primary_paired_deltas.csv", index=False)
    schedule_sensitivity.to_csv(
        args.output_dir / "schedule_sensitivity.csv",
        index=False,
    )
    schedule_summary.to_csv(
        args.output_dir / "schedule_sensitivity_summary.csv",
        index=False,
    )
    operators = pd.DataFrame(operator_rows)
    operators.to_csv(
        args.output_dir / "operator_diagnostics.csv",
        index=False,
    )
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = _build_report(
        decision=decision,
        design=design,
        curve=curve,
        deltas=deltas,
        schedule_summary=schedule_summary,
        operators=operators,
        claim_boundary=config["claim_boundary"],
    )
    args.report.write_text(report, encoding="utf-8")
    (args.output_dir / "REPORT.md").write_text(
        report,
        encoding="utf-8",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
