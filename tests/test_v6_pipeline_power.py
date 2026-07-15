from __future__ import annotations

import json
from pathlib import Path

from suica_sim.pipeline_power import run_power_assay


ROOT = Path(__file__).resolve().parents[1]


def test_quick_power_assay_is_diagnostic_and_scenario_specific():
    config = json.loads((ROOT / "configs/sim_v6/power_quick.json").read_text())
    # Keep the unit test independent of ignored local experiment outputs.
    reference = {"max_t_null": [0.1, 0.2, 0.3, 0.4, 0.5]}
    result = run_power_assay(config, "test", reference)
    assert len(result["rows"]) == 7
    assert result["gates"]["power"] is None
    assert all(row["draws"] == 3 for row in result["rows"])
    assert len({row["scenario"] for row in result["rows"]}) > 1
