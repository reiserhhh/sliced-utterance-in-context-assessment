# SUICA D3 — The artifact lockbox

Registered in `docs/SUICA_DEFENSE_PHASE_PLAN.md` section "D3 — The artifact
lockbox: verification must survive this machine" (registration commit 1372902,
BEFORE run). Executor: dispatched agent. Implementation and execution only;
the registration text is binding.

---

## Part 0 — Scope reconciliation, protocol, tool versions

*Written and flushed to disk BEFORE any archive was built.*

### 0.1 Scope reconciliation — the registration's "fifteen" is 17 trees

The registration's Scope paragraph reads: *"The thirteen `results/` trees named
in D2's registration, plus `results/d1_sealed/` and `results/d2_verification/`"*,
and G0X then says *"every file in the fifteen trees"* (13 + 2 = 15).

Enumerating what D2's ten-row claim table actually names gives **fifteen `m4_*`
trees**, not thirteen. The undercount is in the T4-composite row: C6 covers the
whole K2 branch (`k2a` expressive world, `k2b` T4 branch, `k2c` matched pairs,
`k2d` frontier carrier, `k2e` double matching — five trees), and C4 covers both
`k1c_ownership_live_knob` and `k1c_prime_author_share`. So:

| | count |
|---|---|
| `m4_*` trees named by D2's claim table | **15** |
| defense trees added by D3 (`d1_sealed`, `d2_verification`) | **2** |
| **total archived** | **17** |

**Wording observation (not a scope change).** The registration's "thirteen" and
"fifteen" are the same arithmetic slip carried twice; the *named* set is 15 + 2.
D3 archives all 17 — the superset, so no artifact the registration intended is
left out under either reading. Recorded here rather than silently corrected.

### 0.2 Pinned conventions (rule 9 — every convention choice fixed by written rule)

Each of these was fixed before the run and none is data-dependent.

- **D3-R1 (scope)** — the 17 trees of §0.1, in registration order.
- **D3-R2 (compressor)** — *zstd if and only if `import zstandard` succeeds in
  the declared interpreter; otherwise gzip.* The declared interpreter is
  `/Volumes/mobile3/projects/project persona/.venv/bin/python`.
  Result: **zstandard: NOT IMPORTABLE in the declared interpreter** → the compressor is **gzip**, extension `.tar.gz`.
  A `zstd` CLI exists on this machine (`/opt/homebrew/bin/zstd`) but the rule says
  *in the venv*, and a stdlib-only format is the more portable choice for an
  archive whose whole purpose is surviving this machine. gzip parameters:
  `compresslevel=9`, `mtime=0`, `filename=""` (no FNAME field);
  CPython hardcodes the gzip OS byte to 255 (unknown).
- **D3-R3 (tar determinism)** — `USTAR_FORMAT` (longest in-scope path is 70
  chars, all ASCII, so no PAX/GNU long-name extension can fire); members sorted
  by UTF-8 byte order of their path; explicit directory entries for every
  ancestor; `mtime=0`; `uid=gid=0`; `uname=gname=""`;
  mode `0o600` for files and `0o700` for directories
  (source modes are *normalised away*, so the archive does not inherit this
  volume's permission quirks — and extraction stays owner-only, which matters
  for `d1_sealed`). USTAR carries no atime/ctime field at all.
- **D3-R4 (member paths)** — repo-relative *including* the `results/` prefix, so
  `tar -xzf <archive>` at the repo root restores the tree in place.
- **D3-R5 (dual hash)** — both the **inner tar** SHA-256 and the **compressed
  archive** SHA-256 are recorded. Content identity therefore survives a zlib
  version change: a future holder whose gzip bytes differ can still prove the
  payload is bit-identical via the inner-tar hash.
- **D3-R6 (G1X sampling rule)** — the extracted sample per tree is the **largest
  file by byte size**, ties broken by lexicographically first path. Largest
  maximises the bytes actually compared.
- **D3-R7 (determinism probe)** — the archive built **twice** is the tree with
  the **most files**, ties broken by lexicographically first tree name; it
  exercises the most sorting and member-ordering surface.
- **D3-R8 (D2 input list)** — extracted by **AST**, not by eye: constant string
  arguments to D2's `rt()`/`js()` readers; every f-string path template in the
  module, with each formatted slot replaced by `[^/]+` and required to match at
  least one archived file; and `os.path.join(REPO, ...)` reads outside
  `results/`, recorded separately as covered-by-git rather than by the lockbox.

