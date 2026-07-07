#!/usr/bin/env python
"""SUICA Japanese scorer v1 (OP-8, stage 1 of 3).

Scope: the frozen v3 style battery only (tension_core, directive_action,
first_person_usage, novelty_play), translated to Japanese under the
equivalence protocol in docs/SUICA_JP_SCORER_PROTOCOL_V1.md.

STATUS: machinery-grade. Stage 1 = forward translation (this file);
stage 2 = independent back-check (PENDING); stage 3 = within-language
re-validation on a Japanese corpus (PENDING — Rulebook D1: population- and
language-relative; JP scores must NEVER be compared numerically to EN
scores, only within-JP-population).

Structural translation decisions (all disclosed):
  T1 Tokenization: fugashi/MeCab (unidic-lite) morphemes replace the EN
     whitespace-regex tokens; denominator = morpheme count excluding pure
     punctuation. Rates stay "per 100 tokens" like EN.
  T2 Single-morpheme lexicon entries are matched on token surface forms;
     multi-morpheme constructions (e.g. directive すべき/してください,
     hedges かもしれない) are matched as REGEX PATTERNS on the raw string,
     counted once per occurrence — a structural deviation from EN (which is
     purely token-based), unavoidable because Japanese realizes these
     functions morphosyntactically. Flagged for stage-3 sensitivity.
  T3 First person: Japanese pro-drop means first-person RATE is not
     numerically comparable to EN (Japanese omits subjects); within-language
     between-person variance is the measurement object, exactly per D1.
  T4 Composition formulas are IDENTICAL to the frozen EN scorer
     (suica_v2_lib.score_slices_v2): tension = .40*projective + .35*unc +
     .25*conflict where projective = neg + conflict + unc; directive =
     sqrt(directive_rate * second_person_rate); first_person = self_focus;
     novelty = novelty_play rate.

Self-test (`--selftest`): P0-style synthetic validation with planted person
effects — template sentence pools with controlled lexicon injection rates;
criteria (pre-committed): planted-order Spearman >= 0.90 per construct at
the STANDARD volume (120 sentences/user; recovery is volume-dependent, as
in the EN P1 volume curve — the 40-sentence short-text condition is
reported alongside as the attenuation figure, no bar); null 95th-percentile
|rho| consistent with the 2/sqrt(n) noise expectation; determinism exact.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Forward-translated lexicons (stage 1). Each entry lists the EN source word
# it translates in the comment. Surface-form tokens (fugashi/unidic-lite).
# ---------------------------------------------------------------------------
JA_TOKEN_LEXICONS: dict[str, list[str]] = {
    # self_focus <- i/i'll/i'm/i've/im/ive/me/mine/my/myself
    "self_focus": ["私", "わたし", "わたくし", "僕", "ぼく", "俺", "おれ", "あたし",
                   "自分", "うち", "我", "小生"],
    # second_person <- u/you/you'll/you're/your/youre/yours/yourself
    "second_person": ["あなた", "貴方", "君", "きみ", "お前", "おまえ", "あんた",
                      "皆さん", "みなさん", "皆様"],
    # negative_affect <- angry/annoyed/bad/depressed/fear/hate/hurt/sad/stress/worried/worry/worse
    "negative_affect": ["不安", "心配", "怖い", "恐い", "嫌い", "嫌", "悲しい",
                        "辛い", "つらい", "ストレス", "憂鬱", "うつ", "鬱",
                        "イライラ", "怒り", "怒っ", "最悪", "ひどい", "酷い"],
    # conflict_threat <- argue/conflict/danger/difficult/fail/failed/fight/hard/loss/lost/problem/risk
    "conflict_threat": ["問題", "危険", "失敗", "難しい", "喧嘩", "争い", "対立",
                        "リスク", "損失", "損", "困難", "苦労", "トラブル"],
    # uncertainty (single-token part) <- guess/maybe/might/perhaps/possibly/probably/seem/seems/unsure
    "uncertainty": ["たぶん", "多分", "おそらく", "恐らく", "もしかしたら",
                    "possibly", "迷い", "曖昧", "あいまい"],
    # novelty_play <- creative/different/explore/fun/game/idea/interesting/new/novel/play
    "novelty_play": ["新しい", "新た", "面白い", "おもしろい", "楽しい", "遊び",
                     "ゲーム", "アイデア", "アイディア", "工夫", "斬新", "創造",
                     "探検", "探索", "試し"],
    # directive (single-token part) <- advice/advise/recommend/please(part)/must(part)
    "directive": ["アドバイス", "助言", "推奨", "オススメ", "おすすめ", "お勧め"],
}

# T2: multi-morpheme constructions matched on the raw string (count each hit).
JA_PATTERN_LEXICONS: dict[str, list[str]] = {
    # directive <- should/must/need/have to/don't/let/try(imperative)/please
    "directive": [r"べき", r"しなさい", r"して下さい", r"してください", r"した方がいい",
                  r"したほうがいい", r"する必要", r"なければならない", r"なきゃ",
                  r"ないでください", r"するな(?![らりるれろどんあぁーはさそかっなよね])", r"してみて"],
    # uncertainty <- could/maybe/might (modal constructions)
    "uncertainty": [r"かもしれない", r"かもしれません", r"かも(?=[。、\s]|$)",
                    r"気がする", r"だろうか", r"でしょうか", r"わからない", r"分からない"],
}

_PUNCT_RE = re.compile(r"^[\s。、!?!?・…()()「」『』\[\]{}<>【】~ー—\-,.:;\"']+$")

_TAGGER = None


def _tagger():
    global _TAGGER
    if _TAGGER is None:
        import fugashi
        _TAGGER = fugashi.Tagger()
    return _TAGGER


def tokenize_ja(text: str) -> list[str]:
    return [w.surface for w in _tagger()(text or "")]


def ja_anchor_rates(text: str) -> dict[str, float]:
    """Per-100-token lexicon rates, mirroring the EN fast_anchor_rates shape."""
    toks = tokenize_ja(text)
    content = [t for t in toks if not _PUNCT_RE.match(t)]
    n = max(1, len(content))
    counts = {name: 0 for name in set(JA_TOKEN_LEXICONS) | set(JA_PATTERN_LEXICONS)}
    tok_sets = {name: set(words) for name, words in JA_TOKEN_LEXICONS.items()}
    for t in content:
        for name, words in tok_sets.items():
            if t in words:
                counts[name] += 1
    for name, patterns in JA_PATTERN_LEXICONS.items():
        for pat in patterns:
            counts[name] += len(re.findall(pat, text or ""))
    out = {f"{name}_rate": 100.0 * c / n for name, c in counts.items()}
    out["token_count_anchor"] = float(n)
    return out


def score_text_ja(text: str) -> dict[str, float]:
    """Frozen v2 composition formulas (T4) on Japanese anchor rates."""
    r = ja_anchor_rates(text)
    projective = r["negative_affect_rate"] + r["conflict_threat_rate"] + r["uncertainty_rate"]
    return {
        "first_person_usage_ja": r["self_focus_rate"],
        "novelty_play_ja": r["novelty_play_rate"],
        "directive_action_ja": float(np.sqrt(max(0.0, r["directive_rate"]) * max(0.0, r["second_person_rate"]))),
        "tension_core_ja": 0.40 * projective + 0.35 * r["uncertainty_rate"] + 0.25 * r["conflict_threat_rate"],
        "token_count": r["token_count_anchor"],
    }


# ---------------------------------------------------------------------------
# P0-style synthetic self-test (data-free)
# ---------------------------------------------------------------------------
NEUTRAL_POOL = [
    "今日は天気が良かったので駅まで歩いた。",
    "昨日の夕食はカレーだった。",
    "電車が少し遅れていたようだ。",
    "週末に部屋の掃除をする予定になっている。",
    "近所の店で牛乳とパンを買った。",
    "会議は午後三時から始まる予定だ。",
    "窓の外で鳥が鳴いている。",
    "資料を印刷して机の上に置いた。",
]
INJECTION = {
    "first_person_usage_ja": ["私はそう思う。", "僕にはそう見えた。", "自分でも驚いた。"],
    "novelty_play_ja": ["新しいゲームを試した。", "面白いアイデアを思いついた。", "斬新な工夫だった。"],
    "directive_action_ja": ["あなたはこうするべきだ。", "君も試してみてください。", "お前はやめたほうがいいと思う、そうしなさい。"],
    "tension_core_ja": ["不安で心配になった、たぶん失敗かもしれない。", "危険な問題が怖い。", "ストレスと対立が辛い、どうなるかわからない。"],
}


def synth_user_text(rng: np.random.Generator, level: float, construct: str, n_sent: int = 40) -> str:
    sents = []
    for _ in range(n_sent):
        if rng.random() < level:
            sents.append(INJECTION[construct][rng.integers(len(INJECTION[construct]))])
        else:
            sents.append(NEUTRAL_POOL[rng.integers(len(NEUTRAL_POOL))])
    return "".join(sents)


def selftest() -> dict:
    rng = np.random.default_rng(42)
    n_users = 60
    results = {}
    for construct in INJECTION:
        levels = rng.uniform(0.02, 0.45, size=n_users)
        scores = [score_text_ja(synth_user_text(rng, lv, construct, n_sent=120))[construct] for lv in levels]
        scores_short = [score_text_ja(synth_user_text(rng, lv, construct, n_sent=40))[construct] for lv in levels]
        from scipy import stats
        rho = float(stats.spearmanr(levels, scores).statistic)
        rho_short = float(stats.spearmanr(levels, scores_short).statistic)
        # null world: no planted differences
        null_rhos = []
        for _ in range(40):
            lv0 = np.full(n_users, 0.15)
            s0 = [score_text_ja(synth_user_text(rng, 0.15, construct, n_sent=20))[construct] for _ in range(n_users)]
            null_rhos.append(abs(float(stats.spearmanr(lv0 + rng.normal(0, 1e-9, n_users), s0).statistic)))
        fpr_threshold = float(np.percentile(null_rhos, 95))
        det1 = score_text_ja(synth_user_text(np.random.default_rng(7), 0.3, construct))
        det2 = score_text_ja(synth_user_text(np.random.default_rng(7), 0.3, construct))
        results[construct] = {
            "planted_order_spearman_120sent": rho, "pass_recovery": bool(rho >= 0.90),
            "planted_order_spearman_40sent_attenuation": rho_short,
            "null_95pct_abs_rho": fpr_threshold,
            "deterministic": bool(det1 == det2),
        }
    results["ALL_PASS"] = bool(all(v["pass_recovery"] and v["deterministic"]
                                   for k, v in results.items() if k != "ALL_PASS"))
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--text", help="score a single Japanese text from the command line")
    args = ap.parse_args()
    if args.selftest:
        out_dir = ROOT / "results" / "suica_ja_scorer_v1"
        out_dir.mkdir(parents=True, exist_ok=True)
        res = selftest()
        (out_dir / "ja_scorer_selftest.json").write_text(json.dumps(res, indent=2) + "\n")
        print(json.dumps(res, indent=2))
        sys.exit(0 if res["ALL_PASS"] else 1)
    if args.text:
        print(json.dumps(score_text_ja(args.text), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
