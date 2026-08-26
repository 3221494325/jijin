---
name: position-size-framework
description: |
  用户在纠结"买多少 / 算不算分散 / 单只上限 / 要不要集中 / 亏损加仓摊薄"时调用；先定位认知水平（know-nothing 走低费率宽基指数+定投，know-something 在能力圈内集中），再检查伪分散与板块集中度，并对照 FundOS 纪律线。不适用于：单只要不要卖（转 hold-three-conditions / timely-correction）、杠杆或衍生品产品选择（转 do-not-list）。关键 trigger："买多少""算分散吗""单只上限""加仓摊薄""仓位太重""how much to buy""diversify"。
source_book: 《巴菲特致股东信》沃伦·巴菲特（Berkshire Hathaway Shareholder Letters 1977–2024）
source_chapter: 1993 年致股东信（另见 2005/2016/2022）
tags: [仓位管理, 分散与集中, position-sizing, diversification, 指数基金]
related_skills: [hold-three-conditions, do-not-list, timely-correction]
---

# 仓位框架：分散还是集中，取决于你知道多少

## R — 原文（Reading）

> "By periodically investing in an index fund, for example, the know-nothing investor can actually out-perform most investment professionals. Paradoxically, when "dumb" money acknowledges its limitations, it ceases to be dumb. On the other hand, if you are a know-something investor, able to understand business economics and to find five to ten sensibly-priced companies that possess important long-term competitive advantages, conventional diversification makes no sense for you. It is apt simply to hurt your results and increase your risk."
>
> —— Warren Buffett, 1993 年致股东信（candidates/f10；p09/p10 同信佐证）

自译：例如，通过定期投资指数基金，一无所知的投资者反而能跑赢大多数投资专业人士。吊诡的是，当"笨钱"承认自己的局限时，它就不再笨了。另一方面，如果你是"懂行"的投资者，能够理解商业经济、找到 5–10 家价格合理且具长期竞争优势的公司，那么传统的分散化对你毫无意义——它只会损害你的业绩、增加你的风险。

---

## I — 方法论重构（Interpretation）

仓位结构不是"分散教条"的函数，而是"认知水平"的函数。先回答"我是 know-nothing 还是 know-something"，再谈买几只、买多少。

- know-nothing（无法评估具体生意/基金底层资产）：定期定额买入低成本宽基指数基金，反而能跑赢大多数专业人士——"笨钱承认局限就不再笨"；普通人的默认解是低费率宽基指数（2016/2022 反复出现）。
- know-something（能看懂 5–10 个标的）：常规分散只是摊薄收益、增加风险；应把仓位加到"最懂、风险最小"的少数选择上。集中若能提高思考强度与买入前的舒适度门槛，反而降低风险（p10，1993）。
- 风险的定义是"损失或伤害的可能性"（购买力损失），不是价格波动（1993）。
- 伪分散：8 只同涨同跌的主题基金不等于分散；相关性相同等于一只大仓位的重复（x07/1997 过度分散损害结果）。
- 对基金持仓（FundOS 纪律线）：单只 ≤15–20%，单板块 ≤40%；换仓每批 ≤10%；深坑基金（亏损 >15%）越早处理越有利。

---

## A1 — 书中的应用（Past Application）

### 案例 1：指数基金十年赌约（2016 年信）
- **问题**：高收费主动管理（5 只 FOF，内含 100+ 只对冲基金、叠加两层费用）是否值回票价？
- **方法论的用法**：know-nothing 路线实证——一只低费率 Vanguard S&P 500 指数基金对比 5 只 FOF。
- **结论**：前九年指数基金累计 +85.4%（年化 7.1%），5 只 FOF 仅 +2.9% 至 +62.8%。
- **结果**：约 60% 的 FOF 收益被两层管理费吃掉（"Fees never sleep"）；"低成本指数对绝大多数人是更优解"。

### 案例 2：Gotrocks 家族的 Helper 们（2005 年信）
- **问题**：家族（全体投资者）想靠互相交易、请 Helper 打败彼此。
- **方法论的用法**：拆穿摩擦成本——"交易越多，家族分到的饼越小，Helper 拿到的越多；活动是他们的朋友"。
- **结论**：对投资者整体，收益随活动增加而减少（returns decrease as motion increases）。
- **结果**：高频换手与高费率是确定性损耗，配置上应"少动 + 低成本"。

---

## A2 — 触发场景（Future Trigger）★

### 用户会在什么情境下需要这个 skill？

1. "我现在持有 8 只主题基金，算分散吗？"（伪分散检查）
2. "单只基金最多买多少？018354 亏了 19% 要不要加仓摊薄？"（仓位上限/摊薄）
3. "科技/AI/TMT 已经占 48% 了，还要不要加？"（板块集中度）
4. "我是新手，买宽基指数还是主动基金？"（认知定位）

