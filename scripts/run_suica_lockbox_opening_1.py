#!/usr/bin/env python
"""SUICA Lockbox Opening #1 — the preregistered P5 confirmatory analysis.

Governing document: docs/PREREGISTRATION.md in the sealed release repository
(tag v0.1.0-prereg-sealed, seal commit dd5c7805689acd6d5351f7a22864b3ff45eb1d7d).
This script implements that document EXACTLY; where the prereg leaves an
operationalization open, the choice is fixed HERE, before any label is read,
and flagged [FIXED-HERE] for the pre-opening audit.

Stages (run in order; labels are read ONLY in stage `open`):
  dryrun   Full plumbing rehearsal on 1,412 Tier-U users (stable-hash order)
           with SYNTHETIC labels drawn from rng(7). No lockbox contact.
  extract  Pull Tier-L users' comments from the official dump (text only;
           membership from tier CSVs; label files never loaded). Mirrors the
           frozen Tier-U extractor: lang==en, non-empty, no [deleted]/
           [removed], body[:1500], cap 400/user via seeded thinning, seed 42.
  score    Slice+score via the FROZEN prep script (subprocess, out-tag
           lockbox1 -> identical code path: 128-token slices, min 24, max 10
           per cell, >=4 comments/condition, <=8 conditions/user, leak-mask,
           score_slices_v2). Then choice shares over the transported
           condition->class map (EPS=1e-4 log-ratio) and choice entropy.
           Writes predictors.parquet — still label-free.
  open     ONE-SHOT. Hard-fails if the opening sentinel exists. Verifies
           gates, writes the sentinel, reads labels, computes H1-H4+H6-H8
           (confirmatory, BH-FDR within the 7-set) + H5 (secondary) +
           the non-confirmatory Empath-194 delta-R^2, writes the report.

Frozen analysis rules (from the prereg):
  - Eligibility: >= 4 conditions AND >= 12 slices (pass-B, post leak-mask).
  - Pearson r per hypothesis; BH-FDR within the 7 confirmatory hypotheses.
  - SUCCESS = >= 4 of 7 at q < 0.05 AND every significant effect in the
    preregistered direction. Anything else = P5 fail. No re-analysis.
  - H5 (directive -> bridge TF, thinking direction) secondary: CI + direction
    only, excluded from the denominator.
  - Battery: style base raw means (tension_core_v2, directive_action_v2,
    first_person_usage_v2, novelty_play_v2); choice log-ratio axes over the
    12 frozen classes; choice entropy. EXCLUDED: choice_ax_11 (MBTI-community
    leakage), adversity_recovery_v2 (dead construct).

[FIXED-HERE] operationalizations (declared before any label read):
  F1 choice_entropy PRIMARY = unnormalized Shannon entropy (nats) of the
     user's extracted-comment distribution across subreddits (venue breadth,
     literal reading). Declared robustness variants computed in the SAME
     single run, reported non-confirmatorily, never entering the verdict:
     (a) normalized H/log(K) [v1 precedent], (b) H over 12-class shares.
  F2 Choice shares = the user's mapped-comment distribution over the 12
     classes (compositional, class 11 kept in the denominator; axis 11 never
     used as a predictor). Comments in subreddits absent from the frozen map
     are excluded from shares; coverage reported.
  F3 "Conditions" for eligibility = subreddits that produced pass-B cells
     under the frozen prep rules (>=4 comments, top-8 cap); "slices" =
     pass-B slices after leak-mask. Gate: >= 4 conditions AND >= 12 slices.
  F4 Log-ratio population reference = eligible-cohort mean share vector.
     (Pearson r is invariant to this per-class constant; recorded for
     reproducibility only.)
  F5 H5 positive pole verified at runtime from mbti_type_resolved (T=1
     expected); if TF_cont correlates NEGATIVELY with is_T the sign is
     flipped BEFORE reading any correlation with predictors, and the flip is
     recorded. "Thinking direction" for directive = positive r with is_T.
  F6 Abort gates (checked BEFORE the sentinel/label read): realized eligible
     n within +/-15% of the prereg estimates (Big5 1,108, bridge 326);
     extraction users subset of tier_l_users.csv; zero Tier-U overlap.
  F7 Crash rule: the sentinel is written immediately before the label read.
     If the run dies after the sentinel but before OPENING_REPORT.json, a
     rerun with --resume-crashed is permitted ONCE (deterministic pipeline,
     same inputs -> same numbers; this is completion, not a second look).
  F8 delta-R^2 add-on follows P3 conventions exactly: Empath-194
     normalize=True on user text capped at 24,000 chars, Ridge alpha=10,
     KFold(5, shuffle, seed 42); battery = 4 style + 11 axes + entropy = 16.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
DUMP = ROOT / "data_sets" / "PANDORA_official" / "all_comments_since_2015.csv"
CLASS_MAP = ROOT / "results" / "suica_e3_e4_choice_class_v2_s128" / "condition_class_map.csv"
BIG5_LABELS = ROOT / "data_sets" / "prepared" / "pandora_official" / "pandora_official_big5_prepared.csv"
BRIDGE_LABELS = ROOT / "data_sets" / "prepared" / "pandora_official" / "bridge" / "pandora_official_bridge_strict377.csv"
OUT_DIR = ROOT / "results" / "suica_lockbox_opening_1"
DRY_DIR = ROOT / "results" / "suica_lockbox_opening_1_dryrun"
REPORT_MD = ROOT / "reports" / "suica_lockbox_opening_1.md"
LOCKBOX_COMMENTS = TIER_DIR / "tier_l_comments.parquet"
SENTINEL = OUT_DIR / "OPENING_SENTINEL.json"
FINAL_JSON = OUT_DIR / "OPENING_REPORT.json"

USECOLS = ["author", "body", "created_utc", "subreddit", "lang"]
CHUNK = 400_000
CAP_PER_USER = 400
SEED = 42
EPS = 1e-4
STYLE = ["tension_core_v2", "directive_action_v2", "first_person_usage_v2", "novelty_play_v2"]
N_CLASSES = 12
EXCLUDED_AXIS = 11
GAMING_AXIS, POLITICS_AXIS = 5, 6
ESTIMATED_ELIGIBLE = {"big5": 1108, "bridge": 326}
GATE_TOLERANCE = 0.15

# (id, predictor column, target column, cohort, predicted sign, confirmatory)
HYPOTHESES = [
    ("H1", "tension_core_v2", "Neuroticism", "big5", +1, True),
    ("H2", "first_person_usage_v2", "Neuroticism", "big5", +1, True),
    ("H3", "novelty_play_v2", "Openness", "big5", +1, True),
    ("H4", "directive_action_v2", "Agreeableness", "big5", -1, True),
    ("H5", "directive_action_v2", "is_T", "bridge", +1, False),
    ("H6", f"choice_ax_{POLITICS_AXIS:02d}", "Openness", "big5", +1, True),
    ("H7", "choice_entropy", "Openness", "big5", +1, True),
    ("H8", f"choice_ax_{GAMING_AXIS:02d}", "Extraversion", "big5", -1, True),
]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def stable_fraction(value: str) -> float:
    digest = hashlib.sha1(str(value).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16**12 - 1)


def git_head() -> str:
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def extract_lockbox() -> None:
    tier_l = set(pd.read_csv(TIER_DIR / "tier_l_users.csv")["user_id"].astype(str))
    tier_u = set(pd.read_csv(TIER_DIR / "tier_u_users.csv")["user_id"].astype(str))
    assert not (tier_l & tier_u), "tier overlap — tiers corrupted"
    counts: dict[str, int] = {}
    for chunk in pd.read_csv(DUMP, usecols=["author"], chunksize=CHUNK):
        vc = chunk.loc[chunk["author"].astype(str).isin(tier_l), "author"].astype(str).value_counts()
        for user, n in vc.items():
            counts[user] = counts.get(user, 0) + int(n)
    print(f"pass1: {len(counts)} lockbox users seen, {sum(counts.values())} comments")
    keep_p = {u: min(1.0, CAP_PER_USER / max(1, n)) for u, n in counts.items()}
    rng = np.random.default_rng(SEED)
    parts = []
    for chunk in pd.read_csv(DUMP, usecols=USECOLS, chunksize=CHUNK):
        chunk["author"] = chunk["author"].astype(str)
        sub = chunk.loc[chunk["author"].isin(tier_l)].copy()
        if sub.empty:
            continue
        sub = sub.loc[sub["lang"].fillna("en").astype(str).eq("en")]
        body = sub["body"].fillna("").astype(str)
        sub = sub.loc[body.str.len().gt(0) & ~body.isin(["[deleted]", "[removed]"])]
        if sub.empty:
            continue
        p = sub["author"].map(keep_p).fillna(0.0).to_numpy(float)
        sub = sub.loc[rng.random(len(sub)) < p]
        if sub.empty:
            continue
        sub["body"] = sub["body"].astype(str).str.slice(0, 1500)
        parts.append(sub.drop(columns=["lang"]))
    out = pd.concat(parts, ignore_index=True)
    out["created_utc"] = pd.to_numeric(out["created_utc"], errors="coerce")
    out = out.dropna(subset=["created_utc"]).sort_values(["author", "created_utc"]).reset_index(drop=True)
    assert set(out["author"]) <= tier_l
    out.to_parquet(LOCKBOX_COMMENTS, index=False)
    manifest = {"users_in_tier_l": len(tier_l), "users_with_rows": int(out["author"].nunique()),
                "rows": int(len(out)), "cap_per_user": CAP_PER_USER, "seed": SEED,
                "labels_read": False}
    (TIER_DIR / "tier_l_comments_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


def run_frozen_prep(input_parquet: Path, tag: str) -> pd.DataFrame:
    scored_path = TIER_DIR / f"phase2_passB_scored_{tag}.parquet"
    if not scored_path.exists():
        subprocess.run([sys.executable, str(ROOT / "scripts" / "prepare_suica_v2_phase2_slices.py"),
                        "--input-parquet", str(input_parquet), "--out-tag", tag], check=True)
    return pd.read_parquet(scored_path)


def build_predictors(comments: pd.DataFrame, scored_b: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Label-free predictor table: style means, choice axes, entropy, gates."""
    cell = scored_b.groupby(["user_id", "condition"]).size().rename("n").reset_index()
    n_conds = cell.groupby("user_id").size().rename("n_conditions")
    n_slices = scored_b.groupby("user_id").size().rename("n_slices")
    style = scored_b.groupby("user_id")[STYLE].mean()

    cmap = pd.read_csv(CLASS_MAP)
    mapped = comments.merge(cmap, left_on="subreddit", right_on="condition", how="inner")
    total_c = comments.groupby("author").size()
    mapped_c = mapped.groupby("author").size()
    share = (mapped.groupby(["author", "class_id"]).size().unstack(fill_value=0)
             .reindex(columns=range(N_CLASSES), fill_value=0))
    share = share.div(share.sum(axis=1).replace(0, np.nan), axis=0)

    def shannon(p: np.ndarray) -> float:
        p = p[p > 0]
        return float(-(p * np.log(p)).sum()) if len(p) else np.nan

    venue = comments.groupby(["author", "subreddit"]).size()
    ent, ent_norm = {}, {}
    for u, g in venue.groupby(level=0):
        p = (g / g.sum()).to_numpy(float)
        ent[u] = shannon(p)
        ent_norm[u] = ent[u] / np.log(len(p)) if len(p) > 1 else 0.0
    ent_class = {u: shannon(share.loc[u].to_numpy(float)) for u in share.index}

    pred = style.join([n_conds, n_slices], how="left")
    pred["choice_entropy"] = pd.Series(ent)
    pred["choice_entropy_norm_v1"] = pd.Series(ent_norm)
    pred["choice_entropy_class"] = pd.Series(ent_class)
    pred = pred.join(share.add_prefix("share_"), how="left")
    pred["map_coverage"] = (mapped_c / total_c).reindex(pred.index)
    meta = {"n_users_scored": int(len(pred)),
            "median_map_coverage": float(pred["map_coverage"].median()),
            "class_map_sha256": sha256_of(CLASS_MAP)}
    return pred, meta


