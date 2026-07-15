#!/usr/bin/env python3
"""Describe V7 cross-view spectral effective rank without claiming factors."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v7_multiview_method_benchmark import (  # noqa: E402
    DEFAULT_CONFIG,
    _aligned_ids,
    _blocks,
    _cohort_commitment,
    _cohort_recipe,
    _fit_representation,
    _operator_specs,
    _select_declared_cohort,
    _transform,
)
from scripts.run_suica_v7_operator_smoke import DEFAULT_INPUT, _infer_column, _load_config, _read_table  # noqa: E402
from scripts.run_suica_v7_temporal_geometry_baselines import (  # noqa: E402
    DEFAULT_E0,
    DEFAULT_E1,
    DEFAULT_E2_CONFIG,
    DEFAULT_E4_CONFIG,
    DEFAULT_CONFIG as W3_CONFIG,
    _prior_exclusions,
)
from suica_core.v7_crossview_spectrum import broken_correspondence_spectra, excess_spectral_profile, profile_cosine  # noqa: E402
from suica_core.v7_governance import append_ledger_event, write_artifact_inventory, write_run_manifest  # noqa: E402
from suica_core.v7_multiview import common_feature_columns, fit_block_scalers  # noqa: E402
from suica_core.v7_observations import build_observations, canonicalize_comments, prepare_source_panel, select_reference_authors  # noqa: E402
from suica_core.v7_psychometric import author_features_from_embeddings  # noqa: E402


DEFAULT_RANK_CONFIG = ROOT / "configs" / "v7_multiview_method_benchmark_rank_extension.json"


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_RANK_CONFIG)
    parser.add_argument("--e0-cohort", type=Path, default=DEFAULT_E0)
    parser.add_argument("--e1-cohort", type=Path, default=DEFAULT_E1)
    parser.add_argument("--e2-config", type=Path, default=DEFAULT_E2_CONFIG)
    parser.add_argument("--e4-config", type=Path, default=DEFAULT_E4_CONFIG)
    parser.add_argument("--w3-config", type=Path, default=W3_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def _report(path: Path, *, table: pd.DataFrame, similarity: pd.DataFrame, decision: dict[str, Any], output_dir: Path) -> None:
    """Write a clear capacity diagnostic with no latent-factor interpretation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# SUICA V7 Cross-View Effective-Rank Diagnostic\n\n"
        "## Scope\n\n"
        "This diagnostic describes the spectrum of split-centered off-diagonal cross-view covariance after subtracting a split-specific correspondence-breaking null envelope. It retains positive observed modes above the registered 95-percent null envelope. It measures distributed shared-text geometry in a frozen common-coordinate representation; it neither selects a factor count nor names components.\n\n"
        f"### Split Profiles\n\n{table.to_markdown(index=False, floatfmt='.3f')}\n\n"
        f"### Excess-Profile Similarity\n\n{similarity.to_markdown(index=False, floatfmt='.3f')}\n\n"
        f"## Decision\n\n```json\n{json.dumps(decision, ensure_ascii=False, indent=2)}\n```\n\n"
        "## Boundary\n\n"
        "Entropy effective rank, participation rank, and 90%-energy rank are capacity descriptors of a representation-specific positive-excess covariance spectrum. They are not the number of human traits, scales, psychological factors, or clinical states. The method requires common frozen feature coordinates; it is not invariant to independent rotations, arbitrary domain transforms, or different embedding runtimes. Confirmation rows reuse the registered W4b cohort and are therefore a derived technical diagnostic, not a new independent replication.\n\n"
        f"Artifacts: `{output_dir}`\n",
        encoding="utf-8",
    )