### 0.3 Sealed-content discipline

`results/d1_sealed/` is archived as **opaque bytes**. Its contents are never
parsed, printed, or summarised — here, in the manifest, or on stdout. Only
(path, size, SHA-256) appear, which is what the registration binds the manifest
to carry for every file.

### 0.4 Tool versions

| tool | version |
|---|---|
| `python` | `3.14.3` |
| `python_executable` | `/Volumes/mobile3/projects/project persona/.venv/bin/python` |
| `platform` | `Darwin 25.4.0 arm64` |
| `tarfile_format` | `USTAR_FORMAT` |
| `zlib` | `1.2.12` |
| `zstd` | `zstandard: NOT IMPORTABLE in the declared interpreter` |
| `git_head` | `1372902d89af984bd0df8d098b922bc668dfbba7` |
| `git_branch` | `main` |

### 0.5 G2X purity, declared before the run

Stdlib imports only (`ast gzip hashlib io json os platform re subprocess sys
tarfile time zlib`). No world builder, no panel builder, no leg module, no RNG.
`suica_core/` is not written and not read. Enforcement — a `sys.modules` audit —
is reported in Part 6.
Modules matching `suica*` already loaded at entry: **0**

---

## Part 1 — Enumeration and readability (G0X, second half)

All **17** trees present. **363** regular files, **168,659,718** source bytes. Every file was opened and read to EOF while hashing; **0** present-but-unreadable defects.

| # | tree | files | source bytes | archive bytes | ratio | archive SHA-256 |
|---|---|---:|---:|---:|---:|---|
| 1 | `results/m4_k1_issuer` | 6 | 133,705 | 62,271 | 0.466 | `b1f20a5ba738227a929a561ee185ecf35c3150d0b667553b932d588900e8fcff` |
| 2 | `results/m4_k1b_composition_ownership` | 9 | 112,759 | 36,208 | 0.321 | `1bfd7c75f21ee1e94b9c8cfa25d2cc231f0681f8e6182d657e2fe206ff2306a6` |
| 3 | `results/m4_k1c_ownership_live_knob` | 6 | 55,380 | 14,155 | 0.256 | `c8cbf8bdec20f4212c575a1cb7069128f893ac15a0c2f11c1162c43f407fd547` |
| 4 | `results/m4_k1c_prime_author_share` | 9 | 268,819 | 77,924 | 0.290 | `4f4679c50b5239048cbbcdced3ace1f5c00522ae98e79bc74f43f3f6964cb74f` |
| 5 | `results/m4_k1d_replicate_axis` | 20 | 68,949 | 18,989 | 0.275 | `44c2f8a2f43f8af44657c5b3144582d95a186dfd7aa64fc6afe1bda00401dfcf` |
| 6 | `results/m4_k2a_expressive_world` | 21 | 16,897,812 | 7,723,414 | 0.457 | `9263e1b540a8e47721729641bb99163adc9efe9043a602e6c3451a5942bbb154` |
| 7 | `results/m4_k2b_t4_branch` | 22 | 11,969,836 | 5,247,966 | 0.438 | `ed7da06478592aee00cf057acce915e3c1678ae45e2e7effdd3d47e71c102a6e` |
| 8 | `results/m4_k2c_matched_pairs` | 37 | 47,651,909 | 20,918,081 | 0.439 | `3d8d3b6f401dc3c6b5db0640d7ccaaab515226ea0af9a1fd10ed4721cbce0eba` |
| 9 | `results/m4_k2d_frontier_carrier` | 35 | 41,030,116 | 17,977,119 | 0.438 | `866c94148401c6f4f4812b169ee81c331d74550ae2ee99e1befaf3d5eed2881f` |
| 10 | `results/m4_k2e_double_matching` | 35 | 41,081,618 | 17,958,875 | 0.437 | `09a708bb2b24379c034c338bcb641df78c1bf9abbeaa485b015cdfc668b64563` |
| 11 | `results/m4_k3_similarity_geometry` | 15 | 7,644,007 | 1,819,499 | 0.238 | `b5cd5e6626aee46586a7a85f1a43be70a352c0c36f157465ecb70052b05cab01` |
| 12 | `results/m4_kr1_deframing_repair` | 55 | 443,896 | 113,298 | 0.255 | `ca73426aa7b54eda0ac6f3cba9b3b80f01e25a09b81279484c848c6ef5ace5fb` |
| 13 | `results/m4_l1_typed_world` | 25 | 254,943 | 70,826 | 0.278 | `12386e1f18a02f871d6a2067c7102daec76f39cd21e76bb506f4bbbc96e9e1e3` |
| 14 | `results/m4_l2_threshold_continuum` | 25 | 462,275 | 156,672 | 0.339 | `fe7f9b757be06841cc292743f234e022e1edd310bc4393bd88fbe7a5403ae17d` |
| 15 | `results/m4_l3_taxometer_meter` | 20 | 522,272 | 180,419 | 0.345 | `38177d675dc80b7a094b49a66e91671ae07918a6f3bc84a2bd38df027c61cbd1` |
| 16 | `results/d1_sealed` (opaque) | 2 | 20,448 | 6,216 | 0.304 | `ecbbc56048c0a49b835fa545e9ed24cf5f7c9552d1db68ab8af71870fa9e5c35` |
| 17 | `results/d2_verification` | 21 | 40,974 | 10,456 | 0.255 | `0e47fab6295a937af1fd18d25671f296c6c7632526cec6d265f4dadedaceffe5` |
| | **total** | **363** | **168,659,718** | **72,392,388** | **0.429** | |

