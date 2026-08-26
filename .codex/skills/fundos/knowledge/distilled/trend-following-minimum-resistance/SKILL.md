---
name: trend-following-minimum-resistance
description: |
  用户在纠结"板块/指数接下来是涨是跌、现在该不该进场、要不要等突破确认"时使用。适用: 判断市场大方向(多/空/震荡)、识别最小阻力线与关键点、震荡市忍住不动手。不适用: 已亏损仓位要不要止损(转 stop-loss-admission)、盈利仓位要不要兑现(转 hold-winners)、纯新闻利好利空判断。
  关键触发词: "最小阻力线"、"关键点"、"突破了吗"、"方向未明"、"要不要等确认"、"现在该不该买"、"横盘/震荡"、"line of least resistance"、"breakout"、"pivotal point"、"trend following"。
source_book: 《股票大作手回忆录》 Edwin Lefèvre
source_chapter: 第10-11章 (part_04 chunk)
tags: [趋势跟随, 最小阻力线, 关键点, 突破确认, 顺势]
related_skills: [sector-rotation-detector, right-side-entry-pyramid, stop-loss-admission, hold-winners]
---

# 趋势跟随：最小阻力线与关键点

## R — 原文 (Reading)

> "For purposes of easy explanation we will say that prices, like everything else, move along the line of least resistance. They will do whatever comes easiest, therefore they will go up if there is less resistance to an advance than to a decline; and vice versa. Nobody should be puzzled as to whether a market is a bull market or a bear market after it fairly starts."
>
> — Edwin Lefèvre, 《股票大作手回忆录》第10-11章

---

## I — 方法论骨架 (Interpretation)

不预测价格目标，先判断"价格沿哪个方向运行最省力"：上涨阻力小于下跌阻力就顺势看多，反之看跌；阻力相当就是震荡，震荡期不预测、不操作。判定依据来自市场自身行为（价格与成交的配合），不是个人观点、估值或消息。方向未明时，唯一正确的动作是等——等最小阻力线"自我定义"，即价格突破区间边界的那一刻，那才是进场信号（关键点）。先定大方向，再配仓位；价格高低本身不构成买卖理由，趋势位置才是。

---

## A1 — 书中的应用 (Past Application)

### 案例 1: 小麦 $1.20 关键点（第11章）
- **问题**: 想参与小麦行情，但不知道它会涨还是跌
- **方法论的使用**: 不预测，等待价格突破 $1.20——"by crossing $1.20 the line of least resistance of wheat prices was established"
- **结论**: 突破之前不行动、不抢跑；突破后最小阻力线才确立
- **结果**: 信号出现后顺势参与，避免了两头挨打

### 案例 2: 1915 年 Bethlehem Steel（第14章）
- **问题**: 破产四年后只剩一次"第一单必须盈利"的机会
- **方法论的使用**: 六周只看盘不动手，等最有把握的 Bethlehem 突破面值 100（关键点）再进场
- **结论**: 98-99 买入 500 股，当夜收 114-115，次日 145
- **结果**: 关键点突破是最可靠的进场信号之一，一次翻身

---

## A2 — 触发场景 (Future Trigger)

### 用户会在什么情境下需要这个 skill?

1. 持仓板块横盘/震荡，用户问"是不是要变盘了、我先买点行吗"
2. 某板块/指数刚放量，用户问"是不是右侧启动了、现在能不能进"
3. 市场方向不明时用户手痒想做波段，需要"忍住不动手"的依据

### 语言信号 (用户的话里出现这些就应激活)

- "最小阻力线" / "关键点" / "突破了吗" / "破位了吗"
- "方向未明" / "要不要等确认" / "现在该不该买" / "先看看再说"
- "横盘" / "震荡" / "突破前高" / "line of least resistance" / "breakout"

### 与相邻 skill 的区分

- 与 `right-side-entry-pyramid` 的区别: 本技能决定"何时方向成立"，右侧建仓决定"成立后怎么分批进场"
- 与 `stop-loss-admission` 的区别: 本技能管"进场前"，止损管"进场后错了怎么办"
- 与 `hold-winners` 的区别: 本技能判断趋势方向与确认点，持有技能管"趋势确立后怎么拿住"

---

## E — 可执行步骤 (Execution)

当 skill 被激活后，agent 应按以下步骤执行:

1. **判定当前市场状态**
   - 执行: `python D:\基金项目\market_scan.py` 看全市场主线；对目标持仓板块，用其指数近 20-60 日高低点划定区间
   - 完成标准: 输出"上涨阻力小 / 下跌阻力小 / 震荡"三选一及依据

2. **震荡期不操作**
   - 设观察位 = 区间上沿（突破候选）与下沿（破位风险）
   - 判停条件: 价格未突破前不给出买卖建议，只给观察提醒
   - 完成标准: 明确告知"方向未明，等突破确认"

3. **突破确认后进入执行层**
   - 收盘站上区间上沿且伴随量能 → 方向成立，转 `right-side-entry-pyramid` 分批流程
   - 收盘跌破区间下沿 → 转 `stop-loss-admission` 评估持仓
   - 完成标准: 突破/破位的判定有明确价格与量能条件

4. **输出完整建议**
   - 格式: 市场环境 → 方向判断 → 操作思路（加/减/持 + 分批节奏）→ 风险提示 + 止损位 → 免责声明
   - 完成标准: 五段齐全，不出现"必涨/必跌"式硬性指令

---

## B — 边界 (Boundary)

### 不要在以下情况使用此 skill

- 用户只问单只基金净值/盈亏 → 用 fundos_core 诊断
- 持仓已经深亏、在纠结止损 → 转 `stop-loss-admission`
- 纯基本面/估值问题，无价格行为数据支撑 → 不适合用关键点框架

### 作者在书中警告的失败模式

- x07 "sprinting too soon": 方向对但时机早、急于重仓，行情启动前先被反向轧出局——突破确认前绝不抢跑
- x08 接飞刀: 只看到"便宜"就买入下跌中的弱势标的，不看价格是否沿最小阻力线运行——持续下跌本身就是价格在定义方向

### 作者的盲点 / 时代局限

- 1920s 美股无证监会、高杠杆、内幕横行，与今日 A 股/公募基金规则差异巨大
- 假设"关键点"信号有稳定概率优势；现代市场效率与程序化交易会削弱它
- 只讲价格行为，几乎不谈基本面估值与公司质量，基金场景需叠加基本面验证

### 容易混淆的邻近方法论

- "关键点"是趋势转折的确认时刻，不是支撑位/阻力位
- "最小阻力线"是跟随路径，不是预测工具
- "突破"不等于"追高": 突破买的是确认，追高买的是情绪

---

## 相关 skills (阶段 3 填充)

- depends-on: `sector-rotation-detector`（主线判断）、market_scan.py（数据源）
- contrasts-with: `hold-winners`（进场前方向判断 vs 进场后持有纪律）
- composes-with: `right-side-entry-pyramid`、`stop-loss-admission`

---

## 审计信息

- **验证通过**: V1 ✓（小麦/Reading/Bethlehem 多语境）/ V2 ✓（震荡板块要不要动）/ V3 ✓（不预测、等市场自我定义方向）
- **测试通过率**: 见 test-prompts.json
- **蒸馏时间**: 2026-08-08
- **蒸馏源**: 《股票大作手回忆录》r01 单元（f01/f02/p01/p08）
