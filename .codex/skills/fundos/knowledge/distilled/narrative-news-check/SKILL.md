---
name: narrative-news-check
description: |
  用户收到重大利好新闻、想确认"这条消息能不能加仓"时使用。把每条利好拆成事实层/叙事层/杠杆层，判断上涨由哪一层驱动；只有事实兑现且无杠杆强化的上涨才可作为加仓依据。不适用于：无新闻的纯走势讨论、净值查询、新闻采集本身。关键触发词："这消息是利好还是利空"、"利好出尽了吗"、"能追吗"、"为什么大涨"、"消息真假"。
source_book: 《非同寻常的大众幻想与群众性癫狂》(Memoirs of Extraordinary Popular Delusions and the Madness of Crowds) — Charles Mackay, 1841/1852
source_chapter: 南海泡沫（THE SOUTH-SEA BUBBLE）/ 密西西比计划（MONEY MANIA）
tags: [叙事检查, 利好利空, 新闻分析, 情绪驱动, 追高风险]
related_skills: [deep-news, sector-rotation-detector, mania-cycle-map, herd-contagion-check]
---

# 利好新闻叙事检查器

## R — 原文 (Reading)

> "One rumour alone, asserted with the utmost confidence, had an immediate effect upon
> the stock. It was said that Earl Stanhope had received overtures in France from the
> Spanish government to exchange Gibraltar and Port Mahon for some places on the coast
> of Peru... 'Visions of ingots danced before their eyes,' and stock rose rapidly."
>
> — Charles Mackay, 南海泡沫（THE SOUTH-SEA BUBBLE），chunks/sub_02.txt（阶段1已验证）

> "Every body had heard of the gold and silver mines of Peru and Mexico; every one
> believed them to be inexhaustible, and that it was only necessary to send the
> manufactures of England to the coast to be repaid a hundred fold in gold and silver
> ingots by the natives."
>
> — Charles Mackay, 南海泡沫（THE SOUTH-SEA BUBBLE），chunks/sub_02.txt（阶段1已验证）

---

## I — 方法论骨架 (Interpretation)

南海案例显示：一条"西班牙将让出直布罗陀与梅诺卡港"的谣言就能让股价应声大涨——定价的不是事实，而是"金锭在眼前跳舞"的想象。因此每条利好都要拆成三层：

1. **事实层**：已发生、可验证、能改变企业现金流/订单/盈利的硬信息；
2. **叙事层**：对"未来会怎样"的想象与故事，无法立即验证；
3. **杠杆层**：放大了想象的信用工具（融资盘、增发纸币、配资）。

判断规则：若上涨主要由叙事+杠杆驱动而非事实，则价格是脆弱的——叙事一旦被证伪，杠杆会反向加速下跌；"利好出尽"往往就是叙事兑现、无人接力的时刻。先问"这条消息改变了现金流，还是只改变了情绪"，再决定是否加仓。

---

## A1 — 书中的应用 (Past Application)

### 案例 1: 南海谣言驱动股价暴涨（1720）
- **问题**: 一条未经证实的换地谣言，让南海股价应声大涨。
- **方法论的使用**: 把谣言拆三层——事实层为零（谈判未证实），叙事层极强（秘鲁金银矿取之不尽），杠杆层（认购/股份制度）放大想象。
- **结论**: 上涨完全由叙事驱动，任何一条反向消息都会让价格失去支撑。
- **结果**: 泡沫破裂后股价一泻千里，"金锭"从未兑现。

### 案例 2: 伦敦"不知名公司"五小时募足一千股
- **问题**: 一家"承办好处极大、但没人知道是什么"的公司，仅凭募股书五小时募足一千股、卷走 2000 英镑后骗子消失。
- **方法论的使用**: 事实层为零、叙事层宏大（"重大事业"）、杠杆层（2 英镑/股的低门槛定金）——三层结构完全失衡。
- **结论**: 故事本身即可募资，不需要基本面；凡"说不清底层资产赚什么钱、但故事很宏大"的产品按欺诈或投机定价处理。
- **结果**: 上百家仿效"气泡公司"遍地开花，枢密院下令全部解散，成为戳破南海泡沫的导火索之一。

---

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 收到重大政策/行业新闻，问"这是利好还是利空、能不能加仓"；
2. 持仓板块单日大涨，问"为什么涨、涨得实在吗"；
3. 利好发布后犹豫不决，问"利好出尽了吗、现在追高会不会接盘"。

### 语言信号（用户的话里出现这些就应激活）

