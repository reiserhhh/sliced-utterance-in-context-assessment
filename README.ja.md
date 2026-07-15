# Sliced Utterance In-Context Assessment (SUICA)

[English](README.md) | **日本語** | [简体中文](README.zh.md)

SUICA はテキスト行動の測定フレームワークである。人の自発的な書き言葉を、
自然に生じた文脈の中で測定された多数の小さな行動観察(スライスされた発話 =
sliced utterances)として扱い、そこから解釈可能・凍結済み・監査可能な
参照集団相対の座標を構築する——質問紙法と自由反応式アセスメントの間に
将来の測定法を構築するための方法論的基盤であり、完成済み人格尺度ではない。

*名称の SUICA は日本語の「スイカ(西瓜)」に掛けている。本手法の中核である
「皮モデル」は、話題・状況をノイズとして除去するのではなく、自己選択を通じて
人物シグナルを運ぶ「皮」とみなす。本プロジェクトはまずこの主張の素朴な形を
自ら反証し(統計的な条件中心化はシグナルを破壊する)、その後に設計原理として
再構築した(文脈は設計で統制する。選択そのものを1つのチャネルとして測定する)。*

## このリリースに含まれるもの (v0.2.0)

- **V7 技術コア** — 観測演算子・参照集団で添字付けされた相対テキスト幾何、
  凍結バンドル、拒否規則、多視点較正、不確実性および将来データ・ゲート。
  最高位の主張は `OPERATOR_INDEXED_RELATIVE_TEXT_GEOMETRY_WITHIN_DECLARED_DOMAIN`。
  人格、信頼性、臨床、普遍言語、または市場予測の主張ではない。
- **手法** — `docs/THEORY.md`(皮モデル、3チャネル: choice / style /
  react)、`docs/RULEBOOK.md`(実験設計の拘束ルール。各ルールは実測された
  根拠に遡れる)、`docs/VALIDATION_PLAN.md`(P0-P5 反証フレームワーク)。
- **実施例** — `docs/WORKED_EXAMPLE_MANUAL.md`: PANDORA(Reddit)上での
  19構成概念バッテリー + 12選択軸の完全な監査済み構築記録。開発層アンカー
  性能(例: MBTI thinking-feeling ridge CV r = 0.346、Essays Big5 移送
  平均 r ~ 0.144 ——19個の解釈可能スコアから)とスコア解釈規則を含む。
- **監査記録** — `docs/CLAIMS_LEDGER.md`: 全主張のステータス、7回の
  敵対的監査ラウンド、撤回を含む。台帳が正式な記録であり、本文の記述は
  台帳ステータスを超えてはならない。
- **AI 運用標準** — `docs/AI_ANALYST_GUIDE.md`: 役割分離(scorer /
  builder / coder / auditor / interpreter / human)、固定プロンプト、
  ガードレール G1-G11(それぞれ実際に捕捉された失敗に遡れる)。
- **封印済み事前登録** — `docs/PREREGISTRATION.md`: 封印は本リポジトリの
  初期コミットハッシュ。**開封#1は 2026-07-07 に実行済み**(コミット固定
  スクリプト+敵対的事前監査): 事前登録の成功規則は**不合格**(BH-FDR
  q<.05 で 2/7、規則は ≥4/7 を要求)——全結果は
  `reports/suica_lockbox_opening_1.md` に無修正で記録。H2(一人称使用 →
  神経症傾向、r=+0.111, q=.002)と H6(政治/ニュース選択軸 → 開放性、
  r=+0.096, q=.006)はロックボックス級で確認された。残り開封 1 回。
  Essays 確認半分のラベルは依然未接触。
- **コード** — `suica_core/` + `suica_sim/` + `scripts/` + `tests/`。
  制限付きコーパスなしで v0.2.0 の技術ロックボックスを検証できる。

## クイックスタート(データ不要)

```bash
pip install -r requirements.txt
python -m pytest -q tests/test_suica.py          # 39件合格
python -m pytest -q -p no:cacheprovider          # リリース監査: 302件合格
python scripts/verify_suica_v020_lockbox.py       # v0.2.0 封印の検証
python scripts/run_suica_synthetic_ground_truth_v2.py   # P0: 推定機構
python scripts/run_suica_p0b_thin_cell_regime_v3.py     # P0-B: 薄セル
```

これらの合成ハーネスは、実データを一切使わずに、推定層全体を植え込み正解に
対して検証する。実施例を再現するには `docs/DATA_ACCESS.md` に従って
データセットを取得すること(本リリースはユーザーテキスト・ユーザーIDを
一切含まない。SHA-256 マニフェストによりバイト同一のデータ準備を検証できる)。

## 証拠状況の正直な要約

ホールドアウト級(T3)で確認済み: 選択軸の安定性(5/5 軸、縮小 0.027)、
発見された 15/15 構成概念の未見ユーザーでの確認、他人帰無の下での react
シグネチャ 2 構成概念。反証・撤退済み: 条件平均中心化(独立に3通り)、
感情語率の特性/機会状態測定としての使用、アテンション重みの測定証拠と
しての使用。確認的(T4、開封#1、2026-07-07): 事前登録の成功規則は
不合格(2/7。全記録・再分析なし)——一人称使用 → 神経症傾向(r=+0.111)
と政治/ニュース選択 → 開放性(r=+0.096)の 2 関係がロックボックス級で
確認され、tension・novelty・directive・venue entropy・gaming choice は
確認されなかった。開封は残り 1 回封印中。スコープ: 英語、
1プラットフォーム + 学生エッセイ。対話および臨床利用は設計済みだが
未検証(OPEN_PROBLEMS OP-7/8/14 — OP-7a レジスタ代理と OP-8 stage 1 は
2026-07-07 にクローズ、CLAIMS_LEDGER 参照)。

## V7.3 現在地

v0.2.0 は `V7_THEORETICAL_CORE_CLOSED_WITH_EMPIRICAL_GATES` を封印する。
信頼性、MDD、状態・特性分解、外的構成概念妥当性、臨床利用、言語・文化不変性、
市場予測は未検証であり、匿名座標に人格名は付与しない。詳細は
`docs/V7_LOCKBOX_V020.md` と `docs/RELEASE_NOTES_V020.md` を参照。

## 来歴

非公開開発リポジトリ `project persona` のコミット
`154822a`, `05be394`, `cad83d5`, `c27727b`, `1c417fa`, `8447541`,
`5189168`, `b9f65a6`, `0650936`, `5485a02`
(+ `docs/FREEZE_NOTES.md` に記録された凍結コミット)から凍結。
ガイドに記録された builder/auditor プロトコルの下で AI 支援研究として
構築され、7回の監査ラウンドのうち5回で実際のアーティファクトが捕捉・
修正された——監査記録そのものが手法の一部である。