### 语言信号（出现这些就应激活）

- "买多少 / 仓位 / 分散 / 集中 / 上限 / 摊薄 / 太重了"
- "how much to buy / position size / diversify / overweight / average down"

### 与相邻 skill 的区别

- 与 `hold-three-conditions`：本技能管"组合结构怎么摆、买多少"；后者管"单只标的该不该继续持有"。
- 与 `timely-correction`：本技能管"仓位上限/结构"，不管"逻辑证伪后的卖出动作"；纠错时的分批减仓可与之 composes。
- 与 `do-not-list`：杠杆/衍生品产品"能不能碰"由 do-not-list 一票否决，本技能只在其通过后谈占比。

---

## E — 可执行步骤（Execution）

1. **定位认知水平**
   - 问用户：能否在 3 分钟内写出该基金底层资产的 3 条长期判断（商业模式、现金流、竞争格局）？
   - 完成标准：能 → know-something；不能/犹豫 → 默认 know-nothing。

2. **结构体检**
   - 用 `python D:\基金项目\fundos_core.py` 拉取持仓（portfolio_snapshot.json），计算：单基金占比（纪律 ≤15–20%）、板块占比（≤40%）、QDII/现金占比。
   - 检查伪分散：统计 8 只持仓中同涨同跌的数量（如同为科技/AI/TMT、同为 QDII），给出"有效独立下注数"。
   - 完成标准：输出"当前结构 vs 纪律线"对照表。

3. **判停**
   - know-nothing 且重仓单行业 → 先降超限部分（每批 ≤10%），并默认切换低费率宽基指数 + 定投。
   - know-something → 允许集中，但单只仍 ≤15–20%、单板块 ≤40%，不可 all-in 单行业。

4. **处理深坑**
   - 对亏损 >15% 的持仓（如 018354，-19.15%）用回本数学评估：亏 10% 需涨 11.1%、亏 20% 需涨 25%、亏 30% 需涨 42.9%；纳入纠错优先级，绝不盲目加仓摊薄。

5. **记录与输出**
   - 结构体检与调整写入 `python D:\基金项目\trade_journal.py`（add：体检日期、结构数据、调整批次）。
   - 输出 2–3 条可执行调整（含每批比例与目标仓位）。

---

## B — 边界（Boundary）★

### 不要使用本 skill 的场景

- 单只基金"要不要卖/继续持有"——转 `hold-three-conditions`；逻辑证伪后的止损——转 `timely-correction`。
- 杠杆 ETF / 衍生品 / 结构化产品选择——`do-not-list` 一票否决，先过清单再谈仓位。
- 纯净值查询、组合当日涨跌计算——直接用 fundos-core。

### 作者警告的失败模式（来自反例）

- 价值陷阱（x08）：别因为"便宜/跌了很多"重仓摊薄——困难企业"厨房里从来不止一只蟑螂"，时间站在平庸企业对面。
- 换手与费用（x07）：结构反复折腾本身就是损耗，Helper 在鼓励活动。
- 杠杆（x01）：集中 + 杠杆 = 双倍出局风险；"一串漂亮数字乘以零等于零"。

### 作者的盲点 / 时代局限

- 集中持仓回撤巨大（伯克希尔多次回撤 50%+），书中对回撤期心理承受讲得少。
- 浮存金式低成本杠杆是伯克希尔独有结构，散户无法复制。
- "集中"的前提是真正 know-something，散户常高估自己的认知——用"能否写出 3 条底层判断"自测。

### 容易混淆的邻近方法论

- "分散" ≠ "多买几只"：要算相关性，同类资产买 8 只等于一只大仓位的重复。
- "集中" ≠ "all-in 单行业"：纪律线（单只 ≤15–20%、单板块 ≤40%）仍然存在。
- 指数基金建议不排斥少数主动基金——前提是费后超额收益可验证（p09/g08）。

---

## 相关 skills（阶段 3 填充）

- depends-on: fundos-core（持仓与占比数据）
- contrasts-with: hold-three-conditions（组合结构 vs 单只持有）
- composes-with: timely-correction（深坑处理）、do-not-list（新产品入库前先过否决清单）

---

## 审计信息

- **验证通过**：V1 ✅（1993 know-nothing/know-something、1997 过度分散、2016 赌局、2005 Helper 多信印证）/ V2 ✅（"持有 8 只主题基金算分散吗"→ 伪分散推导）/ V3 ✅（"笨钱承认局限就不再笨"+"集中可能降低风险"反分散教条）
- **蒸馏时间**：2026-08-08
- **来源**：books/buffett-letters（verified.md b06 + candidates f10/p09/p10/g08/c08/x07/x08）