def main() -> int:
    args = _args()
    config = _load_config(args.config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        args.output_dir / "run_manifest.json", repository_root=ROOT,
        input_paths=[args.input, args.config, args.e0_cohort, args.e1_cohort, args.e2_config, args.e4_config, args.w3_config],
        config_path=args.config,
        code_paths=[Path(__file__), ROOT / "suica_core" / "v7_crossview_spectrum.py", ROOT / "suica_core" / "v7_multiview.py"],
        estimand_id="V7.3-W4b-crossview-effective-rank-diagnostic", external_labels_read=False, raw_identifiers_persisted=False,
    )
    raw = _read_table(args.input)
    columns = [str(column) for column in raw.columns]
    canonical = canonicalize_comments(
        raw,
        user_col=str(_infer_column(columns, ["author", "user_id", "participant_id", "user", "id"], None, required=True)),
        text_col=str(_infer_column(columns, ["body", "text", "comment", "content", "message"], None, required=True)),
        order_col=_infer_column(columns, ["created_utc", "timestamp", "time", "date", "created_at"], None, required=False),
        condition_col=_infer_column(columns, ["subreddit", "condition", "platform", "task", "forum"], None, required=False),
        min_tokens=int(config["min_tokens_per_unit"]),
    )
    exclusions = _prior_exclusions(canonical, e0_path=args.e0_cohort, e1_path=args.e1_cohort, e2_config_path=args.e2_config, e4_config_path=args.e4_config)
    w3 = _load_config(args.w3_config)
    w3_selected = select_reference_authors(canonical, min_comments_per_user=int(w3["min_comments_per_user"]), max_users=int(w3["max_users"]), seed=int(w3["seed"]), exclude_user_ids=exclusions, cohort_salt="v7.3-w3-temporal-geometry-1")
    exclusions.update(w3_selected["user_id"].astype(str))
    for raw_recipe in config.get("exclude_w4_cohorts", []):
        previous = _select_declared_cohort(canonical, exclusions=exclusions, recipe=dict(raw_recipe))
        exclusions.update(previous["user_id"].astype(str))
    recipe = _cohort_recipe(config)
    selected = _select_declared_cohort(canonical, exclusions=exclusions, recipe=recipe)
    specs = _operator_specs(config)
    source_panel = prepare_source_panel(selected, specs[0])
    views = tuple(spec.name for spec in specs)
    units = {spec.name: build_observations(source_panel, spec) for spec in specs}
    rows: list[dict[str, Any]] = []
    similarity_rows: list[dict[str, Any]] = []
    for rep_index, rep in enumerate(config["representations"]):
        vectorizer, reducer = _fit_representation(source_panel.loc[source_panel["split"].eq("discovery"), "text"], rep, seed=int(config["seed"]) + rep_index)
        frames = {view: author_features_from_embeddings(units[view], _transform(vectorizer, reducer, units[view]["text"])) for view in views}
        feature_names = common_feature_columns(frames, views)
        ids = {split: _aligned_ids(frames, views, split) for split in ("discovery", "calibration", "confirmation")}
        scalers = fit_block_scalers(frames, view_names=views, feature_names=feature_names, discovery_user_ids=ids["discovery"])
        blocks = {split: _blocks(frames, scalers, views, ids[split]) for split in ids}
        # The null spectrum depends on the number of aligned authors. Each
        # split therefore receives its own correspondence-breaking envelope;
        # discovery's n=120 null is not reused for smaller panels.
        nulls = {
            split: broken_correspondence_spectra(
                blocks[split],
                view_names=views,
                iterations=int(config["broken_correspondence_iterations"]),
                seed=int(config["seed"]) + 9000 + 100 * rep_index + split_index,
            )
            for split_index, split in enumerate(("discovery", "calibration", "confirmation"))
        }
        profiles = {
            split: excess_spectral_profile(blocks[split], view_names=views, null_upper=np.quantile(nulls[split], 0.95, axis=0))
            for split in blocks
        }
        for split, profile in profiles.items():
            rows.append({
                "representation": rep["name"],
                "split": split,
                "n_authors": int(len(ids[split])),
                "n_positive_excess": profile["n_positive_excess"],
                "entropy_effective_rank": profile["entropy_effective_rank"],
                "participation_effective_rank": profile["participation_effective_rank"],
                "excess_energy_90_rank": profile["excess_energy_90_rank"],
            })
        for target in ("calibration", "confirmation"):
            similarity_rows.append({
                "representation": rep["name"],
                "reference_split": "discovery",
                "target_split": target,
                "excess_profile_cosine": profile_cosine(profiles["discovery"]["excess_eigenvalues"], profiles[target]["excess_eigenvalues"]),
            })
    table = pd.DataFrame(rows)
    similarity = pd.DataFrame(similarity_rows)
    decision = {
        "status": "CROSSVIEW_EFFECTIVE_RANK_DESCRIBED",
        "rank_interpretation": "CAPACITY_DESCRIPTOR_NOT_FACTOR_COUNT",
        "spectrum_estimand": "POSITIVE_OBSERVED_MODES_ABOVE_SPLIT_SPECIFIC_BROKEN_CORRESPONDENCE_95_PERCENT_ENVELOPE",
        "null_calibration": "SPLIT_SPECIFIC_AUTHOR_COUNT",
        "coordinate_requirement": "Common frozen feature coordinates within one representation only.",
        "cohort_commitment": _cohort_commitment(source_panel["user_id"], recipe=recipe),
        "confirmation_reused_from_w4b": True,
        "claim_boundary": "No factor count, personality, causal, clinical, or universal-language claim.",
    }
    table.to_csv(args.output_dir / "effective_rank_profiles.csv", index=False)
    similarity.to_csv(args.output_dir / "effective_rank_profile_similarity.csv", index=False)
    (args.output_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.update({"cohort_commitment": decision["cohort_commitment"], "external_labels_read": False, "raw_identifiers_persisted": False, "claim_boundary": decision["claim_boundary"]})
    (args.output_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _report(args.report, table=table, similarity=similarity, decision=decision, output_dir=args.output_dir)
    append_ledger_event(args.output_dir / "evidence_ledger.jsonl", {"estimand_id": manifest["estimand_id"], "status": decision["status"], "claim_boundary": decision["claim_boundary"]})
    inventory = write_artifact_inventory(args.output_dir, args.output_dir / "artifact_inventory.json")
    print(json.dumps({"status": decision["status"], "output_dir": str(args.output_dir), "artifact_files": inventory["n_files"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
