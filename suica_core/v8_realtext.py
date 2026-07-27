"""Label-free, deidentified real-text utilities for the SUICA V8 pilot."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .joint_process import same_author_auc
from .suica import tokenize


URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
FIRST_PERSON_RE = re.compile(r"\b(?:i|me|my|mine|myself|we|us|our|ours)\b|(?:私|僕|俺|自分)", re.IGNORECASE)
DIRECTIVE_RE = re.compile(r"\b(?:should|must|need to|try|please|recommend|suggest|let us|let's)\b|(?:べき|必要|してください|しよう)", re.IGNORECASE)


def stable_digest(value: str, *, salt: str) -> str:
    """Return a deterministic non-reversible identifier for persisted outputs."""
    return hashlib.sha256(f"{salt}::{value}".encode("utf-8")).hexdigest()[:20]


def stable_order(value: str, *, salt: str) -> int:
    """Return a stable integer used only for deterministic sampling."""
    return int.from_bytes(
        hashlib.sha256(f"{salt}::{value}".encode("utf-8")).digest()[:8],
        "big",
    )


def v8_author_split(author_id: str, *, seed: int = 20260724) -> str:
    """Assign authors to 50/25/25 discovery/calibration/confirmation splits."""
    bucket = stable_order(str(author_id), salt=f"v8-split-{seed}") % 10_000
    if bucket < 5_000:
        return "discovery"
    if bucket < 7_500:
        return "calibration"
    return "confirmation"


def require_local_reference(*, corpus: str, reference_corpus: str) -> None:
    """Refuse a score when its norm/reference was fitted on another corpus."""
    if str(corpus) != str(reference_corpus):
        raise ValueError(
            "REFUSE_NONLOCAL_REFERENCE: each V8.4 corpus requires its own "
            "discovery reference and calibration"
        )


def document_segments(
    text: str,
    *,
    count: int,
    min_tokens: int = 24,
    max_tokens: int = 96,
) -> list[str]:
    """Create non-overlapping, evenly covered text segments."""
    tokens = tokenize(str(text or ""))
    if len(tokens) < int(count) * int(min_tokens):
        return []
    boundaries = np.linspace(0, len(tokens), num=int(count) + 1, dtype=int)
    segments: list[str] = []
    for left, right in zip(boundaries[:-1], boundaries[1:], strict=True):
        midpoint = (int(left) + int(right)) // 2
        half = int(max_tokens) // 2
        start = max(int(left), midpoint - half)
        end = min(int(right), start + int(max_tokens))
        if end - start < int(min_tokens):
            return []
        segments.append(" ".join(tokens[start:end]))
    return segments


def _sample_authors(
    authors: Iterable[str],
    *,
    max_authors: int,
    salt: str,
) -> list[str]:
    values = sorted(set(map(str, authors)), key=lambda value: stable_order(value, salt=salt))
    return values[: int(max_authors)]


def load_document_panel(
    path: str | Path,
    *,
    corpus: str,
    user_col: str,
    text_col: str,
    max_authors: int,
    segments_per_author: int,
    seed: int,
) -> pd.DataFrame:
    """Load one-document-per-author corpora without reading label columns."""
    frame = pd.read_csv(path, usecols=[user_col, text_col], dtype={user_col: str})
    rows: list[dict[str, Any]] = []
    candidates: list[tuple[str, list[str]]] = []
    for value in frame.itertuples(index=False, name=None):
        user, text = str(value[0]), str(value[1])
        segments = document_segments(text, count=segments_per_author)
        if segments:
            candidates.append((user, segments))
    selected = set(_sample_authors(
        (user for user, _ in candidates),
        max_authors=max_authors,
        salt=f"{corpus}-{seed}",
    ))
    for user, segments in candidates:
        if user not in selected:
            continue
        for index, text in enumerate(segments):
            rows.append({
                "corpus": corpus,
                "author_internal": user,
                "author_id": stable_digest(user, salt=f"{corpus}-author"),
                "split": v8_author_split(user, seed=seed),
                "segment_id": f"{corpus}-{stable_digest(user, salt='segment-author')}-{index:02d}",
                "span_id": f"{corpus}-span-{stable_digest(user, salt='span-author')}-{index:02d}",
                "unit_index": index,
                "text": text,
                "condition": "<document>",
            })
    return pd.DataFrame(rows)


def load_pandora_panel(
    parquet_path: str | Path,
    *,
    eligible_authors: pd.DataFrame,
    max_by_split: dict[str, int],
    segments_per_author: int,
    seed: int,
) -> pd.DataFrame:
    """Load source-disjoint PANDORA comments for a declared V7 author panel."""
    required = {"user_id", "split"}
    if not required.issubset(eligible_authors):
        raise ValueError("eligible_authors must contain user_id and split")
    selected: set[str] = set()
    split_map: dict[str, str] = {}
    for split, group in eligible_authors.groupby("split", observed=True):
        users = _sample_authors(
            group["user_id"].astype(str),
            max_authors=int(max_by_split.get(str(split), 0)),
            salt=f"pandora-v8-{split}-{seed}",
        )
        selected.update(users)
        split_map.update({user: str(split) for user in users})
    raw = pd.read_parquet(
        parquet_path,
        columns=["author", "body", "created_utc", "subreddit"],
        filters=[("author", "in", sorted(selected))],
    )
    raw["author"] = raw["author"].astype(str)
    raw["body"] = raw["body"].fillna("").astype(str)
    raw["token_count"] = raw["body"].map(lambda value: len(tokenize(value)))
    raw = raw.loc[raw["token_count"] >= 24].copy()
    rows: list[dict[str, Any]] = []
    for user, group in raw.sort_values(["author", "created_utc"], kind="stable").groupby(
        "author", observed=True, sort=False
    ):
        if len(group) < segments_per_author:
            continue
        indices = np.unique(np.linspace(0, len(group) - 1, num=segments_per_author, dtype=int))
        if len(indices) != segments_per_author:
            continue
        for index, value in enumerate(group.iloc[indices].itertuples(index=False)):
            tokens = tokenize(str(value.body))
            midpoint = len(tokens) // 2
            start = max(0, midpoint - 48)
            text = " ".join(tokens[start:start + 96])
            rows.append({
                "corpus": "pandora",
                "author_internal": str(user),
                "author_id": stable_digest(str(user), salt="pandora-author"),
                "split": split_map[str(user)],
                "segment_id": f"pandora-{stable_digest(str(user), salt='segment-author')}-{index:02d}",
                "span_id": f"pandora-span-{stable_digest(str(user), salt='span-author')}-{index:02d}",
                "unit_index": index,
                "text": text,
                "condition": str(value.subreddit),
            })
    return pd.DataFrame(rows)


def load_pandora_source_disjoint_panels(
    parquet_path: str | Path,
    *,
    eligible_authors: pd.DataFrame,
    max_by_split: dict[str, int],
    semantic_segments_per_author: int,
    geometry_units_per_half: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build aligned semantic and frozen-V7 geometry panels.

    Each author first contributes a deterministic pool of source comments.
    Alternating comments from that pool define source-disjoint left/right
    geometry halves.  The smaller semantic panel is sampled within those
    halves, so its even/odd aggregation preserves the same side assignment.
    """
    if int(semantic_segments_per_author) < 2 or int(semantic_segments_per_author) % 2:
        raise ValueError("semantic_segments_per_author must be an even integer >= 2")
    if int(geometry_units_per_half) < int(semantic_segments_per_author) // 2:
        raise ValueError("geometry_units_per_half cannot be smaller than a semantic half")
    required = {"user_id", "split"}
    if not required.issubset(eligible_authors):
        raise ValueError("eligible_authors must contain user_id and split")

    selected: set[str] = set()
    split_map: dict[str, str] = {}
    for split, group in eligible_authors.groupby("split", observed=True):
        users = _sample_authors(
            group["user_id"].astype(str),
            max_authors=int(max_by_split.get(str(split), 0)),
            salt=f"pandora-v8-{split}-{seed}",
        )
        selected.update(users)
        split_map.update({user: str(split) for user in users})

    raw = pd.read_parquet(
        parquet_path,
        columns=["author", "body", "created_utc", "subreddit"],
        filters=[("author", "in", sorted(selected))],
    )
    raw["author"] = raw["author"].astype(str)
    raw["body"] = raw["body"].fillna("").astype(str)
    raw["token_count"] = raw["body"].map(lambda value: len(tokenize(value)))
    raw = raw.loc[raw["token_count"] >= 24].copy()

    semantic_rows: list[dict[str, Any]] = []
    geometry_rows: list[dict[str, Any]] = []
    pool_size = 2 * int(geometry_units_per_half)
    semantic_per_half = int(semantic_segments_per_author) // 2
    for user, group in raw.sort_values(["author", "created_utc"], kind="stable").groupby(
        "author", observed=True, sort=False
    ):
        if len(group) < pool_size:
            continue
        indices = np.unique(np.linspace(0, len(group) - 1, num=pool_size, dtype=int))
        if len(indices) != pool_size:
            continue
        pool = group.iloc[indices].reset_index(drop=True)
        author_id = stable_digest(str(user), salt="pandora-author")
        sides = {
            "left": pool.iloc[::2].reset_index(drop=True),
            "right": pool.iloc[1::2].reset_index(drop=True),
        }
        if any(len(side) != int(geometry_units_per_half) for side in sides.values()):
            continue
        for side_name, side in sides.items():
            for value in side.itertuples(index=False):
                geometry_rows.append({
                    "user_id": author_id,
                    "split": side_name,
                    "token_count": int(value.token_count),
                    "text": str(value.body),
                })
            semantic_indices = np.unique(
                np.linspace(
                    0,
                    len(side) - 1,
                    num=semantic_per_half,
                    dtype=int,
                )
            )
            if len(semantic_indices) != semantic_per_half:
                continue
            side_offset = 0 if side_name == "left" else 1
            for rank, value in enumerate(side.iloc[semantic_indices].itertuples(index=False)):
                tokens = tokenize(str(value.body))
                midpoint = len(tokens) // 2
                start = max(0, midpoint - 48)
                text = " ".join(tokens[start:start + 96])
                unit_index = 2 * rank + side_offset
                semantic_rows.append({
                    "corpus": "pandora",
                    "author_internal": str(user),
                    "author_id": author_id,
                    "split": split_map[str(user)],
                    "segment_id": (
                        f"pandora-{stable_digest(str(user), salt='segment-author')}-"
                        f"{unit_index:02d}"
                    ),
                    "span_id": (
                        f"pandora-span-{stable_digest(str(user), salt='span-author')}-"
                        f"{unit_index:02d}"
                    ),
                    "unit_index": unit_index,
                    "text": text,
                    "condition": str(value.subreddit),
                })
    semantic = pd.DataFrame(semantic_rows)
    geometry = pd.DataFrame(geometry_rows)
    if not semantic.empty:
        complete = semantic.groupby("author_id", observed=True).size()
        complete_ids = set(
            complete.loc[complete == int(semantic_segments_per_author)].index.astype(str)
        )
        semantic = semantic.loc[semantic["author_id"].isin(complete_ids)].copy()
        geometry = geometry.loc[geometry["user_id"].isin(complete_ids)].copy()
    return (
        semantic.sort_values(["author_id", "unit_index"], kind="stable").reset_index(drop=True),
        geometry.sort_values(["user_id", "split"], kind="stable").reset_index(drop=True),
    )


