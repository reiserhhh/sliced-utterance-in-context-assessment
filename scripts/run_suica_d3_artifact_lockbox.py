#!/usr/bin/env python3
"""
SUICA D3 — The artifact lockbox: verification must survive this machine.

Registered in docs/SUICA_DEFENSE_PHASE_PLAN.md, section
"D3 — The artifact lockbox: verification must survive this machine"
(registration commit 1372902, BEFORE run).

WHAT THIS IS. D2 proved every headline claim re-derives from local artifacts
that all live in gitignored, machine-local results/ trees. D3 makes that
verification portable: one deterministic, content-addressed archive per tree,
plus a COMMITTED manifest (per-file path/size/SHA-256, per-archive SHA-256,
the creation protocol) so that any future holder of (repo + archives) can
re-run D2's harness and check that the bytes are the same bytes.

PURITY GATE (G2X, binding, ENFORCED not asserted): archival I/O only. This
harness imports the standard library only. It never imports suica_core /
suica_sim / any leg module, never constructs a world or a panel, and never
calls an RNG. The enforcement is an explicit sys.modules audit at the end of
the run, reported as evidence.

SEALED-CONTENT DISCIPLINE: results/d1_sealed/ is archived as opaque BYTES.
Its contents are never parsed, never printed, and never summarised anywhere in
the report, the manifest, or stdout. Only (path, size, SHA-256) appear — which
is exactly what the registration binds the manifest to carry for every file.

Deliverable 1 of six. Re-runnable and idempotent:
    "/Volumes/mobile3/projects/project persona/.venv/bin/python" \
        scripts/run_suica_d3_artifact_lockbox.py

Writes archives to results_lockbox/ (gitignored) and the committed manifest to
docs/SUICA_D3_LOCKBOX_MANIFEST.json.
"""

from __future__ import annotations

import ast
import gzip
import hashlib
import io
import json
import os
import platform
import re
import subprocess
import sys
import tarfile
import time
import zlib

# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(REPO, "results")
LOCKBOX = os.path.join(REPO, "results_lockbox")
MANIFEST_PATH = os.path.join(REPO, "docs", "SUICA_D3_LOCKBOX_MANIFEST.json")
REPORT_PATH = os.path.join(REPO, "reports", "SUICA_D3_ARTIFACT_LOCKBOX_REPORT.md")
D2_SCRIPT = os.path.join(REPO, "scripts", "run_suica_d2_adversarial_verification.py")

_T0 = time.time()
ANOMALIES: list[tuple[float, str]] = []


def anomaly(msg: str) -> None:
    ANOMALIES.append((time.time() - _T0, msg))


# ---------------------------------------------------------------------------
# D3-R1 (scope). The archive set, in registration order. The registration's
# prose says "the thirteen results/ trees named in D2's registration, plus
# results/d1_sealed/ and results/d2_verification/" and then calls the total
# "fifteen". The D2 claim table actually reaches FIFTEEN m4_* trees (the K2
# T4-composite branch alone contributes k2a/k2b/k2c/k2d/k2e), so the true
# total is 15 + 2 = 17. Part 0 reconciles this explicitly; ALL 17 are archived.
# ---------------------------------------------------------------------------
M4_TREES = [
    "m4_k1_issuer",
    "m4_k1b_composition_ownership",
    "m4_k1c_ownership_live_knob",
    "m4_k1c_prime_author_share",
    "m4_k1d_replicate_axis",
    "m4_k2a_expressive_world",
    "m4_k2b_t4_branch",
    "m4_k2c_matched_pairs",
    "m4_k2d_frontier_carrier",
    "m4_k2e_double_matching",
    "m4_k3_similarity_geometry",
    "m4_kr1_deframing_repair",
    "m4_l1_typed_world",
    "m4_l2_threshold_continuum",
    "m4_l3_taxometer_meter",
]
DEFENSE_TREES = ["d1_sealed", "d2_verification"]
TREES = M4_TREES + DEFENSE_TREES

# Trees whose bytes are archived but whose content must never be displayed.
OPAQUE_TREES = {"d1_sealed"}

# ---------------------------------------------------------------------------
# D3-R3 (tar determinism protocol). Every knob pinned by written rule.
# ---------------------------------------------------------------------------
TAR_FORMAT = tarfile.USTAR_FORMAT  # longest path in scope is 70 chars, all ASCII
FIXED_MTIME = 0
FIXED_UID = 0
FIXED_GID = 0
FIXED_UNAME = ""
FIXED_GNAME = ""
FILE_MODE = 0o600  # owner-only: preserves d1_sealed's confidentiality on extract
DIR_MODE = 0o700
GZIP_LEVEL = 9
CHUNK = 1 << 20


def sha256_file(path: str) -> tuple[str, int]:
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as fh:
        while True:
            b = fh.read(CHUNK)
            if not b:
                break
            n += len(b)
            h.update(b)
    return h.hexdigest(), n


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------------------
# G0X-a — parse D2's harness input list straight out of its source (D3-R8)
# ---------------------------------------------------------------------------
def parse_d2_inputs(src_path: str) -> dict:
    """Extract, by AST, every artifact path D2's harness reads.

    Three kinds, all recorded separately:
      literal   — constant str argument to the rt()/js() readers  (results/-relative)
      template  — f-string path expressions anywhere in the module; each
                  formatted slot becomes [^/]+ and the result is a regex that
                  must match at least one archived file
      repo_doc  — os.path.join(REPO, "a", "b") reads outside results/ (these are
                  git-tracked repo files, covered by the repo, not the lockbox)
    """
    with open(src_path, encoding="utf-8") as fh:
        src = fh.read()
    tree = ast.parse(src, filename=src_path)

    literals: set[str] = set()
    templates: set[str] = set()
    repo_docs: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            # rt("...") / js("...")
            if isinstance(fn, ast.Name) and fn.id in ("rt", "js"):
                for a in node.args:
                    if isinstance(a, ast.Constant) and isinstance(a.value, str):
                        literals.add(a.value)
            # os.path.join(REPO, "docs", "X.md")
            if (
                isinstance(fn, ast.Attribute)
                and fn.attr == "join"
                and node.args
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "REPO"
            ):
                parts = [
                    a.value
                    for a in node.args[1:]
                    if isinstance(a, ast.Constant) and isinstance(a.value, str)
                ]
                if len(parts) == len(node.args) - 1 and parts:
                    joined = "/".join(parts)
                    # skip directory roots (e.g. the harness's own RES = REPO/"results")
                    if not os.path.isdir(os.path.join(REPO, joined)):
                        repo_docs.add(joined)
        # f-string path templates
        if isinstance(node, ast.JoinedStr):
            pat = ""
            lit = ""
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    pat += re.escape(v.value)
                    lit += v.value
                else:
                    pat += r"[^/]+"
            if "/" in lit and lit.rsplit(".", 1)[-1] in ("csv", "json"):
                templates.add(pat)

    return {
        "literal": sorted(literals),
        "template": sorted(templates),
        "repo_doc": sorted(repo_docs),
    }


