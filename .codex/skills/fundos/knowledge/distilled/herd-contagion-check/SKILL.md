---
name: herd-contagion-check
description: |
  用户开始用"大家都在买/别人都赚钱/大V推荐"解释买入决策，或复盘时怀疑自己跟风时使用。执行社会证明失效检查：理由是否依赖他人行动作证据；若是则强制暂停新增，回到独立可验证的基本面证据与事前清单。不适用于：有明确独立依据的正常决策复盘、纯理论讨论。关键触发词："大家都说好"、"跟大V买的"、"看别人赚了"、"我是不是被割"、"我这次很理性"。
source_book: 《非同寻常的大众幻想与群众性癫狂》(Memoirs of Extraordinary Popular Delusions and the Madness of Crowds) — Charles Mackay, 1841/1852
source_chapter: 密西西比计划（MONEY MANIA）/ 南海泡沫（THE SOUTH-SEA BUBBLE 总结段）
tags: [从众传染, 社会证明失效, 行为偏差, 事前清单, 自我欺骗]
related_skills: [mass-participation-top, mania-cycle-map, narrative-news-check]
---

# 从众传染检查器

## R — 原文 (Reading)

> "The success of one project generally produces others of a similar kind. Popular
> imitativeness will always, in a trading nation, seize hold of such successes, and
> drag a community too anxious for profits into an abyss from which extrication is
> difficult."
>
> — Charles Mackay, 南海泡沫总结段（THE SOUTH-SEA BUBBLE），chunks/sub_03.txt（阶段1已验证）

> "Two sober, quiet, and philosophic men of letters, M. de la Motte and the Abbé
> Terrason, congratulated each other, that they, at least, were free from this strange
> infatuation. A few days afterwards... they agreed that a man ought never to swear
> against his doing any one thing, and that there was no sort of extravagance of which
> even a wise man was not capable."
>
> — Charles Mackay, 密西西比计划（MONEY MANIA），chunks/sub_01.txt（阶段1已验证）

---

## I — 方法论骨架 (Interpretation)

作者明确指出大众的**模仿性（imitativeness）**：一个项目的成功必然催生同类项目，群体在逐利焦虑中被拖入难以脱身的深渊。传染路径是"看到别人赚钱→放弃自己的判断→跟进"——这不是信息学习，而是**社会证明失效**：人们模仿的是他人的行动本身，而不是行动背后的逻辑。

最讽刺的证据是两位自认清醒的文人拉莫特与神父泰拉松：他们互相打赌"绝不会陷入这种狂热"，几天后却在交易所里撞见对方正在买密西西比股票。结论：**任何人不该发誓"我绝不会做某件蠢事"，智力、专业、经验都不能免疫从众**。

对基金的意义：把"我很理性、不会被割"当作最危险的假设；用事前写下的买入/卖出清单替代狂热中的临场判断，因为现场的你不再是冷静的你。

---

## A1 — 书中的应用 (Past Application)

### 案例 1: 两位哲学家的"真香"时刻
- **问题**: 拉莫特与泰拉松互相保证自己绝不会碰密西西比股票。
- **方法论的使用**: 检验"我例外"假设——用事后证据（两人都在交易所买入）证伪个体理性免疫。
- **结论**: 从众不是愚蠢者的专利，聪明人同样会被传染。
- **结果**: 两人从此闭口不谈此事；作者借此点破"智者亦随众"的普遍性。

### 案例 2: 南海"气泡公司"的模仿传染（1720）
- **问题**: 一家公司成功后，上百家仿效"气泡公司"遍地开花。
- **方法论的使用**: 用模仿性框架解释——成功催生同类项目，大众不再验证每个项目的基本面。
- **结论**: 传染靠的是"别人在做"，而不是"项目本身成立"。
- **结果**: 枢密院下令解散全部气泡公司，成了戳破南海泡沫的导火索之一；跟风者集体巨亏。

---

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 用户承认买入理由是"别人都在买/大V晒收益/邻居赚钱了"；
2. 复盘时用户怀疑自己当时是不是被从众传染；
3. 用户即将跟风下单前，需要一次"社会证明失效"检查。

