# V6-W9 -- Format-aware windowing (PANDORA raw text, label-free)

Registered commit: e2b2240 (F12.10, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)

Candidates (body >= 1200 chars): 35181. Census strata: m_raw 2-3: n=32266, quote/list/code shares 0.0001/0.0147/0.0004; m_raw >= 4: n=72, 0.0000/0.0000/0.0000.

Cohort: RAW 69 texts / 342 windows; STRIPPED 69 texts / 342 windows (dropped below m>=4: 0, leak-tripped: 0). Anchors: cache-vs-W2a max rho1 diff 0.00e+00; rebuild-vs-cache max score diff 0.000e+00 (raw arm source: rebuild).

## Dynamics (axes + W2a saturation set)

| series | RAW rho1 | RAW p | RAW theta | STRIPPED rho1 | STRIPPED p | STRIPPED theta |
|---|---|---|---|---|---|---|
| gust1_E | -0.8563 | 0.0000 | 1.000 | -0.8564 | 0.0000 | 1.000 |
| gust1_P | -0.7434 | 0.4420 | 0.024 | -0.7435 | 0.4465 | 0.026 |
| wcl_36 | -0.9947 | 0.0000 | 1.000 | -0.9947 | 0.0000 | 1.000 |
| wcl_11 | -0.9755 | 0.0000 | 1.000 | -0.9754 | 0.0000 | 1.000 |
| wcl_02 | -0.8454 | 0.0010 | 1.000 | -0.8454 | 0.0000 | 1.000 |
| novelty_play_v2 | -0.9670 | 0.0000 | 1.000 | -0.9670 | 0.0000 | 1.000 |
| wcl_60 | -0.7211 | 0.6805 | 0.000 | -0.7211 | 0.6655 | 0.000 |
| wcl_35 | -0.8356 | 0.0020 | 1.000 | -0.8356 | 0.0015 | 1.000 |
| wcl_15 | -0.8300 | 0.0045 | 1.000 | -0.8300 | 0.0030 | 1.000 |

## Axis excess (rho1 - null_mean)

- gust1_E: raw -0.1194, stripped -0.1199 (|stripped| <= |raw|/2: no)
- gust1_P: raw -0.0065, stripped -0.0071 (|stripped| <= |raw|/2: no)

Saturations (theta >= 0.99, of 21): RAW 7 ['gust1_E', 'novelty_play_v2', 'wcl_36', 'wcl_11', 'wcl_02', 'wcl_35', 'wcl_15']; STRIPPED 7 ['gust1_E', 'novelty_play_v2', 'wcl_36', 'wcl_11', 'wcl_02', 'wcl_35', 'wcl_15'].

Null: 2000 iid-normal replicates per arm, m-composition matched; seed 20260712. RAW null shared with the cache anchor (same composition).