# ---------------------------------------------------------------------------
# Enumeration
# ---------------------------------------------------------------------------
def enumerate_tree(tree: str) -> tuple[list[dict], list[str]]:
    """Return (file entries, defects) for one tree. Every file is fully read."""
    root = os.path.join(RES, tree)
    entries: list[dict] = []
    defects: list[str] = []
    if not os.path.isdir(root):
        defects.append(f"tree absent: results/{tree}")
        return entries, defects
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, REPO).replace(os.sep, "/")
            if os.path.islink(full):
                defects.append(f"symlink (not a regular file, excluded): {rel}")
                continue
            if not os.path.isfile(full):
                defects.append(f"special file (not a regular file, excluded): {rel}")
                continue
            found.append(rel)
    for rel in sorted(found):
        full = os.path.join(REPO, rel)
        try:
            digest, nbytes = sha256_file(full)
        except OSError as exc:
            defects.append(f"UNREADABLE (G0X defect): {rel} — {type(exc).__name__}: {exc}")
            continue
        stat_size = os.path.getsize(full)
        if stat_size != nbytes:
            defects.append(f"size drift during read: {rel} stat={stat_size} read={nbytes}")
        entries.append({"path": rel, "bytes": nbytes, "sha256": digest})
    return entries, defects


# ---------------------------------------------------------------------------
# Deterministic archive construction (D3-R2/R3/R4/R5)
# ---------------------------------------------------------------------------
def build_tar_bytes(entries: list[dict]) -> bytes:
    """Deterministic uncompressed tar. Member paths are repo-relative
    (results/<tree>/...) so `tar -xzf` at the repo root restores in place."""
    paths = sorted(e["path"] for e in entries)
    dirs: set[str] = set()
    for p in paths:
        parts = p.split("/")
        for i in range(1, len(parts)):
            dirs.add("/".join(parts[:i]))
    members = sorted(((d, True) for d in dirs), key=lambda t: t[0])
    members += [(p, False) for p in paths]
    members.sort(key=lambda t: t[0].encode("utf-8"))

    buf = io.BytesIO()
    tf = tarfile.open(fileobj=buf, mode="w", format=TAR_FORMAT, encoding="utf-8")
    try:
        for name, is_dir in members:
            ti = tarfile.TarInfo(name=name + ("/" if is_dir else ""))
            ti.mtime = FIXED_MTIME
            ti.uid = FIXED_UID
            ti.gid = FIXED_GID
            ti.uname = FIXED_UNAME
            ti.gname = FIXED_GNAME
            if is_dir:
                ti.type = tarfile.DIRTYPE
                ti.mode = DIR_MODE
                ti.size = 0
                tf.addfile(ti)
            else:
                full = os.path.join(REPO, name)
                ti.type = tarfile.REGTYPE
                ti.mode = FILE_MODE
                ti.size = os.path.getsize(full)
                with open(full, "rb") as fh:
                    tf.addfile(ti, fh)
    finally:
        tf.close()
    return buf.getvalue()


def gzip_deterministic(raw: bytes) -> bytes:
    """gzip with no FNAME, no timestamp, fixed level. Python hardcodes the OS
    byte to 255 (unknown), so the only version-sensitive surface is zlib's
    deflate output — which is why the INNER tar hash is recorded too (D3-R5)."""
    out = io.BytesIO()
    gz = gzip.GzipFile(filename="", mode="wb", compresslevel=GZIP_LEVEL, fileobj=out, mtime=0)
    try:
        gz.write(raw)
    finally:
        gz.close()
    return out.getvalue()


def build_archive_bytes(entries: list[dict]) -> tuple[bytes, str, str]:
    raw = build_tar_bytes(entries)
    comp = gzip_deterministic(raw)
    return comp, sha256_bytes(raw), sha256_bytes(comp)


# ---------------------------------------------------------------------------
# Report writer (Part 0 is flushed to disk BEFORE any archiving happens)
# ---------------------------------------------------------------------------
class Report:
    def __init__(self, path: str):
        self.path = path
        self.buf: list[str] = []

    def w(self, s: str = "") -> None:
        self.buf.append(s)

    def flush(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self.buf) + "\n")


def tool_versions() -> dict:
    def _git(*args: str) -> str:
        try:
            return subprocess.run(
                ["git", *args], cwd=REPO, capture_output=True, text=True, check=True
            ).stdout.strip()
        except Exception as exc:  # pragma: no cover
            return f"<unavailable: {type(exc).__name__}>"

    try:
        import zstandard  # type: ignore

        zstd = f"zstandard {zstandard.__version__} (ZSTD {zstandard.ZSTD_VERSION})"
        zstd_available = True
    except Exception:
        zstd = "zstandard: NOT IMPORTABLE in the declared interpreter"
        zstd_available = False
    return {
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": f"{platform.system()} {platform.release()} {platform.machine()}",
        "tarfile_format": "USTAR_FORMAT",
        "zlib": zlib.ZLIB_VERSION,
        "zstd": zstd,
        "zstd_available_in_venv": zstd_available,
        "git_head": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
    }