def load_meps_panel(
    root: str | Path,
    *,
    max_authors: int,
    segments_per_author: int,
    seed: int,
) -> pd.DataFrame:
    """Load participant utterances only from the MEPS free-chat files."""
    candidates: dict[str, pd.DataFrame] = {}
    for path in Path(root).rglob("*_free_chat.csv"):
        if path.name.startswith("._"):
            continue
        participant = path.parent.name
        try:
            frame = pd.read_csv(path, usecols=["ts_iso", "role", "content"])
        except (OSError, ValueError, pd.errors.ParserError):
            continue
        frame = frame.loc[
            frame["role"].astype(str).str.lower().eq("user")
            & frame["content"].fillna("").astype(str).str.strip().ne("")
        ].copy()
        if len(frame) >= segments_per_author:
            candidates[participant] = frame
    selected = _sample_authors(
        candidates,
        max_authors=max_authors,
        salt=f"meps-{seed}",
    )
    rows: list[dict[str, Any]] = []
    for participant in selected:
        frame = candidates[participant].sort_values("ts_iso", kind="stable")
        indices = np.unique(np.linspace(0, len(frame) - 1, num=segments_per_author, dtype=int))
        for index, value in enumerate(frame.iloc[indices].itertuples(index=False)):
            rows.append({
                "corpus": "meps",
                "author_internal": participant,
                "author_id": stable_digest(participant, salt="meps-author"),
                "split": v8_author_split(participant, seed=seed),
                "segment_id": f"meps-{stable_digest(participant, salt='segment-author')}-{index:02d}",
                "span_id": f"meps-span-{stable_digest(participant, salt='span-author')}-{index:02d}",
                "unit_index": index,
                "text": str(value.content)[:1200],
                "condition": "free_chat",
            })
    return pd.DataFrame(rows)


