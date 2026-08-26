---
name: hold-winners
description: |
  用户盈利持仓纠结"要不要止盈落袋、卖飞了怎么办、涨多了怕回吐"时使用。适用: 判断浮盈是否兑现、趋势是否终结、拿住盈利仓、移动止盈保护线。不适用: 浮亏止损(转 stop-loss-admission)、建仓节奏(转 right-side-entry-pyramid)、新主线选择(转 sector-rotation-detector)。
  关键触发词: "止盈"、"落袋为安"、"卖飞"、"要不要卖"、"涨多了"、"拿不住"、"回吐"、"take profit"、"sell too early"、"let profits run"。
source_book: 《股票大作手回忆录》 Edwin Lefèvre
source_chapter: 第5章 + 第10章 (part_02/part_04 chunk)
tags: [持有盈利, 让利润奔跑, 防卖飞, 移动止盈, 坐得住]
related_skills: [stop-loss-admission, trend-following-minimum-resistance, right-side-entry-pyramid]
---

# 拿住盈利：看对 + 拿住才赚大钱

## R — 原文 (Reading)

> "It never was my thinking that made the big money for me. It was always my sitting. Got that? My sitting tight! It is no trick at all to be right on the market. You always find lots of early bulls in bull markets and early bears in bear markets. ... Men who can both be right and sit tight are uncommon. I found it one of the hardest things to learn."
>
> — Edwin Lefèvre, 《股票大作手回忆录》第5章

---

## I — 方法论骨架 (Interpretation)

看对方向的人很多，看对又拿得住的人极少——大钱不是赚在进场时，而是赚在持有期。老火鸡 Partridge 的"这是我的位置"说明：位置 = 大趋势中的持仓资格，比眼前几个点的差价更值钱。离场依据是"趋势是否终结"，不是固定点数或短期回撤；止盈不追求卖顶（"Never try to sell at the top"），用分批兑现代替一把梭。恐惧让人拿不住：该盼的是利润变大，而不是害怕回吐。对基金：止盈 15-20% 是评估点不是机械卖点，先问趋势，趋势未破则持有，破位才走。

---

## A1 — 书中的应用 (Past Application)

### 案例 1: 老火鸡 Partridge（第5章）
- **问题**: 旁人劝他先止盈 Climax Motors、等回调再买回
- **方法论的使用**: 拒绝——"如果我卖了，我就失去了我的仓位（position）"
- **结论**: 大钱来自大趋势中的持仓，而非单个波动的差价
- **结果**: 作者自己牛市起点看对却频繁止盈，该赚 2 万只赚 2 千，从此立下"坐得住"原则

### 案例 2: "4 点利润"卖飞牛市（第5/10章）
- **问题**: 趋势仍在，因恐惧回吐急于兑现小利润
- **方法论的使用**: "Where I should have made twenty thousand dollars I made two thousand. … Fear keeps you from making as much money as you ought to."
- **结论**: 固定小点数止盈 = 把主升浪让给市场
- **结果**: 判断 100% 正确，盈利只有应得的一成；还养成追高买回的坏习惯

---

## A2 — 触发场景 (Future Trigger)

### 用户会在什么情境下需要这个 skill?

1. 盈利基金涨到止盈区间（15-20%），用户问"要不要落袋"
2. 盈利仓短期回撤，用户"拿不住"想跑
3. 用户卖飞过、想学会"怎么拿住盈利"的方法

### 语言信号 (用户的话里出现这些就应激活)

- "止盈" / "落袋为安" / "要不要卖" / "卖飞"
- "涨多了" / "拿不住" / "怕回吐" / "赚了 10% 要卖吗"
- "take profit" / "cash out" / "sell too early" / "let profits run"

### 与相邻 skill 的区分

- 与 `stop-loss-admission` 的区别: 对称姊妹纪律——盈利仓"拿"，亏损仓"砍"，判断先看盈亏方向
- 与 `right-side-entry-pyramid` 的区别: 本技能管"进场后怎么拿"，建仓技能管"拿之前怎么买"
- 与 `trend-following-minimum-resistance` 的区别: 趋势技能给"方向是否成立"的判定，本技能给"方向未破时如何持有"的纪律

---

## E — 可执行步骤 (Execution)

当 skill 被激活后，agent 应按以下步骤执行:

1. **分类持仓**
   - 把 8 只基金按盈亏分成盈利仓 / 亏损仓；盈利仓进入本流程，亏损仓转 `stop-loss-admission`
   - 完成标准: 分类清单，明确哪些持仓适用本技能

2. **判断趋势是否终结**
   - 用 `python D:\基金项目\market_scan.py` 看该板块相对强弱是否仍在前列、指数是否跌破关键均线/区间下沿
   - 完成标准: 明确"趋势持续 / 趋势终结 / 未明"三选一
   - 判停条件: 趋势终结 → 直接进入分批兑现，不讨论"再拿拿"

3. **设移动止盈保护线**
   - 从近期高点回撤 8-10%，或跌破区间下沿 → 执行第一批兑现（≤ 20%）
   - 完成标准: 保护线有具体数字与触发条件

4. **分批兑现**
   - 止盈 15-20% 区间分批评估兑现（每次 ≤ 20%），不追求卖顶
   - 执行: `python D:\基金项目\trade_journal.py add` 记录每批逻辑
   - 完成标准: 兑现批次、金额、理由完整可追溯
   - 风险提示: 趋势破位必须执行保护线；回吐 ≠ 错误，但破位不走就是死扛；免责声明

---

## B — 边界 (Boundary)

### 不要在以下情况使用此 skill

- 持仓已破位或基本面恶化 → 转 `stop-loss-admission`，不能死拿
- 单行业占比已超 40% → 先降集中度，而不是讨论"拿住"
- 用户有明确的现金需求（买房/教育）→ 兑现优先于趋势

### 作者在书中警告的失败模式

- x06 过早止盈: "But neither do you grow rich taking a four-point profit in a bull market."——小止盈卖飞大行情
- x01 的对称提醒: 该走不走（亏损仓）与不该走先走（盈利仓）是同一枚硬币的两面
- c03 追高买回: 卖飞后情绪化追回，成本更高、心态更差

### 作者的盲点 / 时代局限

- 作者没有固定止盈数学，"坐着不动"依赖个人意志；基金需要量化保护线
- 1920s 市场高波动、高杠杆；现代基金"坐着不动"遇到 2008 式长熊会回吐殆尽——保护线必须机械执行
- 半自传体叙事有幸存者偏差，不能证明"拿住"必然赚钱

### 容易混淆的邻近方法论

- "拿住" ≠ "死扛": 盈利仓可以拿，亏损仓不能扛
- "让利润奔跑" ≠ "永不止盈": 是分批兑现 + 移动保护线
- "止盈评估线" ≠ "机械卖点": 15-20% 是评估点，趋势破位才是执行点

---

## 相关 skills (阶段 3 填充)

- depends-on: `trend-following-minimum-resistance`（趋势是否终结的判定）
- contrasts-with: `stop-loss-admission`（让利润奔跑 vs 截断亏损）
- composes-with: `right-side-entry-pyramid`（右侧进场 → 持有 → 破位离场闭环）

---

## 审计信息

- **验证通过**: V1 ✓（Partridge/4点利润/1907空头巨仓多语境）/ V2 ✓（盈利15%要不要止盈）/ V3 ✓（"看对又拿住的人极少"差异化断言）
- **测试通过率**: 见 test-prompts.json
- **蒸馏时间**: 2026-08-08
- **蒸馏源**: 《股票大作手回忆录》r04 单元（f05/p03/p04/p11/x06/c03）
