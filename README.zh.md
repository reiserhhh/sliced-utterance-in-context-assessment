# Sliced Utterance In-Context Assessment (SUICA)

[English](README.md) | [日本語](README.ja.md) | **简体中文**

SUICA 是一个文本行为测量框架:它将一个人的自发书写视为许多小的行为观察
("切片话语",sliced utterances),在其自然发生的语境中进行测量,并由此
构建可审计、相对于参照群体的坐标——这是用于未来文本心理测量的理论与
工程基础，介于问卷法与自由反应评估之间，但不是已经完成的人格量表。

*Suica(スイカ)在日语中意为"西瓜":本方法核心的"瓜皮模型"主张,话题/
情境不是需要剥除的噪声,而是通过自我选择承载个人信号的"瓜皮"——本项目
首先证伪了这一主张的朴素形式(统计上的条件中心化会摧毁信号),随后将其
重建为设计原则(通过设计来控制语境;把选择本身作为一个通道来测量)。*

## 本版本包含的内容 (v0.2.0)

- **V7 技术核心** — 由观测算子与参照群体索引的相对文本几何、冻结 bundle、
  拒绝规则、多视图校准、不确定性协议和未来数据 gate。最高可支持声明是
  `OPERATOR_INDEXED_RELATIVE_TEXT_GEOMETRY_WITHIN_DECLARED_DOMAIN`，不是人格、
  信度、临床、跨语言普适性或市场预测声明。
- **方法** — `docs/THEORY.md`(瓜皮模型,三通道:choice / style /
  react)、`docs/RULEBOOK.md`(具约束力的实验设计规则,每条均可追溯到
  实测证据)、`docs/VALIDATION_PLAN.md`(P0-P5 证伪框架)。
- **完整算例** — `docs/WORKED_EXAMPLE_MANUAL.md`:在 PANDORA(Reddit)
  上完整、经审计地构建 19 构念电池 + 12 条选择轴,含开发层锚定性能
  (如 MBTI thinking-feeling ridge CV r = 0.346;Essays 大五迁移平均
  r ~ 0.144,来自 19 个可解释分数)及分数解读规则。
- **审计记录** — `docs/CLAIMS_LEDGER.md`:每条主张的状态、七轮对抗性
  审计、包括撤回。台账是权威记录;正文表述不得超出台账状态。
- **AI 操作标准** — `docs/AI_ANALYST_GUIDE.md`:角色分离(scorer /
  builder / coder / auditor / interpreter / human)、固定提示词、
  护栏 G1-G11(每条均可追溯到一次被实际捕获的失败)。
- **已封存的预注册** — `docs/PREREGISTRATION.md`:封印即本仓库的初始
  提交哈希。**开箱 #1 已于 2026-07-07 执行**(提交固定的脚本 + 对抗性
  预审计):预注册的成功规则**未通过**(BH-FDR q<.05 下 2/7,规则要求
  ≥4/7)——全部结果原样记录于 `reports/suica_lockbox_opening_1.md`。
  H2(第一人称使用 → 神经质,r=+0.111, q=.002)与 H6(政治/新闻选择轴 →
  开放性,r=+0.096, q=.006)在锁箱层级获得确认。剩余 1 次开箱;
  Essays 确认半的标签仍未接触。
- **代码** — `suica_core/` + `suica_sim/` + `scripts/` + `tests/`。
  无需受限语料即可验证 v0.2.0 技术锁箱。

## 快速开始(无需数据)

```bash
pip install -r requirements.txt
python -m pytest -q tests/test_suica.py          # 39 个通过
python -m pytest -q -p no:cacheprovider          # 发布审计: 301 个通过
python scripts/verify_suica_v020_lockbox.py       # 验证 v0.2.0 封印
python scripts/run_suica_synthetic_ground_truth_v2.py   # P0:估计器
python scripts/run_suica_p0b_thin_cell_regime_v3.py     # P0-B:薄单元
```

这些合成测试装置在不使用任何真实数据的情况下,以植入真值验证整个估计层。
要复现完整算例,请按 `docs/DATA_ACCESS.md` 获取数据集(本版本不包含任何
用户文本或用户 ID;SHA-256 清单可用于逐字节校验数据准备)。

## 证据状态的诚实总结

已在留出级(T3)确认:选择轴稳定性(5/5 轴,收缩 0.027)、15/15 个被发现
构念在未见用户上的确认、陌生人零假设下 2 个构念的 react 签名。已证伪并
退役:条件均值中心化(三种独立方式)、情感词频作为特质或场合状态的测量、
注意力权重作为测量证据。验证性(T4,开箱 #1,2026-07-07):预注册成功
规则未通过(2/7;全程记录,无再分析)——第一人称使用 → 神经质
(r=+0.111)与政治/新闻选择 → 开放性(r=+0.096)为两条获锁箱级确认的
关系;tension、novelty、directive、场所熵与游戏选择未获确认。剩余 1 次
开箱仍封存。适用范围:英语、单一平台 + 学生作文;对话与临床应用已完成
设计但未经检验(OPEN_PROBLEMS OP-7/8/14 — OP-7a 语域代理与 OP-8 第一
阶段已于 2026-07-07 关闭,见 CLAIMS_LEDGER)。

## V7.3 当前状态

v0.2.0 冻结 `V7_THEORETICAL_CORE_CLOSED_WITH_EMPIRICAL_GATES`。信度、MDD、
state-trait 分解、外部构念效度、临床用途、语言/文化不变性和市场预测仍未验证；
匿名坐标暂不命名为人格因子。详见 `docs/V7_LOCKBOX_V020.md` 与
`docs/RELEASE_NOTES_V020.md`。

## 来源

自私有开发仓库 `project persona` 的提交
`154822a`, `05be394`, `cad83d5`, `c27727b`, `1c417fa`, `8447541`,
`5189168`, `b9f65a6`, `0650936`, `5485a02`
(+ 记录于 `docs/FREEZE_NOTES.md` 的冻结提交)冻结而来。在指南所记录的
builder/auditor 协议下以 AI 辅助研究方式构建;七轮审计中有五轮捕获并
修正了真实的伪影——审计记录本身即是方法的一部分。