def load_x_panel(
    root: str | Path,
    *,
    max_authors: int,
    segments_per_author: int,
    seed: int,
) -> pd.DataFrame:
    """Load a deterministic multilingual X author panel from daily files."""
    pieces: list[pd.DataFrame] = []
    for path in sorted(Path(root).rglob("x_posts.csv")):
        try:
            frame = pd.read_csv(
                path,
                usecols=["account_id", "timestamp", "text", "symbol", "lang"],
                dtype={"account_id": str},
            )
        except (OSError, ValueError, pd.errors.ParserError):
            continue
        pieces.append(frame)
    if not pieces:
        return pd.DataFrame()
    raw = pd.concat(pieces, ignore_index=True)
    raw["text"] = raw["text"].fillna("").astype(str)
    raw = raw.loc[raw["account_id"].notna() & raw["text"].str.strip().ne("")].copy()
    counts = raw.groupby("account_id", observed=True).size()
    eligible = counts.loc[counts >= segments_per_author].index.astype(str)
    selected = set(_sample_authors(
        eligible,
        max_authors=max_authors,
        salt=f"x-{seed}",
    ))
    rows: list[dict[str, Any]] = []
    for user, group in raw.loc[raw["account_id"].isin(selected)].sort_values(
        ["account_id", "timestamp"], kind="stable"
    ).groupby("account_id", observed=True, sort=False):
        indices = np.unique(np.linspace(0, len(group) - 1, num=segments_per_author, dtype=int))
        for index, value in enumerate(group.iloc[indices].itertuples(index=False)):
            rows.append({
                "corpus": "x_market",
                "author_internal": str(user),
                "author_id": stable_digest(str(user), salt="x-author"),
                "split": v8_author_split(str(user), seed=seed),
                "segment_id": f"x-{stable_digest(str(user), salt='segment-author')}-{index:02d}",
                "span_id": f"x-span-{stable_digest(str(user), salt='span-author')}-{index:02d}",
                "unit_index": index,
                "text": str(value.text)[:1200],
                "condition": f"{value.symbol}|{value.lang}",
            })
    return pd.DataFrame(rows)


