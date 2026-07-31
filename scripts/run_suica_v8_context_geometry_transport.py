#!/usr/bin/env python3
"""Run same-author cross-context relation-geometry transport."""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v8_context_geometry_transport import (  # noqa: E402
    ContextTransportSpec,
    evaluate_context_transport,
)
from suica_core.v8_event_set_composition_knockout import (  # noqa: E402
    build_event_tensor,
)
from suica_core.v8_exchangeable_background_audit import (  # noqa: E402
    exchangeable_set_reallocation,
)
from suica_core.v8_marginal_background_quotient import (  # noqa: E402
    MarginalQuotientSpec,
    fit_marginal_background,
    quotient_blocks,
    quotient_views,
    tensor_feature_blocks,
)
from suica_core.v8_nuisance_filtration import (  # noqa: E402
    build_nuisance_profiles,
    fit_nuisance_residualizer,
)
from suica_core.v8_realtext_relation_field import (  # noqa: E402
    RealTextRelationSpec,
    assign_d0_d1_d2,
    frozen_random_directions,
    stable_bucket,
)
from suica_core.v8_residual_geometry_correspondence import (  # noqa: E402
    frozen_bandwidth,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_context_geometry_transport.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_context_geometry_transport"
    / "audit_20260828"
)
DEFAULT_REPORT = (
    ROOT / "reports" / "V8_CONTEXT_GEOMETRY_TRANSPORT.md"
)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _spread_exact(group: pd.DataFrame, count: int) -> pd.DataFrame:
    indices = np.unique(
        np.linspace(0, len(group) - 1, num=count, dtype=int)
    )
    if len(indices) != count:
        return group.iloc[:0]
    return group.iloc[indices]


def _split_counts(
    authors: pd.Index,
    *,
    corpus: str,
    feature_spec: RealTextRelationSpec,
) -> dict[str, int]:
    mapping = assign_d0_d1_d2(
        map(str, authors),
        salt=f"v8rt-{corpus}-{feature_spec.seed}",
    )
    return {
        split: int(sum(value == split for value in mapping.values()))
        for split in ("D0", "D1", "D2")
    }


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


