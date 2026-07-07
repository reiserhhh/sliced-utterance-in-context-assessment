# OP-8 stage 2 — DeepSeek blind back-check of JP lexicons

Overall blind match: 0.833; categories passing (>=0.80): 5/7

```json
{
  "self_focus": {
    "n": 12,
    "match_rate": 1.0,
    "pass": true
  },
  "second_person": {
    "n": 10,
    "match_rate": 1.0,
    "pass": true
  },
  "negative_affect": {
    "n": 19,
    "match_rate": 1.0,
    "pass": true
  },
  "conflict_threat": {
    "n": 13,
    "match_rate": 0.385,
    "pass": false
  },
  "uncertainty": {
    "n": 9,
    "match_rate": 1.0,
    "pass": true
  },
  "novelty_play": {
    "n": 15,
    "match_rate": 1.0,
    "pass": true
  },
  "directive": {
    "n": 6,
    "match_rate": 0.0,
    "pass": false
  }
}
```

## Mismatches (adjudication targets)

- conflict_threat: `問題` -> negative_affect (gloss: problem)
- conflict_threat: `失敗` -> negative_affect (gloss: failure)
- conflict_threat: `難しい` -> negative_affect (gloss: difficult)
- conflict_threat: `損失` -> negative_affect (gloss: loss)
- conflict_threat: `損` -> negative_affect (gloss: loss)
- conflict_threat: `困難` -> negative_affect (gloss: hardship)
- conflict_threat: `苦労` -> negative_affect (gloss: toil)
- conflict_threat: `トラブル` -> negative_affect (gloss: trouble)
- directive: `アドバイス` -> OTHER_none_of_these (gloss: advice)
- directive: `助言` -> OTHER_none_of_these (gloss: advice)
- directive: `推奨` -> OTHER_none_of_these (gloss: recommendation)
- directive: `オススメ` -> OTHER_none_of_these (gloss: recommendation)
- directive: `おすすめ` -> OTHER_none_of_these (gloss: recommendation)
- directive: `お勧め` -> OTHER_none_of_these (gloss: recommendation)
