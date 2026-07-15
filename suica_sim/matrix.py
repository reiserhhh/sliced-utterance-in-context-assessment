"""Configuration, execution, and reporting for the W0-W8 matrix."""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

from .worlds import run_world


def load_config(path: str | Path) -> tuple[dict[str, Any], str]:
    raw = Path(path).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def run_matrix(config: dict[str, Any], config_hash: str) -> dict[str, Any]:
    seed = int(config["seed"])
    children = np.random.SeedSequence(seed).spawn(9)
    rows = []
    for i in range(9):
        rows.extend(run_world(i, np.random.default_rng(children[i]), config))
    root = Path(__file__).resolve().parents[1]
    # Hash only this runner's transitive source set. Unrelated future modules
    # must not invalidate an already archived simulation artifact.
    code_files = [root / "suica_sim/__init__.py", root / "suica_sim/algebra.py",
                  root / "suica_sim/worlds.py", root / "suica_sim/matrix.py",
                  root / "scripts/run_v6_simulation_matrix.py"]
    code_hash = hashlib.sha256(b"".join(p.read_bytes() for p in code_files)).hexdigest()
    try:
        git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                  capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_head = None
    return {"schema_version": 2, "config_hash": config_hash, "code_hash": code_hash,
            "git_head": git_head, "python_version": platform.python_version(),
            "numpy_version": np.__version__, "seed": seed, "profile": config["profile"],
            "mc": config["mc"], "rows": rows}


def write_reports(result: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"v6_simulation_matrix_{result['profile']}"
    json_path, csv_path, md_path = out / f"{stem}.json", out / f"{stem}.csv", out / f"{stem}.md"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    fields = sorted({k for row in result["rows"] for k in row})
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(result["rows"])
    lines = [f"# V6 simulation matrix ({result['profile']})", "",
             f"- config hash: `{result['config_hash']}`", f"- code hash: `{result['code_hash']}`",
             f"- git head: `{result['git_head']}`", f"- Python / NumPy: `{result['python_version']} / {result['numpy_version']}`",
             f"- seed: `{result['seed']}`",
             f"- Monte Carlo replicates: `{result['mc']}`", "",
             "| world | theory targets | scenario | metric type | estimate | truth | bias | MC CI | CI coverage | FPR | power | guard rate | criterion | verdict |",
             "|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---|---|"]
    for r in result["rows"]:
        lines.append("| " + " | ".join(str(r.get(k, "")) for k in
            ("world", "theory_targets", "scenario", "metric_type", "estimate", "truth", "bias")) +
            f" | [{r['mc_ci_low']}, {r['mc_ci_high']}] | " + " | ".join(str(r.get(k, "")) for k in
            ("ci_coverage", "fpr", "power", "guard_rate", "criterion_id", "verdict")) + " |")
    md_path.write_text("\n".join(lines) + "\n")
    return {"json": str(json_path), "csv": str(csv_path), "markdown": str(md_path)}
