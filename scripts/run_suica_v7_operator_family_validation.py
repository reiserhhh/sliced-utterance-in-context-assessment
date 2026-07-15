#!/usr/bin/env python3
"""Run the registered V7 cross-representation operator family with max-T FWER.

This is intentionally label-free.  It tests text-geometry transport among
predeclared operators and two TF-IDF representations.  It does not discover or
name psychological factors, and a non-significant view-private comparison is
reported as unresolved rather than as an absence of author structure.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v7_condition_opportunity import _eligible_users  # noqa: E402
from scripts.run_suica_v7_operator_smoke import DEFAULT_INPUT, _infer_column, _load_config, _read_table, _write_json  # noqa: E402
from suica_core.v7_governance import write_artifact_inventory  # noqa: E402
from suica_core.v7_multiview import (  # noqa: E402
    common_feature_columns,
    evaluate_cross_view,
    fit_block_scalers,
    fit_consensus_model,
    fit_direct_predictors,
    transform_feature_block,
)
from suica_core.v7_operator_controls import source_disjoint_partition  # noqa: E402
from suica_core.v7_observations import ObservationSpec, build_observations, canonicalize_comments, prepare_source_panel, select_reference_authors  # noqa: E402
from suica_core.v7_psychometric import author_features_from_embeddings  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v7_operator_family_registry.json"
DEFAULT_E0 = ROOT / "results" / "v7_operator_boundary_audit" / "e0_full_20260714" / "scores_native.csv"
DEFAULT_E1 = ROOT / "results" / "v7_multiview_projection" / "e1_full_20260714" / "author_features_native.csv"
DEFAULT_E2_CONFIG = ROOT / "configs" / "v7_condition_opportunity.json"


def parse_args() -> argparse.Namespace:
    """Parse a registered operator-family validation request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--e0-cohort", type=Path, default=DEFAULT_E0)
    parser.add_argument("--e1-cohort", type=Path, default=DEFAULT_E1)
    parser.add_argument("--e2-config", type=Path, default=DEFAULT_E2_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _read_user_ids(path: Path) -> set[str]:
    """Read prior-cohort identifiers locally only to prevent author reuse."""
    if not path.exists():
        raise FileNotFoundError(f"Required prior cohort artifact is missing: {path}")
    return set(pd.read_csv(path, usecols=["user_id"])["user_id"].dropna().astype(str))


def _operator_specs(config: dict[str, Any]) -> list[ObservationSpec]:
    defaults = {
        "min_tokens": int(config["min_tokens_per_unit"]),
        "max_units_per_user": int(config["max_units_per_user"]),
        "max_source_comments_per_user": int(config["max_source_comments_per_user"]),
        "max_source_tokens_per_user": int(config["max_source_tokens_per_user"]),
    }
    return [ObservationSpec(**{**defaults, **raw}) for raw in config["operators"]]


def _fit_representation(texts: pd.Series, spec: dict[str, Any], seed: int) -> tuple[TfidfVectorizer, TruncatedSVD]:
    vectorizer = TfidfVectorizer(
        analyzer=str(spec["analyzer"]),
        lowercase=True,
        strip_accents="unicode",
        ngram_range=tuple(int(value) for value in spec["ngram_range"]),
        max_features=int(spec["max_features"]),
        min_df=1,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(texts.fillna("").astype(str))
    components = min(int(spec["svd_dimensions"]), matrix.shape[0] - 1, matrix.shape[1] - 1)
    if components < 2:
        raise RuntimeError(f"Representation {spec['name']} has insufficient discovery rank: {matrix.shape}")
    svd = TruncatedSVD(n_components=int(components), random_state=seed)
    svd.fit(matrix)
    return vectorizer, svd


def _transform(vectorizer: TfidfVectorizer, svd: TruncatedSVD, texts: pd.Series) -> np.ndarray:
    return svd.transform(vectorizer.transform(texts.fillna("").astype(str)))


def _aligned_ids(frames: dict[str, pd.DataFrame], views: tuple[str, ...], split: str) -> list[str]:
    shared: set[str] | None = None
    for view in views:
        ids = set(frames[view].loc[frames[view]["split"].eq(split), "user_id"].astype(str))
        shared = ids if shared is None else shared.intersection(ids)
    return sorted(shared or set())


def _blocks(frames: dict[str, pd.DataFrame], scalers: dict, views: tuple[str, ...], ids: list[str]) -> dict[str, np.ndarray]:
    return {view: transform_feature_block(frames[view], scaler=scalers[view], user_ids=ids) for view in views}


def _global_r2(target: np.ndarray, prediction: np.ndarray) -> float:
    denominator = float(np.sum((target - np.mean(target, axis=0, keepdims=True)) ** 2))
    return float(1.0 - np.sum((target - prediction) ** 2) / denominator) if denominator > 1e-14 else float("nan")


def _cross_rep_prediction(train_source: np.ndarray, train_target: np.ndarray, test_source: np.ndarray, test_target: np.ndarray, *, alpha: float) -> float:
    model = Ridge(alpha=float(alpha), fit_intercept=True).fit(train_source, train_target)
    return _global_r2(test_target, model.predict(test_source))


def _source_disjoint_alignment_auc(left: np.ndarray, right: np.ndarray, *, pairing: np.ndarray | None = None) -> float:
    """Measure own-vs-stranger source-disjoint alignment without a linear map.

    This is a technical author-alignment metric.  It asks whether a left-half
    feature vector is closer to its own right-half vector than to the other
    right-half authors. It does not identify a factor or a psychological trait.
    """
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    if x.shape != y.shape or len(x) < 2:
        return float("nan")
    selected = np.arange(len(x), dtype=int) if pairing is None else np.asarray(pairing, dtype=int)
    distances = np.linalg.norm(x[:, None, :] - y[None, :, :], axis=2)
    values: list[float] = []
    for index, own_index in enumerate(selected):
        own = distances[index, own_index]
        strangers = np.delete(distances[index], own_index)
        values.append(float(np.mean(own < strangers) + 0.5 * np.mean(own == strangers)))
    return float(np.mean(values))


def _derive_prior_exclusions(canonical: pd.DataFrame, *, e0: Path, e1: Path, e2_config_path: Path) -> set[str]:
    """Reconstruct E2's deterministic cohort without exporting its author IDs."""
    excluded = _read_user_ids(e0).union(_read_user_ids(e1))
    e2 = _load_config(e2_config_path)
    eligible = _eligible_users(canonical, e2)
    candidate = canonical.loc[canonical["user_id"].astype(str).isin(eligible)].copy()
    e2_selected = select_reference_authors(
        candidate,
        min_comments_per_user=int(e2["min_comments_per_user"]),
        max_users=int(e2["max_users"]),
        seed=int(e2["seed"]),
        exclude_user_ids=excluded,
        cohort_salt="v7.1-e2-condition-opportunity-v1",
    )
    return excluded.union(set(e2_selected["user_id"].astype(str)))


def _max_t_adjust(actual: pd.DataFrame, null_max: np.ndarray) -> pd.DataFrame:
    output = actual.copy()
    output["max_t_fwer_p"] = [float((1 + np.sum(null_max >= value)) / (len(null_max) + 1)) for value in output["statistic"]]
    output["status"] = np.where(output["max_t_fwer_p"] <= 0.05, "FWER_SUPPORTED", "UNRESOLVED_VIEW_SPECIFIC")
    return output


def _write_report(path: Path, *, output_dir: Path, manifest: dict[str, Any], endpoints: pd.DataFrame, alignment: pd.DataFrame, null_count: int) -> None:
    table = endpoints.to_markdown(index=False, floatfmt=".3f")
    alignment_table = alignment.to_markdown(index=False, floatfmt=".3f")
    text = f"""# SUICA V7 Registered Cross-Representation Operator Family

## Design

This run freezes five observation operators and two representations before any
result inspection: `whole`, `native`, `sentence_pack_160`,
`fixed_128_cross`, `fixed_128_within_comment`; `WORD12_TFIDF_SVD24` and
`CHAR35_TFIDF_SVD24`. The selected cohort excludes reconstructed E0, E1, and
E2 author cohorts. No external label was read.

All shared-subspace, directed-edge, same-operator cross-representation, and
source-disjoint technical-transport endpoints are corrected together by one
synchronized max-T permutation family (`B={null_count}`). A failed endpoint is
`UNRESOLVED_VIEW_SPECIFIC`; it is not evidence that an operator's private
structure is absent or noise.

## Endpoints

{table}

## Source-Disjoint Alignment Control

This separate AUC family does not require a linear coordinate map. It compares
each source-disjoint left half with its own right half against right-half
strangers. It distinguishes stable relative author positioning from failure of
the stricter linear transport endpoint above. Its max-T correction is confined
to the ten registered alignment endpoints and is not pooled with R2 values.

{alignment_table}

## Claim Boundary

These results can establish only registered, author-aligned transport within
the declared corpus, operator family, and representations. They do not name
factors, establish a universal best slice, identify personality, or license
clinical interpretation. `FWER_SUPPORTED` establishes only a registered
endpoint. A stronger `SHARED_WITHIN_OPERATOR_SET` label additionally requires
bootstrap loading-subspace recurrence and an independent fresh confirmation
family; it is not granted by this run alone.

## Artifacts

- `{output_dir / 'registered_endpoints.csv'}`
- `{output_dir / 'max_t_null.parquet'}` (or CSV fallback)
- `{output_dir / 'source_disjoint_alignment.csv'}`
- `{output_dir / 'source_disjoint_alignment_max_t_null.parquet'}` (or CSV fallback)
- `{output_dir / 'run_manifest.json'}`
- `{output_dir / 'artifact_inventory.json'}`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    config = _load_config(args.config)
    if args.quick:
        config["max_users"] = min(int(config["max_users"]), 120)
        config["max_source_comments_per_user"] = min(int(config["max_source_comments_per_user"]), 16)
        config["min_comments_per_user"] = min(int(config["min_comments_per_user"]), 16)
        config["max_units_per_user"] = min(int(config["max_units_per_user"]), 64)
        config["permutation_iterations"] = min(int(config["permutation_iterations"]), 29)
        for rep in config["representations"]:
            rep["max_features"] = min(int(rep["max_features"]), 2000)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw = _read_table(args.input)
    columns = [str(column) for column in raw.columns]
    column_map = {
        "user": _infer_column(columns, ["author", "user_id", "participant_id", "user", "id"], None, required=True),
        "text": _infer_column(columns, ["body", "text", "comment", "content", "message"], None, required=True),
        "order": _infer_column(columns, ["created_utc", "timestamp", "time", "date", "created_at"], None, required=False),
        "condition": _infer_column(columns, ["subreddit", "condition", "platform", "task", "forum"], None, required=False),
    }
    canonical = canonicalize_comments(raw, user_col=column_map["user"], text_col=column_map["text"], order_col=column_map["order"], condition_col=column_map["condition"], min_tokens=int(config["min_tokens_per_unit"]))
    excluded = _derive_prior_exclusions(canonical, e0=args.e0_cohort, e1=args.e1_cohort, e2_config_path=args.e2_config)
    selected = select_reference_authors(
        canonical,
        min_comments_per_user=int(config["min_comments_per_user"]),
        max_users=int(config["max_users"]),
        seed=int(config["seed"]),
        exclude_user_ids=excluded,
        cohort_salt="v7.2-registered-operator-family-1",
    )
    specs = _operator_specs(config)
    source_panel = prepare_source_panel(selected, specs[0])
    split_counts = source_panel.groupby("split", observed=True)["user_id"].nunique().to_dict()
    if min(int(split_counts.get(split, 0)) for split in ("discovery", "calibration", "confirmation")) < 16:
        raise RuntimeError(f"Insufficient fresh operator-family split support: {split_counts}")
    views = tuple(spec.name for spec in specs)
    units = {spec.name: build_observations(source_panel, spec) for spec in specs}
    source_left, source_right = source_disjoint_partition(source_panel, seed=int(config["seed"]) + 71)
    if set(source_left["source_row"].astype(int)).intersection(source_right["source_row"].astype(int)):
        raise RuntimeError("Source-disjoint operator family split leaked source comments.")
    records: dict[str, dict[str, Any]] = {}
    disjoint_records: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    alignment_records: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    endpoints: list[dict[str, Any]] = []
    for rep_index, rep in enumerate(config["representations"]):
        vectorizer, svd = _fit_representation(source_panel.loc[source_panel["split"].eq("discovery"), "text"], rep, int(config["seed"]) + rep_index)
        frames = {view: author_features_from_embeddings(units[view], _transform(vectorizer, svd, units[view]["text"])) for view in views}
        feature_names = common_feature_columns(frames, views)
        discovery_ids = _aligned_ids(frames, views, "discovery")
        calibration_ids = _aligned_ids(frames, views, "calibration")
        confirmation_ids = _aligned_ids(frames, views, "confirmation")
        scalers = fit_block_scalers(frames, view_names=views, feature_names=feature_names, discovery_user_ids=discovery_ids)
        train_ids = [*discovery_ids, *calibration_ids]
        train = _blocks(frames, scalers, views, train_ids)
        confirmation = _blocks(frames, scalers, views, confirmation_ids)
        model = fit_consensus_model(train, view_names=views, rank=int(config["shared_rank"]), ridge_alpha=float(config["ridge_alpha"]))
        direct = fit_direct_predictors(train, view_names=views, ridge_alpha=float(config["ridge_alpha"]))
        permuted = fit_direct_predictors(train, view_names=views, ridge_alpha=float(config["ridge_alpha"]), permutation_seed=int(config["seed"]) + 91 + rep_index)
        cross = evaluate_cross_view(confirmation, model=model, direct_models=direct, permuted_models=permuted)
        endpoints.append({"family_component": "shared_subspace", "representation": rep["name"], "source": "all_views", "target": "all_views", "statistic": float(cross["consensus_global_r2"].mean())})
        for row in cross.itertuples(index=False):
            endpoints.append({"family_component": "directed_edge", "representation": rep["name"], "source": row.source_view, "target": row.target_view, "statistic": float(row.direct_global_r2)})
        records[rep["name"]] = {
            "vectorizer": vectorizer, "svd": svd, "frames": frames, "scalers": scalers,
            "train": train, "confirmation": confirmation, "model": model,
            "confirmation_ids": confirmation_ids,
        }
        left_units = {view: build_observations(source_left, spec) for view, spec in zip(views, specs, strict=True)}
        right_units = {view: build_observations(source_right, spec) for view, spec in zip(views, specs, strict=True)}
        for view in views:
            left_frame = author_features_from_embeddings(
                left_units[view], _transform(vectorizer, svd, left_units[view]["text"])
            )
            right_frame = author_features_from_embeddings(
                right_units[view], _transform(vectorizer, svd, right_units[view]["text"])
            )
            paired = {"left": left_frame, "right": right_frame}
            paired_ids = {
                split: _aligned_ids(paired, ("left", "right"), split)
                for split in ("discovery", "calibration", "confirmation")
            }
            if min(len(value) for value in paired_ids.values()) < 16:
                raise RuntimeError(f"Insufficient source-disjoint support for {rep['name']}::{view}: {paired_ids}")
            paired_features = common_feature_columns(paired, ("left", "right"))
            paired_scalers = fit_block_scalers(
                paired,
                view_names=("left", "right"),
                feature_names=paired_features,
                discovery_user_ids=paired_ids["discovery"],
            )
            paired_train_ids = [*paired_ids["discovery"], *paired_ids["calibration"]]
            left_train = transform_feature_block(left_frame, scaler=paired_scalers["left"], user_ids=paired_train_ids)
            right_train = transform_feature_block(right_frame, scaler=paired_scalers["right"], user_ids=paired_train_ids)
            left_confirm = transform_feature_block(left_frame, scaler=paired_scalers["left"], user_ids=paired_ids["confirmation"])
            right_confirm = transform_feature_block(right_frame, scaler=paired_scalers["right"], user_ids=paired_ids["confirmation"])
            endpoints.append({
                "family_component": "source_disjoint_transport",
                "representation": rep["name"],
                "source": view,
                "target": view,
                "statistic": _cross_rep_prediction(
                    left_train,
                    right_train,
                    left_confirm,
                    right_confirm,
                    alpha=float(config["ridge_alpha"]),
                ),
            })
            disjoint_records[(rep["name"], view)] = {
                "left_train": left_train,
                "right_train": right_train,
                "left_confirm": left_confirm,
                "right_confirm": right_confirm,
            }
            alignment_records[(rep["name"], view)] = {
                "left_confirm": left_confirm,
                "right_confirm": right_confirm,
            }
        joblib.dump({"vectorizer": vectorizer, "svd": svd, "scalers": scalers, "model": model, "views": views}, args.output_dir / f"runtime_{rep['name']}.joblib")
    first, second = [rep["name"] for rep in config["representations"]]
    for view in views:
        for source_rep, target_rep in ((first, second), (second, first)):
            source = records[source_rep]
            target = records[target_rep]
            score = _cross_rep_prediction(source["train"][view], target["train"][view], source["confirmation"][view], target["confirmation"][view], alpha=float(config["ridge_alpha"]))
            endpoints.append({"family_component": "cross_representation", "representation": f"{source_rep}->{target_rep}", "source": view, "target": view, "statistic": score})
    endpoint_frame = pd.DataFrame(endpoints)
    alignment_frame = pd.DataFrame([
        {
            "representation": rep["name"],
            "operator": view,
            "statistic": _source_disjoint_alignment_auc(
                alignment_records[(rep["name"], view)]["left_confirm"],
                alignment_records[(rep["name"], view)]["right_confirm"],
            ),
        }
        for rep in config["representations"]
        for view in views
    ])
    rng = np.random.default_rng(int(config["seed"]) + 999)
    null_rows: list[dict[str, float]] = []
    alignment_null_rows: list[dict[str, float]] = []
    for iteration in range(int(config["permutation_iterations"])):
        null_statistics: list[float] = []
        for rep in config["representations"]:
            record = records[rep["name"]]
            train = record["train"]
            shuffled = {view: values.copy() for view, values in train.items()}
            for view in views[1:]:
                shuffled[view] = shuffled[view][rng.permutation(len(shuffled[view]))]
            null_model = fit_consensus_model(shuffled, view_names=views, rank=int(config["shared_rank"]), ridge_alpha=float(config["ridge_alpha"]))
            null_direct = fit_direct_predictors(train, view_names=views, ridge_alpha=float(config["ridge_alpha"]), permutation_seed=int(rng.integers(0, 2**31 - 1)))
            null_cross = evaluate_cross_view(record["confirmation"], model=null_model, direct_models=null_direct, permuted_models=null_direct)
            null_statistics.append(float(null_cross["consensus_global_r2"].mean()))
            null_statistics.extend(float(value) for value in null_cross["direct_global_r2"])
        for view in views:
            for source_rep, target_rep in ((first, second), (second, first)):
                source, target = records[source_rep], records[target_rep]
                target_train = target["train"][view][rng.permutation(len(target["train"][view]))]
                null_statistics.append(_cross_rep_prediction(source["train"][view], target_train, source["confirmation"][view], target["confirmation"][view], alpha=float(config["ridge_alpha"])))
        for rep in config["representations"]:
            for view in views:
                record = disjoint_records[(rep["name"], view)]
                permuted_target = record["right_train"][rng.permutation(len(record["right_train"]))]
                null_statistics.append(_cross_rep_prediction(
                    record["left_train"],
                    permuted_target,
                    record["left_confirm"],
                    record["right_confirm"],
                    alpha=float(config["ridge_alpha"]),
                ))
        null_rows.append({"permutation": int(iteration), "max_statistic": float(np.nanmax(null_statistics))})
        alignment_null_rows.append({
            "permutation": int(iteration),
            "max_statistic": float(np.nanmax([
                _source_disjoint_alignment_auc(
                    alignment_records[(rep["name"], view)]["left_confirm"],
                    alignment_records[(rep["name"], view)]["right_confirm"],
                    pairing=rng.permutation(len(alignment_records[(rep["name"], view)]["left_confirm"])),
                )
                for rep in config["representations"]
                for view in views
            ])),
        })
    null = pd.DataFrame(null_rows)
    alignment_null = pd.DataFrame(alignment_null_rows)
    adjusted = _max_t_adjust(endpoint_frame, null["max_statistic"].to_numpy(float))
    alignment_adjusted = _max_t_adjust(alignment_frame, alignment_null["max_statistic"].to_numpy(float)).rename(columns={"statistic": "alignment_auc", "status": "alignment_status", "max_t_fwer_p": "alignment_max_t_fwer_p"})
    adjusted.to_csv(args.output_dir / "registered_endpoints.csv", index=False)
    alignment_adjusted.to_csv(args.output_dir / "source_disjoint_alignment.csv", index=False)
    null_path = args.output_dir / "max_t_null.parquet"
    try:
        null.to_parquet(null_path, index=False)
        null_format = "parquet"
    except (ImportError, ModuleNotFoundError):
        null_path = args.output_dir / "max_t_null.csv"
        null.to_csv(null_path, index=False)
        null_format = "csv_fallback_missing_parquet_engine"
    alignment_null_path = args.output_dir / "source_disjoint_alignment_max_t_null.parquet"
    try:
        alignment_null.to_parquet(alignment_null_path, index=False)
        alignment_null_format = "parquet"
    except (ImportError, ModuleNotFoundError):
        alignment_null_path = args.output_dir / "source_disjoint_alignment_max_t_null.csv"
        alignment_null.to_csv(alignment_null_path, index=False)
        alignment_null_format = "csv_fallback_missing_parquet_engine"
    manifest = {
        "timestamp_utc": datetime.now(UTC).isoformat(), "config": config,
        "input": str(args.input), "column_map": column_map,
        "n_selected_authors": int(source_panel["user_id"].nunique()),
        "split_counts": {key: int(value) for key, value in split_counts.items()},
        "source_disjoint_overlap_count": 0,
        "prior_author_exclusions": int(len(excluded)), "external_labels_read": False,
        "multiplicity_family": config["family"], "max_t_permutations": int(len(null)),
        "null_artifact": str(null_path), "null_artifact_format": null_format,
        "source_disjoint_alignment_family": "registered_source_disjoint_own_vs_stranger_max_t",
        "source_disjoint_alignment_null_artifact": str(alignment_null_path),
        "source_disjoint_alignment_null_artifact_format": alignment_null_format,
        "claim_boundary": "Registered operator-family transport only; no personality or clinical interpretation.",
    }
    _write_json(args.output_dir / "run_manifest.json", manifest)
    _write_report(args.report, output_dir=args.output_dir, manifest=manifest, endpoints=adjusted, alignment=alignment_adjusted, null_count=len(null))
    inventory = write_artifact_inventory(args.output_dir, args.output_dir / "artifact_inventory.json")
    print(json.dumps({"output_dir": str(args.output_dir), "report": str(args.report), "n_endpoints": len(adjusted), "n_fwer_supported": int(adjusted["status"].eq("FWER_SUPPORTED").sum()), "n_alignment_supported": int(alignment_adjusted["alignment_status"].eq("FWER_SUPPORTED").sum()), "artifact_files": inventory["n_files"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