Inner-tar SHA-256 (D3-R5 — the compressor-independent content hash):

| tree | inner tar SHA-256 |
|---|---|
| `results/m4_k1_issuer` | `2412a211aa7f71dc4b62af42f0e3de1415200840ad246e8291749cae5c406be2` |
| `results/m4_k1b_composition_ownership` | `ae7b807d87b996551ddac7b981b76462b41f18e9e549bfd6278c71d67acf4288` |
| `results/m4_k1c_ownership_live_knob` | `d5ff44c903a76711d390de30106493799875171d24c6b566a90261a5a8b2c2d6` |
| `results/m4_k1c_prime_author_share` | `89f857c49b1ff52f50ae40585d00a3d2223db4b83f6f86b48d49c5080a923b29` |
| `results/m4_k1d_replicate_axis` | `646d5b5ffbcd8cf008d09cacad2a9c544dcd6f6625598a175f3738326c8333c4` |
| `results/m4_k2a_expressive_world` | `9abfa7639858c4743b0abb6178a0329d5f5f4ca3db74846ce065752284c40850` |
| `results/m4_k2b_t4_branch` | `628a8a3f0011c932f897e5b267eee304b7f10c9f2fd5e6f7b1246319aee5520f` |
| `results/m4_k2c_matched_pairs` | `b80de75555cf437ac10a222b3eec77336bfe1328b2b226dee1c73b5057d97c0a` |
| `results/m4_k2d_frontier_carrier` | `479624ee867f97a6f5dc5bb535b184d4e955757e2b13f162af31ea8a646dca5a` |
| `results/m4_k2e_double_matching` | `c32212354f63fa8a81e88c063860d8a7109546ee0e6b1c9b6f30e2d1f77b7000` |
| `results/m4_k3_similarity_geometry` | `acfe9ed7edf441b51b55d405aa28a240d62b93be3c9e586d2cb7c3052f31c191` |
| `results/m4_kr1_deframing_repair` | `fe4c5f2315a6dbd14f1a49595b934ded3e06996ea1e0090f05fe11bbec2c0b24` |
| `results/m4_l1_typed_world` | `ea667210d0356f9a6ef052f4e18f9a2b5a238125101ce11c8c5cb5b5d0be21b5` |
| `results/m4_l2_threshold_continuum` | `ee157e9b04bf826cd244da37765f0914cc3b880909f89675e446ef305af7da45` |
| `results/m4_l3_taxometer_meter` | `0dbd4ec597160322cf18f732d254a8d345bb64eff52ce2bdba8e8b8d8d71d646` |
| `results/d1_sealed` | `c282147fd9bb41028e8ad4b01f234c687f9f2b61861117be104bbf07eed0340b` |
| `results/d2_verification` | `c3d40505f17c85e3af1535a842648a847b7fac96bc058568f4defe6c18138f5f` |

No symlinks, no special files, no unreadable files, no size drift during read.

---

## Part 2 — G0X completeness against D2's own input list

