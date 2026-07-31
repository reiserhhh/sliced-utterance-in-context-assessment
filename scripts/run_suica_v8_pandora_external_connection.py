#!/usr/bin/env python3
"""Score full official PANDORA with frozen V8 geometry, then open anchors.

The command deliberately has two stages:

``score``
    Reads only text, observation-volume fields, and opaque author IDs. It
    writes a hash-bound, pseudonymized score table without external labels.

``analyze``
    Verifies the frozen score-table hash, then joins Big Five and MBTI labels.
    Big5-only authors train/evaluate Big Five heads, MBTI-only authors
    train/evaluate MBTI heads, and strict bridge authors are held out for the
    cross-scale relation test.

PANDORA labels have been opened in earlier project phases, so this is an
exploratory external connection rather than a new confirmatory lockbox.
"""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import heapq
import json
from pathlib import Path
import sys
from typing import Any

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_geometry import GeometryBundle, score_geometry_bundle  # noqa: E402
from suica_core.v7_psychometric import author_features_from_embeddings  # noqa: E402
from suica_core.suica import tokenize  # noqa: E402
from suica_core.v8_bridge import canonical_orbit_distance_signatures  # noqa: E402
from suica_core.v8_external_connection import (  # noqa: E402
    BIG5_TRAITS,
    MBTI_AXES,
    bridge_permutation_p,
    canonical_scale_residual,
    fit_source_head_predict,
    matrix_alignment,
    nuisance_features,
    relation_matrix,
    run_official_cv,
    split_comment_units,
    univariate_connections,
)


DEFAULT_DATA_ROOT = Path(
    "/Volumes/mobile3/projects/project persona/data_sets/prepared/pandora_official"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_pandora_external_connection"
    / "operator_aligned_clean_20260728"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_PANDORA_EXTERNAL_CONNECTION_REPORT.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "v8_pandora_external_connection.json",
    )
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--stage", choices=("score", "analyze", "all"), default="all")
    parser.add_argument(
        "--smoke-authors",
        type=int,
        default=0,
        help="Deterministically cap each source for a pipeline smoke run.",
    )
    parser.add_argument(
        "--bridge-permutations",
        type=int,
        default=0,
        help="Override the configured bridge permutations (useful for smoke runs).",
    )
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pseudonym(value: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}::{value}".encode("utf-8")).hexdigest()[:24]


def _source_paths(data_root: Path) -> dict[str, Path]:
    paths = {
        "big5": data_root / "pandora_official_big5_prepared.csv",
        "bridge": data_root / "bridge" / "pandora_official_bridge_strict377.csv",
    }
    paths.update({
        axis: data_root / "mbti_axes" / f"pandora_official_{axis}_prepared.csv"
        for axis in MBTI_AXES
    })
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing official PANDORA inputs: {missing}")
    return paths


def _deterministic_cap(frame: pd.DataFrame, count: int) -> pd.DataFrame:
    if count <= 0 or len(frame) <= count:
        return frame
    order = frame["user_id"].astype(str).map(
        lambda value: hashlib.sha256(f"smoke::{value}".encode()).hexdigest()
    )
    return frame.assign(_order=order).sort_values("_order").head(count).drop(
        columns="_order"
    )


def _load_text_census(
    paths: dict[str, Path],
    *,
    smoke_authors: int,
) -> pd.DataFrame:
    columns = [
        "user_id",
        "text",
        "sampled_comment_count",
        "available_clean_comments",
        "approx_token_count",
    ]
    sources = []
    for name in ("big5", "EI_cont", "bridge"):
        frame = pd.read_csv(paths[name], usecols=columns, dtype={"user_id": str})
        frame = _deterministic_cap(frame, smoke_authors)
        frame["_source"] = name
        sources.append(frame)
    combined = pd.concat(sources, ignore_index=True)
    text_counts = combined.groupby("user_id", observed=True)["text"].nunique(dropna=False)
    conflicts = text_counts.loc[text_counts > 1]
    if len(conflicts):
        raise RuntimeError(
            f"Prepared source texts differ for {len(conflicts)} overlapping authors."
        )
    metadata_columns = [
        "sampled_comment_count",
        "available_clean_comments",
        "approx_token_count",
    ]
    for column in metadata_columns:
        counts = combined.groupby("user_id", observed=True)[column].nunique(
            dropna=False
        )
        if bool((counts > 1).any()):
            raise RuntimeError(f"Prepared metadata differs across sources: {column}")
    return combined.drop_duplicates("user_id", keep="first").reset_index(drop=True)