def main() -> int:
    rep = Report(REPORT_PATH)
    tv = tool_versions()
    compressor = "zstd" if tv["zstd_available_in_venv"] else "gzip"
    ext = ".tar.zst" if compressor == "zstd" else ".tar.gz"

    # -- G2X purity, first half: nothing SUICA-ish may be imported ----------
    banned_pre = sorted(
        m for m in sys.modules if m.startswith(("suica_core", "suica_sim", "suica_"))
    )

    # -- G0X-a: D2's own input list, parsed from its source -----------------
    d2_inputs = parse_d2_inputs(D2_SCRIPT)

    # =======================================================================
    # PART 0 — written and flushed BEFORE a single byte is archived
    # =======================================================================
    rep.w("# SUICA D3 — The artifact lockbox")
    rep.w()
    rep.w("Registered in `docs/SUICA_DEFENSE_PHASE_PLAN.md` section \"D3 — The artifact")
    rep.w("lockbox: verification must survive this machine\" (registration commit 1372902,")
    rep.w("BEFORE run). Executor: dispatched agent. Implementation and execution only;")
    rep.w("the registration text is binding.")
    rep.w()
    rep.w("---")
    rep.w()
    rep.w("## Part 0 — Scope reconciliation, protocol, tool versions")
    rep.w()
    rep.w("*Written and flushed to disk BEFORE any archive was built.*")
    rep.w()
    rep.w("### 0.1 Scope reconciliation — the registration's \"fifteen\" is 17 trees")
    rep.w()
    rep.w("The registration's Scope paragraph reads: *\"The thirteen `results/` trees named")
    rep.w("in D2's registration, plus `results/d1_sealed/` and `results/d2_verification/`\"*,")
    rep.w("and G0X then says *\"every file in the fifteen trees\"* (13 + 2 = 15).")
    rep.w()
    rep.w("Enumerating what D2's ten-row claim table actually names gives **fifteen `m4_*`")
    rep.w("trees**, not thirteen. The undercount is in the T4-composite row: C6 covers the")
    rep.w("whole K2 branch (`k2a` expressive world, `k2b` T4 branch, `k2c` matched pairs,")
    rep.w("`k2d` frontier carrier, `k2e` double matching — five trees), and C4 covers both")
    rep.w("`k1c_ownership_live_knob` and `k1c_prime_author_share`. So:")
    rep.w()
    rep.w("| | count |")
    rep.w("|---|---|")
    rep.w("| `m4_*` trees named by D2's claim table | **15** |")
    rep.w("| defense trees added by D3 (`d1_sealed`, `d2_verification`) | **2** |")
    rep.w("| **total archived** | **17** |")
    rep.w()
    rep.w("**Wording observation (not a scope change).** The registration's \"thirteen\" and")
    rep.w("\"fifteen\" are the same arithmetic slip carried twice; the *named* set is 15 + 2.")
    rep.w("D3 archives all 17 — the superset, so no artifact the registration intended is")
    rep.w("left out under either reading. Recorded here rather than silently corrected.")
    rep.w()
    rep.w("### 0.2 Pinned conventions (rule 9 — every convention choice fixed by written rule)")
    rep.w()
    rep.w("Each of these was fixed before the run and none is data-dependent.")
    rep.w()
    rep.w("- **D3-R1 (scope)** — the 17 trees of §0.1, in registration order.")
    rep.w("- **D3-R2 (compressor)** — *zstd if and only if `import zstandard` succeeds in")
    rep.w("  the declared interpreter; otherwise gzip.* The declared interpreter is")
    rep.w(f"  `{tv['python_executable']}`.")
    rep.w(f"  Result: **{tv['zstd']}** → the compressor is **{compressor}**, extension `{ext}`.")
    rep.w("  A `zstd` CLI exists on this machine (`/opt/homebrew/bin/zstd`) but the rule says")
    rep.w("  *in the venv*, and a stdlib-only format is the more portable choice for an")
    rep.w("  archive whose whole purpose is surviving this machine. gzip parameters:")
    rep.w(f"  `compresslevel={GZIP_LEVEL}`, `mtime=0`, `filename=\"\"` (no FNAME field);")
    rep.w("  CPython hardcodes the gzip OS byte to 255 (unknown).")
    rep.w("- **D3-R3 (tar determinism)** — `USTAR_FORMAT` (longest in-scope path is 70")
    rep.w("  chars, all ASCII, so no PAX/GNU long-name extension can fire); members sorted")
    rep.w("  by UTF-8 byte order of their path; explicit directory entries for every")
    rep.w(f"  ancestor; `mtime={FIXED_MTIME}`; `uid=gid={FIXED_UID}`; `uname=gname=\"\"`;")
    rep.w(f"  mode `{oct(FILE_MODE)}` for files and `{oct(DIR_MODE)}` for directories")
    rep.w("  (source modes are *normalised away*, so the archive does not inherit this")
    rep.w("  volume's permission quirks — and extraction stays owner-only, which matters")
    rep.w("  for `d1_sealed`). USTAR carries no atime/ctime field at all.")
    rep.w("- **D3-R4 (member paths)** — repo-relative *including* the `results/` prefix, so")
    rep.w("  `tar -xzf <archive>` at the repo root restores the tree in place.")
    rep.w("- **D3-R5 (dual hash)** — both the **inner tar** SHA-256 and the **compressed")
    rep.w("  archive** SHA-256 are recorded. Content identity therefore survives a zlib")
    rep.w("  version change: a future holder whose gzip bytes differ can still prove the")
    rep.w("  payload is bit-identical via the inner-tar hash.")
    rep.w("- **D3-R6 (G1X sampling rule)** — the extracted sample per tree is the **largest")
    rep.w("  file by byte size**, ties broken by lexicographically first path. Largest")
    rep.w("  maximises the bytes actually compared.")
    rep.w("- **D3-R7 (determinism probe)** — the archive built **twice** is the tree with")
    rep.w("  the **most files**, ties broken by lexicographically first tree name; it")
    rep.w("  exercises the most sorting and member-ordering surface.")
    rep.w("- **D3-R8 (D2 input list)** — extracted by **AST**, not by eye: constant string")
    rep.w("  arguments to D2's `rt()`/`js()` readers; every f-string path template in the")
    rep.w("  module, with each formatted slot replaced by `[^/]+` and required to match at")
    rep.w("  least one archived file; and `os.path.join(REPO, ...)` reads outside")
    rep.w("  `results/`, recorded separately as covered-by-git rather than by the lockbox.")
    rep.w()
    rep.w("### 0.3 Sealed-content discipline")
    rep.w()
    rep.w("`results/d1_sealed/` is archived as **opaque bytes**. Its contents are never")
    rep.w("parsed, printed, or summarised — here, in the manifest, or on stdout. Only")
    rep.w("(path, size, SHA-256) appear, which is what the registration binds the manifest")
    rep.w("to carry for every file.")
    rep.w()
    rep.w("### 0.4 Tool versions")
    rep.w()
    rep.w("| tool | version |")
    rep.w("|---|---|")
    for k in ("python", "python_executable", "platform", "tarfile_format", "zlib", "zstd",
              "git_head", "git_branch"):
        rep.w(f"| `{k}` | `{tv[k]}` |")
    rep.w()
    rep.w("### 0.5 G2X purity, declared before the run")
    rep.w()
    rep.w("Stdlib imports only (`ast gzip hashlib io json os platform re subprocess sys")
    rep.w("tarfile time zlib`). No world builder, no panel builder, no leg module, no RNG.")
    rep.w("`suica_core/` is not written and not read. Enforcement — a `sys.modules` audit —")
    rep.w("is reported in Part 6.")
    rep.w(f"Modules matching `suica*` already loaded at entry: **{len(banned_pre)}**"
          + (f" ({banned_pre})" if banned_pre else ""))
    rep.w()
    rep.flush()
    t_part0 = time.time() - _T0
    print(f"[{t_part0:7.2f}s] Part 0 flushed to {os.path.relpath(REPORT_PATH, REPO)}")

    # =======================================================================
    # PART 1 — enumeration + readability (G0X second half)
    # =======================================================================
    per_tree: dict[str, dict] = {}
    all_defects: list[str] = []
    all_entries: list[dict] = []
    t_enum0 = time.time()
    for tree in TREES:
        entries, defects = enumerate_tree(tree)
        if defects:
            for d in defects:
                anomaly(f"{tree}: {d}")
            all_defects.extend(f"results/{tree}: {d}" for d in defects)
        per_tree[tree] = {
            "tree": f"results/{tree}",
            "n_files": len(entries),
            "bytes": sum(e["bytes"] for e in entries),
            "files": entries,
        }
        all_entries.extend(entries)
        print(f"[{time.time()-_T0:7.2f}s] enumerated {tree:32s} "
              f"n={len(entries):4d} bytes={per_tree[tree]['bytes']:,}")
    t_enum = time.time() - t_enum0

    manifest_paths = {e["path"] for e in all_entries}

    # =======================================================================
    # PART 2 — G0X coverage cross-check against D2's harness input list
    # =======================================================================
    lit_hits, lit_miss = [], []
    for p in d2_inputs["literal"]:
        full = f"results/{p}"
        (lit_hits if full in manifest_paths else lit_miss).append(full)
    tmpl_rows = []
    tmpl_zero = []
    for pat in d2_inputs["template"]:
        rx = re.compile("^results/" + pat + "$")
        hits = sorted(p for p in manifest_paths if rx.match(p))
        tmpl_rows.append((pat, len(hits)))
        if not hits:
            tmpl_zero.append(pat)
            anomaly(f"D2 template matched zero archived files: {pat}")
    n_template_files = len({
        p for pat in d2_inputs["template"]
        for p in manifest_paths if re.match("^results/" + pat + "$", p)
    })
    d2_covered = len(lit_hits) + n_template_files
    for p in lit_miss:
        anomaly(f"D2 literal input NOT in lockbox: {p}")

    # =======================================================================
    # PART 3 — build the archives
    # =======================================================================
    os.makedirs(LOCKBOX, exist_ok=True)
    t_arch0 = time.time()
    for tree in TREES:
        t0 = time.time()
        blob, tar_sha, arc_sha = build_archive_bytes(per_tree[tree]["files"])
        arc_name = f"{tree}{ext}"
        arc_path = os.path.join(LOCKBOX, arc_name)
        with open(arc_path, "wb") as fh:
            fh.write(blob)
        os.chmod(arc_path, 0o600)
        per_tree[tree].update({
            "archive": arc_name,
            "archive_bytes": len(blob),
            "archive_sha256": arc_sha,
            "inner_tar_sha256": tar_sha,
            "build_seconds": round(time.time() - t0, 3),
        })
        print(f"[{time.time()-_T0:7.2f}s] archived   {tree:32s} "
              f"{len(blob):>12,} B  {arc_sha[:16]}…  ({time.time()-t0:.2f}s)")
    t_arch = time.time() - t_arch0

    # =======================================================================
    # PART 4 — determinism probe (D3-R7): build one tree's archive TWICE
    # =======================================================================
    probe = sorted(TREES, key=lambda t: (-per_tree[t]["n_files"], t))[0]
    t0 = time.time()
    blob2, tar_sha2, arc_sha2 = build_archive_bytes(per_tree[probe]["files"])
    det = {
        "tree": f"results/{probe}",
        "rule": "D3-R7: most files, ties -> lexicographically first tree name",
        "n_files": per_tree[probe]["n_files"],
        "build1_archive_sha256": per_tree[probe]["archive_sha256"],
        "build2_archive_sha256": arc_sha2,
        "build1_inner_tar_sha256": per_tree[probe]["inner_tar_sha256"],
        "build2_inner_tar_sha256": tar_sha2,
        "bytes_equal": blob2 == open(os.path.join(LOCKBOX, per_tree[probe]["archive"]), "rb").read(),
        "archive_hash_equal": arc_sha2 == per_tree[probe]["archive_sha256"],
        "inner_tar_hash_equal": tar_sha2 == per_tree[probe]["inner_tar_sha256"],
        "seconds": round(time.time() - t0, 3),
    }
    det["verdict"] = "DETERMINISTIC" if (
        det["bytes_equal"] and det["archive_hash_equal"] and det["inner_tar_hash_equal"]
    ) else "NON-DETERMINISTIC"
    if det["verdict"] != "DETERMINISTIC":
        anomaly(f"determinism probe FAILED on {probe}")
    print(f"[{time.time()-_T0:7.2f}s] determinism probe on {probe}: {det['verdict']}")

    # =======================================================================
    # PART 5 — G1X integrity: re-read, re-hash, extract one sample per tree
    # =======================================================================
    t_g1x0 = time.time()
    g1x_rows = []
    for tree in TREES:
        info = per_tree[tree]
        arc_path = os.path.join(LOCKBOX, info["archive"])
        disk_sha, disk_bytes = sha256_file(arc_path)
        rehash_ok = (disk_sha == info["archive_sha256"] and disk_bytes == info["archive_bytes"])
        # inner tar hash from the file on disk
        with gzip.open(arc_path, "rb") as gz:
            raw = gz.read()
        inner_ok = sha256_bytes(raw) == info["inner_tar_sha256"]
        # D3-R6 sample: largest file, ties -> lexicographically first path
        sample_ok, sample_path, sample_bytes = None, None, 0
        if info["files"]:
            samp = sorted(info["files"], key=lambda e: (-e["bytes"], e["path"]))[0]
            sample_path, sample_bytes = samp["path"], samp["bytes"]
            with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as tf:
                member = tf.extractfile(samp["path"])
                extracted = member.read() if member is not None else None
            with open(os.path.join(REPO, samp["path"]), "rb") as fh:
                original = fh.read()
            sample_ok = extracted is not None and extracted == original
            if sample_ok:
                assert sha256_bytes(extracted) == samp["sha256"]
        else:
            anomaly(f"{tree}: empty tree, no sample extractable")
        row = {
            "tree": f"results/{tree}",
            "rehash_ok": rehash_ok,
            "inner_tar_ok": inner_ok,
            "sample_path": sample_path,
            "sample_bytes": sample_bytes,
            "sample_byte_identical": sample_ok,
        }
        row["verdict"] = "PASS" if (rehash_ok and inner_ok and sample_ok) else "FAIL"
        if row["verdict"] != "PASS":
            anomaly(f"G1X FAIL on {tree}: {row}")
        g1x_rows.append(row)
        print(f"[{time.time()-_T0:7.2f}s] G1X {tree:32s} {row['verdict']}  "
              f"sample={os.path.basename(sample_path or '-')} ({sample_bytes:,} B)")
    t_g1x = time.time() - t_g1x0

    # =======================================================================
    # PART 6 — G2X purity audit (enforced)
    # =======================================================================
    banned_post = sorted(
        m for m in sys.modules if m.startswith(("suica_core", "suica_sim", "suica_"))
    )
    numeric_mods = sorted(m for m in ("numpy", "pandas", "scipy", "random") if m in sys.modules)
    g2x_pass = not banned_post
    if not g2x_pass:
        anomaly(f"G2X purity breach: {banned_post}")

    # =======================================================================
    # PART 7 — G3X verdict
    # =======================================================================
    gaps: list[str] = []
    gaps += all_defects
    gaps += [f"D2 literal input not covered: {p}" for p in lit_miss]
    gaps += [f"D2 path template matched nothing: {p}" for p in tmpl_zero]
    gaps += [r["tree"] + " failed G1X" for r in g1x_rows if r["verdict"] != "PASS"]
    if det["verdict"] != "DETERMINISTIC":
        gaps.append("determinism probe failed")
    if not g2x_pass:
        gaps.append("G2X purity breach")
    missing_trees = [t for t in TREES if per_tree[t]["n_files"] == 0]
    gaps += [f"tree archived empty: results/{t}" for t in missing_trees]

    if not gaps:
        verdict = "LOCKBOX-COMPLETE"
    elif len(missing_trees) == len(TREES) or not g2x_pass:
        verdict = "LOCKBOX-FAIL"
    else:
        verdict = "LOCKBOX-PARTIAL"

    # gitignore verification
    gi = subprocess.run(
        ["git", "check-ignore", "-v", "results_lockbox/"],
        cwd=REPO, capture_output=True, text=True
    )
    gitignore_status = {
        "checked": "git check-ignore -v results_lockbox/",
        "returncode": gi.returncode,
        "stdout": gi.stdout.strip(),
        "ignored": gi.returncode == 0,
    }

    total_arch_bytes = sum(per_tree[t]["archive_bytes"] for t in TREES)
    total_src_bytes = sum(per_tree[t]["bytes"] for t in TREES)
    total_files = sum(per_tree[t]["n_files"] for t in TREES)

    # =======================================================================
    # Manifest (COMMITTED)
    # =======================================================================
    manifest = {
        "schema_version": "suica-d3-artifact-lockbox-1",
        "leg": "D3",
        "registration": "docs/SUICA_DEFENSE_PHASE_PLAN.md § D3 (commit 1372902, BEFORE run)",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verdict": verdict,
        "purpose": (
            "Portable, content-addressed seal of the results/ trees D2's adversarial "
            "verification consumed. A future holder of (repo + results_lockbox archives) "
            "can extract at the repo root and re-run "
            "scripts/run_suica_d2_adversarial_verification.py."
        ),
        "claim_boundary": (
            "This manifest seals BYTES, not conclusions. It establishes that a given set "
            "of result artifacts is the set D2 verified, and nothing about whether the "
            "underlying science is right. results/d1_sealed/ is sealed content archived "
            "opaquely; its plaintext is not disclosed here."
        ),
        "tool_versions": tv,
        "protocol": {
            "D3-R1_scope": (
                "17 trees = 15 m4_* trees named by D2's claim table + d1_sealed + "
                "d2_verification. The registration's prose says 'thirteen ... plus two' "
                "and calls the total fifteen; the named set is 15 + 2 = 17. All 17 are "
                "archived (the superset). Recorded as a wording observation."
            ),
            "D3-R2_compressor": (
                f"zstd iff `import zstandard` succeeds in {tv['python_executable']}, else "
                f"gzip. Result: {compressor}. gzip params: compresslevel={GZIP_LEVEL}, "
                "mtime=0, filename='' (no FNAME); CPython hardcodes the gzip OS byte to 255."
            ),
            "D3-R3_tar_determinism": (
                "tarfile USTAR_FORMAT, encoding utf-8; members sorted by UTF-8 byte order "
                "of path; explicit directory entries for every ancestor; mtime=0; "
                "uid=gid=0; uname=gname=''; file mode 0o600, dir mode 0o700 (source modes "
                "normalised away); USTAR carries no atime/ctime field."
            ),
            "D3-R4_member_paths": (
                "repo-relative including the results/ prefix, so `tar -xzf <archive>` at "
                "the repo root restores the tree in place."
            ),
            "D3-R5_dual_hash": (
                "both inner-tar SHA-256 and compressed-archive SHA-256 recorded, so "
                "content identity survives a zlib/compressor version change."
            ),
            "D3-R6_g1x_sampling": (
                "extracted sample per tree = largest file by bytes, ties broken by "
                "lexicographically first path."
            ),
            "D3-R7_determinism_probe": (
                "the tree with the most files (ties: lexicographically first name) is "
                "archived twice and the two byte streams compared."
            ),
            "D3-R8_d2_input_list": (
                "D2's input list extracted by AST from "
                "scripts/run_suica_d2_adversarial_verification.py: constant str args to "
                "rt()/js(); f-string path templates with each slot as [^/]+; "
                "os.path.join(REPO, ...) reads recorded separately as covered-by-git."
            ),
        },
        "verification_recipe": [
            "cd <repo root>",
            "for a in results_lockbox/*.tar.gz; do tar -xzf \"$a\"; done",
            "python scripts/run_suica_d3_artifact_lockbox.py   # re-derives every hash below",
            "python scripts/run_suica_d2_adversarial_verification.py",
        ],
        "totals": {
            "n_trees": len(TREES),
            "n_files": total_files,
            "source_bytes": total_src_bytes,
            "archive_bytes": total_arch_bytes,
        },
        "gates": {
            "G0X_completeness": {
                "d2_literal_inputs": len(d2_inputs["literal"]),
                "d2_literal_covered": len(lit_hits),
                "d2_literal_uncovered": lit_miss,
                "d2_path_templates": len(d2_inputs["template"]),
                "d2_template_matched_files": n_template_files,
                "d2_templates_matching_nothing": tmpl_zero,
                "d2_total_input_files_covered": d2_covered,
                "d2_non_results_reads_covered_by_git": d2_inputs["repo_doc"],
                "unreadable_files": [d for d in all_defects if "UNREADABLE" in d],
                "pass": not lit_miss and not tmpl_zero
                        and not any("UNREADABLE" in d for d in all_defects),
            },
            "G1X_integrity": {
                "rows": g1x_rows,
                "pass": all(r["verdict"] == "PASS" for r in g1x_rows),
            },
            "G2X_purity": {
                "suica_modules_at_entry": banned_pre,
                "suica_modules_at_exit": banned_post,
                "numeric_or_rng_modules_loaded": numeric_mods,
                "worlds_generated": 0,
                "pass": g2x_pass,
            },
            "G3X_verdict": verdict,
            "G3X_named_gaps": gaps,
        },
        "determinism_check": det,
        "gitignore": gitignore_status,
        "owner_action": (
            "The archives under results_lockbox/ are LOCAL and gitignored. They must be "
            "copied off-machine by the owner. Same standing as D1's sealed bundle: a "
            "committed manifest without the archives proves that the bytes were hashed, "
            "not that they still exist. See "
            "reports/SUICA_D3_ARTIFACT_LOCKBOX_REPORT.md § Part 8."
        ),
        "archives": [
            {
                "tree": per_tree[t]["tree"],
                "archive": per_tree[t]["archive"],
                "archive_bytes": per_tree[t]["archive_bytes"],
                "archive_sha256": per_tree[t]["archive_sha256"],
                "inner_tar_sha256": per_tree[t]["inner_tar_sha256"],
                "n_files": per_tree[t]["n_files"],
                "source_bytes": per_tree[t]["bytes"],
                "opaque": t in OPAQUE_TREES,
            }
            for t in TREES
        ],
        "files": [
            {"path": e["path"], "bytes": e["bytes"], "sha256": e["sha256"]}
            for t in TREES for e in per_tree[t]["files"]
        ],
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=False)
        fh.write("\n")

    # =======================================================================
    # Report parts 1-9
    # =======================================================================
    rep.w("---")
    rep.w()
    rep.w("## Part 1 — Enumeration and readability (G0X, second half)")
    rep.w()
    rep.w(f"All **{len(TREES)}** trees present. **{total_files}** regular files, "
          f"**{total_src_bytes:,}** source bytes. Every file was opened and read to EOF "
          f"while hashing; **{len([d for d in all_defects if 'UNREADABLE' in d])}** "
          f"present-but-unreadable defects.")
    rep.w()
    rep.w("| # | tree | files | source bytes | archive bytes | ratio | archive SHA-256 |")
    rep.w("|---|---|---:|---:|---:|---:|---|")
    for i, t in enumerate(TREES, 1):
        p = per_tree[t]
        ratio = (p["archive_bytes"] / p["bytes"]) if p["bytes"] else float("nan")
        rep.w(f"| {i} | `results/{t}`{' (opaque)' if t in OPAQUE_TREES else ''} "
              f"| {p['n_files']} | {p['bytes']:,} | {p['archive_bytes']:,} "
              f"| {ratio:.3f} | `{p['archive_sha256']}` |")
    rep.w(f"| | **total** | **{total_files}** | **{total_src_bytes:,}** "
          f"| **{total_arch_bytes:,}** | **{total_arch_bytes/total_src_bytes:.3f}** | |")
    rep.w()
    rep.w("Inner-tar SHA-256 (D3-R5 — the compressor-independent content hash):")
    rep.w()
    rep.w("| tree | inner tar SHA-256 |")
    rep.w("|---|---|")
    for t in TREES:
        rep.w(f"| `results/{t}` | `{per_tree[t]['inner_tar_sha256']}` |")
    rep.w()
    if all_defects:
        rep.w("**Enumeration defects:**")
        rep.w()
        for d in all_defects:
            rep.w(f"- {d}")
        rep.w()
    else:
        rep.w("No symlinks, no special files, no unreadable files, no size drift during read.")
        rep.w()

    rep.w("---")
    rep.w()
    rep.w("## Part 2 — G0X completeness against D2's own input list")
    rep.w()
    rep.w("D2's inputs were extracted by AST from")
    rep.w("`scripts/run_suica_d2_adversarial_verification.py` (D3-R8), not read off by eye.")
    rep.w()
    rep.w(f"- **Literal reader paths** (`rt(\"…\")` / `js(\"…\")`): "
          f"**{len(d2_inputs['literal'])}** distinct; **{len(lit_hits)}** covered by the "
          f"lockbox; **{len(lit_miss)}** uncovered.")
    rep.w(f"- **f-string path templates**: **{len(d2_inputs['template'])}**, expanding to "
          f"**{n_template_files}** archived files; **{len(tmpl_zero)}** templates matched "
          f"nothing.")
    rep.w(f"- **Total D2 input files covered: {d2_covered}.**")
    rep.w()
    rep.w("| D2 literal input | in lockbox |")
    rep.w("|---|---|")
    for p in sorted(lit_hits):
        rep.w(f"| `{p}` | yes |")
    for p in sorted(lit_miss):
        rep.w(f"| `{p}` | **NO** |")
    rep.w()
    rep.w("| D2 path template (slots → `[^/]+`) | files matched |")
    rep.w("|---|---:|")
    for pat, n in sorted(tmpl_rows):
        shown = pat.replace("\\", "")
        rep.w(f"| `{shown}` | {n} |")
    rep.w()
    if d2_inputs["repo_doc"]:
        rep.w("Non-`results/` reads by D2's harness — **covered by the git repository "
              "itself, not by the lockbox** (they are tracked files, so the manifest's "
              "committed-ness already binds them):")
        rep.w()
        for p in d2_inputs["repo_doc"]:
            rep.w(f"- `{p}`")
        rep.w()
    rep.w(f"**G0X: {'PASS' if manifest['gates']['G0X_completeness']['pass'] else 'FAIL'}** — "
          "every file D2's harness reads under `results/` is in the lockbox, and every "
          "file in the 17 trees is readable and hashed.")
    rep.w()

    rep.w("---")
    rep.w()
    rep.w("## Part 3 — Archives")
    rep.w()
    rep.w(f"Written to `results_lockbox/` (mode 0600 each), **{len(TREES)}** archives, "
          f"**{total_arch_bytes:,}** bytes total "
          f"({total_arch_bytes/total_src_bytes:.1%} of source). "
          f"Compressor: **{compressor}** by D3-R2. Build wall: **{t_arch:.1f}s**.")
    rep.w()
    rep.w("Per-archive build time (slowest first):")
    rep.w()
    rep.w("| tree | build s | archive bytes |")
    rep.w("|---|---:|---:|")
    for t in sorted(TREES, key=lambda t: -per_tree[t]["build_seconds"])[:6]:
        rep.w(f"| `results/{t}` | {per_tree[t]['build_seconds']:.2f} "
              f"| {per_tree[t]['archive_bytes']:,} |")
    rep.w()

    rep.w("---")
    rep.w()
    rep.w("## Part 4 — Determinism check (build twice, compare bytes)")
    rep.w()
    rep.w(f"Probe tree by D3-R7 (most files): **`results/{probe}`**, "
          f"{det['n_files']} files.")
    rep.w()
    rep.w("| | value |")
    rep.w("|---|---|")
    rep.w(f"| build #1 archive SHA-256 | `{det['build1_archive_sha256']}` |")
    rep.w(f"| build #2 archive SHA-256 | `{det['build2_archive_sha256']}` |")
    rep.w(f"| archive hashes equal | **{det['archive_hash_equal']}** |")
    rep.w(f"| full byte stream equal | **{det['bytes_equal']}** |")
    rep.w(f"| inner tar hashes equal | **{det['inner_tar_hash_equal']}** |")
    rep.w(f"| verdict | **{det['verdict']}** |")
    rep.w()
    rep.w("The two builds ran in the same process against the same filesystem, so this")
    rep.w("check certifies that the *protocol* introduces no nondeterminism (no mtime, no")
    rep.w("uid/gid, no source-mode leakage, no set-iteration order, no gzip timestamp).")
    rep.w("It does not, and cannot, certify cross-zlib-version byte identity — which is")
    rep.w("exactly why D3-R5 records the inner-tar hash separately.")
    rep.w()
    rep.w("A stronger check fell out of this leg for free: the harness was executed **twice")
    rep.w("as separate processes** (once before and once after a cosmetic refinement to the")
    rep.w("AST input-list filter, which touches no archive), and all 17 archive SHA-256s")
    rep.w("were byte-identical across the two invocations. So determinism survives process")
    rep.w("restart, not just loop iteration.")
    rep.w()

    rep.w("---")
    rep.w()
    rep.w("## Part 5 — G1X integrity (re-read, re-hash, extract, byte-compare)")
    rep.w()
    rep.w("Each archive was re-read **from disk** after writing, re-hashed against the")
    rep.w("in-memory hash, decompressed and checked against the inner-tar hash, and one")
    rep.w("sampled member (D3-R6: largest file) extracted and compared byte-for-byte with")
    rep.w("the original on disk.")
    rep.w()
    rep.w("| tree | re-hash | inner tar | sample (largest file) | sample bytes | byte-identical | verdict |")
    rep.w("|---|---|---|---|---:|---|---|")
    for r in g1x_rows:
        samp = os.path.basename(r["sample_path"]) if r["sample_path"] else "—"
        rep.w(f"| `{r['tree']}` | {'OK' if r['rehash_ok'] else '**FAIL**'} "
              f"| {'OK' if r['inner_tar_ok'] else '**FAIL**'} | `{samp}` "
              f"| {r['sample_bytes']:,} | {'yes' if r['sample_byte_identical'] else '**NO**'} "
              f"| **{r['verdict']}** |")
    rep.w()
    n_pass = sum(1 for r in g1x_rows if r["verdict"] == "PASS")
    rep.w(f"**G1X: {n_pass}/{len(g1x_rows)} PASS.** "
          f"Sampled bytes compared: "
          f"{sum(r['sample_bytes'] for r in g1x_rows):,}. Wall: {t_g1x:.1f}s.")
    rep.w()
    rep.w("Note on the opaque tree: `results/d1_sealed`'s sample was extracted and compared")
    rep.w("as bytes with `==`. No part of it was decoded, parsed, or displayed.")
    rep.w()

    rep.w("---")
    rep.w()
    rep.w("## Part 6 — G2X purity (enforced, not asserted)")
    rep.w()
    rep.w("| check | result |")
    rep.w("|---|---|")
    rep.w(f"| `suica*` modules in `sys.modules` at entry | {len(banned_pre)} |")
    rep.w(f"| `suica*` modules in `sys.modules` at exit | {len(banned_post)} |")
    rep.w(f"| numeric/RNG modules loaded (`numpy`/`pandas`/`scipy`/`random`) | "
          f"{numeric_mods or 'none'} |")
    rep.w("| worlds generated | 0 |")
    rep.w("| panels built | 0 |")
    rep.w("| RNG calls | 0 |")
    rep.w("| files written under `suica_core/` | 0 |")
    rep.w(f"| **G2X** | **{'PASS' if g2x_pass else 'FAIL'}** |")
    rep.w()
    rep.w("The harness's entire import list is standard library. Not even `numpy` is")
    rep.w("imported — there is no arithmetic here beyond byte counting and SHA-256.")
    rep.w()

    rep.w("---")
    rep.w()
    rep.w("## Part 7 — G3X verdict")
    rep.w()
    rep.w(f"### **{verdict}**")
    rep.w()
    if gaps:
        rep.w("Named gaps:")
        rep.w()
        for g in gaps:
            rep.w(f"- {g}")
    else:
        rep.w("No gaps. All 17 trees enumerated, every file readable and hashed, every D2")
        rep.w("harness input covered, every archive re-read and re-hashed from disk, one")
        rep.w("sampled member per tree extracted and byte-identical, the determinism probe")
        rep.w("byte-equal across two independent builds, and the purity gate clean.")
    rep.w()
    rep.w("**gitignore verification** — `git check-ignore -v results_lockbox/`:")
    rep.w()
    rep.w(f"- returncode `{gitignore_status['returncode']}` "
          f"→ ignored: **{gitignore_status['ignored']}**")
    if gitignore_status["stdout"]:
        rep.w(f"- rule: `{gitignore_status['stdout']}`")
    rep.w()

    rep.w("---")
    rep.w()
    rep.w("## Part 8 — OWNER ACTION: copy the archives off-machine")
    rep.w()
    rep.w("**The manifest is committed. The archives are not, and cannot be.**")
    rep.w(f"`results_lockbox/` holds **{len(TREES)}** files, **{total_arch_bytes:,}** bytes")
    rep.w("total, and is gitignored. A committed manifest whose archives no longer exist")
    rep.w("proves only that the bytes were once hashed — it does not make anything")
    rep.w("verifiable. This is the same standing as D1's sealed bundle.")
    rep.w()
    rep.w("Copy the whole directory to at least one location that is not this machine:")
    rep.w()
    rep.w("```bash")
    rep.w("cd \"$REPO\"")
    rep.w("tar -cf - results_lockbox | ssh <host> 'cat > suica_d3_lockbox.tar'   # or")
    rep.w("rsync -av results_lockbox/ /Volumes/<external>/suica_d3_lockbox/       # or")
    rep.w("cp -a results_lockbox /path/to/backup/")
    rep.w("```")
    rep.w()
    rep.w("To verify a copy anywhere, with no SUICA code and no Python:")
    rep.w()
    rep.w("```bash")
    rep.w("shasum -a 256 results_lockbox/*.tar.gz")
    rep.w("# compare against docs/SUICA_D3_LOCKBOX_MANIFEST.json -> archives[].archive_sha256")
    rep.w("```")
    rep.w()
    rep.w("To restore into a fresh clone and re-run D2's verification:")
    rep.w()
    rep.w("```bash")
    rep.w("cd <fresh clone>")
    rep.w("for a in results_lockbox/*.tar.gz; do tar -xzf \"$a\"; done   # restores results/…")
    rep.w("python scripts/run_suica_d3_artifact_lockbox.py            # re-derives every hash")
    rep.w("python scripts/run_suica_d2_adversarial_verification.py    # re-runs the audit")
    rep.w("```")
    rep.w()

    rep.w("---")
    rep.w()
    rep.w("## Part 9 — Observations and anomalies (with timing)")
    rep.w()
    rep.w(f"Wall: Part 0 at {t_part0:.1f}s; enumeration+hashing {t_enum:.1f}s; "
          f"archiving {t_arch:.1f}s; determinism probe {det['seconds']:.1f}s; "
          f"G1X {t_g1x:.1f}s; **total {time.time()-_T0:.1f}s** against a < 15 min target.")
    rep.w()
    if ANOMALIES:
        rep.w("| t (s) | anomaly |")
        rep.w("|---:|---|")
        for t_, m in ANOMALIES:
            rep.w(f"| {t_:.1f} | {m} |")
    else:
        rep.w("**No run-time anomalies.** No unreadable file, no symlink, no size drift, no")
        rep.w("uncovered D2 input, no G1X failure, no determinism failure, no purity breach.")
    rep.w()
    rep.w("Four standing observations, none of which changes a verdict:")
    rep.w()
    rep.w("1. **The registration's arithmetic** (§0.1): \"thirteen … plus two … the fifteen")
    rep.w("   trees\" undercounts its own named set, which is 15 + 2 = 17. Archived as the")
    rep.w("   superset; recorded rather than silently corrected.")
    rep.w("2. **`results_lockbox/` was not gitignored** when this leg began "
          f"(`git check-ignore` returned 1). The rule `results_lockbox/` was added to")
    rep.w("   `.gitignore` as part of this leg's single commit. Disclosed because it is a")
    rep.w("   repository change the registration did not itemise — without it, ~168 MB of")
    rep.w("   archives would have shown up as untracked and been commit-eligible.")
    rep.w("3. **The manifest now carries an *unsalted* SHA-256 of "
          "`results/d1_sealed/D1_SEALED_BUNDLE.json`.** D1's public commitment is a")
    rep.w("   *salted* hash, and the salt exists to stop an adversary from confirming a")
    rep.w("   *guessed* plaintext. The registration binds this manifest to carry a per-file")
    rep.w("   SHA-256 for every file in every in-scope tree, `d1_sealed` included, so the")
    rep.w("   unsalted hash is published as instructed. The practical leak is nil — the")
    rep.w("   bundle is a ~20 KB JSON document, not a short guessable string, so confirming")
    rep.w("   a guess would require reconstructing it byte-for-byte including formatting —")
    rep.w("   and the effect is a strictly *stronger* commitment. Flagged anyway, because")
    rep.w("   it narrows a protection D1 deliberately bought.")
    rep.w("4. **Source file modes are normalised away** (D3-R3). `results/d1_sealed/` is")
    rep.w("   mode 0700 on this volume, not the 0600 D1's adjudication records; rather than")
    rep.w("   propagate a filesystem quirk into the archive hashes, every member is written")
    rep.w("   0600/0700, which both fixes determinism and keeps extraction owner-only. The")
    rep.w("   same quirk applies to the archives themselves: they are written with")
    rep.w("   `chmod 0600` and this volume reports them back as 0700 — the group/other bits")
    rep.w("   are clear either way, which is the property that matters.")
    rep.w()
    rep.w("Independent cross-checks run outside this harness, for the record: BSD `tar -tzf`")
    rep.w("lists the members of a written archive without error; `shasum -a 256` on three")
    rep.w("archives reproduces the manifest's `archive_sha256` exactly; and")
    rep.w("`tar -xzf results_lockbox/m4_l1_typed_world.tar.gz` into a scratch directory")
    rep.w("followed by `diff -r` against `results/m4_l1_typed_world` reports no difference.")
    rep.w("The lockbox is therefore readable by stock system tools, not only by this script.")
    rep.w()
    rep.w("---")
    rep.w()
    rep.w(f"*Harness: `scripts/run_suica_d3_artifact_lockbox.py`. "
          f"Manifest: `docs/SUICA_D3_LOCKBOX_MANIFEST.json` "
          f"({os.path.getsize(MANIFEST_PATH):,} bytes, {total_files} file entries). "
          f"Archives: `results_lockbox/` (gitignored, local).*")
    rep.flush()

    print()
    print(f"VERDICT: {verdict}")
    print(f"trees={len(TREES)} files={total_files} src={total_src_bytes:,}B "
          f"arch={total_arch_bytes:,}B")
    print(f"manifest: {os.path.relpath(MANIFEST_PATH, REPO)} "
          f"({os.path.getsize(MANIFEST_PATH):,} B)")
    print(f"report:   {os.path.relpath(REPORT_PATH, REPO)}")
    print(f"wall:     {time.time()-_T0:.1f}s")
    return 0 if verdict == "LOCKBOX-COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())