D2's inputs were extracted by AST from
`scripts/run_suica_d2_adversarial_verification.py` (D3-R8), not read off by eye.

- **Literal reader paths** (`rt("…")` / `js("…")`): **20** distinct; **20** covered by the lockbox; **0** uncovered.
- **f-string path templates**: **2**, expanding to **48** archived files; **0** templates matched nothing.
- **Total D2 input files covered: 68.**

| D2 literal input | in lockbox |
|---|---|
| `results/m4_k1_issuer/abs_cells.csv` | yes |
| `results/m4_k1_issuer/decision.json` | yes |
| `results/m4_k1_issuer/rel_cells.csv` | yes |
| `results/m4_k1b_composition_ownership/decision.json` | yes |
| `results/m4_k1c_prime_author_share/decision.json` | yes |
| `results/m4_k1d_replicate_axis/cells.csv` | yes |
| `results/m4_k1d_replicate_axis/decision.json` | yes |
| `results/m4_k2d_frontier_carrier/decision.json` | yes |
| `results/m4_k2d_frontier_carrier/pair_differences.csv` | yes |
| `results/m4_k2e_double_matching/decision.json` | yes |
| `results/m4_k2e_double_matching/pair_differences.csv` | yes |
| `results/m4_k3_similarity_geometry/decision.json` | yes |
| `results/m4_kr1_deframing_repair/decision.json` | yes |
| `results/m4_kr1_deframing_repair/per_arm.csv` | yes |
| `results/m4_l1_typed_world/cells.csv` | yes |
| `results/m4_l1_typed_world/decision.json` | yes |
| `results/m4_l2_threshold_continuum/cells.csv` | yes |
| `results/m4_l2_threshold_continuum/decision.json` | yes |
| `results/m4_l3_taxometer_meter/cells.csv` | yes |
| `results/m4_l3_taxometer_meter/decision.json` | yes |

| D2 path template (slots → `[^/]+`) | files matched |
|---|---:|
| `m4_kr1_deframing_repair/cell_[^/]+_deframed_[^/]+.csv` | 24 |
| `m4_kr1_deframing_repair/cell_[^/]+_intact_[^/]+.csv` | 24 |

Non-`results/` reads by D2's harness — **covered by the git repository itself, not by the lockbox** (they are tracked files, so the manifest's committed-ness already binds them):

- `docs/SUICA_M4_F_PANEL_DESIGN_SYNTHESIS.md`

**G0X: PASS** — every file D2's harness reads under `results/` is in the lockbox, and every file in the 17 trees is readable and hashed.

---

## Part 3 — Archives

Written to `results_lockbox/` (mode 0600 each), **17** archives, **72,392,388** bytes total (42.9% of source). Compressor: **gzip** by D3-R2. Build wall: **11.1s**.

Per-archive build time (slowest first):

| tree | build s | archive bytes |
|---|---:|---:|
| `results/m4_k2c_matched_pairs` | 3.20 | 20,918,081 |
| `results/m4_k2e_double_matching` | 2.77 | 17,958,875 |
| `results/m4_k2d_frontier_carrier` | 2.76 | 17,977,119 |
| `results/m4_k2a_expressive_world` | 1.15 | 7,723,414 |
| `results/m4_k2b_t4_branch` | 0.80 | 5,247,966 |
| `results/m4_k3_similarity_geometry` | 0.34 | 1,819,499 |

---

## Part 4 — Determinism check (build twice, compare bytes)

Probe tree by D3-R7 (most files): **`results/m4_kr1_deframing_repair`**, 55 files.

| | value |
|---|---|
| build #1 archive SHA-256 | `ca73426aa7b54eda0ac6f3cba9b3b80f01e25a09b81279484c848c6ef5ace5fb` |
| build #2 archive SHA-256 | `ca73426aa7b54eda0ac6f3cba9b3b80f01e25a09b81279484c848c6ef5ace5fb` |
| archive hashes equal | **True** |
| full byte stream equal | **True** |
| inner tar hashes equal | **True** |
| verdict | **DETERMINISTIC** |

The two builds ran in the same process against the same filesystem, so this
check certifies that the *protocol* introduces no nondeterminism (no mtime, no
uid/gid, no source-mode leakage, no set-iteration order, no gzip timestamp).
It does not, and cannot, certify cross-zlib-version byte identity — which is
exactly why D3-R5 records the inner-tar hash separately.