- "这条消息是利好还是利空" / "这新闻能信吗"
- "利好出尽了吗" / "能追吗" / "现在买会不会接盘"
- "XX大涨是因为什么" / "消息真假怎么查"

### 与相邻 skill 的区分

- 与 `deep-news` 的区别: deep-news 负责采集与初筛分类，本 skill 负责把已获得的利好做三层拆解与可信度判定；
- 与 `sector-rotation-detector` 的区别: 轮动识别回答"涨在哪"，本 skill 回答"这条消息能不能解释上涨"；
- 与 `mania-cycle-map` 的区别: 周期定位判断"过热没有"，本 skill 判断"消息本身值不值得信"。

---

## E — 可执行步骤 (Execution)

当 skill 被激活后，按以下步骤执行：

1. **采集并过滤新闻**
   - 执行: `python D:\基金项目\deep_news.py`（或 news_engine.py）
   - 完成标准: 只保留近 5 天新闻，标题含核心关键词，剔除旧闻/聚合文；自动化分类只做初筛，关键条目人工复核（E-006 教训）

2. **三层拆解**
   - 事实层：是否已发生、可验证、改变现金流/订单/政策落地；
   - 叙事层：属于对未来的想象、无法立即验证；
   - 杠杆层：是否有融资余额、份额激增、低门槛认购等信用放大
   - 完成标准: 每条利好输出"事实=…、叙事=…、杠杆=…"三行清单

3. **判定驱动层**
   - 若事实兑现且无杠杆强化 → 可考虑加仓；
   - 若纯叙事+杠杆 → 脆弱信号，不追高、不加仓；
   - 若叙事已被证伪/利好出尽 → 提示减仓或落袋
   - 判停条件: 用户只问"有没有这则新闻"（信息查询）→ 停在本步，不做仓位建议

4. **对照持仓与仓位规则**
   - 结合 fundos-core 持仓（科技总仓 ≤40%、单基金 ≤15–20%、-15% 止损），给加/减/持建议与分批节奏（每次 ≤20%）

5. **记录与复盘**
   - 将"消息→三层判断→动作"写入 `trade_journal.py add`，便于日后回查消息兑现情况

---

## B — 边界 (Boundary) ★

### 不要使用此 skill 的场景

- 无新闻的纯走势讨论、K线分析 → 用 `sector-rotation-detector` / `fundos-core`；
- 纯净值查询 → 不需要做新闻检查；
- 用户要求采集大量新闻（采集工作）→ 先走 `deep-news.py`，本 skill 在消息到手后介入。

### 作者在书中警告的失败模式

- 轻信故事与名人背书：议员、贵族、文人与平民一起上了"不知名公司"的当（反例 x03）；
- 故事越宏大、来源越"权威"，越容易被当成事实；"名人站台"不构成安全边际；
- 只有叙事没有事实兑现的上涨，不能作为加仓依据。

### 作者的盲点 / 时代局限

- 19 世纪无定量验证手段，新闻可信度只能靠常识判断；
- 现代自动化分类有局限：关键词情感分析会把"英伟达否认X"误判为利好（E-006 实战教训），必须人工复核关键条目；
- 作者倾向把一切高价解释为"狂热"，可能低估某些新技术（铁路/互联网/AI）长期兑现的真实价值——"这次不一样"有时是对的。

### 容易混淆的邻近方法论

- "利好新闻" ≠ "利好兑现"：消息落地（叙事兑现）后往往是无接力之时；
- "信息查证" ≠ "新闻情绪分析"：本 skill 先查事实，再判情绪，顺序不能反。

---

## 相关 skills

- depends-on: deep-news.py / news_engine.py（新闻数据源）、fundos-core（持仓规则）
- contrasts-with: deep-news（采集分类 vs 叙事拆解）
- composes-with: mania-cycle-map（起源段叙事验证）、herd-contagion-check（消息传播中的从众检查）

---

## 审计信息

- **验证通过**: V1 ✓ 跨域同构（南海谣言/密西西比故事/不知名公司同一叙事驱动模式）；V2 ✓ 可预测性（三层拆解→可验证的加仓判定）；V3 ✓ 排他性（只判消息真假与驱动层，不与轮动/周期/持仓诊断抢答）
- **测试通过率**: 待执行（详见 test-prompts.json）
- **蒸馏时间**: 2026-08-08
- **蒸馏源**: 《EPD》阶段1候选 f04/p02 + 反例 x03 + 实战经验 E-006