def _pandora_pair_events(
    raw: pd.DataFrame,
    context_a: str,
    context_b: str,
    *,
    events_per_context: int,
    eligibility_events_per_context: int | None = None,
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
    eligibility = int(
        eligibility_events_per_context
        if eligibility_events_per_context is not None
        else events_per_context
    )
    if eligibility < events_per_context:
        raise ValueError(
            "eligibility_events_per_context cannot be smaller than "
            "events_per_context."
        )
    authors = counts.index[
        counts[[context_a, context_b]]
        .ge(eligibility)
        .all(axis=1)
    ]
    selected = selected.loc[selected["author"].isin(authors)]
    result = {}
    for context in (context_a, context_b):
        rows = []
        context_rows = selected.loc[
            selected["subreddit"].eq(context)
        ].sort_values(
            ["author", "created_utc"],
            kind="stable",
        )
        for author, group in context_rows.groupby(
            "author",
            observed=True,
            sort=False,
        ):
            sampled = _spread_exact(group, events_per_context)
            for order, row in enumerate(sampled.itertuples(index=False)):
                rows.append(
                    {
                        "author_id": str(author),
                        "context": context,
                        "order": order,
                        "text": str(row.body),
                        "timestamp": row.created_utc,
                    }
                )
        result[context] = pd.DataFrame(rows)
    return authors, result


def _pandora_budget_feasibility(
    raw: pd.DataFrame,
    pairs: list[list[str]],
    budgets: list[int],
    *,
    feature_spec: RealTextRelationSpec,
    minimum_held_authors: int,
) -> pd.DataFrame:
    counts = (
        raw.groupby(["author", "subreddit"], observed=True)
        .size()
        .unstack()
    )
    rows = []
    for budget in map(int, budgets):
        for context_a, context_b in pairs:
            if context_a in counts and context_b in counts:
                authors = counts.index[
                    counts[[context_a, context_b]]
                    .ge(budget)
                    .all(axis=1)
                ]
            else:
                authors = pd.Index([])
            split = _split_counts(
                authors,
                corpus="pandora",
                feature_spec=feature_spec,
            )
            rows.append(
                {
                    "events_per_context": budget,
                    "events_per_replicate": budget // 2,
                    "pair_id": f"pandora::{context_a}::{context_b}",
                    "context_a": context_a,
                    "context_b": context_b,
                    "authors": int(len(authors)),
                    **{
                        f"authors_{key}": value
                        for key, value in split.items()
                    },
                    "held_panel_admissible": bool(
                        split["D1"] >= minimum_held_authors
                        and split["D2"] >= minimum_held_authors
                    ),
                }
            )
    return pd.DataFrame(rows)


def _x_feasibility(
    config: dict[str, Any],
    pairs: list[list[str]],
    *,
    events_per_context: int,
    feature_spec: RealTextRelationSpec,
) -> list[dict[str, Any]]:
    context_column = str(config["context_column"])
    raw = pd.read_csv(
        _resolve(config["path"]),
        usecols=["account_id", context_column, "text"],
        dtype={"account_id": str},
    )
    raw["text"] = raw["text"].fillna("").astype(str)
    raw = raw.loc[
        raw["text"].str.len().ge(int(config["minimum_text_characters"]))
    ]
    counts = (
        raw.groupby(["account_id", context_column], observed=True)
        .size()
        .unstack()
    )
    rows = []
    for context_a, context_b in pairs:
        if context_a in counts and context_b in counts:
            authors = counts.index[
                counts[[context_a, context_b]]
                .ge(events_per_context)
                .all(axis=1)
            ]
        else:
            authors = pd.Index([])
        split = _split_counts(
            authors,
            corpus="x_market",
            feature_spec=feature_spec,
        )
        rows.append(
            {
                "pair_id": f"x_market::{context_a}::{context_b}",
                "corpus": "x_market",
                "context_a": context_a,
                "context_b": context_b,
                "authors": int(len(authors)),
                **{f"authors_{key}": value for key, value in split.items()},
            }
        )
    return rows


def _fit_arm(
    events: pd.DataFrame,
    *,
    corpus: str,
    pair_id: str,
    context: str,
    feature_spec: RealTextRelationSpec,
    directions: np.ndarray,
    background_spec: MarginalQuotientSpec,
    nuisance_config: dict[str, Any],
    declared_groups: list[str],
    seed: int,
    expected_events: int = 8,
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
    columns = sorted(
        {
            column
            for group in declared_groups
            for column in profiles.groups[group]
        }
    )
    background, _ = fit_marginal_background(
        tensor,
        marginal_directions=directions,
        spec=background_spec,
        rng=np.random.default_rng(
            seed
            + stable_bucket(
                f"{pair_id}-{context}",
                salt="v8-context-transport-background",
                modulus=2**31 - 1,
            )
        ),
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
        columns=columns,
        ridge_ratio=float(nuisance_config["ridge_ratio"]),
    )
    residual = residualizer.transform(raw, profiles.values)
    nuisance = (
        profiles.values[..., residualizer.active_columns]
        - residualizer.center
    ) / residualizer.scale
    return {
        "metadata": tensor.metadata.reset_index(drop=True),
        "values": residual,
        "nuisance": nuisance,
        "bandwidth": frozen_bandwidth(residual, tensor.metadata),
        "active_nuisance_columns": int(
            len(residualizer.active_columns)
        ),
    }


def _align_arms(
    left: dict[str, Any],
    right: dict[str, Any],
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    left_meta = left["metadata"].copy()
    right_meta = right["metadata"].copy()
    common = left_meta["author_id"].astype(str)
    if set(common) != set(right_meta["author_id"].astype(str)):
        raise ValueError("Context arms do not contain the same authors.")
    right_order = (
        right_meta.reset_index()
        .set_index("author_id")
        .loc[common, "index"]
        .to_numpy()
    )
    right_meta = right_meta.iloc[right_order].reset_index(drop=True)
    if not left_meta["split"].reset_index(drop=True).equals(
        right_meta["split"]
    ):
        raise ValueError("Context arms do not share split assignments.")
    return (
        left_meta.reset_index(drop=True),
        left["values"],
        right["values"][right_order],
        left["nuisance"],
        right["nuisance"][right_order],
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
    transport_spec = ContextTransportSpec(**config["transport_spec"])
    background_draws = int(config["background_draws"])
    if args.quick:
        background_draws = 49
        transport_spec = replace(
            transport_spec,
            d0_null_draws=99,
            test_null_draws=99,
            bootstrap_draws=99,
        )
    background_spec = MarginalQuotientSpec(
        background_draws=background_draws,
        null_draws=99,
        diagnostic_null_draws=99,
        bootstrap_draws=99,
        bootstrap_reference_worlds=8,
        local_length_block=int(nuisance_config["local_length_block"]),
        seed=transport_spec.seed,
    )
    directions = frozen_random_directions(
        event_dimensions=2 * feature_spec.hash_dimensions,
        count=feature_spec.random_directions,
        seed=feature_spec.seed + 17,
    )[0]
    declared_groups = nuisance_config["tiers"][
        nuisance_config["primary_tier"]
    ]
    events_per_context = int(
        config["matched_events_per_author_per_context"]
    )
    eligibility_events = int(
        config.get(
            "eligibility_events_per_author_per_context",
            events_per_context,
        )
    )
    raw_pandora = _load_pandora_source(base["data"]["pandora"])
    budget_feasibility = _pandora_budget_feasibility(
        raw_pandora,
        config["pandora_context_pairs"],
        config["information_budget_audit"],
        feature_spec=feature_spec,
        minimum_held_authors=transport_spec.minimum_held_authors,
    )
    feasibility_rows: list[dict[str, Any]] = []
    panels: dict[str, dict[str, Any]] = {}
    bandwidth_rows = []
    for context_a, context_b in config["pandora_context_pairs"]:
        pair_id = f"pandora::{context_a}::{context_b}"
        authors, events = _pandora_pair_events(
            raw_pandora,
            context_a,
            context_b,
            events_per_context=events_per_context,
            eligibility_events_per_context=eligibility_events,
        )
        split = _split_counts(
            authors,
            corpus="pandora",
            feature_spec=feature_spec,
        )
        feasible = bool(
            split["D0"] >= 8
            and split["D1"] >= transport_spec.minimum_held_authors
            and split["D2"] >= transport_spec.minimum_held_authors
        )
        feasibility_rows.append(
            {
                "pair_id": pair_id,
                "corpus": "pandora",
                "context_a": context_a,
                "context_b": context_b,
                "authors": int(len(authors)),
                **{f"authors_{key}": value for key, value in split.items()},
                "feasibility": "ELIGIBLE" if feasible else "NO_OVERLAP",
            }
        )
        if not feasible:
            continue
        left = _fit_arm(
            events[context_a],
            corpus="pandora",
            pair_id=pair_id,
            context=context_a,
            feature_spec=feature_spec,
            directions=directions,
            background_spec=background_spec,
            nuisance_config=nuisance_config,
            declared_groups=declared_groups,
            seed=transport_spec.seed,
            expected_events=events_per_context,
        )
        right = _fit_arm(
            events[context_b],
            corpus="pandora",
            pair_id=pair_id,
            context=context_b,
            feature_spec=feature_spec,
            directions=directions,
            background_spec=background_spec,
            nuisance_config=nuisance_config,
            declared_groups=declared_groups,
            seed=transport_spec.seed,
            expected_events=events_per_context,
        )
        metadata, values_a, values_b, nuisance_a, nuisance_b = (
            _align_arms(left, right)
        )
        panels[pair_id] = {
            "metadata": metadata,
            "values_a": values_a,
            "values_b": values_b,
            "nuisance_a": nuisance_a,
            "nuisance_b": nuisance_b,
            "bandwidth_a": left["bandwidth"],
            "bandwidth_b": right["bandwidth"],
            "scales": config["successful_rbf_scales"]["pandora"],
            "corpus": "pandora",
            "context_a": context_a,
            "context_b": context_b,
        }
        for context, arm in ((context_a, left), (context_b, right)):
            bandwidth_rows.append(
                {
                    "pair_id": pair_id,
                    "context": context,
                    "d0_frozen_bandwidth": arm["bandwidth"],
                    "active_nuisance_columns": (
                        arm["active_nuisance_columns"]
                    ),
                }
            )
    x_rows = _x_feasibility(
        base["data"]["x_market"],
        config["x_context_pairs"],
        events_per_context=events_per_context,
        feature_spec=feature_spec,
    )
    for row in x_rows:
        row["feasibility"] = (
            "ELIGIBLE"
            if row["authors_D0"] >= 8
            and row["authors_D1"] >= transport_spec.minimum_held_authors
            and row["authors_D2"] >= transport_spec.minimum_held_authors
            else "NO_OVERLAP"
        )
    feasibility_rows.extend(x_rows)
    feasibility = pd.DataFrame(feasibility_rows)

    result = evaluate_context_transport(panels, spec=transport_spec)
    pair_status = feasibility.merge(
        result["pair_status"],
        on="pair_id",
        how="left",
    )
    pair_status["status"] = pair_status["status"].fillna(
        pair_status["feasibility"]
    )
    pair_status["transport_scales"] = pair_status[
        "transport_scales"
    ].fillna("")
    eligible_status = pair_status.loc[
        pair_status["feasibility"].eq("ELIGIBLE"),
        "status",
    ]
    if eligible_status.eq(
        "CONTEXT_TRANSPORTABLE_RELATION_GEOMETRY"
    ).all() and len(eligible_status):
        overall = "CONTEXT_TRANSPORTABLE_RELATION_GEOMETRY"
    elif eligible_status.eq(
        "CONTEXT_TRANSPORTABLE_RELATION_GEOMETRY"
    ).any():
        overall = "PARTIAL_CONTEXT_TRANSPORT"
    elif eligible_status.eq("CROSS_CONTEXT_UNDERRESOLVED").any():
        overall = "CROSS_CONTEXT_UNDERRESOLVED"
    else:
        overall = "CONTEXT_TRANSPORT_UNDERRESOLVED"
    decision = {
        "status": "CONTEXT_GEOMETRY_TRANSPORT_COMPLETED",
        "overall_status": overall,
        "eligible_pairs": int(
            pair_status["feasibility"].eq("ELIGIBLE").sum()
        ),
        "transportable_pairs": int(
            pair_status["status"]
            .eq("CONTEXT_TRANSPORTABLE_RELATION_GEOMETRY")
            .sum()
        ),
        "no_overlap_pairs": int(
            pair_status["status"].eq("NO_OVERLAP").sum()
        ),
        "version": config["version"],
        "events_per_context": events_per_context,
        "eligibility_events_per_context": eligibility_events,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_boundary": config["claim_boundary"],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    feasibility.to_csv(
        args.output_dir / "pair_feasibility.csv",
        index=False,
    )
    budget_feasibility.to_csv(
        args.output_dir / "information_budget_feasibility.csv",
        index=False,
    )
    result["cells"].to_csv(
        args.output_dir / "transport_cells.csv",
        index=False,
    )
    pair_status.to_csv(
        args.output_dir / "pair_status.csv",
        index=False,
    )
    pd.DataFrame(bandwidth_rows).to_csv(
        args.output_dir / "context_bandwidths.csv",
        index=False,
    )
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    held = result["cells"].loc[
        result["cells"]["split"].isin(["D1", "D2"])
    ]
    report = (
        "# V8 Same-Author Context Geometry Transport\n\n"
        f"Status: `{overall}`\n\n"
        "This opened-panel experiment tests whether the same authors preserve "
        "opportunity-filtered relation geometry across two observed text "
        "contexts after each context first passes its own technical "
        "replication gate.\n\n"
        "## Decision\n\n"
        f"```json\n{json.dumps(decision, ensure_ascii=False, indent=2)}\n```\n\n"
        "## Pair status\n\n"
        f"{pair_status.to_markdown(index=False)}\n\n"
        "## Information-budget feasibility\n\n"
        "This table is a support audit, not an outcome search. It shows the "
        "number of same-author context pairs remaining before any held-panel "
        "metric is read.\n\n"
        f"{budget_feasibility.to_markdown(index=False)}\n\n"
        "## Held-out cells\n\n"
        f"{held.to_markdown(index=False)}\n\n"
        "## Interpretation boundary\n\n"
        f"{config['claim_boundary']}\n"
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
