---
name: right-side-entry-pyramid
description: |
  用户问"要不要补仓/加仓、怎么分批"，或在亏损后想"越跌越买摊薄成本"时使用。适用: 右侧确认后的分批建仓、试探仓+盈利再加码、金字塔加仓、拒绝摊平亏损。不适用: 方向未明时抢跑(转 trend-following-minimum-resistance)、已有浮亏是否止损(转 stop-loss-admission)、盈利仓位拿不拿(转 hold-winners)。
  关键触发词: "补仓"、"加仓"、"摊薄成本"、"越跌越买"、"一次买多少"、"分批买"、"试探仓"、"金字塔"、"加码"、"抄底"、"pyramid"、"averaging down"、"add position"。
source_book: 《股票大作手回忆录》 Edwin Lefèvre
source_chapter: 第11章 + 第7章 (part_04/part_03 chunk)
tags: [右侧建仓, 金字塔加仓, 试探仓, 分批, 绝不摊平]
related_skills: [trend-following-minimum-resistance, stop-loss-admission, hold-winners]
---

# 右侧建仓：试探仓 + 金字塔加仓，绝不摊平

## R — 原文 (Reading)

> "He should accumulate his line on the way up. Let him buy one-fifth of his full line. If that does not show him a profit he must not increase his holdings because he has obviously begun wrong; he is wrong temporarily and there is no profit in being wrong at any time. ... Suppose the line of least resistance indicated a bull movement. Well, I would buy ten thousand bales. After I got through buying that, if the market went up ten points over my initial purchase price, I would take on another ten thousand bales."
>
> — Edwin Lefèvre, 《股票大作手回忆录》第11章

---

## I — 方法论骨架 (Interpretation)

建仓分步验证：先买计划仓位的五分之一（试探仓），只有市场证明方向正确（出现浮盈）才允许加仓；首仓浮亏说明"开始就错了"，绝不加仓摊平，立即退出。加仓幅度随盈利扩大而递增（涨 10 点加 10 千包，涨 20 点加 20 千包），形成金字塔。对称规则同样重要：卖掉亏损的、拿住盈利的；摊平亏损是最大的投机错误之一。对基金：把建仓拆成"验证-确认-加码"三段，分批 3 次、右侧确认、不追大涨，用市场验证代替个人自信。

---

## A1 — 书中的应用 (Past Application)

### 案例 1: Reading 试探做空 111→92（第8章）
- **问题**: 全场皆跌唯 Reading 横盘，判断它是"大众不敢卖"而非真强势
- **方法论的使用**: 同时向两个经纪人各下 4,000 股试探卖单验证方向
- **结论**: 试探单应声砸出跳水，方向被市场确认
- **结果**: 111 开始、几分钟内在 92 全部回补，每股约 19 点利润

### 案例 2: 5 万包棉花的反向教训（第13章）
- **问题**: 棉花亏、小麦赚，他却"砍盈利、留亏损、越亏越买"
- **方法论的使用**: 违反"绝不摊平亏损"——"Of all speculative blunders there are few greater than trying to average a losing game"
- **结论**: 摊平 = 放大错误仓位的暴露
- **结果**: 几乎破产，从此把"先小仓验证、盈利再加码"立为铁律

---

## A2 — 触发场景 (Future Trigger)

### 用户会在什么情境下需要这个 skill?

1. 持仓浮亏后想补仓"摊薄成本"
2. 主线确认后想加仓，问"一次买多少、怎么分批"
3. 回调后想抄底/分批建仓，需要节奏设计

### 语言信号 (用户的话里出现这些就应激活)

- "补仓" / "加仓" / "摊薄成本" / "越跌越买"
- "一次买多少" / "分批买" / "试探仓" / "金字塔加仓" / "加码"
- "抄底" / "右侧确认" / "pyramid" / "averaging down" / "add position"

### 与相邻 skill 的区分