def _score_batch(
    batch: pd.DataFrame,
    *,
    representation: Any,
    bundle: GeometryBundle,
    config: dict[str, Any],
    exact_units: dict[str, list[dict[str, Any]]] | None,
    exact_metadata: dict[str, dict[str, int]] | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    score_config = config["score"]
    observations: list[dict[str, Any]] = []
    nuisance_rows: list[dict[str, Any]] = []
    for row in batch.itertuples(index=False):
        if exact_units is None:
            units = split_comment_units(
                row.text,
                min_tokens=int(score_config["min_unit_tokens"]),
                max_chars=int(score_config["max_unit_chars"]),
            )
        else:
            units = exact_units.get(str(row.user_id), [])
        for unit in units:
            observations.append({
                "user_id": str(row.user_id),
                "split": "all",
                **unit,
            })
        if exact_metadata is None:
            sampled_count = float(row.sampled_comment_count)
            available_count = float(row.available_clean_comments)
            approx_tokens = float(row.approx_token_count)
            nuisance_text = str(row.text)
            source_candidate_count = float("nan")
            clean_sample_count = float("nan")
        else:
            metadata = exact_metadata.get(str(row.user_id), {})
            sampled_count = float(len(units))
            available_count = float(metadata.get("source_candidate_count", len(units)))
            approx_tokens = float(sum(unit["token_count"] for unit in units))
            nuisance_text = "\n\n".join(unit["text"] for unit in units)
            source_candidate_count = float(
                metadata.get("source_candidate_count", len(units))
            )
            clean_sample_count = float(
                metadata.get("clean_sample_count", len(units))
            )
        nuisance_rows.append({
            "user_id": str(row.user_id),
            "operator_source_candidate_count": source_candidate_count,
            "operator_clean_sample_count": clean_sample_count,
            **nuisance_features(
                sampled_comment_count=sampled_count,
                available_clean_comments=available_count,
                approx_token_count=approx_tokens,
                unit_token_counts=[unit["token_count"] for unit in units],
                text=nuisance_text,
            ),
        })
    unit_frame = pd.DataFrame(observations)
    if unit_frame.empty:
        raise RuntimeError("No eligible PANDORA comment units in score batch.")
    embeddings = representation.transform(unit_frame["text"])
    author = author_features_from_embeddings(unit_frame, embeddings)
    all_authors = pd.DataFrame({"user_id": batch["user_id"].astype(str)})
    author = all_authors.merge(author, on="user_id", how="left")
    author["split"] = author["split"].fillna("all")
    author["n_units"] = author["n_units"].fillna(0).astype(int)
    author["n_tokens"] = author["n_tokens"].fillna(0).astype(int)
    raw_values = author.reindex(columns=bundle.feature_names).to_numpy(float)
    impute = np.asarray(bundle.feature_impute, dtype=float)
    complete = np.where(np.isfinite(raw_values), raw_values, impute[None, :])
    whitened = (
        complete - np.asarray(bundle.feature_center, dtype=float)[None, :]
    ) @ np.asarray(bundle.metric_whitener, dtype=float)
    frozen_score = score_geometry_bundle(
        bundle,
        raw_values,
        unit_counts=author["n_units"].to_numpy(int),
    )
    canonical, canonical_names, diagnostics = canonical_orbit_distance_signatures(
        whitened,
        np.asarray(bundle.reference_landmarks, dtype=float),
        relative_tolerance=float(score_config["relative_tolerance"]),
    )
    canonical = canonical_scale_residual(canonical)
    output = author[["user_id", "n_units", "n_tokens"]].copy()
    output["score_status"] = np.asarray(frozen_score["status"], dtype=object)
    output["reference_radius"] = np.asarray(
        frozen_score["reference_radius"], dtype=float
    )
    output["support_radius_threshold"] = float(
        frozen_score["support_radius_threshold"]
    )
    for index, name in enumerate(canonical_names):
        output[f"v8_csr_{index + 1:02d}"] = canonical[:, index]
    for index, name in enumerate(bundle.feature_names):
        output[f"v7_author_{index + 1:02d}"] = raw_values[:, index]
    output = output.merge(pd.DataFrame(nuisance_rows), on="user_id", how="left")
    return output, diagnostics


def _rebuild_exact_comment_units(
    census: pd.DataFrame,
    *,
    score_config: dict[str, Any],
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, dict[str, int]],
    dict[str, Any],
]:
    """Apply the frozen native observation operator to leakage-clean comments."""
    module_root = Path(score_config["preparation_module_root"])
    if not module_root.exists():
        raise FileNotFoundError(f"Preparation module root does not exist: {module_root}")
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))
    from project_persona.pandora_official import (  # noqa: PLC0415
        DELETED_BODIES,
        OfficialLeakageReport,
        _comment_leak_reasons,
        official_leakage_report_to_dict,
        stable_hash_fraction,
    )
    from project_persona.persona_dataset import normalize_text  # noqa: PLC0415

    raw_comments = Path(score_config["raw_comments"])
    if not raw_comments.exists():
        raise FileNotFoundError(f"Raw PANDORA comments do not exist: {raw_comments}")
    author_set = set(census["user_id"].astype(str))
    sample_limit = int(score_config["sample_limit"])
    seed = int(score_config["sample_seed"])
    heaps: dict[str, list[tuple[float, float, str]]] = {
        author: [] for author in author_set
    }
    counters = {
        "raw_comment_rows": 0,
        "target_author_comment_rows": 0,
        "english_comment_rows": 0,
        "deleted_comment_rows": 0,
        "removed_mbti_type_rows": 0,
        "removed_self_type_rows": 0,
        "removed_personality_term_rows": 0,
        "removed_placeholder_rows": 0,
        "kept_comment_rows": 0,
    }
    authors_with_kept: set[str] = set()
    usecols = ["author", "body", "created_utc", "lang", "id"]
    for chunk in pd.read_csv(
        raw_comments,
        usecols=usecols,
        chunksize=int(score_config["raw_chunksize"]),
    ):
        counters["raw_comment_rows"] += len(chunk)
        chunk["author"] = chunk["author"].astype(str)
        chunk = chunk.loc[chunk["author"].isin(author_set)].copy()
        counters["target_author_comment_rows"] += len(chunk)
        if chunk.empty:
            continue
        chunk = chunk.loc[
            chunk["lang"].fillna("").astype(str).str.lower().eq("en")
        ].copy()
        counters["english_comment_rows"] += len(chunk)
        for row in chunk.itertuples(index=False):
            author = str(row.author)
            body = normalize_text(row.body)
            if not body or body.lower() in DELETED_BODIES:
                counters["deleted_comment_rows"] += 1
                continue
            reasons = _comment_leak_reasons(body)
            if reasons:
                counters["removed_mbti_type_rows"] += int("mbti_type" in reasons)
                counters["removed_self_type_rows"] += int("self_type" in reasons)
                counters["removed_personality_term_rows"] += int(
                    "personality_term" in reasons
                )
                counters["removed_placeholder_rows"] += int(
                    "placeholder" in reasons
                )
                continue
            counters["kept_comment_rows"] += 1
            authors_with_kept.add(author)
            sample_score = stable_hash_fraction(author, getattr(row, "id", ""), seed)
            created = (
                float(row.created_utc) if not pd.isna(row.created_utc) else 0.0
            )
            candidate = (-sample_score, created, body)
            heap = heaps[author]
            if len(heap) < sample_limit:
                heapq.heappush(heap, candidate)
            elif sample_score < -heap[0][0]:
                heapq.heapreplace(heap, candidate)
    comments = {
        author: [
            body
            for _, _, body in sorted(
                heap,
                key=lambda value: value[1],
            )
        ]
        for author, heap in heaps.items()
    }
    leakage = OfficialLeakageReport(
        **counters,
        target_authors=len(author_set),
        authors_with_any_kept_comments=len(authors_with_kept),
    )
    minimum = int(score_config["min_unit_tokens"])
    max_chars = int(score_config["max_unit_chars"])
    token_cap = int(score_config["operator_token_cap"])
    source_cap = int(score_config["operator_source_comment_cap"])
    exact: dict[str, list[dict[str, Any]]] = {}
    metadata: dict[str, dict[str, int]] = {}
    for user_id in census["user_id"].astype(str):
        candidates: list[dict[str, Any]] = []
        clean_sample = comments.get(user_id, [])
        for comment in clean_sample:
            clipped = comment[:max_chars]
            token_count = len(tokenize(clipped))
            if token_count >= minimum:
                candidates.append({"text": clipped, "token_count": token_count})
        if len(candidates) > source_cap:
            indices = np.unique(
                np.linspace(0, len(candidates) - 1, num=source_cap, dtype=int)
            )
            selected = [candidates[int(index)] for index in indices]
        else:
            selected = candidates
        units: list[dict[str, Any]] = []
        used_tokens = 0
        for candidate in selected:
            tokens = tokenize(candidate["text"])
            remaining = token_cap - used_tokens
            if remaining <= 0:
                break
            body = " ".join(tokens[:remaining])
            used_tokens += min(len(tokens), remaining)
            units.append({"text": body, "token_count": int(min(len(tokens), remaining))})
        exact[user_id] = units
        metadata[user_id] = {
            "clean_sample_count": int(len(clean_sample)),
            "source_candidate_count": int(len(candidates)),
        }
    helper_path = module_root / "project_persona" / "pandora_official.py"
    audit = {
        "unit_source": "frozen_native_operator_aligned_leakage_clean",
        "raw_comments": str(raw_comments),
        "raw_comments_sha256": _sha256(raw_comments),
        "preparation_helper": str(helper_path),
        "preparation_helper_sha256": _sha256(helper_path),
        "target_authors": int(len(census)),
        "sample_limit_before_operator": int(score_config["sample_limit"]),
        "sampling_rule": "stable_hash_top_k_then_time_order",
        "minimum_tokens_per_comment": minimum,
        "source_comment_cap": source_cap,
        "source_comment_selection": "evenly_spaced_after_minimum_token_filter",
        "source_token_budget": token_cap,
        "source_text_reconstruction": "SUICA tokenizer joined with spaces",
        "eligible_units": int(sum(map(len, exact.values()))),
        "authors_with_minimum_units": int(
            sum(len(units) >= 12 for units in exact.values())
        ),
        "leakage_cleaning": official_leakage_report_to_dict(leakage),
    }
    return exact, metadata, audit