def deterministic_text_features(text: str, *, hash_dimensions: int = 64) -> np.ndarray:
    """Extract a fixed, language-tolerant technical feature vector."""
    value = str(text or "")
    tokens = tokenize(value)
    lowered = [token.lower() for token in tokens]
    characters = max(1, len(value))
    token_count = max(1, len(tokens))
    lexical = [
        np.log1p(len(tokens)),
        np.log1p(len(value)),
        float(len(set(lowered)) / token_count),
        float(np.mean([len(token) for token in tokens])) if tokens else 0.0,
        value.count("?") / characters,
        value.count("!") / characters,
        value.count(",") / characters,
        value.count(".") / characters,
        value.count("\n") / characters,
        sum(char.isdigit() for char in value) / characters,
        sum(char.isupper() for char in value) / characters,
        float(bool(URL_RE.search(value))),
        len(FIRST_PERSON_RE.findall(value)) / token_count,
        len(DIRECTIVE_RE.findall(value)) / token_count,
    ]
    hashed = np.zeros(int(hash_dimensions), dtype=float)
    normalized = " ".join(lowered)
    for size in (3, 4, 5):
        for index in range(max(0, len(normalized) - size + 1)):
            gram = normalized[index:index + size]
            digest = hashlib.blake2b(gram.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest, "big") % int(hash_dimensions)
            sign = 1.0 if digest[0] & 1 else -1.0
            hashed[bucket] += sign
    norm = np.linalg.norm(hashed)
    if norm > 1e-12:
        hashed /= norm
    return np.r_[np.asarray(lexical, dtype=float), hashed]


