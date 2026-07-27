"""Protocol checks for the corrected H4D-R2E.1 runner."""
from __future__ import annotations

from pathlib import Path

from scripts.run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e import (
    _geometry_plan,
)
from scripts.run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e1 import (
    _read,
    r2e,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT
    / "configs"
    / "v8_conditional_heterogeneity_injection_v37h4d_r2e1.json"
)


def test_corrected_protocol_uses_fresh_seed_and_same_13_geometries() -> None:
    corrected = _read(CONFIG)
    original = _read(
        ROOT
        / "configs"
        / "v8_conditional_heterogeneity_injection_v37h4d_r2e.json"
    )
    assert corrected["seed"] != original["seed"]
    assert corrected["smoke_seed"] != original["smoke_seed"]
    assert _geometry_plan(corrected) == _geometry_plan(original)


def test_corrected_source_lock_includes_both_runners() -> None:
    config = _read(CONFIG)
    assert r2e._source_lock(config)["pass"]
    assert (
        "scripts/"
        "run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e.py"
        in config["frozen_source_sha256"]
    )
    assert (
        "scripts/"
        "run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e1.py"
        in config["frozen_source_sha256"]
    )