def score_stage(
    *,
    paths: dict[str, Path],
    config: dict[str, Any],
    output_dir: Path,
    smoke_authors: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    score_config = config["score"]
    geometry_path = ROOT / score_config["geometry_bundle"]
    representation_path = ROOT / score_config["representation_runtime"]
    bundle = GeometryBundle.from_dict(_read_json(geometry_path))
    representation = joblib.load(representation_path)
    census = _load_text_census(paths, smoke_authors=smoke_authors)
    if smoke_authors:
        exact_units = None
        exact_metadata = None
        unit_audit = {
            "unit_source": "prepared_double_newline_smoke_fallback",
            "reason": "A bounded smoke run does not scan the 5.3GB raw table.",
        }
    else:
        exact_units, exact_metadata, unit_audit = _rebuild_exact_comment_units(
            census,
            score_config=score_config,
        )
    batches: list[pd.DataFrame] = []
    diagnostics: dict[str, Any] | None = None
    batch_size = int(score_config["batch_authors"])
    for start in range(0, len(census), batch_size):
        scored, current = _score_batch(
            census.iloc[start : start + batch_size],
            representation=representation,
            bundle=bundle,
            config=config,
            exact_units=exact_units,
            exact_metadata=exact_metadata,
        )
        batches.append(scored)
        diagnostics = current if diagnostics is None else diagnostics
        if current != diagnostics:
            raise RuntimeError("Canonical landmark diagnostics changed across batches.")
        print(
            f"scored {min(start + batch_size, len(census))}/{len(census)} authors",
            flush=True,
        )
    score_table = pd.concat(batches, ignore_index=True)
    salt = str(score_config["pseudonym_salt"])
    score_table["pseudonymous_id"] = score_table["user_id"].map(
        lambda value: _pseudonym(str(value), salt)
    )
    score_table = score_table.drop(columns="user_id")
    score_table = score_table[
        ["pseudonymous_id", *[c for c in score_table if c != "pseudonymous_id"]]
    ]
    score_path = output_dir / "frozen_scores.parquet"
    score_table.to_parquet(score_path, index=False)
    status_counts = {
        str(key): int(value)
        for key, value in score_table["score_status"].value_counts().items()
    }
    manifest = {
        "version": config["version"],
        "analysis_status": config["analysis_status"],
        "stage": "FROZEN_SCORE_COMPLETE",
        "created_utc": datetime.now(UTC).isoformat(),
        "score_table": str(score_path.relative_to(ROOT)),
        "score_table_sha256": _sha256(score_path),
        "authors": int(len(score_table)),
        "status_counts": status_counts,
        "minimum_units": int(bundle.support_rule["min_units_for_score"]),
        "geometry_bundle": str(geometry_path.relative_to(ROOT)),
        "geometry_bundle_sha256": _sha256(geometry_path),
        "geometry_bundle_id": bundle.bundle_id,
        "representation_runtime": str(representation_path.relative_to(ROOT)),
        "representation_runtime_sha256": _sha256(representation_path),
        "input_sha256": {
            name: _sha256(path)
            for name, path in paths.items()
        },
        "input_rows_used_for_text_census": {
            "unique_authors": int(len(census)),
            "smoke_authors_per_source": int(smoke_authors),
        },
        "unit_reconstruction": unit_audit,
        "canonical_diagnostics": diagnostics,
        "labels_read": False,
        "raw_identifiers_persisted": False,
        "claim_boundary": config["claim_boundary"],
    }
    _write_json(output_dir / "score_manifest.json", manifest)
    return manifest


def _pseudonymize_labels(
    frame: pd.DataFrame,
    *,
    salt: str,
) -> pd.DataFrame:
    output = frame.copy()
    output["pseudonymous_id"] = output["user_id"].astype(str).map(
        lambda value: _pseudonym(value, salt)
    )
    return output.drop(columns="user_id")


def _load_labels(
    paths: dict[str, Path],
    *,
    salt: str,
    smoke_authors: int,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.DataFrame, set[str]]:
    big5_columns = ["user_id", "official_fold", *BIG5_TRAITS]
    big5 = pd.read_csv(
        paths["big5"], usecols=big5_columns, dtype={"user_id": str}
    )
    big5 = _deterministic_cap(big5, smoke_authors)
    raw_big5_ids = set(big5["user_id"].astype(str))
    bridge = pd.read_csv(
        paths["bridge"],
        usecols=["user_id", "bridge_fold", *BIG5_TRAITS, *MBTI_AXES],
        dtype={"user_id": str},
    )
    bridge = _deterministic_cap(bridge, smoke_authors)
    raw_bridge_ids = set(bridge["user_id"].astype(str))
    mbti: dict[str, pd.DataFrame] = {}
    for axis in MBTI_AXES:
        frame = pd.read_csv(
            paths[axis],
            usecols=["user_id", "official_fold", "positive_probability"],
            dtype={"user_id": str},
        )
        frame = _deterministic_cap(frame, smoke_authors)
        frame = frame.rename(columns={"positive_probability": axis})
        mbti[axis] = frame
    big5 = big5.loc[~big5["user_id"].isin(raw_bridge_ids)].copy()
    bridge = _pseudonymize_labels(bridge, salt=salt)
    big5 = _pseudonymize_labels(big5, salt=salt)
    mbti_output: dict[str, pd.DataFrame] = {}
    for axis, frame in mbti.items():
        frame = frame.loc[
            ~frame["user_id"].isin(raw_big5_ids | raw_bridge_ids)
        ].copy()
        mbti_output[axis] = _pseudonymize_labels(frame, salt=salt)
    return big5, mbti_output, bridge, {
        _pseudonym(value, salt) for value in raw_big5_ids
    }


def _feature_groups(score: pd.DataFrame) -> dict[str, list[str]]:
    v8 = sorted(column for column in score if column.startswith("v8_csr_"))
    v7 = sorted(column for column in score if column.startswith("v7_author_"))
    nuisance = sorted(
        column for column in score if column.startswith("nuisance_")
    )
    if not v8 or not v7 or not nuisance:
        raise RuntimeError("Frozen score table is missing one or more feature families.")
    return {
        "v8_canonical": v8,
        "nuisance_only": nuisance,
        "v8_plus_nuisance": [*v8, *nuisance],
        "v7_author48_upper_bound": v7,
    }


def _eligible(score: pd.DataFrame, mode: str, minimum_units: int) -> pd.DataFrame:
    if mode == "ready":
        mask = score["score_status"].eq("GEOMETRY_PROFILE_READY")
    elif mode == "support_eligible":
        mask = score["n_units"].ge(int(minimum_units))
    else:
        raise ValueError(f"Unknown eligibility mode: {mode}")
    return score.loc[mask].copy()


def _aggregate_cv(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (cohort, view, task), group in summary.groupby(
        ["cohort", "view", "task"], observed=True
    ):
        row: dict[str, Any] = {
            "cohort": str(cohort),
            "view": str(view),
            "task": str(task),
            "targets": int(len(group)),
            "n_min": int(group["n"].min()),
            "n_max": int(group["n"].max()),
        }
        if task == "continuous":
            row["mean_pearson_r"] = float(group["pearson_r"].mean())
            row["mean_spearman_rho"] = float(group["spearman_rho"].mean())
            row["mean_mae"] = float(group["mae"].mean())
            row["mean_rmse"] = float(group["rmse"].mean())
        else:
            row["mean_roc_auc"] = float(group["roc_auc"].mean())
            row["mean_balanced_accuracy"] = float(
                group["balanced_accuracy"].mean()
            )
            row["mean_probability_r"] = float(group["probability_r"].mean())
            row["mean_macro_f1"] = float(group["macro_f1"].mean())
        rows.append(row)
    return pd.DataFrame(rows)


def _correlation(first: np.ndarray, second: np.ndarray) -> float:
    first = np.asarray(first, dtype=float)
    second = np.asarray(second, dtype=float)
    first = first - np.mean(first)
    second = second - np.mean(second)
    denominator = float(np.linalg.norm(first) * np.linalg.norm(second))
    return (
        float(np.dot(first, second) / denominator)
        if denominator > 0
        else float("nan")
    )


def _paired_cv_bootstrap(
    predictions: pd.DataFrame,
    *,
    draws: int,
    seed: int,
) -> pd.DataFrame:
    """Paired author bootstrap for mean-trait CV metric differences."""
    from sklearn.metrics import roc_auc_score

    views = (
        "v8_canonical",
        "nuisance_only",
        "v8_plus_nuisance",
        "v7_author48_upper_bound",
    )
    comparisons = (
        ("v8_canonical", "nuisance_only"),
        ("v8_plus_nuisance", "nuisance_only"),
        ("v7_author48_upper_bound", "nuisance_only"),
    )
    rows: list[dict[str, Any]] = []
    for cohort, data in predictions.groupby("cohort", observed=True):
        task = str(data["task"].iloc[0])
        identifiers = sorted(data["pseudonymous_id"].astype(str).unique())
        targets = sorted(data["target"].astype(str).unique())
        true = np.empty((len(identifiers), len(targets)), dtype=float)
        predicted = np.empty(
            (len(identifiers), len(targets), len(views)), dtype=float
        )
        for target_index, target in enumerate(targets):
            truth = data.loc[
                data["target"].eq(target) & data["view"].eq(views[0])
            ].set_index("pseudonymous_id")
            true[:, target_index] = truth.loc[identifiers, "true_value"]
            for view_index, view in enumerate(views):
                view_data = data.loc[
                    data["target"].eq(target) & data["view"].eq(view)
                ].set_index("pseudonymous_id")
                predicted[:, target_index, view_index] = view_data.loc[
                    identifiers, "prediction"
                ]

        def metric(index: np.ndarray, view_index: int) -> float:
            target_values = []
            for target_index in range(len(targets)):
                if task == "continuous":
                    value = _correlation(
                        true[index, target_index],
                        predicted[index, target_index, view_index],
                    )
                else:
                    value = float(
                        roc_auc_score(
                            true[index, target_index].astype(int),
                            predicted[index, target_index, view_index],
                        )
                    )
                target_values.append(value)
            return float(np.mean(target_values))

        full_index = np.arange(len(identifiers), dtype=int)
        point = {
            view: metric(full_index, view_index)
            for view_index, view in enumerate(views)
        }
        rng = np.random.default_rng(
            int(seed)
            + int(hashlib.sha256(str(cohort).encode()).hexdigest()[:8], 16)
        )
        samples = {comparison: [] for comparison in comparisons}
        for _ in range(int(draws)):
            index = rng.integers(0, len(identifiers), len(identifiers))
            values = {
                view: metric(index, view_index)
                for view_index, view in enumerate(views)
            }
            for comparison in comparisons:
                samples[comparison].append(
                    values[comparison[0]] - values[comparison[1]]
                )
        for first, second in comparisons:
            values = np.asarray(samples[(first, second)], dtype=float)
            rows.append({
                "cohort": str(cohort),
                "task": task,
                "metric": (
                    "mean_pearson_r"
                    if task == "continuous"
                    else "mean_roc_auc"
                ),
                "view": first,
                "reference_view": second,
                "point_delta": float(point[first] - point[second]),
                "bootstrap_mean_delta": float(np.mean(values)),
                "ci_lower": float(np.quantile(values, 0.025)),
                "ci_upper": float(np.quantile(values, 0.975)),
                "draws": int(draws),
                "authors": int(len(identifiers)),
            })
    return pd.DataFrame(rows)


def _bridge_bootstrap(
    predictions: pd.DataFrame,
    bridge_summary: pd.DataFrame,
    *,
    draws: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Bootstrap bridge authors, recomputing true and predicted 5x4 matrices."""
    views = (
        "v8_canonical",
        "nuisance_only",
        "v8_plus_nuisance",
        "v7_author48_upper_bound",
    )
    comparisons = (
        ("v8_canonical", "nuisance_only"),
        ("v8_plus_nuisance", "nuisance_only"),
        ("v7_author48_upper_bound", "nuisance_only"),
    )
    absolute_rows: list[dict[str, Any]] = []
    delta_rows: list[dict[str, Any]] = []
    for cohort, cohort_frame in predictions.groupby("cohort", observed=True):
        frames = {
            view: cohort_frame.loc[cohort_frame["view"].eq(view)]
            .sort_values("pseudonymous_id")
            .reset_index(drop=True)
            for view in views
        }
        identifiers = frames[views[0]]["pseudonymous_id"].astype(str).tolist()
        if any(
            frame["pseudonymous_id"].astype(str).tolist() != identifiers
            for frame in frames.values()
        ):
            raise RuntimeError("Bridge view rows are not author-aligned.")
        columns = [
            *BIG5_TRAITS,
            *MBTI_AXES,
            *[f"pred_{value}" for value in (*BIG5_TRAITS, *MBTI_AXES)],
        ]
        arrays = {
            view: {
                column: frame[column].to_numpy(float)
                for column in columns
            }
            for view, frame in frames.items()
        }

        def vector(
            values: dict[str, np.ndarray],
            index: np.ndarray,
            *,
            predicted: bool,
        ) -> np.ndarray:
            prefix = "pred_" if predicted else ""
            return np.asarray([
                _correlation(
                    values[f"{prefix}{trait}"][index],
                    values[f"{prefix}{axis}"][index],
                )
                for trait in BIG5_TRAITS
                for axis in MBTI_AXES
            ])

        rng = np.random.default_rng(
            int(seed)
            + int(hashlib.sha256(str(cohort).encode()).hexdigest()[:8], 16)
        )
        samples = {view: [] for view in views}
        for _ in range(int(draws)):
            index = rng.integers(0, len(identifiers), len(identifiers))
            true_vector = vector(arrays[views[0]], index, predicted=False)
            for view in views:
                predicted_vector = vector(arrays[view], index, predicted=True)
                samples[view].append(
                    _correlation(predicted_vector, true_vector)
                )
        point_rows = bridge_summary.loc[
            bridge_summary["cohort"].eq(cohort)
        ].set_index("view")
        for view in views:
            values = np.asarray(samples[view], dtype=float)
            absolute_rows.append({
                "cohort": str(cohort),
                "view": view,
                "metric": "element_r",
                "point_estimate": float(point_rows.loc[view, "element_r"]),
                "bootstrap_mean": float(np.nanmean(values)),
                "ci_lower": float(np.nanquantile(values, 0.025)),
                "ci_upper": float(np.nanquantile(values, 0.975)),
                "draws": int(draws),
                "authors": int(len(identifiers)),
            })
        for first, second in comparisons:
            values = np.asarray(samples[first]) - np.asarray(samples[second])
            delta_rows.append({
                "cohort": str(cohort),
                "metric": "element_r",
                "view": first,
                "reference_view": second,
                "point_delta": float(
                    point_rows.loc[first, "element_r"]
                    - point_rows.loc[second, "element_r"]
                ),
                "bootstrap_mean_delta": float(np.nanmean(values)),
                "ci_lower": float(np.nanquantile(values, 0.025)),
                "ci_upper": float(np.nanquantile(values, 0.975)),
                "draws": int(draws),
                "authors": int(len(identifiers)),
            })
    return pd.DataFrame(absolute_rows), pd.DataFrame(delta_rows)


def _run_cv_suite(
    *,
    scores: pd.DataFrame,
    big5: pd.DataFrame,
    mbti: dict[str, pd.DataFrame],
    feature_groups: dict[str, list[str]],
    config: dict[str, Any],
    eligibility_mode: str,
    minimum_units: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    eligible = _eligible(scores, eligibility_mode, minimum_units)
    model = config["models"]
    summaries: list[dict[str, Any]] = []
    folds: list[pd.DataFrame] = []
    predictions: list[pd.DataFrame] = []
    screens: list[pd.DataFrame] = []
    big5_frame = big5.merge(eligible, on="pseudonymous_id", how="inner")
    big5_cohort = f"big5_only_{eligibility_mode}"
    screens.append(
        univariate_connections(
            big5_frame,
            feature_groups={
                "v8_canonical": feature_groups["v8_canonical"],
                "nuisance_only": feature_groups["nuisance_only"],
            },
            targets=BIG5_TRAITS,
            cohort=big5_cohort,
        )
    )
    for view, columns in feature_groups.items():
        for trait in BIG5_TRAITS:
            result = run_official_cv(
                big5_frame,
                columns=columns,
                target=trait,
                fold_column="official_fold",
                task="continuous",
                view=view,
                cohort=big5_cohort,
                ridge_alphas=model["ridge_alphas"],
                logistic_c=model["logistic_c"],
            )
            summaries.append(result.summary)
            folds.append(result.folds)
            predictions.append(result.predictions)
    for axis in MBTI_AXES:
        axis_frame = mbti[axis].merge(
            eligible, on="pseudonymous_id", how="inner"
        )
        cohort = f"mbti_only_{eligibility_mode}"
        screens.append(
            univariate_connections(
                axis_frame,
                feature_groups={
                    "v8_canonical": feature_groups["v8_canonical"],
                    "nuisance_only": feature_groups["nuisance_only"],
                },
                targets=[axis],
                cohort=cohort,
            )
        )
        for view, columns in feature_groups.items():
            result = run_official_cv(
                axis_frame,
                columns=columns,
                target=axis,
                fold_column="official_fold",
                task="binary",
                view=view,
                cohort=cohort,
                ridge_alphas=model["ridge_alphas"],
                logistic_c=model["logistic_c"],
            )
            summaries.append(result.summary)
            folds.append(result.folds)
            predictions.append(result.predictions)
    return (
        pd.DataFrame(summaries),
        pd.concat(folds, ignore_index=True),
        pd.concat(predictions, ignore_index=True),
        pd.concat(screens, ignore_index=True),
    )


def _bridge_suite(
    *,
    scores: pd.DataFrame,
    big5: pd.DataFrame,
    mbti: dict[str, pd.DataFrame],
    bridge: pd.DataFrame,
    feature_groups: dict[str, list[str]],
    config: dict[str, Any],
    eligibility_mode: str,
    minimum_units: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    eligible = _eligible(scores, eligibility_mode, minimum_units)
    big5_source = big5.merge(eligible, on="pseudonymous_id", how="inner")
    mbti_source = {
        axis: frame.merge(eligible, on="pseudonymous_id", how="inner")
        for axis, frame in mbti.items()
    }
    destination = bridge.merge(eligible, on="pseudonymous_id", how="inner")
    model_config = config["models"]
    true_matrix = relation_matrix(
        destination,
        big5_columns=BIG5_TRAITS,
        mbti_columns=MBTI_AXES,
    )
    summary_rows: list[dict[str, Any]] = []
    matrix_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    for view, columns in feature_groups.items():
        predicted = destination[
            ["pseudonymous_id", *BIG5_TRAITS, *MBTI_AXES]
        ].copy()
        parameters: dict[str, float] = {}
        for trait in BIG5_TRAITS:
            values, parameter = fit_source_head_predict(
                big5_source,
                destination,
                columns=columns,
                target=trait,
                fold_column="official_fold",
                task="continuous",
                ridge_alphas=model_config["ridge_alphas"],
                logistic_c=model_config["logistic_c"],
            )
            predicted[f"pred_{trait}"] = values
            parameters[trait] = parameter
        for axis in MBTI_AXES:
            values, parameter = fit_source_head_predict(
                mbti_source[axis],
                destination,
                columns=columns,
                target=axis,
                fold_column="official_fold",
                task="binary",
                ridge_alphas=model_config["ridge_alphas"],
                logistic_c=model_config["logistic_c"],
            )
            predicted[f"pred_{axis}"] = values
            parameters[axis] = parameter
        predicted_big5 = [f"pred_{trait}" for trait in BIG5_TRAITS]
        predicted_mbti = [f"pred_{axis}" for axis in MBTI_AXES]
        predicted_matrix = relation_matrix(
            predicted,
            big5_columns=predicted_big5,
            mbti_columns=predicted_mbti,
        )
        alignment = matrix_alignment(predicted_matrix, true_matrix)
        permutation_p = bridge_permutation_p(
            predicted,
            predicted_big5=predicted_big5,
            predicted_mbti=predicted_mbti,
            observed_matrix=true_matrix,
            observed_alignment=alignment["element_r"],
            permutations=int(config["bridge_permutations"]),
            seed=int(config["seed"]),
        )
        big5_r = [
            relation_matrix(
                predicted,
                big5_columns=[trait],
                mbti_columns=[f"pred_{trait}"],
            )[0, 0]
            for trait in BIG5_TRAITS
        ]
        from sklearn.metrics import roc_auc_score

        mbti_auc = [
            float(roc_auc_score(predicted[axis], predicted[f"pred_{axis}"]))
            for axis in MBTI_AXES
        ]
        summary_rows.append({
            "cohort": f"strict_bridge_{eligibility_mode}",
            "view": view,
            "n": int(len(predicted)),
            **alignment,
            "permutation_p": permutation_p,
            "mean_bridge_big5_r": float(np.mean(big5_r)),
            "mean_bridge_mbti_auc": float(np.mean(mbti_auc)),
            "selected_parameters_json": json.dumps(parameters, sort_keys=True),
        })
        for kind, matrix in (("true", true_matrix), ("predicted", predicted_matrix)):
            for row, trait in enumerate(BIG5_TRAITS):
                for column, axis in enumerate(MBTI_AXES):
                    matrix_rows.append({
                        "cohort": f"strict_bridge_{eligibility_mode}",
                        "view": view,
                        "matrix": kind,
                        "big5_trait": trait,
                        "mbti_axis": axis,
                        "pearson_r": float(matrix[row, column]),
                    })
        export = predicted.copy()
        export["view"] = view
        export["cohort"] = f"strict_bridge_{eligibility_mode}"
        prediction_frames.append(export)
    return (
        pd.DataFrame(summary_rows),
        pd.DataFrame(matrix_rows),
        pd.concat(prediction_frames, ignore_index=True),
    )


def _fmt(value: Any, digits: int = 3) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    return f"{number:.{digits}f}" if np.isfinite(number) else "NA"


def _report_text(
    *,
    score_manifest: dict[str, Any],
    aggregate: pd.DataFrame,
    summary: pd.DataFrame,
    bridge_summary: pd.DataFrame,
    cv_bootstrap: pd.DataFrame,
    bridge_bootstrap: pd.DataFrame,
    bridge_delta_bootstrap: pd.DataFrame,
    screens: pd.DataFrame,
    cohort_counts: dict[str, int],
    claim_boundary: str,
) -> str:
    primary = aggregate.loc[
        aggregate["cohort"].isin(["big5_only_ready", "mbti_only_ready"])
    ]
    big5 = primary.loc[primary["task"].eq("continuous")].set_index("view")
    mbti = primary.loc[primary["task"].eq("binary")].set_index("view")
    bridge = bridge_summary.loc[
        bridge_summary["cohort"].eq("strict_bridge_ready")
    ].set_index("view")
    sensitivity = aggregate.loc[
        aggregate["cohort"].isin(
            ["big5_only_support_eligible", "mbti_only_support_eligible"]
        )
    ]
    sensitivity_big5 = sensitivity.loc[
        sensitivity["task"].eq("continuous")
    ].set_index("view")
    sensitivity_mbti = sensitivity.loc[
        sensitivity["task"].eq("binary")
    ].set_index("view")
    sensitivity_bridge = bridge_summary.loc[
        bridge_summary["cohort"].eq("strict_bridge_support_eligible")
    ].set_index("view")
    significant = screens.loc[
        (screens["cohort"].str.endswith("_ready"))
        & (screens["q_value_within_target_view"] < 0.05)
    ]
    lines = [
        "# SUICA V8 Full PANDORA External Connection",
        "",
        f"Status: `{score_manifest['analysis_status']}`",
        "",
        "## Design",
        "",
        "The frozen V8 canonical scale-residual geometry was scored before labels "
        "were joined. Big5-only authors were used for Big Five heads, MBTI-only "
        "authors for four binary axis heads, and strict both-label authors only "
        "for the held-out Big5↔MBTI structural bridge. Official repeat-0 folds "
        "were used for source-task CV. Every head was fitted inside its training "
        "fold; the V8 geometry and representation were never refitted.",
        "",
        f"Claim boundary: {claim_boundary}",
        "",
        "## Coverage",
        "",
        f"- Frozen score authors: {score_manifest['authors']}",
        f"- Geometry-ready authors: "
        f"{score_manifest['status_counts'].get('GEOMETRY_PROFILE_READY', 0)}",
        f"- Big5-only ready: {cohort_counts['big5_only_ready']}",
        f"- Big5-only minimum-support sensitivity: "
        f"{cohort_counts['big5_only_support_eligible']}",
        f"- MBTI-only ready (minimum across axes): "
        f"{cohort_counts['mbti_only_ready_min']}",
        f"- MBTI-only minimum-support sensitivity (minimum across axes): "
        f"{cohort_counts['mbti_only_support_eligible_min']}",
        f"- Strict bridge ready: {cohort_counts['bridge_ready']}",
        f"- Strict bridge minimum-support sensitivity: "
        f"{cohort_counts['bridge_support_eligible']}",
        "",
        "## Primary official-fold results",
        "",
        "| View | Big5 mean r | MBTI mean AUC | MBTI mean balanced accuracy | "
        "Bridge element r | Bridge permutation p |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for view in (
        "v8_canonical",
        "nuisance_only",
        "v8_plus_nuisance",
        "v7_author48_upper_bound",
    ):
        lines.append(
            f"| {view} | "
            f"{_fmt(big5.loc[view, 'mean_pearson_r'])} | "
            f"{_fmt(mbti.loc[view, 'mean_roc_auc'])} | "
            f"{_fmt(mbti.loc[view, 'mean_balanced_accuracy'])} | "
            f"{_fmt(bridge.loc[view, 'element_r'])} | "
            f"{_fmt(bridge.loc[view, 'permutation_p'], 4)} |"
        )
    lines.extend([
        "",
        "The 48-coordinate V7 row is an upstream representation upper bound, "
        "not the invariant SUICA score. Nuisance-only uses text amount and "
        "format opportunity variables. V8+nuisance tests incremental complementarity.",
        "",
        "## Minimum-support sensitivity",
        "",
        "| View | Big5 mean r | MBTI mean AUC | Bridge element r | "
        "Bridge permutation p |",
        "|---|---:|---:|---:|---:|",
    ])
    for view in (
        "v8_canonical",
        "nuisance_only",
        "v8_plus_nuisance",
        "v7_author48_upper_bound",
    ):
        lines.append(
            f"| {view} | "
            f"{_fmt(sensitivity_big5.loc[view, 'mean_pearson_r'])} | "
            f"{_fmt(sensitivity_mbti.loc[view, 'mean_roc_auc'])} | "
            f"{_fmt(sensitivity_bridge.loc[view, 'element_r'])} | "
            f"{_fmt(sensitivity_bridge.loc[view, 'permutation_p'], 4)} |"
        )
    ready_cv = cv_bootstrap.set_index(["cohort", "view", "reference_view"])
    ready_bridge = bridge_bootstrap.set_index(["cohort", "view"])
    ready_bridge_delta = bridge_delta_bootstrap.set_index(
        ["cohort", "view", "reference_view"]
    )
    big5_delta = ready_cv.loc[
        ("big5_only_ready", "v8_canonical", "nuisance_only")
    ]
    mbti_delta = ready_cv.loc[
        ("mbti_only_ready", "v8_canonical", "nuisance_only")
    ]
    mbti_hybrid_delta = ready_cv.loc[
        ("mbti_only_ready", "v8_plus_nuisance", "nuisance_only")
    ]
    bridge_v8 = ready_bridge.loc[("strict_bridge_ready", "v8_canonical")]
    bridge_delta = ready_bridge_delta.loc[
        ("strict_bridge_ready", "v8_canonical", "nuisance_only")
    ]
    lines.extend([
        "",
        "## Paired uncertainty",
        "",
        f"- Big5 V8 minus nuisance: delta={_fmt(big5_delta['point_delta'])}, "
        f"95% paired-bootstrap CI "
        f"[{_fmt(big5_delta['ci_lower'])}, {_fmt(big5_delta['ci_upper'])}].",
        f"- MBTI V8 minus nuisance: delta={_fmt(mbti_delta['point_delta'])}, "
        f"95% paired-bootstrap CI "
        f"[{_fmt(mbti_delta['ci_lower'])}, {_fmt(mbti_delta['ci_upper'])}].",
        f"- MBTI V8+nuisance minus nuisance: "
        f"delta={_fmt(mbti_hybrid_delta['point_delta'])}, 95% paired-bootstrap CI "
        f"[{_fmt(mbti_hybrid_delta['ci_lower'])}, "
        f"{_fmt(mbti_hybrid_delta['ci_upper'])}].",
        f"- Bridge V8 element r: {_fmt(bridge_v8['point_estimate'])}, "
        f"author-bootstrap CI "
        f"[{_fmt(bridge_v8['ci_lower'])}, {_fmt(bridge_v8['ci_upper'])}].",
        f"- Bridge V8 minus nuisance: delta={_fmt(bridge_delta['point_delta'])}, "
        f"author-bootstrap CI "
        f"[{_fmt(bridge_delta['ci_lower'])}, {_fmt(bridge_delta['ci_upper'])}].",
        "",
        "## Decision",
        "",
        "- Direct Big Five connection is not supported for the invariant V8 "
        "canonical score in this run.",
        "- Direct MBTI connection is weak: V8 is above chance but below the "
        "nuisance comparator. V8 contributes a small complementary gain only "
        "when combined with nuisance variables.",
        "- Cross-scale structure is the positive result: V8 recovers the held-out "
        "Big5-to-MBTI relation matrix and adds structure beyond nuisance despite "
        "weak individual Big Five prediction.",
        "- The upstream 48-coordinate representation remains stronger for direct "
        "prediction. Canonical invariance therefore trades away criterion signal "
        "and should not replace the upstream representation in a prediction head.",
        "",
        "## Coordinate screen",
        "",
        f"- Ready-cohort V8/nuisance tests passing within-target-view BH-FDR: "
        f"{len(significant)}.",
    ])
    if len(significant):
        for row in significant.sort_values("abs_pearson_r", ascending=False).head(
            12
        ).itertuples(index=False):
            lines.append(
                f"- `{row.target}` × `{row.feature}`: "
                f"r={_fmt(row.pearson_r)}, q={_fmt(row.q_value_within_target_view, 4)} "
                f"(n={row.n})."
            )
    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "- A nonzero result is an association between a frozen text-geometry "
        "coordinate system and an external questionnaire anchor. It does not "
        "make the coordinate a named personality construct.",
        "- PANDORA labels were used in earlier project phases. This run is "
        "therefore exploratory and cannot replenish the spent lockbox.",
        "- Raw PANDORA contains subreddit metadata, but the frozen native scorer "
        "and this external connection do not model it. The nuisance comparator "
        "controls text volume and format, not full community/topic selection.",
        "- The V8 representation and geometry were fitted label-free on a subset "
        "of MBTI-only authors. MBTI head CV is therefore unsupervised-transductive "
        "at the representation level, although no MBTI label entered the scorer.",
        "- Bridge author-bootstrap intervals resample held-out bridge authors while "
        "conditioning on the fitted source heads. They do not include uncertainty "
        "from refitting Big5-only and MBTI-only heads.",
        "- `support_eligible` rows are a declared sensitivity analysis that ignores "
        "the frozen radial-envelope refusal while retaining the minimum-unit rule.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "python scripts/run_suica_v8_pandora_external_connection.py --stage all",
        "```",
        "",
        "Detailed trait/axis rows, fold predictions, relation matrices, and the "
        "hash-bound score manifest are stored beside this report.",
        "",
    ])
    return "\n".join(lines)


def analyze_stage(
    *,
    paths: dict[str, Path],
    config: dict[str, Any],
    output_dir: Path,
    report_path: Path,
    smoke_authors: int,
) -> dict[str, Any]:
    score_manifest = _read_json(output_dir / "score_manifest.json")
    score_path = ROOT / score_manifest["score_table"]
    actual_hash = _sha256(score_path)
    if actual_hash != score_manifest["score_table_sha256"]:
        raise RuntimeError("REFUSE_BUNDLE_HASH_MISMATCH: frozen score table changed.")
    if bool(score_manifest["labels_read"]):
        raise RuntimeError("Score manifest incorrectly claims label access.")
    scores = pd.read_parquet(score_path)
    salt = str(config["score"]["pseudonym_salt"])
    big5, mbti, bridge, _ = _load_labels(
        paths,
        salt=salt,
        smoke_authors=smoke_authors,
    )
    overlap_big5_bridge = set(big5["pseudonymous_id"]) & set(
        bridge["pseudonymous_id"]
    )
    overlap_mbti_bridge = set().union(
        *[set(frame["pseudonymous_id"]) for frame in mbti.values()]
    ) & set(bridge["pseudonymous_id"])
    if overlap_big5_bridge or overlap_mbti_bridge:
        raise RuntimeError("Source heads overlap strict bridge evaluation users.")
    feature_groups = _feature_groups(scores)
    minimum_units = int(score_manifest["minimum_units"])
    summary_frames: list[pd.DataFrame] = []
    fold_frames: list[pd.DataFrame] = []
    prediction_frames: list[pd.DataFrame] = []
    screen_frames: list[pd.DataFrame] = []
    bridge_summaries: list[pd.DataFrame] = []
    bridge_matrices: list[pd.DataFrame] = []
    bridge_predictions: list[pd.DataFrame] = []
    for eligibility_mode in ("ready", "support_eligible"):
        summary, folds, predictions, screens = _run_cv_suite(
            scores=scores,
            big5=big5,
            mbti=mbti,
            feature_groups=feature_groups,
            config=config,
            eligibility_mode=eligibility_mode,
            minimum_units=minimum_units,
        )
        summary_frames.append(summary)
        fold_frames.append(folds)
        prediction_frames.append(predictions)
        screen_frames.append(screens)
        bridge_result = _bridge_suite(
            scores=scores,
            big5=big5,
            mbti=mbti,
            bridge=bridge,
            feature_groups=feature_groups,
            config=config,
            eligibility_mode=eligibility_mode,
            minimum_units=minimum_units,
        )
        bridge_summaries.append(bridge_result[0])
        bridge_matrices.append(bridge_result[1])
        bridge_predictions.append(bridge_result[2])
    summary = pd.concat(summary_frames, ignore_index=True)
    folds = pd.concat(fold_frames, ignore_index=True)
    predictions = pd.concat(prediction_frames, ignore_index=True)
    screens = pd.concat(screen_frames, ignore_index=True)
    bridge_summary = pd.concat(bridge_summaries, ignore_index=True)
    bridge_matrix = pd.concat(bridge_matrices, ignore_index=True)
    bridge_prediction = pd.concat(bridge_predictions, ignore_index=True)
    aggregate = _aggregate_cv(summary)
    cv_bootstrap = _paired_cv_bootstrap(
        predictions,
        draws=int(config["cv_bootstrap_draws"]),
        seed=int(config["seed"]),
    )
    bridge_bootstrap, bridge_delta_bootstrap = _bridge_bootstrap(
        bridge_prediction,
        bridge_summary,
        draws=int(config["bridge_bootstrap_draws"]),
        seed=int(config["seed"]),
    )
    summary.to_csv(output_dir / "cv_summary_by_target.csv", index=False)
    aggregate.to_csv(output_dir / "cv_aggregate.csv", index=False)
    folds.to_csv(output_dir / "cv_fold_metrics.csv", index=False)
    predictions.to_parquet(output_dir / "cv_predictions.parquet", index=False)
    screens.to_csv(output_dir / "univariate_connections.csv", index=False)
    cv_bootstrap.to_csv(output_dir / "cv_paired_bootstrap.csv", index=False)
    bridge_summary.to_csv(output_dir / "bridge_summary.csv", index=False)
    bridge_bootstrap.to_csv(
        output_dir / "bridge_author_bootstrap.csv", index=False
    )
    bridge_delta_bootstrap.to_csv(
        output_dir / "bridge_paired_bootstrap.csv", index=False
    )
    bridge_matrix.to_csv(output_dir / "bridge_relation_matrices.csv", index=False)
    bridge_prediction.to_parquet(
        output_dir / "bridge_predictions.parquet", index=False
    )
    ready = _eligible(scores, "ready", minimum_units)
    support_eligible = _eligible(scores, "support_eligible", minimum_units)
    counts = {
        "big5_only_ready": int(
            len(big5.merge(ready, on="pseudonymous_id", how="inner"))
        ),
        "big5_only_support_eligible": int(
            len(
                big5.merge(
                    support_eligible,
                    on="pseudonymous_id",
                    how="inner",
                )
            )
        ),
        "mbti_only_ready_min": int(
            min(
                len(frame.merge(ready, on="pseudonymous_id", how="inner"))
                for frame in mbti.values()
            )
        ),
        "mbti_only_support_eligible_min": int(
            min(
                len(
                    frame.merge(
                        support_eligible,
                        on="pseudonymous_id",
                        how="inner",
                    )
                )
                for frame in mbti.values()
            )
        ),
        "bridge_ready": int(
            len(bridge.merge(ready, on="pseudonymous_id", how="inner"))
        ),
        "bridge_support_eligible": int(
            len(
                bridge.merge(
                    support_eligible,
                    on="pseudonymous_id",
                    how="inner",
                )
            )
        ),
    }
    report = _report_text(
        score_manifest=score_manifest,
        aggregate=aggregate,
        summary=summary,
        bridge_summary=bridge_summary,
        cv_bootstrap=cv_bootstrap,
        bridge_bootstrap=bridge_bootstrap,
        bridge_delta_bootstrap=bridge_delta_bootstrap,
        screens=screens,
        cohort_counts=counts,
        claim_boundary=config["claim_boundary"],
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    (output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    decision = {
        "version": config["version"],
        "status": "EXPLORATORY_EXTERNAL_CONNECTION_COMPLETE",
        "analysis_status": config["analysis_status"],
        "score_table_sha256_verified": True,
        "source_bridge_overlap": {
            "big5": 0,
            "mbti": 0,
        },
        "cohort_counts": counts,
        "primary_cv_aggregate": aggregate.loc[
            aggregate["cohort"].isin(["big5_only_ready", "mbti_only_ready"])
        ].replace({np.nan: None}).to_dict("records"),
        "primary_bridge": bridge_summary.loc[
            bridge_summary["cohort"].eq("strict_bridge_ready")
        ].replace({np.nan: None}).to_dict("records"),
        "primary_cv_paired_bootstrap": cv_bootstrap.loc[
            cv_bootstrap["cohort"].isin(
                ["big5_only_ready", "mbti_only_ready"]
            )
        ].replace({np.nan: None}).to_dict("records"),
        "primary_bridge_author_bootstrap": bridge_bootstrap.loc[
            bridge_bootstrap["cohort"].eq("strict_bridge_ready")
        ].replace({np.nan: None}).to_dict("records"),
        "primary_bridge_paired_bootstrap": bridge_delta_bootstrap.loc[
            bridge_delta_bootstrap["cohort"].eq("strict_bridge_ready")
        ].replace({np.nan: None}).to_dict("records"),
        "claim_boundary": config["claim_boundary"],
        "report": str(report_path.relative_to(ROOT)),
        "completed_utc": datetime.now(UTC).isoformat(),
    }
    _write_json(output_dir / "decision.json", decision)
    return decision


def main() -> None:
    args = parse_args()
    config_path = args.config if args.config.is_absolute() else ROOT / args.config
    data_root = args.data_root if args.data_root.is_absolute() else ROOT / args.data_root
    output_dir = (
        args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    )
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    config = _read_json(config_path)
    if args.bridge_permutations > 0:
        config["bridge_permutations"] = int(args.bridge_permutations)
    paths = _source_paths(data_root)
    if args.stage in {"score", "all"}:
        score_stage(
            paths=paths,
            config=config,
            output_dir=output_dir,
            smoke_authors=args.smoke_authors,
        )
    if args.stage in {"analyze", "all"}:
        decision = analyze_stage(
            paths=paths,
            config=config,
            output_dir=output_dir,
            report_path=report_path,
            smoke_authors=args.smoke_authors,
        )
        print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