def finalize_axes(pred: pd.DataFrame, eligible_idx: pd.Index) -> pd.DataFrame:
    """Log-ratio axes with the eligible-cohort mean as reference (F4)."""
    shares = pred.loc[eligible_idx, [f"share_{k}" for k in range(N_CLASSES)]]
    pop = shares.mean(axis=0)
    for k in range(N_CLASSES):
        pred.loc[eligible_idx, f"choice_ax_{k:02d}"] = np.log(
            (shares[f"share_{k}"] + EPS) / (pop[f"share_{k}"] + EPS))
    return pred


def bh_fdr(pvals: list[float]) -> list[float]:
    n = len(pvals)
    order = np.argsort(pvals)
    q = np.empty(n)
    prev = 1.0
    for rank_pos in range(n - 1, -1, -1):
        i = order[rank_pos]
        val = min(prev, pvals[i] * n / (rank_pos + 1))
        q[i] = val
        prev = val
    return q.tolist()


def pearson_row(x: pd.Series, y: pd.Series) -> dict:
    j = pd.concat([x, y], axis=1).dropna()
    r, p = stats.pearsonr(j.iloc[:, 0], j.iloc[:, 1])
    n = len(j)
    zcrit = stats.norm.ppf(0.975)
    z = np.arctanh(r)
    lo, hi = np.tanh(z - zcrit / np.sqrt(n - 3)), np.tanh(z + zcrit / np.sqrt(n - 3))
    return {"n": n, "r": float(r), "p": float(p), "ci_lo": float(lo), "ci_hi": float(hi)}


