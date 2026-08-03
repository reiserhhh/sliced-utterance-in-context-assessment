#!/usr/bin/env python3
"""Run V8-REALTEXT-RELATION-FIELD-1 on PANDORA, Essays, and X."""
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

from suica_core.v8_realtext_relation_field import (  # noqa: E402
    FAMILY_NAMES,
    CorpusFeaturePanel,
    RealTextRelationSpec,
    approximate_gromov_wasserstein,
    author_coordinates,
    build_feature_panel,
    corpus_pair_names,
    evaluate_corpus_local,
    fit_corpus_calibration,
    frgw_summary,
    stable_bucket,
    transport_calibration,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_realtext_relation_field.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_realtext_relation_field" / "discovery_20260805"
DEFAULT_REPORT = ROOT / "reports" / "V8_REALTEXT_RELATION_FIELD_REPORT.md"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _stable_sort(values: pd.Series, *, salt: str) -> pd.Series:
    return values.astype(str).map(
        lambda value: stable_bucket(value, salt=salt, modulus=2**63 - 1)
    )


def _allocate_unique_author_contexts(
    counts: pd.DataFrame,
    *,
    context_column: str,
    author_column: str,
    context_count: int,
    maximum_authors_per_context: int,
    salt: str,
) -> tuple[list[str], pd.DataFrame]:
    eligible_counts = (
        counts.groupby(context_column, observed=True)[author_column]
        .nunique()
        .sort_values(ascending=False)
    )
    selected_contexts = eligible_counts.head(int(context_count)).index.astype(str).tolist()
    used: set[str] = set()
    allocations = []
    # Allocate rare contexts first so one broad context cannot consume the panel.
    for context in sorted(
        selected_contexts,
        key=lambda value: int(eligible_counts.loc[value]),
    ):
        candidates = counts.loc[counts[context_column].astype(str).eq(context)].copy()
        candidates = candidates.loc[~candidates[author_column].astype(str).isin(used)]
        candidates["stable_order"] = _stable_sort(
            candidates[author_column],
            salt=f"{salt}-{context}",
        )
        candidates = candidates.sort_values(
            ["stable_order", "count"],
            ascending=[True, False],
            kind="stable",
        ).head(int(maximum_authors_per_context))
        candidates[context_column] = context
        allocations.append(candidates)
        used.update(candidates[author_column].astype(str))
    if not allocations:
        return [], pd.DataFrame()
    return selected_contexts, pd.concat(allocations, ignore_index=True)


def _spread_events(
    group: pd.DataFrame,
    *,
    maximum_events: int,
) -> pd.DataFrame:
    count = min(len(group), int(maximum_events))
    if count % 2:
        count -= 1
    if count < 4:
        return group.iloc[:0]
    indices = np.unique(np.linspace(0, len(group) - 1, num=count, dtype=int))
    if len(indices) != count:
        return group.iloc[:0]
    return group.iloc[indices]


def load_pandora_events(config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build a non-personality-community PANDORA author-context panel."""
    path = _resolve(config["path"])
    raw = pd.read_parquet(
        path,
        columns=["author", "body", "created_utc", "subreddit"],
    )
    raw["author"] = raw["author"].astype(str)
    raw["subreddit"] = raw["subreddit"].fillna("<missing>").astype(str)
    raw["body"] = raw["body"].fillna("").astype(str)
    raw = raw.loc[
        raw["body"].str.len().ge(int(config["minimum_text_characters"]))
    ].copy()
    excluded = {str(value).casefold() for value in config.get("excluded_contexts", [])}
    raw = raw.loc[~raw["subreddit"].str.casefold().isin(excluded)].copy()
    counts = (
        raw.groupby(["author", "subreddit"], observed=True)
        .size()
        .rename("count")
        .reset_index()
    )
    counts = counts.loc[counts["count"].ge(int(config["minimum_events"]))]
    contexts, allocation = _allocate_unique_author_contexts(
        counts,
        context_column="subreddit",
        author_column="author",
        context_count=int(config["contexts"]),
        maximum_authors_per_context=int(config["maximum_authors_per_context"]),
        salt="v8rt-pandora",
    )
    if allocation.empty:
        raise ValueError("PANDORA has no eligible author-context cells.")
    keys = set(
        zip(
            allocation["author"].astype(str),
            allocation["subreddit"].astype(str),
            strict=True,
        )
    )
    selected = raw.loc[
        [
            (str(author), str(context)) in keys
            for author, context in zip(
                raw["author"],
                raw["subreddit"],
                strict=True,
            )
        ]
    ].copy()
    rows = []
    for (author, context), group in selected.sort_values(
        ["author", "subreddit", "created_utc"],
        kind="stable",
    ).groupby(["author", "subreddit"], observed=True, sort=False):
        sampled = _spread_events(
            group,
            maximum_events=int(config["maximum_events"]),
        )
        for order, row in enumerate(sampled.itertuples(index=False)):
            rows.append(
                {
                    "author_id": str(author),
                    "context": str(context),
                    "order": order,
                    "text": str(row.body),
                    "timestamp": row.created_utc,
                }
            )
    events = pd.DataFrame(rows)
    schema = {
        "corpus": "pandora",
        "source": str(path),
        "source_rows": int(len(raw)),
        "authors": int(events["author_id"].nunique()),
        "events": int(len(events)),
        "contexts": contexts,
        "context_role": "SELF_SELECTED_OBSERVATIONAL",
        "replicate_type": "SOURCE_COMMENT_DISJOINT_TECHNICAL",
        "external_labels_loaded": False,
    }
    return events, schema


def load_essays_events(config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build buffered within-document pseudo-replicates without label columns.

    2026-08-03 governance note: this loader reads the TEXT of every Essays row
    and orders authors by fresh salt, ignoring the frozen dev/confirm 50/50
    split. The Essays confirm-half is therefore no longer text-untouched
    (labels were never read; the label budget is intact). Do not use this
    loader for any design that claims a text-blind holdout — see ledger row
    V8-ESSAYS-TEXT1 in docs/CLAIMS_LEDGER.md.
    """
    path = _resolve(config["path"])
    raw = pd.read_csv(path, usecols=["user_id", "text"], dtype={"user_id": str})
    candidates = []
    chunks = int(config["chunks"])
    chunk_tokens = int(config["chunk_tokens"])
    required = chunks * chunk_tokens
    for row in raw.itertuples(index=False):
        tokens = str(row.text or "").split()
        if len(tokens) < required:
            continue
        candidates.append((str(row.user_id), tokens))
    candidates.sort(
        key=lambda item: stable_bucket(
            item[0],
            salt="v8rt-essays",
            modulus=2**63 - 1,
        )
    )
    candidates = candidates[: int(config["maximum_authors"])]
    rows = []
    for author, tokens in candidates:
        boundaries = np.linspace(0, len(tokens), num=chunks + 1, dtype=int)
        for order, (left, right) in enumerate(
            zip(boundaries[:-1], boundaries[1:], strict=True)
        ):
            midpoint = (int(left) + int(right)) // 2
            start = max(int(left), midpoint - chunk_tokens // 2)
            text = " ".join(tokens[start : start + chunk_tokens])
            rows.append(
                {
                    "author_id": author,
                    "context": "<single_essay_prompt>",
                    "order": order,
                    "text": text,
                }
            )
    events = pd.DataFrame(rows)
    schema = {
        "corpus": "essays",
        "source": str(path),
        "source_rows": int(len(raw)),
        "authors": int(events["author_id"].nunique()),
        "events": int(len(events)),
        "contexts": ["<single_essay_prompt>"],
        "context_role": "SINGLE_DOCUMENT_FIXED_PROMPT",
        "replicate_type": "WITHIN_DOCUMENT_PSEUDOREPLICATE",
        "external_labels_loaded": False,
    }
    return events, schema


def load_x_events(config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build collector-conditioned X author-context paths."""
    path = _resolve(config["path"])
    context_column = str(config["context_column"])
    usecols = ["account_id", "timestamp", "text", context_column, "lang", "symbol"]
    raw = pd.read_csv(path, usecols=usecols, dtype={"account_id": str})
    raw["account_id"] = raw["account_id"].astype(str)
    raw["text"] = raw["text"].fillna("").astype(str)
    raw[context_column] = raw[context_column].fillna("<missing>").astype(str)
    raw = raw.loc[
        raw["text"].str.len().ge(int(config["minimum_text_characters"]))
    ].copy()
    counts = (
        raw.groupby(["account_id", context_column], observed=True)
        .size()
        .rename("count")
        .reset_index()
    )
    counts = counts.loc[counts["count"].ge(int(config["minimum_events"]))]
    contexts, allocation = _allocate_unique_author_contexts(
        counts,
        context_column=context_column,
        author_column="account_id",
        context_count=int(config["contexts"]),
        maximum_authors_per_context=int(config["maximum_authors_per_context"]),
        salt="v8rt-x",
    )
    if allocation.empty:
        raise ValueError("X has no eligible collector-context cells.")
    keys = set(
        zip(
            allocation["account_id"].astype(str),
            allocation[context_column].astype(str),
            strict=True,
        )
    )
    selected = raw.loc[
        [
            (str(author), str(context)) in keys
            for author, context in zip(
                raw["account_id"],
                raw[context_column],
                strict=True,
            )
        ]
    ].copy()
    rows = []
    for (author, context), group in selected.sort_values(
        ["account_id", context_column, "timestamp"],
        kind="stable",
    ).groupby(["account_id", context_column], observed=True, sort=False):
        sampled = _spread_events(
            group,
            maximum_events=int(config["maximum_events"]),
        )
        for order, row in enumerate(sampled.itertuples(index=False)):
            rows.append(
                {
                    "author_id": str(author),
                    "context": str(context),
                    "order": order,
                    "text": str(row.text),
                    "timestamp": row.timestamp,
                    "lang": (
                        "<missing>" if pd.isna(row.lang) else str(row.lang)
                    ),
                    "symbol": (
                        "<missing>" if pd.isna(row.symbol) else str(row.symbol)
                    ),
                }
            )
    events = pd.DataFrame(rows)
    schema = {
        "corpus": "x_market",
        "source": str(path),
        "source_rows": int(len(raw)),
        "authors": int(events["author_id"].nunique()),
        "events": int(len(events)),
        "contexts": contexts,
        "context_role": "COLLECTOR_MEDIATED_OBSERVATIONAL",
        "replicate_type": "SOURCE_POST_DISJOINT_TECHNICAL",
        "external_labels_loaded": False,
        "selection_warning": (
            "query_group is a collector-mediated observed stratum, not an "
            "author choice or causal pre-response context"
        ),
    }
    return events, schema


def _table(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    for column in frame.columns:
        if frame[column].map(lambda value: isinstance(value, (list, dict))).any():
            frame[column] = frame[column].map(
                lambda value: json.dumps(value, ensure_ascii=False)
                if isinstance(value, (list, dict))
                else value
            )
    return frame


def _non_d0_coordinates(
    panel: CorpusFeaturePanel,
    calibration: Any,
) -> tuple[pd.DataFrame, np.ndarray]:
    pieces = []
    metadata_parts = []
    for split in ("D1", "D2"):
        metadata, values = author_coordinates(panel, calibration, split=split)
        if values.shape[1] == 0:
            continue
        metadata_parts.append(metadata)
        pieces.append(values)
    if not pieces:
        return pd.DataFrame(), np.empty((0, 0))
    return pd.concat(metadata_parts, ignore_index=True), np.vstack(pieces)


def _context_relation_objects(
    relation_rows: list[dict[str, Any]],
    agreement_rows: list[dict[str, Any]],
    corpus: str,
) -> list[dict[str, Any]]:
    licensed_contexts = {
        str(row["context"])
        for row in agreement_rows
        if row["corpus"] == corpus
        and row["classification"]
        in {
            "RELATION_OPERATOR_REPLICATED",
            "GAUGE_INVARIANT_EXCESS_SPECTRUM_REPLICATED",
        }
    }
    selected = [
        row
        for row in relation_rows
        if row["corpus"] == corpus
        and row.get("relation_license", 0) == 1
        and str(row["context"]) in licensed_contexts
    ]
    result = []
    contexts = sorted({str(row["context"]) for row in selected})
    for context in contexts:
        rows = [row for row in selected if str(row["context"]) == context]
        if {str(row["split"]) for row in rows} != {"D1", "D2"}:
            continue
        spectra = np.vstack([np.asarray(row["spectrum"], dtype=float) for row in rows])
        result.append(
            {
                "context": context,
                "spectrum": spectra.mean(axis=0).tolist(),
                "weight": float(np.mean([row["weight"] for row in rows])),
            }
        )
    return result


def _report(
    *,
    decision: dict[str, Any],
    schemas: list[dict[str, Any]],
    support: pd.DataFrame,
    relation: pd.DataFrame,
    macro: pd.DataFrame,
    transport: pd.DataFrame,
    geometry: pd.DataFrame,
    frgw: pd.DataFrame,
) -> str:
    return (
        "# V8 Real-Text Support-Fibered Relation Field\n\n"
        f"Status: `{decision['status']}`\n\n"
        "This prospective label-free experiment applies one frozen event map and "
        "two non-equivalent measurement families to PANDORA, Essays, and X. "
        "It tests technical support, relation, population geometry, and transport; "
        "it does not name a psychological construct.\n\n"
        "## Data roles\n\n"
        f"{pd.DataFrame(schemas).to_markdown(index=False)}\n\n"
        "## Local support\n\n"
        f"{support.to_markdown(index=False) if not support.empty else 'No resolved support.'}\n\n"
        "## Local relation field\n\n"
        f"{relation.to_markdown(index=False) if not relation.empty else 'No licensed local relation.'}\n\n"
        "## Macro decomposition\n\n"
        f"{macro.to_markdown(index=False) if not macro.empty else 'No multi-context macro field.'}\n\n"
        "## Frozen-source transport\n\n"
        f"{transport.to_markdown(index=False) if not transport.empty else 'No transport estimate.'}\n\n"
        "## Population geometry\n\n"
        f"{geometry.to_markdown(index=False) if not geometry.empty else 'No resolved geometry comparison.'}\n\n"
        "## Support-fibered FRGW synthesis\n\n"
        f"{frgw.to_markdown(index=False) if not frgw.empty else 'No FRGW estimate.'}\n\n"
        "## Decision boundary\n\n"
        f"{decision['claim_boundary']}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    config = _json(args.config)
    spec = RealTextRelationSpec(**config["spec"])
    if args.quick:
        spec = replace(
            spec,
            support_permutations=19,
            relation_permutations=39,
            support_subsamples=9,
            transition_null_draws=min(8, spec.transition_null_draws),
            gw_authors=24,
            gw_iterations=10,
        )
        for corpus in ("pandora", "x_market"):
            config["data"][corpus]["maximum_authors_per_context"] = min(
                80,
                int(config["data"][corpus]["maximum_authors_per_context"]),
            )
        config["data"]["essays"]["maximum_authors"] = min(
            320,
            int(config["data"]["essays"]["maximum_authors"]),
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    loaders = {
        "pandora": load_pandora_events,
        "essays": load_essays_events,
        "x_market": load_x_events,
    }
    panels: dict[str, CorpusFeaturePanel] = {}
    calibrations = {}
    schemas = []
    refusals: list[dict[str, Any]] = []
    local_tables: dict[str, list[dict[str, Any]]] = {
        "support": [],
        "relation": [],
        "macro": [],
        "agreement": [],
    }
    alias_rows = []
    for corpus, loader in loaders.items():
        try:
            events, schema = loader(config["data"][corpus])
            panel = build_feature_panel(
                events,
                corpus=corpus,
                context_role=schema["context_role"],
                replicate_type=schema["replicate_type"],
                spec=spec,
            )
            schema["split_counts"] = panel.metadata["split"].value_counts().to_dict()
            schemas.append(schema)
            calibration = fit_corpus_calibration(corpus, panel, spec=spec)
            panels[corpus] = panel
            calibrations[corpus] = calibration
            alias_rows.append({"corpus": corpus, **calibration.alias})
            result = evaluate_corpus_local(panel, calibration)
            for table in local_tables:
                local_tables[table].extend(result[table])
        except Exception as exc:  # Refusal is an output, not silent omission.
            refusals.append(
                {
                    "corpus": corpus,
                    "arm": "corpus_local",
                    "refusal_code": type(exc).__name__,
                    "evidence": str(exc),
                }
            )

    transport_support: list[dict[str, Any]] = []
    transport_relation: list[dict[str, Any]] = []
    for source, calibration in calibrations.items():
        for target, panel in panels.items():
            if source == target:
                continue
            result = transport_calibration(calibration, panel)
            transport_support.extend(result["support"])
            transport_relation.extend(result["relation"])

    coordinate_panels = {
        corpus: _non_d0_coordinates(panel, calibrations[corpus])
        for corpus, panel in panels.items()
    }
    geometry_rows = []
    context_geometry: dict[tuple[str, str], np.ndarray] = {}
    for corpus_a, corpus_b in corpus_pair_names(panels):
        meta_a, values_a = coordinate_panels[corpus_a]
        meta_b, values_b = coordinate_panels[corpus_b]
        if values_a.shape[1] == 0 or values_b.shape[1] == 0:
            continue
        global_result = approximate_gromov_wasserstein(
            values_a,
            values_b,
            maximum_authors=spec.gw_authors,
            iterations=spec.gw_iterations,
            seed=spec.seed + stable_bucket(
                f"{corpus_a}-{corpus_b}",
                salt="gw-global",
                modulus=100_000,
            ),
        )
        geometry_rows.append(
            {
                "corpus_a": corpus_a,
                "corpus_b": corpus_b,
                "context_a": "<global>",
                "context_b": "<global>",
                **global_result,
            }
        )
        objects_a = _context_relation_objects(
            local_tables["relation"],
            local_tables["agreement"],
            corpus_a,
        )
        objects_b = _context_relation_objects(
            local_tables["relation"],
            local_tables["agreement"],
            corpus_b,
        )
        cost = np.full((len(objects_a), len(objects_b)), np.nan, dtype=float)
        for row, left in enumerate(objects_a):
            mask_a = meta_a["context"].astype(str).eq(left["context"]).to_numpy()
            for column, right in enumerate(objects_b):
                mask_b = meta_b["context"].astype(str).eq(right["context"]).to_numpy()
                result = approximate_gromov_wasserstein(
                    values_a[mask_a],
                    values_b[mask_b],
                    maximum_authors=spec.gw_authors,
                    iterations=spec.gw_iterations,
                    seed=spec.seed
                    + stable_bucket(
                        f"{corpus_a}-{left['context']}-{corpus_b}-{right['context']}",
                        salt="gw-context",
                        modulus=100_000,
                    ),
                )
                geometry_rows.append(
                    {
                        "corpus_a": corpus_a,
                        "corpus_b": corpus_b,
                        "context_a": left["context"],
                        "context_b": right["context"],
                        **result,
                    }
                )
                if result["status"] == "GW_APPROXIMATED":
                    cost[row, column] = float(result["distance"])
        if cost.size and np.isfinite(cost).all():
            context_geometry[(corpus_a, corpus_b)] = cost

    frgw_rows = []
    for corpus_a, corpus_b in corpus_pair_names(panels):
        frgw_rows.append(
            frgw_summary(
                corpus_a,
                corpus_b,
                transport_support,
                _context_relation_objects(
                    local_tables["relation"],
                    local_tables["agreement"],
                    corpus_a,
                ),
                _context_relation_objects(
                    local_tables["relation"],
                    local_tables["agreement"],
                    corpus_b,
                ),
                context_geometry.get((corpus_a, corpus_b)),
            )
        )

    support_frame = _table(local_tables["support"])
    relation_frame = _table(local_tables["relation"])
    macro_frame = _table(local_tables["macro"])
    agreement_frame = _table(local_tables["agreement"])
    alias_frame = _table(alias_rows)
    transport_support_frame = _table(transport_support)
    transport_relation_frame = _table(transport_relation)
    geometry_frame = _table(geometry_rows)
    frgw_frame = _table(frgw_rows)
    refusals_frame = _table(refusals)

    outputs = {
        "support.csv": support_frame,
        "alias_audit.csv": alias_frame,
        "relation_field.csv": relation_frame,
        "relation_agreement.csv": agreement_frame,
        "macro.csv": macro_frame,
        "support_transport.csv": transport_support_frame,
        "transport_relation.csv": transport_relation_frame,
        "population_geometry.csv": geometry_frame,
        "frgw.csv": frgw_frame,
        "refusals.csv": refusals_frame,
    }
    for name, frame in outputs.items():
        frame.to_csv(args.output_dir / name, index=False)
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(schemas, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    energy_licensed = (
        agreement_frame.assign(
            energy_confirmed=agreement_frame["classification"].ne(
                "RELATION_NOT_REPLICATED"
            )
        )
        .groupby("corpus")["energy_confirmed"]
        .max()
        if not agreement_frame.empty
        else pd.Series(dtype=float)
    )
    relation_licensed = (
        agreement_frame.groupby("corpus")["d1_d2_agreement"].max()
        if not agreement_frame.empty
        else pd.Series(dtype=float)
    )
    transport_accepted = (
        transport_support_frame.groupby(["source", "target"])["decision"]
        .apply(lambda values: bool((values == "TRANSPORT_SUPPORT_ACCEPT").all()))
        if not transport_support_frame.empty
        else pd.Series(dtype=bool)
    )
    if int(relation_licensed.sum()) >= 2 and int(transport_accepted.sum()) == 0:
        status = "UNIVERSAL_PROCEDURE_LOCAL_SUPPORT_OBSERVED"
    elif int(relation_licensed.sum()) >= 2 and int(transport_accepted.sum()) > 0:
        status = "CROSS_CORPUS_TECHNICAL_RELATION_CANDIDATE"
    elif int(relation_licensed.sum()) >= 1:
        status = "REALTEXT_TECHNICAL_RELATION_PARTIAL"
    elif int(energy_licensed.sum()) >= 2:
        status = "REALTEXT_SOFT_SUPPORT_DEPENDENCE_ENERGY_ONLY"
    elif len(panels) >= 2 and not support_frame.empty:
        status = "REALTEXT_SOFT_SUPPORT_ONLY_RELATION_UNRESOLVED"
    else:
        status = "REALTEXT_RELATION_NOT_RESOLVED"
    decision = {
        "status": status,
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "corpora_completed": sorted(panels),
        "local_relation_corpora": sorted(
            relation_licensed.loc[
                relation_licensed.astype(bool)
            ].index.astype(str)
        ),
        "dependence_energy_corpora": sorted(
            energy_licensed.loc[
                energy_licensed.astype(bool)
            ].index.astype(str)
        ),
        "accepted_transport_pairs": [
            list(index)
            for index, accepted in transport_accepted.items()
            if bool(accepted)
        ],
        "refusal_count": int(len(refusals_frame)),
        "exploratory_frgw": True,
        "claim_boundary": config["claim_boundary"],
    }
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = _report(
        decision=decision,
        schemas=schemas,
        support=support_frame,
        relation=relation_frame,
        macro=macro_frame,
        transport=transport_support_frame,
        geometry=geometry_frame,
        frgw=frgw_frame,
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
