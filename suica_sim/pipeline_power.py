"""Repeated-alternative power assay for the V6 falsification pipeline."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .pipeline import _statistic, wilson
from .pipeline_worlds import generate_pipeline_world


SPECS = (
    ("SIM-P0", "P0_alt"), ("SIM-P1", "P0_alt"),
    ("SIM-P2", "P2_artifact"), ("SIM-P3", "P3_lowrank"),
    ("SIM-P4", "P4_person"), ("SIM-P5", "P5_alt"),
    ("SIM-P6", "P6_person"),
)


def run_power_assay(config: dict[str, Any], config_hash: str,
                    reference: dict[str, Any]) -> dict[str, Any]:
    """Estimate per-scenario power against a preregistered max-T threshold."""
    threshold = float(np.quantile(reference["max_t_null"], .95))
    rows = []
    for idx, (label, alt_world) in enumerate(SPECS):
        hits, statistics = 0, []
        for draw in range(config["alternative_draws"]):
            seed = int(np.random.SeedSequence([config["seed"], idx, draw]).generate_state(1)[0])
            data = generate_pipeline_world(
                seed, alt_world, persons=config["persons"], occasions=config["occasions"],
                windows=config["windows"], constructs=config["constructs"],
                jitter=config.get("segmentation_jitter", .8),
            )
            statistic = float(_statistic(data, config, seed + 1)["statistic"])
            statistics.append(statistic); hits += statistic > threshold
        power = hits / config["alternative_draws"]
        rows.append({"world": label, "scenario": alt_world, "hits": hits,
                     "draws": config["alternative_draws"], "power": power,
                     "power_wilson_ci": wilson(hits, config["alternative_draws"]),
                     "mean_statistic": float(np.mean(statistics)),
                     "max_t_q95": threshold})
    source_hash = hashlib.sha256(json.dumps(reference, sort_keys=True).encode()).hexdigest()
    return {
        "schema_version": 1, "profile": config["profile"], "seed": config["seed"],
        "config_hash": config_hash, "reference_artifact_hash": source_hash,
        "alternative_draws": config["alternative_draws"], "rows": rows,
        "gates": {"power": None if config["profile"] == "quick" else
                  all(row["power_wilson_ci"][0] >= .80 for row in rows)},
    }


def write_power_report(result: dict[str, Any], output_dir: str | Path) -> Path:
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    path = out / f"v6_pipeline_power_{result['profile']}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return path