def aggregate_half_features(
    panel: pd.DataFrame,
    segment_vectors: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Aggregate even/odd source-disjoint segment vectors per author."""
    rows: list[dict[str, str]] = []
    left: list[np.ndarray] = []
    right: list[np.ndarray] = []
    for author, group in panel.sort_values(["author_id", "unit_index"], kind="stable").groupby(
        "author_id", observed=True, sort=False
    ):
        first = [
            segment_vectors[str(row.segment_id)]
            for row in group.itertuples(index=False)
            if int(row.unit_index) % 2 == 0 and str(row.segment_id) in segment_vectors
        ]
        second = [
            segment_vectors[str(row.segment_id)]
            for row in group.itertuples(index=False)
            if int(row.unit_index) % 2 == 1 and str(row.segment_id) in segment_vectors
        ]
        if not first or not second:
            continue
        rows.append({
            "author_id": str(author),
            "split": str(group["split"].iloc[0]),
            "corpus": str(group["corpus"].iloc[0]),
        })
        left.append(np.mean(np.vstack(first), axis=0))
        right.append(np.mean(np.vstack(second), axis=0))
    return pd.DataFrame(rows), np.vstack(left), np.vstack(right)


def fit_standardizer(
    left: np.ndarray,
    right: np.ndarray,
    mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit one discovery-only pooled standardizer."""
    values = np.vstack([left[mask], right[mask]])
    center = values.mean(axis=0)
    scale = values.std(axis=0)
    scale[scale < 1e-8] = 1.0
    return center, scale


def auc_contributions(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return each author's own-vs-stranger rank contribution."""
    a = left / np.maximum(np.linalg.norm(left, axis=1, keepdims=True), 1e-12)
    b = right / np.maximum(np.linalg.norm(right, axis=1, keepdims=True), 1e-12)
    similarity = a @ b.T
    rows: list[float] = []
    for index in range(len(similarity)):
        negatives = np.delete(similarity[index], index)
        positive = similarity[index, index]
        rows.append(float(np.mean(positive > negatives) + 0.5 * np.mean(positive == negatives)))
    return np.asarray(rows)


def cross_fitted_semantic_increment(
    metadata: pd.DataFrame,
    baseline_left: np.ndarray,
    baseline_right: np.ndarray,
    semantic_left: np.ndarray,
    semantic_right: np.ndarray,
    *,
    weights: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0, 2.0),
    bootstrap_draws: int = 2000,
    seed: int = 20260724,
) -> dict[str, Any]:
    """Tune semantic weight on calibration and report only confirmation delta."""
    splits = metadata["split"].astype(str).to_numpy()
    discovery = splits == "discovery"
    calibration = splits == "calibration"
    confirmation = splits == "confirmation"
    if min(discovery.sum(), calibration.sum(), confirmation.sum()) < 4:
        return {
            "status": "REFUSE_INSUFFICIENT_SPLIT_SUPPORT",
            "n_discovery": int(discovery.sum()),
            "n_calibration": int(calibration.sum()),
            "n_confirmation": int(confirmation.sum()),
        }
    base_center, base_scale = fit_standardizer(baseline_left, baseline_right, discovery)
    sem_center, sem_scale = fit_standardizer(semantic_left, semantic_right, discovery)
    bl = (baseline_left - base_center) / base_scale
    br = (baseline_right - base_center) / base_scale
    sl = (semantic_left - sem_center) / sem_scale
    sr = (semantic_right - sem_center) / sem_scale
    candidates: list[dict[str, float]] = []
    for weight in weights:
        left = np.hstack([bl, float(weight) * sl])
        right = np.hstack([br, float(weight) * sr])
        candidates.append({
            "weight": float(weight),
            "calibration_auc": float(same_author_auc(left[calibration], right[calibration])),
        })
    winner = sorted(candidates, key=lambda row: (-row["calibration_auc"], row["weight"]))[0]
    weight = float(winner["weight"])
    augmented_left = np.hstack([bl, weight * sl])
    augmented_right = np.hstack([br, weight * sr])
    base_contrib = auc_contributions(bl[confirmation], br[confirmation])
    augmented_contrib = auc_contributions(
        augmented_left[confirmation], augmented_right[confirmation]
    )
    delta = augmented_contrib - base_contrib
    rng = np.random.default_rng(seed)
    draws = delta[rng.integers(0, len(delta), size=(int(bootstrap_draws), len(delta)))].mean(axis=1)
    return {
        "status": "TECHNICAL_INCREMENT_EVALUATED",
        "selected_semantic_weight": weight,
        "calibration_candidates": candidates,
        "n_discovery": int(discovery.sum()),
        "n_calibration": int(calibration.sum()),
        "n_confirmation": int(confirmation.sum()),
        "baseline_confirmation_auc": float(base_contrib.mean()),
        "augmented_confirmation_auc": float(augmented_contrib.mean()),
        "delta_auc": float(delta.mean()),
        "delta_auc_ci_lower": float(np.quantile(draws, 0.025)),
        "delta_auc_ci_upper": float(np.quantile(draws, 0.975)),
    }