- 与 `trend-following-minimum-resistance` 的区别: 先确认方向（那个技能），本技能只负责确认后的进场节奏
- 与 `stop-loss-admission` 的区别: 首仓浮亏时本技能要求"不加仓"，去留交给止损纪律
- 与 `hold-winners` 的区别: 本技能管"怎么买进去"，持有技能管"买对后怎么拿住"

---

## E — 可执行步骤 (Execution)

当 skill 被激活后，agent 应按以下步骤执行:

1. **确认右侧信号**
   - 承接 `trend-following-minimum-resistance`: 目标基金/板块指数是否已收盘站上区间上沿或确认企稳
   - 完成标准: 明确"已确认 / 未确认"
   - 判停条件: 未确认 → 只给观察提醒，不给加仓建议

2. **设计分批方案**
   - 计划总仓分 3 批，首仓 ≈ 1/5 至 1/3；单次调仓 ≤ 20%；保留 10-20% 弹药；单行业 ≤ 40%
   - 完成标准: 输出每批的金额、触发条件、间隔节奏

3. **首仓验证后决定是否加码**
   - 首仓浮盈 → 执行第 2 批（金字塔加码，越加越多需重新评估集中度）
   - 首仓浮亏 → 不加仓不摊平；浮亏达 -15% → 转 `stop-loss-admission`
   - 判停条件: 浮亏状态下任何"补仓"请求都先按止损流程处理
   - 完成标准: 加码与否有明确的盈亏状态依据

4. **记录与复盘**
   - 执行: `python D:\基金项目\trade_journal.py add ...` 记录每批逻辑
   - 完成标准: 每笔操作有可追溯的触发理由

5. **风险提示**
   - 不追大涨（单日大涨后等回踩）；强调回本数学（亏 20% 需涨 25% 才回本）
   - 完成标准: 输出免责声明与止损位

---

## B — 边界 (Boundary)

### 不要在以下情况使用此 skill

- 方向未确认、只是"感觉便宜"想买 → 转 `trend-following-minimum-resistance`
- 持仓已深亏、在纠结去留 → 转 `stop-loss-admission`
- 单行业占比已超 40%，或弹药不足 10% → 先降风险，不讨论加仓

### 作者在书中警告的失败模式

- x07 "sprinting too soon": 方向对但急于重仓，行情启动前先被反向轧——首仓永远是小仓
- x08 接飞刀: 在下跌途中买"看起来很便宜"的标的——没有确认信号时那不是建仓是接盘
- p06 摊平亏损: 棉花一战砍盈利留亏损、越亏越买，几乎破产

### 作者的盲点 / 时代局限

- 书中没有给出加仓比例的数学依据（1/5、10 千包都是经验值），基金场景需用量化纪律固定
- 试探仓在申赎费率高、确认延迟的基金环境下摩擦成本更高，批次不宜过碎
- 1920s 高杠杆环境与公募基金无杠杆、不可盘中交易的性质差异大，节奏必须放慢

### 容易混淆的邻近方法论

- "分批买入" ≠ "摊平亏损": 前者是右侧验证后加码，后者是越跌越买
- "加仓" ≠ "追涨": 加仓有分批与回踩节奏，追涨是情绪
- "试探仓" ≠ "随便买一点": 试探仓有验证标准和失败退出条件

---

## 相关 skills (阶段 3 填充)

- depends-on: `trend-following-minimum-resistance`（方向确认）、`stop-loss-admission`（首仓失败的退出前提）
- contrasts-with: `hold-winners`（进场节奏 vs 持有纪律）
- composes-with: `trend-following-minimum-resistance`、`hold-winners`（右侧进场→持有→破位离场闭环）

---

## 审计信息

- **验证通过**: V1 ✓（Reading/Bethlehem/棉花多案例）/ V2 ✓（被套要不要补仓摊薄）/ V3 ✓（与"越跌越买"完全相反）
- **测试通过率**: 见 test-prompts.json
- **蒸馏时间**: 2026-08-08
- **蒸馏源**: 《股票大作手回忆录》r02 单元（f03/p07/p06/c05）