def empath_delta_r2(comments: pd.DataFrame, pred: pd.DataFrame, labels: pd.DataFrame,
                    eligible: pd.Index, battery_cols: list[str]) -> dict:
    from empath import Empath
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import KFold
    from sklearn.preprocessing import StandardScaler

    text = comments.loc[comments["author"].isin(eligible)].groupby("author")["body"].apply(
        lambda s: " ".join(s)[:24000])
    lex = Empath()
    emp = pd.DataFrame({u: (lex.analyze(t, normalize=True) or {}) for u, t in text.items()}).T.fillna(0.0)

    def cv_r2(x: np.ndarray, y: np.ndarray) -> float:
        kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
        preds = np.empty_like(y)
        for tr, te in kf.split(x):
            sc = StandardScaler().fit(x[tr])
            m = Ridge(alpha=10.0).fit(sc.transform(x[tr]), y[tr])
            preds[te] = m.predict(sc.transform(x[te]))
        ss_res = float(((y - preds) ** 2).sum())
        ss_tot = float(((y - y.mean()) ** 2).sum())
        return 1.0 - ss_res / ss_tot

    out = {}
    for target in ["Neuroticism", "Openness"]:
        j = emp.join(labels[target], how="inner").join(pred[battery_cols], how="inner").dropna()
        y = j[target].to_numpy(float)
        base = cv_r2(j[emp.columns].to_numpy(float), y)
        aug = cv_r2(j[list(emp.columns) + battery_cols].to_numpy(float), y)
        out[target] = {"n": int(len(j)), "empath_r2": base, "empath_plus_battery_r2": aug,
                       "delta_r2": aug - base}
    return out


