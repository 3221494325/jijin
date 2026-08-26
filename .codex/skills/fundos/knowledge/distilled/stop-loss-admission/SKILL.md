---
name: stop-loss-admission
description: |
  用户持仓浮亏、纠结"要不要割肉/等回本/再观察"时使用。适用: 单基金亏损达-15%评估线、买入逻辑被证伪、想"等反弹再走"的拖延心理。不适用: 盈利仓位要不要止盈(转 hold-winners)、建仓节奏(转 right-side-entry-pyramid)、纯情绪倾诉。
  关键触发词: "止损"、"割肉"、"等回本"、"被套"、"要不要卖"、"再等等"、"反弹就卖"、"浮亏"、"stop loss"、"cut loss"、"wait for breakeven"。
source_book: 《股票大作手回忆录》 Edwin Lefèvre
source_chapter: 第12章 + 第9章 (part_04/part_03 chunk)
tags: [止损, 认错, 截断亏损, 机械执行, 防拖延]
related_skills: [hold-winners, right-side-entry-pyramid, timely-correction]
---

# 止损即认错：亏损不是错误，不认错才是

## R — 原文 (Reading)

> "Losing money is the least of my troubles. A loss never bothers me after I take it. I forget it overnight. But being wrong--not taking the loss--that is what does the damage to the pocketbook and to the soul. ... 'I am carrying so much cotton that I can't sleep thinking about it. It is wearing me out. What can I do?' 'Sell down to the sleeping point,' answered the friend."
>
> — Edwin Lefèvre, 《股票大作手回忆录》第12章

---

## I — 方法论骨架 (Interpretation)

把"亏损"与"犯错"分开：已实现的亏损是过去的信息，执行后立即翻篇；真正的伤害来自"错了却不肯认、不肯执行离场"。止损是用规则对抗希望——"希望"让人把每一天都当成最后一天，把小亏拖成大亏。配套操作意象是"卖到能睡着的仓位规模"。回本数学是硬约束：亏 10% 需涨 11.1%，亏 20% 需涨 25%，亏 30% 需涨 42.9%。对基金：预先设定单基金止损评估线（-15%），达到条件机械评估执行，与"想不想认"解耦，事后不报复性交易。

---

## A1 — 书中的应用 (Past Application)

### 案例 1: 5 万包棉花，小亏拖成 25 万美元（第17章）
- **问题**: 棉花浮亏时总对自己说"等反弹再走"，反弹永远不够深、价格不断新高
- **方法论的使用**: 拖延止损、被盈利仓位分散注意力——"the price would rally again, and go higher than ever"
- **结论**: 止损不能依赖"等个好价"，规则必须无条件执行
- **结果**: 浮亏滚到 25 万美元才认亏，典型小亏拖成大亏

### 案例 2: Anaconda "想走就走"（第9章）
- **问题**: 判断错误后犹豫于离场方式与价格
- **方法论的使用**: "When you want to get out, get out"——离场不与价格讨价还价
- **结论**: 认错 = 停止错误，不纠结于卖出价格
- **结果**: 保住本金，留出后手

---

## A2 — 触发场景 (Future Trigger)

### 用户会在什么情境下需要这个 skill?

1. 单基金浮亏达到或逼近 -15% 评估线，用户问"割不割"
2. 用户说"再等等，说不定下周就反弹回本"（hope 拖延信号）
3. 用户为浮亏焦虑，需要"卖到能睡着"的仓位决策

### 语言信号 (用户的话里出现这些就应激活)

- "止损" / "割肉" / "要不要卖" / "被套"
- "等回本" / "再等等" / "反弹就卖" / "舍不得" / "浮亏"
- "stop loss" / "cut my losses" / "wait for breakeven" / "hoping for a rebound"

### 与相邻 skill 的区分

- 与 `hold-winners` 的区别: 姊妹纪律——亏损仓用本技能截断，盈利仓用持有技能奔跑，不可混用
- 与 `right-side-entry-pyramid` 的区别: 止损是首仓浮亏时的出口；本技能判定去留，建仓技能管右侧再进场
- 与 `timely-correction` 的区别: 后者管"买入逻辑被证伪"的止损，本技能管"达到阈值 + 心理拖延"的机械执行

---

## E — 可执行步骤 (Execution)

当 skill 被激活后，agent 应按以下步骤执行:

1. **盘点亏损持仓**
   - 逐只计算 8 只基金的当前盈亏%，对照 -15% 评估线
   - 完成标准: 输出亏损持仓清单：代码、名称、亏损%、距离评估线

2. **已达线 → 机械评估**
   - 用 `python D:\基金项目\deep_news.py` + market_scan.py 核查初始买入逻辑是否仍成立
   - 逻辑证伪或亏损 > -20% 硬线 → 分批离场（每次 ≤ 20%，分 2-3 批，不赌反弹）
   - 判停条件: 逻辑仍成立且未达硬线 → 转步骤 3 观察，不割在情绪低点
   - 完成标准: 每个已达线持仓给出"离场 / 观察"二选一及理由

3. **未达线 → 设观察位**
   - 记录"跌破哪个位/哪个条件就执行止损"，写入 manual_updates.json
   - 完成标准: 有明确的预先触发条件，而非"看情况"

4. **执行后翻篇**
   - 止损后不报复性交易；用 `python D:\基金项目\trade_journal.py add` 记录复盘
   - 完成标准: 操作记录完整，明确下一步按 `right-side-entry-pyramid` 右侧重建
   - 风险提示: 回本数学 + 免责声明

---

## B — 边界 (Boundary)

### 不要在以下情况使用此 skill

- 持仓是盈利的 → 转 `hold-winners`
- 系统性恐慌日流动性枯竭时（参考 1907 恐慌），不要在最低点恐慌性割肉；基金无杠杆，可分批执行
- 用户没有持仓、纯理论讨论止损 → 不调用

### 作者在书中警告的失败模式

- x01 hope 心理: "dreading the pain of a small loss at the beginning, were now about to suffer total amputation--without anaesthetics"——小亏拖成总截肢
- x10 频繁进出: 止损纪律被乱砍代替，变成小胜多次、大亏一次
- c10 注意力分散: 因盈利仓位"太忙"而拖延处理亏损仓

### 作者的盲点 / 时代局限

- 作者的"止损"是主观判断"我错了"，没有固定百分比；基金需要预先量化
- 基金申赎有确认延迟，无法像股票一样"想走就走"，止损要提前分批
- 1923 年的经验不能直接迁移到现代基金定投/长线持有场景

### 容易混淆的邻近方法论

- "止损" ≠ "割在地板上": 分批 + 规则，而非恐慌单笔
- "认错" ≠ "否定自己": 认错是动作，不是人格评价
- "等回本"是希望不是计划: 回本数学决定了拖延的成本

---

## 相关 skills (阶段 3 填充)

- depends-on: fundos_core（组合诊断）、deep_news.py / market_scan.py（逻辑核查）
- contrasts-with: `hold-winners`（截断亏损 vs 让利润奔跑，对称姊妹纪律）
- composes-with: `right-side-entry-pyramid`（止损后按右侧纪律重建仓位）

---

## 审计信息

- **验证通过**: V1 ✓（棉花/Anaconda/1907 恐慌多语境）/ V2 ✓（浮亏10%要不要等回本）/ V3 ✓（"亏损不是错误，不认错才是"）
- **测试通过率**: 见 test-prompts.json
- **蒸馏时间**: 2026-08-08
- **蒸馏源**: 《股票大作手回忆录》r03 单元（f04/p05/x01/x10/c10）
