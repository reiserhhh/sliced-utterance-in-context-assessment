"""Directory and reference registry for the private MEPS + AI experiment.

This module separates three things that must never be conflated:

1. ``decrypted_output/``: authoritative user-text exports for SUICA's
   fixed-condition protocol pilot;
2. ``research2_anal/``: the same-session questionnaire and analytic pipeline;
3. ``research1_anal/``: a different, larger study with only partial overlap.

The registry is intentionally *reference only*.  It reads participant-code
columns to verify a linkage, but it never loads scale values into the SUICA
pipeline.  This implements the project decision that MEPS is not a training
source and is not an external-validity evaluation in the present phase.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


EXPECTED_EXPORT_SUFFIX = "questions"


@dataclass(frozen=True)
class ReferenceSpec:
    """A known adjacent source and its strict access policy."""

    key: str
    relative_path: str
    id_column: str | None
    source_class: str
    policy: str
    description: str


REFERENCE_SPECS: tuple[ReferenceSpec, ...] = (
    ReferenceSpec(
        "r2_pre_questionnaire_scored",
        "research2_anal/processed/pre_questionnaire_scored.csv",
        "participant_id",
        "same_session_pre_measure",
        "WITHHELD_NOT_FOR_TRAINING_OR_VALIDATION",
        "Pre-session AI mind-attribution, attachment, trust, and usage measures.",
    ),
    ReferenceSpec(
        "r2_post_questionnaire_scored",
        "research2_anal/processed/post_questionnaire_scored.csv",
        "participant_id",
        "same_session_post_measure",
        "WITHHELD_NOT_FOR_TRAINING_OR_VALIDATION",
        "Post-session perceived empathy, session evaluation, mind attribution, attachment, and disclosure measures.",
    ),
    ReferenceSpec(
        "r2_participant_protocol",
        "research2_anal/processed/participants.csv",
        "participant_id",
        "same_session_protocol_metadata",
        "STRUCTURAL_CONTEXT_ONLY",
        "Experiment timing, condition exposure, and AI-use opportunity metadata.",
    ),
    ReferenceSpec(
        "r2_analysis_master",
        "research2_anal/processed/analysis_master.csv",
        "participant_id",
        "derived_joined_analysis",
        "DO_NOT_LOAD_BY_DEFAULT",
        "Convenience join containing many downstream fields; not an authoritative SUICA input.",
    ),
    ReferenceSpec(
        "r2_raw_qualtrics",
        "research2_anal/survey_rawdata",
        None,
        "raw_questionnaire_export",
        "EXCLUDE_PII_AND_DO_NOT_READ",
        "Raw survey exports may contain direct identifiers and must remain outside SUICA.",
    ),
    ReferenceSpec(
        "r2_content_coding",
        "research2_anal/coding",
        None,
        "duplicate_human_text_and_codes",
        "EXCLUDE_DUPLICATE_TEXT_BY_DEFAULT",
        "Coding files duplicate free-chat content and must not become a second text source.",
    ),
    ReferenceSpec(
        "r1_prior_study_panel",
        "research1_anal/data_cleaned.csv",
        "anon7",
        "different_study_partial_overlap",
        "NEVER_AUTO_MERGE",
        "Larger Study 1 panel; any overlap requires a separately declared longitudinal analysis.",
    ),
)


DIRECTORY_ROLES: tuple[tuple[str, str, str], ...] = (
    ("decrypted_output", "authoritative_private_text_export", "READ_FOR_FIXED_CONDITION_PILOT"),
    ("research2_anal/processed", "same_session_deidentified_analysis", "REFERENCE_ONLY"),
    ("research2_anal/questionnaire", "same_session_questionnaire_import", "REFERENCE_ONLY"),
    ("research2_anal/survey_rawdata", "raw_questionnaire_export", "EXCLUDE_PII_AND_DO_NOT_READ"),
    ("research2_anal/coding", "duplicate_free_chat_content_coding", "EXCLUDE_DUPLICATE_TEXT_BY_DEFAULT"),
    ("research1_anal", "different_study_analysis", "NEVER_AUTO_MERGE"),
    ("research_docs", "protocol_and_scale_provenance", "READ_FOR_DOCUMENTATION_ONLY"),
    ("output_formal_encrypted", "encrypted_archive", "DO_NOT_USE_WHEN_DECRYPTED_EXPORT_EXISTS"),
    ("keys", "cryptographic_material", "EXCLUDE_SECRET"),
    ("dist", "experiment_application_bundle", "EXCLUDE_RUNTIME_ARTIFACT"),
)


@dataclass(frozen=True)
class MEPSExperimentLayout:
    """Resolved private bundle layout without exposing its absolute path publicly."""

    experiment_root: Path
    text_export_root: Path
    resolution_mode: str

    def public_manifest(self) -> dict[str, Any]:
        """Return paths relative to the supplied experiment bundle only."""
        try:
            text_relative = str(self.text_export_root.relative_to(self.experiment_root))
        except ValueError:
            text_relative = "."
        return {
            "resolution_mode": self.resolution_mode,
            "text_export_relative_path": text_relative,
            "directory_roles": [
                {"relative_path": path, "role": role, "policy": policy}
                for path, role, policy in DIRECTORY_ROLES
            ],
        }


def normalize_participant_code(value: object) -> str:
    """Normalize full-width/numeric participant codes without emitting them."""
    if value is None or pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKC", str(value)).strip()
    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    return text.zfill(7) if text.isdigit() and len(text) <= 7 else text


def _looks_like_text_export_root(root: Path) -> bool:
    if not root.is_dir():
        return False
    for folder in root.iterdir():
        if not folder.is_dir() or folder.name.startswith((".", "._")):
            continue
        if (folder / f"{folder.name}_{EXPECTED_EXPORT_SUFFIX}.csv").is_file():
            return True
    return False


def resolve_meps_experiment_layout(input_root: Path) -> MEPSExperimentLayout:
    """Resolve either the complete experiment bundle or direct text-export root.

    New imports pass the complete ``MEPS+AI_conv_experiment`` directory and
    resolve its ``decrypted_output`` child.  The direct export path remains
    supported for reproducibility and synthetic tests.
    """
    root = Path(input_root).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"MEPS input root does not exist: {root}")
    decrypted = root / "decrypted_output"
    if _looks_like_text_export_root(decrypted):
        return MEPSExperimentLayout(root, decrypted, "bundle_decrypted_output")
    if _looks_like_text_export_root(root):
        experiment_root = root.parent if root.name == "decrypted_output" else root
        return MEPSExperimentLayout(experiment_root, root, "direct_text_export_root")
    raise ValueError(
        "could not locate participant exports: expected <input>/decrypted_output/"
        "<participant>/<participant>_questions.csv or a direct export root"
    )


def _text_export_codes(text_export_root: Path) -> set[str]:
    return {
        normalize_participant_code(folder.name)
        for folder in text_export_root.iterdir()
        if folder.is_dir() and not folder.name.startswith((".", "._"))
    }


def reference_registry(layout: MEPSExperimentLayout) -> pd.DataFrame:
    """Verify reference linkage using only ID columns, never scale values."""
    text_codes = _text_export_codes(layout.text_export_root)
    rows: list[dict[str, Any]] = []
    for spec in REFERENCE_SPECS:
        path = layout.experiment_root / spec.relative_path
        row: dict[str, Any] = {
            "key": spec.key,
            "relative_path": spec.relative_path,
            "source_class": spec.source_class,
            "policy": spec.policy,
            "description": spec.description,
            "present": path.exists(),
            "id_column": spec.id_column or "",
            "reference_unique_codes": pd.NA,
            "matched_text_export_codes": pd.NA,
            "text_export_coverage": pd.NA,
            "note": "not_read",
        }
        if path.is_file() and spec.id_column:
            try:
                header = pd.read_csv(path, encoding="utf-8-sig", nrows=0)
                if spec.id_column not in header.columns:
                    row["note"] = "declared_id_column_missing"
                else:
                    codes = pd.read_csv(
                        path,
                        encoding="utf-8-sig",
                        usecols=[spec.id_column],
                        dtype={spec.id_column: str},
                    )[spec.id_column].map(normalize_participant_code)
                    reference_codes = {code for code in codes if code}
                    overlap = len(reference_codes & text_codes)
                    row.update({
                        "reference_unique_codes": len(reference_codes),
                        "matched_text_export_codes": overlap,
                        "text_export_coverage": overlap / len(text_codes) if text_codes else pd.NA,
                        "note": "id_column_only",
                    })
            except (OSError, UnicodeError, pd.errors.ParserError, ValueError) as error:
                row["note"] = f"id_audit_error:{type(error).__name__}"
        rows.append(row)
    return pd.DataFrame(rows)


def directory_registry(layout: MEPSExperimentLayout) -> pd.DataFrame:
    """Return the curated root-level map without recursively cataloguing binaries."""
    rows = []
    for relative_path, role, policy in DIRECTORY_ROLES:
        rows.append({
            "relative_path": relative_path,
            "role": role,
            "policy": policy,
            "present": (layout.experiment_root / relative_path).exists(),
        })
    return pd.DataFrame(rows)
