# Sliced Utterance In-Context Assessment (SUICA)

[English](README.md) | [日本語](README.ja.md) | **简体中文**

SUICA 是一个文本行为测量框架:它将一个人的自发书写视为许多小的行为观察
("切片话语",sliced utterances),在其自然发生的语境中进行测量,并由此
构建可解释、已冻结、可审计的分数——一种介于问卷法与自由反应评估之间的
量表构建方法。

*Suica(スイカ)在日语中意为"西瓜":本方法核心的"瓜皮模型"主张,话题/
情境不是需要剥除的噪声,而是通过自我选择承载个人信号的"瓜皮"——本项目
首先证伪了这一主张的朴素形式(统计上的条件中心化会摧毁信号),随后将其
重建为设计原则(通过设计来控制语境;把选择本身作为一个通道来测量)。*

## 本版本包含的内容 (v0.1.0-prereg-sealed)

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
- **已封存的预注册** — `docs/PREREGISTRATION.md`:外部效度确认
  (锁箱:PANDORA Big5 + MBTI bridge + Essays 确认半)未开封
  (预算 2/2)。本仓库的初始提交哈希即为封印。任何拥有数据访问权的人
  都可以在冻结规则下恰好执行一次开箱。
- **代码** — `suica_core/` + `scripts/`(完整验证流水线)+ `tests/`
  (39 个测试,无需数据)。

## 快速开始(无需数据)

```bash
pip install -r requirements.txt
python -m pytest -q tests/test_suica.py          # 39 个通过
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
注意力权重作为测量证据。已封存:全部验证性外部效度(见 PREREGISTRATION)。
适用范围:英语、单一平台 + 学生作文;对话与临床应用已完成设计但未经检验
(OPEN_PROBLEMS OP-7/8/14)。

## 来源

自私有开发仓库 `project persona` 的提交
`154822a`, `05be394`, `cad83d5`, `c27727b`, `1c417fa`, `8447541`,
`5189168`, `b9f65a6`, `0650936`, `5485a02`
(+ 记录于 `docs/FREEZE_NOTES.md` 的冻结提交)冻结而来。在指南所记录的
builder/auditor 协议下以 AI 辅助研究方式构建;七轮审计中有五轮捕获并
修正了真实的伪影——审计记录本身即是方法的一部分。