### 语言信号（用户的话里出现这些就应激活）

- "大家都说好" / "跟着大V买的" / "看别人赚了钱"
- "我是不是被当韭菜了" / "我这次很理性，不会冲动"
- "别人都在加仓，我也加了"

### 与相邻 skill 的区分

- 与 `mass-participation-top` 的区别: 本 skill 检查"我个人有没有被传染"；全民参与检查"社会整体参与度是否过热"；
- 与 `mania-cycle-map` 的区别: 周期定位判断市场处于哪一段；本 skill 判断"我的决策是否独立"；
- 与 `narrative-news-check` 的区别: 新闻检查验证消息真假；本 skill 检查"我是否在用别人的行动代替证据"。

---

## E — 可执行步骤 (Execution)

当 skill 被激活后，按以下步骤执行：

1. **重放决策理由**
   - 列出当初买入的 3 条理由，逐条标注来源：独立分析 / 他人行动 / 情绪冲动
   - 完成标准: 输出理由清单与来源标签

2. **社会证明失效测试**
   - 问：去掉"别人在做/大家都在买"这条理由后，剩下的证据能否独立支持买入？
   - 判停条件: 若剩余证据为零 → 判定为从众买入，进入第 3 步强制处理

3. **强制暂停新增**
   - 执行: 暂停一切新买入/追加（至少 24 小时冷静期），恢复独立可验证的基本面、估值、资金流数据
   - 完成标准: 输出"暂停新增"结论与恢复条件（证据清单补齐）

4. **事前清单重审**
   - 对照已持仓（如科技智选 -0.71%、全球成长 -19.15%）：现在是否愿意按清单条款持有/止损
   - 完成标准: 给出持有/减仓/止损的明确动作与仓位上限（单基金 ≤15–20%、-15% 止损）

5. **记录**
   - 将"理由来源→是否从众→动作"写入 `trade_journal.py add`，为下次决策留档

---

## B — 边界 (Boundary) ★

### 不要使用此 skill 的场景

- 用户有明确独立依据（订单、估值、政策）的正常决策复盘 → 不需要从众检查；
- 纯心理学理论讨论、无实际决策 → 不执行仓位动作；
- 纯净值查询 → 用 `fundos-core`。

### 作者在书中警告的失败模式

- "我比其他人清醒/我例外"是最危险的假设——智者亦随众（反例 x01）；
- 模仿他人行动而不是逻辑，会让整个社区被拖入难以脱身的深淵；
- 当"大家都在买"成为决策理由时，个体理性已经失效。

### 作者的盲点 / 时代局限

- 作者假设群体永远错、少数清醒者永远对；实际泡沫中离场过早（踏空）同样损失巨大；
- "逆向=正确"的过度修正同样是从众的变体——反对大众本身也可能是一种社会证明依赖；
- 19 世纪无行为金融学的实验证据，机制描述基于历史叙述。

### 容易混淆的邻近方法论

- "从众" ≠ "跟随有效信息"：如果他人行动背后有可验证的基本面证据，复制它是理性学习；
- "暂停交易" ≠ "永远不买"：从众检查是暂停新增，不是看空结论。

---

## 相关 skills

- depends-on: fundos-core（持仓与阈值）、trade_journal.py（决策留档）
- contrasts-with: mass-participation-top（个人从众 vs 社会破圈）
- composes-with: narrative-news-check（用独立证据替代他人行动）、mania-cycle-map（确认市场所处阶段）

---

## 审计信息

- **验证通过**: V1 ✓ 跨域同构（哲学家案例+南海模仿潮+1825/1845 复制）；V2 ✓ 可预测性（社会证明失效测试→暂停新增动作）；V3 ✓ 排他性（只查个人决策独立性，不做市场方向判断）
- **测试通过率**: 待执行（详见 test-prompts.json）
- **蒸馏时间**: 2026-08-08
- **蒸馏源**: 《EPD》阶段1候选 f03/f08/p05 + 反例 x01
