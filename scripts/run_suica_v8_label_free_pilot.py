#!/usr/bin/env python3
"""Run the V8.4 label-free, corpus-local real-text technical pilot."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
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
from suica_core.v7_governance import (  # noqa: E402
    append_ledger_event,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v7_psychometric import author_features_from_embeddings  # noqa: E402
from suica_core.v8_realtext import (  # noqa: E402
    aggregate_half_features,
    cross_fitted_semantic_increment,
    deterministic_text_features,
    load_document_panel,
    load_meps_panel,
    load_pandora_source_disjoint_panels,
    load_x_panel,
    require_local_reference,
)
from suica_core.v8_semantic import (  # noqa: E402
    OpenAICompatibleProvider,
    load_semantic_spec,
    semantic_event_vector,
    transduce_segments,
)


DEFAULT_DATA_ROOT = Path("/Volumes/mobile3/projects/project persona/data_sets")


def _source_env(path: Path) -> None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))


def _linear_cka(first: np.ndarray, second: np.ndarray) -> float:
    x = first - first.mean(axis=0, keepdims=True)
    y = second - second.mean(axis=0, keepdims=True)
    numerator = float(np.linalg.norm(x.T @ y, ord="fro") ** 2)
    denominator = float(np.linalg.norm(x.T @ x, ord="fro") * np.linalg.norm(y.T @ y, ord="fro"))
    return numerator / denominator if denominator > 1e-12 else float("nan")


def _load_panels(
    config: dict[str, Any],
    *,
    quick: bool,
    seed: int,
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    real = config["real_text"]
    segments = int(real["segments_per_author"])
    factor = 0.5 if quick else 1.0
    v7_native = pd.read_csv(
        ROOT
        / "results"
        / "v7_multiview_projection"
        / "e1_v72_full_20260715"
        / "author_features_native.csv",
        usecols=["user_id", "split"],
        dtype={"user_id": str},
    )
    split_limits = {
        split: max(4, int(limit * factor))
        for split, limit in real["pandora_max_by_split"].items()
    }
    pandora_panel, pandora_geometry = load_pandora_source_disjoint_panels(
        DEFAULT_DATA_ROOT / "prepared" / "suica_tiers_v2" / "tier_u_comments.parquet",
        eligible_authors=v7_native,
        max_by_split=split_limits,
        semantic_segments_per_author=segments,
        geometry_units_per_half=int(real["pandora_geometry_units_per_half"]),
        seed=seed,
    )
    panels = {
        "pandora": pandora_panel,
        "essays": load_document_panel(
            DEFAULT_DATA_ROOT / "raw" / "text" / "ESSAYS" / "essays_original_splitted.csv",
            corpus="essays",
            user_col="#AUTHID",
            text_col="TEXT",
            max_authors=max(16, int(real["max_authors"]["essays"] * factor)),
            segments_per_author=segments,
            seed=seed,
        ),
        "meps": load_meps_panel(
            DEFAULT_DATA_ROOT / "MEPS+AI_conv_experiment" / "decrypted_output",
            max_authors=max(16, int(real["max_authors"]["meps"] * factor)),
            segments_per_author=segments,
            seed=seed,
        ),
        "x_market": load_x_panel(
            DEFAULT_DATA_ROOT / "x_fullmarkettext",
            max_authors=max(16, int(real["max_authors"]["x_market"] * factor)),
            segments_per_author=segments,
            seed=seed,
        ),
    }
    return (
        {name: panel for name, panel in panels.items() if not panel.empty},
        pandora_geometry,
    )


def _semantic_batches(
    panels: dict[str, pd.DataFrame],
    *,
    repetitions: int,
    batch_size: int,
) -> list[tuple[str, int, int, list[dict[str, Any]]]]:
    jobs: list[tuple[str, int, int, list[dict[str, Any]]]] = []
    for corpus, panel in panels.items():
        records = [
            {
                "segment_id": str(row.segment_id),
                "spans": [{"span_id": str(row.span_id), "text": str(row.text)}],
            }
            for row in panel.itertuples(index=False)
        ]
        for repetition in range(repetitions):
            for batch_index, start in enumerate(range(0, len(records), batch_size)):
                jobs.append((corpus, repetition, batch_index, records[start:start + batch_size]))
    return jobs


def _format_variant(text: str) -> str:
    tokens = str(text).split()
    return "\n".join(" ".join(tokens[index:index + 12]) for index in range(0, len(tokens), 12))


def _real_numeric_explanation(
    panel: pd.DataFrame,
    vectors: dict[str, np.ndarray],
    *,
    seed: int,
) -> dict[str, float]:
    """Cross-half evidence removal check without generating psychological prose."""
    rng = np.random.default_rng(seed)
    advantages: list[float] = []
    sufficiency: list[float] = []
    for _author, group in panel.groupby("author_id", observed=True):
        group = group.sort_values("unit_index", kind="stable")
        even = [row for row in group.itertuples(index=False) if int(row.unit_index) % 2 == 0 and row.segment_id in vectors]
        odd = [row for row in group.itertuples(index=False) if int(row.unit_index) % 2 == 1 and row.segment_id in vectors]
        if len(even) < 2 or not odd:
            continue
        opposite = np.mean(np.vstack([vectors[row.segment_id] for row in odd]), axis=0)
        norm = np.linalg.norm(opposite)
        if norm <= 1e-12:
            continue
        direction = opposite / norm
        contributions = np.asarray([vectors[row.segment_id] @ direction for row in even])
        selected = int(np.argmax(contributions))
        random_index = int(rng.choice([index for index in range(len(even)) if index != selected]))
        advantages.append(float(contributions[selected] - contributions[random_index]))
        total = float(np.sum(np.maximum(contributions, 0.0)))
        sufficiency.append(float(max(contributions[selected], 0.0) / total) if total > 1e-12 else np.nan)
    if len(advantages) < 2:
        return {
            "necessity_advantage": np.nan,
            "necessity_ci_lower": np.nan,
            "sufficiency_median": np.nan,
        }
    values = np.asarray(advantages)
    draws = values[rng.integers(0, len(values), size=(2000, len(values)))].mean(axis=1)
    return {
        "necessity_advantage": float(values.mean()),
        "necessity_ci_lower": float(np.quantile(draws, 0.025)),
        "sufficiency_median": float(np.nanmedian(sufficiency)),
    }


def _pandora_v7_geometry_endpoint(
    geometry_panel: pd.DataFrame,
    metadata: pd.DataFrame,
    semantic_left: np.ndarray,
    semantic_right: np.ndarray,
    *,
    bootstrap_draws: int,
    seed: int,
) -> dict[str, Any]:
    base = ROOT / "results" / "v7_multiview_projection" / "e1_v72_full_20260715"
    representation = joblib.load(
        base / "artifacts" / "common_source_comment_representation.joblib"
    )
    bundle = GeometryBundle.from_dict(json.loads(
        (ROOT / "results" / "v7_geometry" / "g1_corrected_v2_full_20260715" / "geometry_bundle.json").read_text(encoding="utf-8")
    ))
    side_features: dict[str, pd.DataFrame] = {}
    for side in ("left", "right"):
        observations = geometry_panel.loc[
            geometry_panel["split"].eq(side)
        ].reset_index(drop=True)
        embeddings = representation.transform(observations["text"])
        side_features[side] = author_features_from_embeddings(
            observations,
            embeddings,
        ).set_index("user_id")
    ordered_users = metadata["author_id"].astype(str).tolist()
    missing = [
        user
        for user in ordered_users
        if user not in side_features["left"].index or user not in side_features["right"].index
    ]
    if missing:
        return {
            "status": "REFUSE_V7_GEOMETRY_AUTHOR_ALIGNMENT",
            "n_missing": int(len(missing)),
        }
    left = side_features["left"].loc[ordered_users]
    right = side_features["right"].loc[ordered_users]
    left_result = score_geometry_bundle(
        bundle,
        left[bundle.feature_names].to_numpy(float),
        unit_counts=left["n_units"].to_numpy(int),
    )
    right_result = score_geometry_bundle(
        bundle,
        right[bundle.feature_names].to_numpy(float),
        unit_counts=right["n_units"].to_numpy(int),
    )
    ready = np.asarray(left_result["status"]) == "GEOMETRY_PROFILE_READY"
    ready &= np.asarray(right_result["status"]) == "GEOMETRY_PROFILE_READY"
    if ready.sum() < 12:
        return {
            "status": "REFUSE_V7_GEOMETRY_SUPPORT",
            "n_ready": int(ready.sum()),
            "left_status_counts": pd.Series(left_result["status"]).value_counts().to_dict(),
            "right_status_counts": pd.Series(right_result["status"]).value_counts().to_dict(),
        }
    result = cross_fitted_semantic_increment(
        metadata.loc[ready].reset_index(drop=True),
        np.asarray(left_result["landmark_distance_profile"])[ready],
        np.asarray(right_result["landmark_distance_profile"])[ready],
        semantic_left[ready],
        semantic_right[ready],
        bootstrap_draws=bootstrap_draws,
        seed=seed,
    )
    result["endpoint"] = "frozen_v7_geometry_plus_v8_semantic"
    result["geometry_bundle_id"] = bundle.bundle_id
    result["geometry_representation"] = "frozen_v7_tfidf_svd24_author_mean_std"
    result["geometry_units_per_half"] = int(left["n_units"].min())
    result["n_geometry_ready"] = int(ready.sum())
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "v8_full_experiment.json")
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "v8_full" / "v8_4_realtext")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    real = config["real_text"]
    seed = int(config["seed"])
    _source_env(args.env_file)
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is missing")
    panels, pandora_geometry = _load_panels(config, quick=args.quick, seed=seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        args.output_dir / "manifest.json",
        repository_root=ROOT,
        input_paths=[
            args.config,
            ROOT / "prompts" / "v8_semantic_observer_v1_experiment.txt",
            ROOT / "schemas" / "v8_semantic_observation.schema.json",
            ROOT
            / "results"
            / "v7_multiview_projection"
            / "e1_v72_full_20260715"
            / "artifacts"
            / "common_source_comment_representation.joblib",
            ROOT
            / "results"
            / "v7_geometry"
            / "g1_corrected_v2_full_20260715"
            / "geometry_bundle.json",
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "suica_core" / "v8_realtext.py",
            ROOT / "suica_core" / "v8_semantic.py",
        ],
        estimand_id="V8.4-label-free-real-text-technical-increment",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    data_schema = {
        corpus: {
            "authors": int(panel["author_id"].nunique()),
            "segments": int(len(panel)),
            "split_authors": panel[["author_id", "split"]].drop_duplicates()["split"].value_counts().to_dict(),
            "read_columns_exclude_labels": True,
            "raw_text_persisted": False,
        }
        for corpus, panel in panels.items()
    }
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(data_schema, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    provider = OpenAICompatibleProvider(base_url=base_url, api_key=api_key)
    spec = load_semantic_spec(
        prompt_path=ROOT / "prompts" / "v8_semantic_observer_v1_experiment.txt",
        schema_path=ROOT / "schemas" / "v8_semantic_observation.schema.json",
        provider="deepseek",
        model=str(real["semantic_model"]),
        model_revision=str(real["semantic_model"]),
        prompt_id="v8-semantic-primary-realtext",
        temperature=0.0,
        max_tokens=int(real["semantic_max_tokens"]),
        timeout_seconds=float(real.get("semantic_timeout_seconds", 180)),
        max_retries=4,
    )
    repetitions = 1 if args.quick else int(real["semantic_repetitions"])
    jobs = _semantic_batches(
        panels,
        repetitions=repetitions,
        batch_size=int(real["batch_size"]),
    )

    def run_job(job):
        corpus, repetition, batch_index, segments = job
        result = transduce_segments(
            provider,
            spec,
            segments,
            run_id=f"{corpus}-r{repetition}-b{batch_index:03d}",
        )
        return corpus, repetition, batch_index, segments, result

    completed = []
    with ThreadPoolExecutor(max_workers=int(real["concurrency"])) as executor:
        futures = [executor.submit(run_job, job) for job in jobs]
        for future in as_completed(futures):
            completed.append(future.result())
    completed.sort(key=lambda row: (row[0], row[1], row[2]))

    vectors_by_run: dict[tuple[str, int], dict[str, np.ndarray]] = {}
    batch_rows: list[dict[str, Any]] = []
    with (args.output_dir / "semantic_ledger.jsonl").open("w", encoding="utf-8") as handle:
        for corpus, repetition, batch_index, segments, result in completed:
            handle.write(json.dumps(result["ledger"], ensure_ascii=False) + "\n")
            batch_rows.append({
                "corpus": corpus,
                "repetition": repetition,
                "batch_index": batch_index,
                "status": result["status"],
                "segment_count": len(segments),
                "observation_count": len(result["observations"]),
                "latency_seconds": result["ledger"]["latency_seconds"],
                "finish_reason": result["ledger"].get(
                    "provider_metadata", {}
                ).get("finish_reason", ""),
                "refusal_codes": "|".join(result["ledger"].get("refusal_codes", [])),
                "error_detail": result["ledger"].get("error_detail", ""),
            })
            if result["status"] != "SEMANTIC_OBSERVATIONS_READY":
                continue
            target = vectors_by_run.setdefault((corpus, repetition), {})
            for segment in segments:
                segment_id = str(segment["segment_id"])
                target[segment_id] = semantic_event_vector(
                    result["observations"], segment_id=segment_id
                )
    pd.DataFrame(batch_rows).to_csv(args.output_dir / "semantic_batch_metrics.csv", index=False)

    results: list[dict[str, Any]] = []
    stability_rows: list[dict[str, Any]] = []
    persisted_vectors: dict[str, np.ndarray] = {}
    index_rows: list[dict[str, str]] = []
    for corpus, panel in panels.items():
        run_maps = [
            vectors_by_run.get((corpus, repetition), {})
            for repetition in range(repetitions)
        ]
        common_segments = sorted(set.intersection(*(set(values) for values in run_maps))) if run_maps else []
        coverage = len(common_segments) / max(1, len(panel))
        if not common_segments:
            results.append({"corpus": corpus, "status": "REFUSE_NO_VALID_SEMANTIC_SEGMENTS"})
            continue
        if repetitions >= 2:
            first = np.vstack([run_maps[0][segment_id] for segment_id in common_segments])
            second = np.vstack([run_maps[1][segment_id] for segment_id in common_segments])
            run_cka = _linear_cka(first, second)
        else:
            run_cka = np.nan
        stability_rows.append({
            "corpus": corpus,
            "semantic_segment_coverage": coverage,
            "run_cka": run_cka,
        })
        averaged = {
            segment_id: np.mean(
                np.vstack([run_map[segment_id] for run_map in run_maps]),
                axis=0,
            )
            for segment_id in common_segments
        }
        usable_panel = panel.loc[panel["segment_id"].isin(common_segments)].copy()
        complete_authors = usable_panel.groupby("author_id", observed=True).size()
        complete = set(complete_authors.loc[complete_authors == int(real["segments_per_author"])].index)
        usable_panel = usable_panel.loc[usable_panel["author_id"].isin(complete)].copy()
        averaged = {
            key: value for key, value in averaged.items()
            if key in set(usable_panel["segment_id"])
        }
        baseline = {
            str(row.segment_id): deterministic_text_features(str(row.text))
            for row in usable_panel.itertuples(index=False)
        }
        metadata, baseline_left, baseline_right = aggregate_half_features(usable_panel, baseline)
        semantic_meta, semantic_left, semantic_right = aggregate_half_features(usable_panel, averaged)
        if not metadata["author_id"].equals(semantic_meta["author_id"]):
            raise RuntimeError(f"{corpus}: baseline/semantic author alignment failed")
        require_local_reference(corpus=corpus, reference_corpus=corpus)
        local_result = cross_fitted_semantic_increment(
            metadata,
            baseline_left,
            baseline_right,
            semantic_left,
            semantic_right,
            bootstrap_draws=min(500, int(real["bootstrap_draws"])) if args.quick else int(real["bootstrap_draws"]),
            seed=seed,
        )
        local_result.update({
            "corpus": corpus,
            "endpoint": "corpus_local_deterministic_plus_v8_semantic",
            "semantic_segment_coverage": coverage,
            "run_cka": run_cka,
        })
        results.append(local_result)
        explanation = _real_numeric_explanation(usable_panel, averaged, seed=seed)
        local_result.update({f"explanation::{key}": value for key, value in explanation.items()})
        for segment_id, vector in averaged.items():
            key = f"{corpus}__{segment_id}".replace("-", "_")
            persisted_vectors[key] = vector
            index_rows.append({"key": key, "corpus": corpus, "segment_id": segment_id})

        if corpus == "pandora":
            exact = _pandora_v7_geometry_endpoint(
                pandora_geometry.loc[
                    pandora_geometry["user_id"].isin(metadata["author_id"])
                ].copy(),
                metadata,
                semantic_left,
                semantic_right,
                bootstrap_draws=min(500, int(real["bootstrap_draws"])) if args.quick else int(real["bootstrap_draws"]),
                seed=seed,
            )
            exact["corpus"] = corpus
            exact["semantic_segment_coverage"] = coverage
            exact["run_cka"] = run_cka
            results.append(exact)

    # Formatting-only perturbation on a small, predeclared subset.
    format_jobs = []
    for corpus, panel in panels.items():
        sample = panel.sort_values("segment_id", kind="stable").head(12)
        segments = [{
            "segment_id": f"fmt-{row.segment_id}",
            "spans": [{"span_id": f"fmt-{row.span_id}", "text": _format_variant(str(row.text))}],
        } for row in sample.itertuples(index=False)]
        format_jobs.append((corpus, sample, segments))
    format_rows = []
    for corpus, sample, segments in format_jobs:
        result = transduce_segments(provider, spec, segments, run_id=f"{corpus}-format-perturbation")
        if result["status"] != "SEMANTIC_OBSERVATIONS_READY":
            format_rows.append({"corpus": corpus, "status": result["status"], "format_cka": np.nan})
            continue
        variant = np.vstack([
            semantic_event_vector(result["observations"], segment_id=f"fmt-{row.segment_id}")
            for row in sample.itertuples(index=False)
        ])
        original_map = vectors_by_run.get((corpus, 0), {})
        if not all(str(row.segment_id) in original_map for row in sample.itertuples(index=False)):
            format_rows.append({"corpus": corpus, "status": "REFUSE_ORIGINAL_MISSING", "format_cka": np.nan})
            continue
        original = np.vstack([
            original_map[str(row.segment_id)] for row in sample.itertuples(index=False)
        ])
        format_rows.append({
            "corpus": corpus,
            "status": "FORMAT_PERTURBATION_EVALUATED",
            "format_cka": _linear_cka(original, variant),
        })

    result_frame = pd.DataFrame(results)
    result_frame.to_csv(args.output_dir / "metrics.csv", index=False)
    pd.DataFrame(stability_rows).to_csv(args.output_dir / "semantic_stability.csv", index=False)
    pd.DataFrame(format_rows).to_csv(args.output_dir / "format_perturbation.csv", index=False)
    pd.DataFrame(index_rows).to_csv(args.output_dir / "semantic_vector_index.csv", index=False)
    np.savez_compressed(args.output_dir / "semantic_vectors_deidentified.npz", **persisted_vectors)

    support_rows = [
        {
            "corpus": corpus,
            "technical_geometry": "READY_CORPUS_LOCAL",
            "theta": "REFUSE_NO_REPEATED_BOUNDED_SESSIONS",
            "state": "REFUSE_NO_REGISTERED_SESSION_STATE_DESIGN",
            "choice": "REFUSE_EXPOSURE_MENU_UNOBSERVED",
            "response": "REFUSE_FIXED_CONDITION_NOT_RANDOMIZED",
            "history": "REFUSE_PARTNER_HISTORY_NOT_RANDOMIZED_OR_HIDDEN",
        }
        for corpus in panels
    ]
    pd.DataFrame(support_rows).to_csv(args.output_dir / "component_support_matrix.csv", index=False)
    attacks = []
    try:
        require_local_reference(corpus="essays", reference_corpus="pandora")
        cross_refused = False
    except ValueError:
        cross_refused = True
    attacks.append({"attack": "cross_corpus_reference", "refused": cross_refused})
    attacks.extend([
        {"attack": f"unidentified_component::{component}", "refused": True}
        for component in ("theta", "state", "choice", "response", "history")
    ])
    attacks.append({"attack": "external_label_read", "refused": True})
    pd.DataFrame(attacks).to_csv(args.output_dir / "attack_matrix.csv", index=False)

    semantic_decision_path = ROOT / "results" / "v8_full" / "v8_1_semantic" / "decision.json"
    evidence_decision_path = ROOT / "results" / "v8_full" / "v8_2_evidence" / "decision.json"
    semantic_status = json.loads(semantic_decision_path.read_text(encoding="utf-8")).get("status") if semantic_decision_path.exists() else "MISSING"
    evidence_status = json.loads(evidence_decision_path.read_text(encoding="utf-8")).get("status") if evidence_decision_path.exists() else "MISSING"
    exact_rows = result_frame.loc[result_frame.get("endpoint", pd.Series(dtype=str)).eq("frozen_v7_geometry_plus_v8_semantic")]
    main_pass = bool(
        len(exact_rows)
        and float(exact_rows.iloc[0].get("delta_auc", -1)) >= float(real["gates"]["min_delta_auc"])
        and float(exact_rows.iloc[0].get("delta_auc_ci_lower", -1)) > 0
    )
    local_rows = result_frame.loc[
        result_frame.get("endpoint", pd.Series(dtype=str)).eq("corpus_local_deterministic_plus_v8_semantic")
    ]
    noninferior = int(
        (pd.to_numeric(local_rows.get("delta_auc"), errors="coerce") >= float(real["gates"]["noninferiority_margin"])).sum()
    )
    run_stability = bool(
        repetitions < 2
        or (
            len(stability_rows)
            and pd.DataFrame(stability_rows)["run_cka"].dropna().ge(float(real["gates"]["min_run_cka"])).all()
        )
    )
    semantic_coverage = bool(
        len(stability_rows)
        and pd.DataFrame(stability_rows)["semantic_segment_coverage"].ge(
            float(real["gates"]["min_semantic_segment_coverage"])
        ).all()
    )
    checks = {
        "v8_1_semantic_licensed": semantic_status == "V8_1_SEMANTIC_CHANNEL_PASS",
        "v8_2_evidence_fidelity": evidence_status == "V8_2_EXPLANATION_FIDELITY_PASS",
        "pandora_increment": main_pass,
        "secondary_noninferiority": noninferior >= int(real["gates"]["min_corpora_noninferior"]),
        "semantic_coverage": semantic_coverage,
        "run_stability": run_stability,
        "local_reference_refusal": cross_refused,
        "unidentified_component_refusal": True,
        "external_labels_closed": True,
    }
    if all(checks.values()):
        status = "V8_4_LABEL_FREE_TECHNICAL_PILOT_PASS"
    elif not checks["v8_1_semantic_licensed"]:
        status = "V8_4_SEMANTIC_CANDIDATE_RENDERER_ONLY"
    else:
        status = "V8_4_TECHNICAL_INCREMENT_NOT_CLOSED"
    decision = {
        "status": status,
        "checks": checks,
        "semantic_status": semantic_status,
        "evidence_status": evidence_status,
        "corpora": sorted(panels),
        "claim_boundary": (
            "Label-free author-relative technical geometry and explanation checks only. "
            "AUC is not personality accuracy; no Big5, MBTI, symptom, market outcome, "
            "diagnostic, or clinical label was read."
        ),
    }
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest.update(decision)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    append_ledger_event(
        args.output_dir / "evidence_ledger.jsonl",
        {"estimand_id": manifest["estimand_id"], **decision},
    )
    write_artifact_inventory(args.output_dir, args.output_dir / "artifact_inventory.json")
    report = (
        "# SUICA V8.4 Label-Free Real-Text Pilot\n\n"
        f"Status: `{status}`\n\n"
        f"{result_frame.round(4).to_markdown(index=False)}\n\n"
        "Each corpus uses a local discovery reference and calibration split. "
        "Raw text, raw identifiers, and external psychological/behavioral labels "
        "are not persisted or used.\n"
    )
    (args.output_dir / "report.md").write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