def analyze(pred: pd.DataFrame, big5: pd.DataFrame, bridge: pd.DataFrame,
            comments: pd.DataFrame, dry: bool) -> dict:
    gate = (pred["n_conditions"] >= 4) & (pred["n_slices"] >= 12)
    inter_b5 = pred.index.intersection(big5.index)
    inter_br = pred.index.intersection(bridge.index)
    big5_elig = inter_b5[gate.loc[inter_b5].fillna(False).to_numpy(bool)]
    bridge_elig = inter_br[gate.loc[inter_br].fillna(False).to_numpy(bool)]
    pred = finalize_axes(pred, big5_elig.union(bridge_elig))

    # F5 pole verification
    tf_flip = False
    if "TF_cont" in bridge.columns and "mbti_type_resolved" in bridge.columns:
        is_t = bridge["mbti_type_resolved"].astype(str).str.upper().str.contains("T").astype(float)
        if bridge["TF_cont"].corr(is_t) < 0:
            tf_flip = True
        bridge = bridge.assign(is_T=np.where(tf_flip, 1.0 - bridge["TF_cont"], bridge["TF_cont"]))
    else:
        bridge = bridge.assign(is_T=bridge["TF_cont"] if "TF_cont" in bridge.columns else np.nan)

    rows = []
    for hid, predictor, target, cohort, sign, confirmatory in HYPOTHESES:
        idx = big5_elig if cohort == "big5" else bridge_elig
        lab = big5 if cohort == "big5" else bridge
        res = pearson_row(pred.loc[idx, predictor], lab.loc[idx, target])
        res.update({"id": hid, "predictor": predictor, "target": target, "cohort": cohort,
                    "predicted_sign": sign, "confirmatory": confirmatory,
                    "direction_match": bool(np.sign(res["r"]) == sign)})
        rows.append(res)
    conf = [r for r in rows if r["confirmatory"]]
    qvals = bh_fdr([r["p"] for r in conf])
    for r, q in zip(conf, qvals):
        r["q_bh"] = q
        r["significant"] = bool(q < 0.05)
    n_pass = sum(1 for r in conf if r["significant"] and r["direction_match"])
    wrong_dir_sig = [r["id"] for r in conf if r["significant"] and not r["direction_match"]]
    success = bool(n_pass >= 4 and not wrong_dir_sig)

    battery_cols = STYLE + [f"choice_ax_{k:02d}" for k in range(N_CLASSES) if k != EXCLUDED_AXIS] + ["choice_entropy"]
    delta = empath_delta_r2(comments, pred, big5, big5_elig, battery_cols)

    robustness = {}
    for variant in ["choice_entropy_norm_v1", "choice_entropy_class"]:
        res = pearson_row(pred.loc[big5_elig, variant], big5.loc[big5_elig, "Openness"])
        robustness[f"H7_variant_{variant}"] = res

    return {
        "dry_run": dry, "git_head": git_head(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "eligible": {"big5": int(len(big5_elig)), "bridge": int(len(bridge_elig))},
        "prereg_estimates": ESTIMATED_ELIGIBLE, "tf_flip_applied": tf_flip,
        "hypotheses": rows,
        "confirmatory_pass_count": n_pass,
        "significant_wrong_direction": wrong_dir_sig,
        "SUCCESS_RULE_MET": success,
        "delta_r2_nonconfirmatory": delta,
        "H7_declared_robustness_nonconfirmatory": robustness,
    }


def load_membership(path: Path) -> pd.Index:
    return pd.Index(pd.read_csv(path, usecols=["user_id"])["user_id"].astype(str).unique())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["dryrun", "extract", "score", "open"])
    ap.add_argument("--resume-crashed", action="store_true")
    args = ap.parse_args()

    if args.stage == "dryrun":
        DRY_DIR.mkdir(parents=True, exist_ok=True)
        tier_u = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet")
        users = sorted(tier_u["author"].astype(str).unique(), key=stable_fraction)[:1412]
        comments = tier_u.loc[tier_u["author"].astype(str).isin(set(users))].copy()
        dry_input = DRY_DIR / "dry_comments.parquet"
        comments.to_parquet(dry_input, index=False)
        scored = run_frozen_prep(dry_input, "lockboxdry")
        pred, meta = build_predictors(comments, scored)
        rng = np.random.default_rng(7)
        fake5 = pd.DataFrame(rng.normal(size=(len(users), 5)),
                             index=pd.Index(users, name="user_id"),
                             columns=["Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness"])
        fake_bridge = fake5.iloc[:375][[]].assign(TF_cont=rng.uniform(size=375),
                                                  mbti_type_resolved=[["INTP", "ENFJ"][i % 2] for i in range(375)])
        report = analyze(pred, fake5, fake_bridge, comments, dry=True)
        report["predictor_meta"] = meta
        (DRY_DIR / "DRYRUN_REPORT.json").write_text(json.dumps(report, indent=2, default=float) + "\n")
        print(json.dumps({k: report[k] for k in ["eligible", "confirmatory_pass_count", "SUCCESS_RULE_MET"]}, indent=2))
        print("dryrun complete — synthetic labels, no lockbox contact")
        return

    if args.stage == "extract":
        extract_lockbox()
        return

    if args.stage == "score":
        comments = pd.read_parquet(LOCKBOX_COMMENTS)
        comments["author"] = comments["author"].astype(str)
        scored = run_frozen_prep(LOCKBOX_COMMENTS, "lockbox1")
        pred, meta = build_predictors(comments, scored)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        pred.to_parquet(OUT_DIR / "predictors.parquet")
        (OUT_DIR / "predictor_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        gate = (pred["n_conditions"] >= 4) & (pred["n_slices"] >= 12)
        big5_m, bridge_m = load_membership(BIG5_LABELS), load_membership(BRIDGE_LABELS)
        realized = {"big5": int(gate.reindex(pred.index.intersection(big5_m), fill_value=False).sum()),
                    "bridge": int(gate.reindex(pred.index.intersection(bridge_m), fill_value=False).sum())}
        print(json.dumps({"realized_eligible": realized, "prereg_estimates": ESTIMATED_ELIGIBLE, **meta}, indent=2))
        print("score complete — predictors written, NO labels read")
        return

    # ---- stage open ----
    if FINAL_JSON.exists():
        raise SystemExit("OPENING ALREADY PERFORMED — report exists. Budget rules forbid a second run.")
    if SENTINEL.exists() and not args.resume_crashed:
        raise SystemExit("Sentinel exists (crashed run?). Rerun with --resume-crashed exactly once.")

    comments = pd.read_parquet(LOCKBOX_COMMENTS)
    comments["author"] = comments["author"].astype(str)
    pred = pd.read_parquet(OUT_DIR / "predictors.parquet")
    big5_m, bridge_m = load_membership(BIG5_LABELS), load_membership(BRIDGE_LABELS)
    gate = (pred["n_conditions"] >= 4) & (pred["n_slices"] >= 12)
    realized = {"big5": int(gate.reindex(pred.index.intersection(big5_m), fill_value=False).sum()),
                "bridge": int(gate.reindex(pred.index.intersection(bridge_m), fill_value=False).sum())}
    for cohort, est in ESTIMATED_ELIGIBLE.items():
        dev = abs(realized[cohort] - est) / est
        if dev > GATE_TOLERANCE:
            raise SystemExit(f"ABORT GATE F6: realized {cohort} eligible {realized[cohort]} deviates "
                             f"{dev:.1%} from prereg estimate {est} — investigate BEFORE opening.")

    SENTINEL.write_text(json.dumps({
        "opened_at_utc": datetime.now(timezone.utc).isoformat(), "git_head": git_head(),
        "realized_eligible": realized,
        "sha256": {"predictors": sha256_of(OUT_DIR / "predictors.parquet"),
                   "class_map": sha256_of(CLASS_MAP),
                   "big5_labels": sha256_of(BIG5_LABELS),
                   "bridge_labels": sha256_of(BRIDGE_LABELS)},
    }, indent=2) + "\n")
    print("SENTINEL WRITTEN — reading lockbox labels now (opening #1 of 2 SPENT)")

    big5 = pd.read_csv(BIG5_LABELS).set_index("user_id")
    big5.index = big5.index.astype(str)
    bridge = pd.read_csv(BRIDGE_LABELS).set_index("user_id")
    bridge.index = bridge.index.astype(str)

    report = analyze(pred, big5, bridge, comments, dry=False)
    report["realized_eligible_at_gate"] = realized
    FINAL_JSON.write_text(json.dumps(report, indent=2, default=float) + "\n")

    lines = ["# SUICA Lockbox Opening #1 — Preregistered Confirmatory Report", "",
             f"Opened: {report['timestamp_utc']}  |  git: `{report['git_head']}`  |  "
             f"prereg seal: `dd5c7805689acd6d5351f7a22864b3ff45eb1d7d`", "",
             f"Eligible: Big5 {report['eligible']['big5']} (est. 1,108), "
             f"bridge {report['eligible']['bridge']} (est. 326)", "",
             "| id | predictor | target | n | r | 95% CI | p | q(BH) | pred. sign | verdict |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in report["hypotheses"]:
        q = f"{r.get('q_bh', float('nan')):.4f}" if r["confirmatory"] else "secondary"
        verdict = ("PASS" if r.get("significant") and r["direction_match"]
                   else "sig-WRONG-DIR" if r.get("significant") else "ns") if r["confirmatory"] else "reported"
        lines.append(f"| {r['id']} | {r['predictor']} | {r['target']} | {r['n']} | {r['r']:+.4f} "
                     f"| [{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}] | {r['p']:.4f} | {q} "
                     f"| {'+' if r['predicted_sign'] > 0 else '-'} | {verdict} |")
    lines += ["", f"**Confirmatory passes: {report['confirmatory_pass_count']}/7 "
              f"(rule: >=4 and no significant wrong-direction)**",
              f"**SUCCESS RULE MET: {report['SUCCESS_RULE_MET']}**", "",
              "## Non-confirmatory add-ons", "",
              "```json", json.dumps({"delta_r2": report["delta_r2_nonconfirmatory"],
                                     "H7_robustness": report["H7_declared_robustness_nonconfirmatory"],
                                     "tf_flip_applied": report["tf_flip_applied"]}, indent=2, default=float),
              "```", ""]
    REPORT_MD.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[6:len(lines) - 8]))
    print(f"\nSUCCESS_RULE_MET = {report['SUCCESS_RULE_MET']}  ({report['confirmatory_pass_count']}/7)")


if __name__ == "__main__":
    main()