A stronger check fell out of this leg for free: the harness was executed **twice
as separate processes** (once before and once after a cosmetic refinement to the
AST input-list filter, which touches no archive), and all 17 archive SHA-256s
were byte-identical across the two invocations. So determinism survives process
restart, not just loop iteration.

---

## Part 5 — G1X integrity (re-read, re-hash, extract, byte-compare)

Each archive was re-read **from disk** after writing, re-hashed against the
in-memory hash, decompressed and checked against the inner-tar hash, and one
sampled member (D3-R6: largest file) extracted and compared byte-for-byte with
the original on disk.

| tree | re-hash | inner tar | sample (largest file) | sample bytes | byte-identical | verdict |
|---|---|---|---|---:|---|---|
| `results/m4_k1_issuer` | OK | OK | `abs_probe_correct.npz` | 68,234 | yes | **PASS** |
| `results/m4_k1b_composition_ownership` | OK | OK | `arms_b.csv` | 38,480 | yes | **PASS** |
| `results/m4_k1c_ownership_live_knob` | OK | OK | `gates.json` | 27,418 | yes | **PASS** |
| `results/m4_k1c_prime_author_share` | OK | OK | `arms_b.csv` | 119,877 | yes | **PASS** |
| `results/m4_k1d_replicate_axis` | OK | OK | `gates.json` | 20,531 | yes | **PASS** |
| `results/m4_k2a_expressive_world` | OK | OK | `cell_phi0.5_occ32_intequal.csv` | 1,488,945 | yes | **PASS** |
| `results/m4_k2b_t4_branch` | OK | OK | `arm_C1_card.csv` | 1,706,572 | yes | **PASS** |
| `results/m4_k2c_matched_pairs` | OK | OK | `arm_A1anc_card_w016_031.csv` | 3,400,713 | yes | **PASS** |
| `results/m4_k2d_frontier_carrier` | OK | OK | `arm_SP56int_card_w016_031.csv` | 3,420,351 | yes | **PASS** |
| `results/m4_k2e_double_matching` | OK | OK | `arm_DM56a_card_w016_031.csv` | 3,403,393 | yes | **PASS** |
| `results/m4_k3_similarity_geometry` | OK | OK | `authors_phi0.9_occ8_intequal.csv` | 2,375,489 | yes | **PASS** |
| `results/m4_kr1_deframing_repair` | OK | OK | `gates.json` | 51,713 | yes | **PASS** |
| `results/m4_l1_typed_world` | OK | OK | `part0_pilot_cells.csv` | 42,444 | yes | **PASS** |
| `results/m4_l2_threshold_continuum` | OK | OK | `part0_pilot_cells.csv` | 92,400 | yes | **PASS** |
| `results/m4_l3_taxometer_meter` | OK | OK | `part0_pilot_cells.csv` | 99,881 | yes | **PASS** |
| `results/d1_sealed` | OK | OK | `D1_SEALED_BUNDLE.json` | 20,205 | yes | **PASS** |
| `results/d2_verification` | OK | OK | `C8_worksheet.json` | 4,214 | yes | **PASS** |

**G1X: 17/17 PASS.** Sampled bytes compared: 16,380,860. Wall: 0.3s.

Note on the opaque tree: `results/d1_sealed`'s sample was extracted and compared
as bytes with `==`. No part of it was decoded, parsed, or displayed.

---

## Part 6 — G2X purity (enforced, not asserted)

| check | result |
|---|---|
| `suica*` modules in `sys.modules` at entry | 0 |
| `suica*` modules in `sys.modules` at exit | 0 |
| numeric/RNG modules loaded (`numpy`/`pandas`/`scipy`/`random`) | none |
| worlds generated | 0 |
| panels built | 0 |
| RNG calls | 0 |
| files written under `suica_core/` | 0 |
| **G2X** | **PASS** |

The harness's entire import list is standard library. Not even `numpy` is
imported — there is no arithmetic here beyond byte counting and SHA-256.

---

## Part 7 — G3X verdict

### **LOCKBOX-COMPLETE**

No gaps. All 17 trees enumerated, every file readable and hashed, every D2
harness input covered, every archive re-read and re-hashed from disk, one
sampled member per tree extracted and byte-identical, the determinism probe
byte-equal across two independent builds, and the purity gate clean.

