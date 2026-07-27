#!/usr/bin/env python3
"""Audit fresh-author and condition support without model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_suica_v8_interpreter_pandora as pandora  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_realtext import stable_digest  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_behavior_v21_fresh_protocol.json"
DEFAULT_RAW_COMMENTS = (
    Path("/Volumes/mobile3/projects/project persona")
    / "data_sets"
    / "PANDORA_official"
    / "all_comments_since_2015.csv"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_behavior_v21_fresh_preflight"
    / "pandora_20260725"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _hash_order(value: str, *, salt: str) -> str:
    return hashlib.sha256(f"{salt}::{value}".encode("utf-8")).hexdigest()


def _canonical_registered_pool(
    raw_authors: set[str],
    v7_authors: set[str],
    *,
    seed: int,
    pool_size: int = 180,
) -> set[str]:
    ordered = sorted(
        raw_authors - v7_authors,
        key=lambda value: hashlib.sha256(
            f"v8-canonical-fresh::{seed}::{value}".encode("utf-8")
        ).hexdigest(),
    )
    return set(ordered[:pool_size])


def _source_signature(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        header = handle.readline()
    stat = path.stat()
    return {
        "path": str(path),
        "size_bytes": int(stat.st_size),
        "mtime_ns": int(stat.st_mtime_ns),
        "header_sha256": hashlib.sha256(header).hexdigest(),
        "full_sha256": None,
        "boundary": (
            "Preflight source signature only. The final fresh run must seal "
            "the complete input file."
        ),
    }


def _read_candidate_comments(
    path: Path,
    candidates: set[str],
    *,
    chunksize: int = 50_000,
) -> pd.DataFrame:
    usecols = [
        "author",
        "body",
        "created_utc",
        "link_id",
        "id",
        "subreddit",
        "lang",
    ]
    selected = []
    for chunk in pd.read_csv(
        path,
        usecols=usecols,
        chunksize=chunksize,
        low_memory=False,
    ):
        authors = chunk["author"].astype(str)
        keep = authors.isin(candidates)
        if keep.any():
            selected.append(chunk.loc[keep].copy())
    if not selected:
        return pd.DataFrame(columns=usecols)
    frame = pd.concat(selected, ignore_index=True)
    frame["author"] = frame["author"].astype(str)
    frame["body"] = frame["body"].fillna("").astype(str).str.strip()
    frame["lang"] = frame["lang"].fillna("").astype(str).str.lower()
    frame["link_id"] = frame["link_id"].fillna("").astype(str)
    frame["id"] = frame["id"].fillna("").astype(str)
    frame["subreddit"] = frame["subreddit"].fillna("").astype(str)
    frame["created_utc"] = pd.to_numeric(
        frame["created_utc"],
        errors="coerce",
    )
    frame = frame.loc[
        frame["lang"].eq("en")
        & frame["body"].ne("")
        & ~frame["body"].str.lower().isin({"[deleted]", "[removed]"})
        & frame["link_id"].ne("")
        & frame["id"].ne("")
        & frame["created_utc"].notna()
    ].drop_duplicates(["author", "id"])
    return frame.reset_index(drop=True)


def _time_even_rows(frame: pd.DataFrame, count: int) -> pd.DataFrame:
    ordered = frame.sort_values(
        ["created_utc", "id"],
        kind="stable",
    ).reset_index(drop=True)
    indices = np.unique(
        np.linspace(0, len(ordered) - 1, num=count, dtype=int)
    )
    if len(indices) != count:
        raise RuntimeError("time-even selection produced duplicate indices")
    return ordered.iloc[indices].copy()


def _thread_disjoint_halves(
    frame: pd.DataFrame,
    *,
    comments_per_half: int,
) -> pd.DataFrame | None:
    threads = (
        frame.groupby("link_id", observed=True)
        .agg(
            comments=("id", "count"),
            median_time=("created_utc", "median"),
        )
        .reset_index()
        .sort_values(["median_time", "link_id"], kind="stable")
    )
    side_threads: dict[str, list[str]] = {"left": [], "right": []}
    side_counts = {"left": 0, "right": 0}
    for row in threads.itertuples(index=False):
        side = min(
            ("left", "right"),
            key=lambda value: (side_counts[value], value),
        )
        side_threads[side].append(str(row.link_id))
        side_counts[side] += int(row.comments)
    if min(side_counts.values()) < comments_per_half:
        return None
    halves = []
    for side in ("left", "right"):
        source = frame.loc[
            frame["link_id"].isin(side_threads[side])
        ]
        selected = _time_even_rows(source, comments_per_half)
        selected["side"] = side
        halves.append(selected)
    result = pd.concat(halves, ignore_index=True)
    left_threads = set(result.loc[result["side"].eq("left"), "link_id"])
    right_threads = set(result.loc[result["side"].eq("right"), "link_id"])
    if left_threads & right_threads:
        raise RuntimeError("thread-disjoint split invariant failed")
    return result


def _panel_rows(
    comments: pd.DataFrame,
    ordered_candidates: list[str],
    *,
    comments_per_half: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected_rows = []
    author_rows = []
    for raw_author in ordered_candidates:
        source = comments.loc[comments["author"].eq(raw_author)]
        halves = _thread_disjoint_halves(
            source,
            comments_per_half=comments_per_half,
        )
        if halves is None:
            continue
        author_id = stable_digest(
            raw_author,
            salt="v8-behavior-v21-fresh-author",
        )
        halves["author_id"] = author_id
        selected_rows.append(halves.drop(columns=["author"]))
        left = halves.loc[halves["side"].eq("left")]
        right = halves.loc[halves["side"].eq("right")]
        author_rows.append({
            "author_id": author_id,
            "valid_comments": int(len(source)),
            "valid_threads": int(source["link_id"].nunique()),
            "left_selected": int(len(left)),
            "right_selected": int(len(right)),
            "left_threads": int(left["link_id"].nunique()),
            "right_threads": int(right["link_id"].nunique()),
            "thread_overlap": int(
                len(set(left["link_id"]) & set(right["link_id"]))
            ),
            "left_time_span_days": float(
                (left["created_utc"].max() - left["created_utc"].min())
                / 86400.0
            ),
            "right_time_span_days": float(
                (right["created_utc"].max() - right["created_utc"].min())
                / 86400.0
            ),
            "subreddit_jaccard": float(
                len(set(left["subreddit"]) & set(right["subreddit"]))
                / max(
                    len(set(left["subreddit"]) | set(right["subreddit"])),
                    1,
                )
            ),
        })
    return (
        pd.DataFrame(author_rows),
        pd.concat(selected_rows, ignore_index=True)
        if selected_rows
        else pd.DataFrame(),
    )


def _assign_splits(
    authors: pd.DataFrame,
    *,
    panel: dict[str, Any],
) -> pd.DataFrame:
    counts = [
        ("discovery", int(panel["discovery_authors"])),
        ("calibration", int(panel["calibration_authors"])),
        ("confirmation", int(panel["confirmation_authors"])),
    ]
    required = sum(value for _, value in counts)
    preextract = int(panel["preextract_target_authors"])
    if len(authors) < preextract:
        raise RuntimeError(
            f"only {len(authors)} ready authors; {preextract} required"
        )
    selected = authors.head(preextract).copy()
    selected["split"] = "reserve"
    offset = 0
    for split, count in counts:
        selected.iloc[
            offset:offset + count,
            selected.columns.get_loc("split"),
        ] = split
        offset += count
    if offset != required:
        raise RuntimeError("split assignment invariant failed")
    return selected


def _condition_support(
    segments: pd.DataFrame,
    assigned: pd.DataFrame,
    *,
    minimum_authors: int,
    minimum_segments: int,
    minimum_cell_segments: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    split_lookup = assigned.set_index("author_id")["split"]
    used = segments.loc[
        segments["author_id"].isin(split_lookup.index)
    ].copy()
    used["split"] = used["author_id"].map(split_lookup)
    discovery = used.loc[used["split"].eq("discovery")]
    conditions = (
        discovery.groupby("subreddit", observed=True)
        .agg(
            discovery_authors=("author_id", "nunique"),
            discovery_segments=("id", "count"),
        )
        .reset_index()
    )
    conditions["exact_supported"] = (
        conditions["discovery_authors"].ge(minimum_authors)
        & conditions["discovery_segments"].ge(minimum_segments)
    )
    supported = set(
        conditions.loc[conditions["exact_supported"], "subreddit"]
    )
    used["condition_arm"] = used["subreddit"].map(
        lambda value: (
            "A"
            if int(
                _hash_order(
                    str(value),
                    salt="v8b21-c2-condition-arm",
                )[:8],
                16,
            ) % 2 == 0
            else "B"
        )
    )
    used["exact_supported"] = used["subreddit"].isin(supported)
    confirmation_ids = set(
        assigned.loc[
            assigned["split"].eq("confirmation"),
            "author_id",
        ]
    )

    def complete_fraction(frame: pd.DataFrame) -> float:
        counts = (
            frame.loc[frame["author_id"].isin(confirmation_ids)]
            .groupby(
                ["author_id", "side", "condition_arm"],
                observed=True,
            )["id"]
            .count()
            .unstack(["side", "condition_arm"], fill_value=0)
        )
        required_columns = [
            ("left", "A"),
            ("left", "B"),
            ("right", "A"),
            ("right", "B"),
        ]
        for column in required_columns:
            if column not in counts:
                counts[column] = 0
        complete = (
            counts[required_columns]
            .ge(minimum_cell_segments)
            .all(axis=1)
        )
        return float(
            complete.reindex(sorted(confirmation_ids), fill_value=False).mean()
        )

    summary = {
        "exact_supported_conditions": int(len(supported)),
        "discovery_segments_in_exact_supported_conditions": float(
            discovery["subreddit"].isin(supported).mean()
        ),
        "confirmation_structural_cell_complete_fraction_all_conditions": (
            complete_fraction(used)
        ),
        "confirmation_structural_cell_complete_fraction_exact_supported": (
            complete_fraction(used.loc[used["exact_supported"]])
        ),
        "boundary": (
            "Opportunity counts are unavailable before observation. These "
            "are structural upper bounds, not a C2 pass."
        ),
    }
    return conditions.sort_values(
        ["exact_supported", "discovery_authors", "discovery_segments"],
        ascending=[False, False, False],
        kind="stable",
    ), summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--raw-comments",
        type=Path,
        default=DEFAULT_RAW_COMMENTS,
    )
    parser.add_argument(
        "--prepared-comments",
        type=Path,
        default=pandora.PANDORA_COMMENTS_PATH,
    )
    parser.add_argument(
        "--eligible-authors",
        type=Path,
        default=pandora.ELIGIBLE_AUTHORS_PATH,
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read_json(args.config)
    panel = config["panel"]
    prepared_counts = pd.read_parquet(
        args.prepared_comments,
        columns=["author"],
    )["author"].astype(str).value_counts()
    v7_authors = set(
        pd.read_csv(
            args.eligible_authors,
            usecols=["user_id"],
            dtype={"user_id": str},
        )["user_id"].astype(str)
    )
    raw_authors = set(prepared_counts.index.astype(str))
    canonical_pool = _canonical_registered_pool(
        raw_authors,
        v7_authors,
        seed=int(config["seed"]),
    )
    available = prepared_counts.drop(
        labels=list(v7_authors | canonical_pool),
        errors="ignore",
    )
    available = available.loc[
        available.ge(int(panel["minimum_comments_per_author"]))
    ]
    ordered_candidates = sorted(
        available.index.astype(str),
        key=lambda value: _hash_order(
            value,
            salt=f"v8-behavior-v21-fresh-{config['seed']}",
        ),
    )[:int(panel["candidate_scan_authors"])]
    raw = _read_candidate_comments(
        args.raw_comments,
        set(ordered_candidates),
    )
    author_support, selected_segments = _panel_rows(
        raw,
        ordered_candidates,
        comments_per_half=int(panel["comments_per_half"]),
    )
    order_lookup = {
        author: index for index, author in enumerate(ordered_candidates)
    }
    raw_to_hash = {
        author: stable_digest(
            author,
            salt="v8-behavior-v21-fresh-author",
        )
        for author in ordered_candidates
    }
    hash_to_order = {
        hashed: order_lookup[raw]
        for raw, hashed in raw_to_hash.items()
    }
    author_support["_order"] = author_support["author_id"].map(hash_to_order)
    author_support = author_support.sort_values(
        "_order",
        kind="stable",
    ).drop(columns="_order").reset_index(drop=True)
    assigned = _assign_splits(author_support, panel=panel)
    condition_table, condition_summary = _condition_support(
        selected_segments,
        assigned,
        minimum_authors=int(
            config["c2"]["exact_condition_minimum_discovery_authors"]
        ),
        minimum_segments=int(
            config["c2"]["exact_condition_minimum_discovery_segments"]
        ),
        minimum_cell_segments=int(
            config["c2"]["minimum_opportunities_per_cell_family"]
        ),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    assigned.to_csv(
        args.output_dir / "fresh_panel_assignment_pseudonymous.csv",
        index=False,
    )
    condition_table.to_csv(
        args.output_dir / "condition_support_preflight.csv",
        index=False,
    )
    split_summary = (
        assigned.groupby("split", observed=True)
        .agg(
            authors=("author_id", "nunique"),
            median_valid_comments=("valid_comments", "median"),
            median_valid_threads=("valid_threads", "median"),
            minimum_time_span_days=(
                "left_time_span_days",
                lambda values: float(
                    min(
                        values.min(),
                        assigned.loc[
                            values.index,
                            "right_time_span_days",
                        ].min(),
                    )
                ),
            ),
            maximum_thread_overlap=("thread_overlap", "max"),
        )
        .reset_index()
    )
    split_summary.to_csv(
        args.output_dir / "fresh_panel_split_summary.csv",
        index=False,
    )
    source_signature = _source_signature(args.raw_comments)
    _write_json(
        args.output_dir / "raw_source_preflight_signature.json",
        source_signature,
    )
    checks = {
        "preextract_author_target": (
            len(assigned) >= int(panel["preextract_target_authors"])
        ),
        "registered_split_counts": (
            assigned["split"].value_counts().to_dict()
            == {
                "confirmation": int(panel["confirmation_authors"]),
                "discovery": int(panel["discovery_authors"]),
                "reserve": (
                    int(panel["preextract_target_authors"])
                    - int(panel["discovery_authors"])
                    - int(panel["calibration_authors"])
                    - int(panel["confirmation_authors"])
                ),
                "calibration": int(panel["calibration_authors"]),
            }
        ),
        "thread_disjoint": bool(assigned["thread_overlap"].eq(0).all()),
        "minimum_half_support": bool(
            assigned[["left_selected", "right_selected"]]
            .ge(int(panel["comments_per_half"]))
            .all(axis=None)
        ),
    }
    status = (
        "V8_BEHAVIOR_V21_FRESH_PREFLIGHT_READY_HUMAN_GATE_CLOSED"
        if all(checks.values())
        else "V8_BEHAVIOR_V21_FRESH_PREFLIGHT_STOP"
    )
    decision = {
        "status": status,
        "checks": checks,
        "candidate_scan_authors": int(len(ordered_candidates)),
        "raw_candidate_rows": int(len(raw)),
        "ready_authors_before_preextract_cap": int(len(author_support)),
        "assigned_authors": int(len(assigned)),
        "split_counts": assigned["split"].value_counts().to_dict(),
        "v7_authors_excluded": int(len(v7_authors)),
        "canonical_registered_pool_excluded": int(len(canonical_pool)),
        "condition_support": condition_summary,
        "joint_c1_preflight_ready": bool(all(checks.values())),
        "c2_reddit_status": (
            "V8_BEHAVIOR_V21_C2_NOT_IDENTIFIABLE_IN_REDDIT"
        ),
        "c2_reddit_execution_licensed": False,
        "fresh_execution_licensed": False,
        "fresh_execution_blocker": (
            "V8_BEHAVIOR_V21_HUMAN_GATE_PASS is not yet available"
        ),
        "new_llm_calls": 0,
        "external_labels_read": False,
        "raw_identifiers_persisted": False,
        "claim_boundary": (
            "This preflight establishes author, thread, time, and condition "
            "support only. It is not a fresh replication, observer-accuracy "
            "result, C2 result, personality result, or geometry bridge."
        ),
    }
    _write_json(args.output_dir / "preflight_decision.json", decision)
    _write_json(args.output_dir / "config.resolved.json", config)
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            args.prepared_comments,
            args.eligible_authors,
        ],
        config_path=args.config,
        code_paths=[Path(__file__)],
        estimand_id="V8-I12-behavior-v21-fresh-support-preflight",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