**gitignore verification** — `git check-ignore -v results_lockbox/`:

- returncode `0` → ignored: **True**
- rule: `.gitignore:3:results_lockbox/	results_lockbox/`

---

## Part 8 — OWNER ACTION: copy the archives off-machine

**The manifest is committed. The archives are not, and cannot be.**
`results_lockbox/` holds **17** files, **72,392,388** bytes
total, and is gitignored. A committed manifest whose archives no longer exist
proves only that the bytes were once hashed — it does not make anything
verifiable. This is the same standing as D1's sealed bundle.

Copy the whole directory to at least one location that is not this machine:

```bash
cd "$REPO"
tar -cf - results_lockbox | ssh <host> 'cat > suica_d3_lockbox.tar'   # or
rsync -av results_lockbox/ /Volumes/<external>/suica_d3_lockbox/       # or
cp -a results_lockbox /path/to/backup/
```

To verify a copy anywhere, with no SUICA code and no Python:

```bash
shasum -a 256 results_lockbox/*.tar.gz
# compare against docs/SUICA_D3_LOCKBOX_MANIFEST.json -> archives[].archive_sha256
```

To restore into a fresh clone and re-run D2's verification:

```bash
cd <fresh clone>
for a in results_lockbox/*.tar.gz; do tar -xzf "$a"; done   # restores results/…
python scripts/run_suica_d3_artifact_lockbox.py            # re-derives every hash
python scripts/run_suica_d2_adversarial_verification.py    # re-runs the audit
```

---

## Part 9 — Observations and anomalies (with timing)

Wall: Part 0 at 0.0s; enumeration+hashing 0.1s; archiving 11.1s; determinism probe 0.0s; G1X 0.3s; **total 11.5s** against a < 15 min target.

**No run-time anomalies.** No unreadable file, no symlink, no size drift, no
uncovered D2 input, no G1X failure, no determinism failure, no purity breach.

Four standing observations, none of which changes a verdict:

1. **The registration's arithmetic** (§0.1): "thirteen … plus two … the fifteen
   trees" undercounts its own named set, which is 15 + 2 = 17. Archived as the
   superset; recorded rather than silently corrected.
2. **`results_lockbox/` was not gitignored** when this leg began (`git check-ignore` returned 1). The rule `results_lockbox/` was added to
   `.gitignore` as part of this leg's single commit. Disclosed because it is a
   repository change the registration did not itemise — without it, ~168 MB of
   archives would have shown up as untracked and been commit-eligible.
3. **The manifest now carries an *unsalted* SHA-256 of `results/d1_sealed/D1_SEALED_BUNDLE.json`.** D1's public commitment is a
   *salted* hash, and the salt exists to stop an adversary from confirming a
   *guessed* plaintext. The registration binds this manifest to carry a per-file
   SHA-256 for every file in every in-scope tree, `d1_sealed` included, so the
   unsalted hash is published as instructed. The practical leak is nil — the
   bundle is a ~20 KB JSON document, not a short guessable string, so confirming
   a guess would require reconstructing it byte-for-byte including formatting —
   and the effect is a strictly *stronger* commitment. Flagged anyway, because
   it narrows a protection D1 deliberately bought.
4. **Source file modes are normalised away** (D3-R3). `results/d1_sealed/` is
   mode 0700 on this volume, not the 0600 D1's adjudication records; rather than
   propagate a filesystem quirk into the archive hashes, every member is written
   0600/0700, which both fixes determinism and keeps extraction owner-only. The
   same quirk applies to the archives themselves: they are written with
   `chmod 0600` and this volume reports them back as 0700 — the group/other bits
   are clear either way, which is the property that matters.

Independent cross-checks run outside this harness, for the record: BSD `tar -tzf`
lists the members of a written archive without error; `shasum -a 256` on three
archives reproduces the manifest's `archive_sha256` exactly; and
`tar -xzf results_lockbox/m4_l1_typed_world.tar.gz` into a scratch directory
followed by `diff -r` against `results/m4_l1_typed_world` reports no difference.
The lockbox is therefore readable by stock system tools, not only by this script.

---

*Harness: `scripts/run_suica_d3_artifact_lockbox.py`. Manifest: `docs/SUICA_D3_LOCKBOX_MANIFEST.json` (79,479 bytes, 363 file entries). Archives: `results_lockbox/` (gitignored, local).*
