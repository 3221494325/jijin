---
name: price-action-first
description: |
  用户在"新闻解释与价格走势打架"（利好不涨、利空不跌）、下跌中找"便宜/洗盘/错杀"理由、或需要判断某个"看起来很合理"的解释可不可信时使用。核心动作：让价格与成交行为做最终裁决，给匿名来源的解释降权——持续下跌极少是洗盘，而是东西本身有问题。
  不适用于：纯新闻事实核查（去 narrative-news-check / deep-news）、无价格数据的纯估值讨论。
  关键触发词："利好不涨" / "为什么不涨" / "主力洗盘" / "错杀" / "超跌" / "这么便宜能抄底吗" / "接飞刀" / "补涨" / price action / inside buying。
source_book: 《股票大作手回忆录》(Reminiscences of a Stock Operator) — Edwin Lefèvre
source_chapter: 第15、17、18、23、24章（f08/g07/g08/g09/x08）
tags: [价格行为, 信息不对称, 反解释, 接飞刀, price-action]
related_skills: [independent-judgment, narrative-news-check, deep-news, sector-rotation-detector, emotion-discipline-system]
---

# 价格行为优先于解释（price-action-first）

## R — 原文 (Reading)

> "The public should beware of explanations that explain only what unnamed insiders wish the public to believe. ... When a stock keeps on going down you can bet there is something wrong with it, either with the market for it or with the company. ... In a bull market and particularly in booms the public at first makes money which it later loses simply by overstaying the bull market."
>
> 译文：公众要警惕那些"解释"，它们只解释匿名内部人想让公众相信的东西。……当一只股票持续下跌，你可以打赌它出了问题——要么是它的市场出了问题，要么是公司本身出了问题。……在牛市尤其是狂热期，公众先赚到钱，后来只是因为在牛市里停留太久而亏光。
>
> — Livermore，第23-24章（f08；另见 g07"解释不了暴跌的利空理由常是反向消息 inverted tip"）

---

## I — 方法论骨架 (Interpretation)

市场存在天然的信息不对称：**内部人买在沉默中、卖也在沉默中**；公开的"解释"多数服务于派发或接盘——利多解释帮内部人出货，利空解释劝散户别卖。

因此判断顺序必须是：**先读价格与成交行为（量价配合、内盘是否在买、是否跟板块领涨），再读解释；两者冲突时，以价格行为为准。**

三条高频裁决规则：
1. **持续下跌极少是"空头袭击/主力洗盘"，而是东西本身有问题**；
2. **利好不涨 = 派发信号**，无需更多解释；
3. **拒绝跟涨的弱势标的 = 内盘在卖**，不是补涨机会。

本技能不判断消息真假，只判断"哪个解释可信、该不该据此动作"。对基金场景：新闻利好利空进入决策前，先过"价格行为是否配合"这一关。

---

## A1 — 书中的应用 (Past Application)

### 案例 1: Guiana Gold——"Inside buying. There wasn't any."（g08）
- **问题**: 股价从 45 跌到 35，散户按"便宜、还有分红"的逻辑接盘，赌超跌反弹。
- **方法论的使用**: 作者不看新闻解释，只盯一个信号——内幕人在自家股票下跌时买不买。
- **结论**: "我是交易者，所以我只看一个信号：内盘买盘。没有。就是没有。"（Inside buying. There wasn't any.）
- **结果**: 据此果断做空；随后传来矿脉变废（"打到的全是废石"）的消息，股价崩盘——价格行为先于公开解释给出答案。

### 案例 2: TT 烟幕——上涨也可能是派发（g09）
- **问题**: TT 股票强势上涨，看起来是"强势股"，散户想追。
- **方法论的使用**: 识别这波上涨只是"烟幕"——操纵性拉升是为了掩护关联方 Equatorial Commercial 的内盘出货。
- **结论**: 上涨不需要解释，但要追问"这波上涨服务于谁"；支撑一撤，价格即跌。
- **结果**: "内幕人一撤走支撑，TT 的价格就跌了。"（The moment the insiders took away their support the price of TT declined.）

### 案例 3: Chester 拒绝跟涨——弱者不是补涨机会（x08）
- **问题**: 汽车股板块普涨，Chester 拒不跟涨，散户按"板块补涨逻辑"买入。
- **方法论的使用**: 作者用长期经验裁决——"经验教会我警惕买入不肯跟随板块领涨者的股票"（beware of buying a stock that refuses to follow the group-leader）。
- **结论**: 不跟涨说明内部人一直在卖，弱是结果不是错杀。
- **结果**: 接盘者被闷杀；Guiana、Consolidated Stove（公众 50 抢购、37 无人问津）同属此类。

---

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. 用户问"这么大的利好，为什么基金/板块不涨？"
2. 用户问"跌这么多是不是主力洗盘？要不要抄底？"
3. 用户在下跌中找"便宜"理由（估值低、有分红、超跌、错杀）；
4. 用户问"这个解释靠谱吗"——消息面与走势打架；
5. 复盘归因："亏都是因为那条利空消息"。

### 语言信号（用户的话里出现这些就应激活）

- "利好不涨" / "利空不跌" / "为什么不涨" / "主力洗盘" / "错杀" / "超跌" / "这么便宜" / "抄底" / "接飞刀" / "补涨"
- "消息面这么好" / "解释一下为什么跌" / "price action" / "洗盘" / "inside buying"

### 与相邻 skill 的区分（初稿，阶段3回填）

- 与 `narrative-news-check`（EPD）: 后者核查新闻叙事逻辑（因果、证据、来源）；本技能不查新闻，只让价格行为裁决解释。
- 与 `deep-news`（FundOS）: 深度新闻流程是"找原因"；本技能是"让走势裁决原因"，先价格后解释。
- 与 `independent-judgment`: 后者过滤"谁的建议"；本技能裁决"哪个解释"，可串联使用。
- 与 `sector-rotation-detector`: 后者识别"钱往哪去"（板块强弱排名）；本技能判断"解释与走势谁可信"。

---

## E — 可执行步骤 (Execution)

当 skill 被激活后，按以下步骤执行:

1. **分离事实与解释**
   - 列出走势事实（价格、成交量、资金流、相对板块强弱）与新闻解释，分成两栏。
   - 完成标准: 一栏是"可观察行为"，一栏是"别人说的理由"，互不混写。

2. **检验解释服务谁**
   - 问: 这个解释对谁有利？可复核吗？是"匿名来源"吗？
   - 完成标准: 标注每条解释的受益者与可复核性。
   - 判停条件: 解释来自匿名/利益冲突来源且与走势冲突 → 解释直接降权，跳到步骤 4。

3. **价格行为裁决**
   - 应用三条高频规则: 持续下跌无内盘买=基本问题；利好不涨=派发；拒绝跟涨=弱者。
   - 完成标准: 给出"走势支持 / 不支持解释"的明确结论。

4. **给出动作**
   - 结论映射: 派发期→不追；接飞刀→不接；方向未明→持有等待确认；基本问题→减仓并联动基本面排雷。
   - 完成标准: 输出可执行建议 + 明确的重新评估触发条件（何时再看一次）。

---

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- 用户只问新闻真假 → 用 `narrative-news-check` / `deep-news` 做事实核查；
- 用户在做无价格数据的纯估值/理论讨论 → 不适用；
- 用户在做长期价值投资深度研究 → 本技能只处理"市场行为 vs 叙事"的背离，不否定基本面。

### 作者在书中警告的失败模式

- **接飞刀**（x08）: 下跌中买"便宜"= 接主力派发的货；Guiana 45→35、Consolidated Stove 50 抢购 37 无人问津。
- **反向消息 inverted tip**（g07）: 券商/圈内人解释暴跌的"利空理由"常是掩护吸货的烟雾，反而阻止你明智地离场。
- **过度停留 overstaying**（f08）: 牛市后期"赚钱在纸上"仍不兑现，最终把利润还给市场。

### 作者的盲点 / 时代局限

- 1920s 无证监会、操纵横行，价格行为信号极强；现代市场有 ETF 套利、程序化与强制披露，噪音更多——"价格行为优先"不等于"无视基本面"。
- 基金场景需配合基本面排雷：财报造假、行业塌方等尾部风险，可能要在价格充分反映前用公开信息先行识别；本技能只裁决"解释"而非替代基本面研究。
- 作者几乎不谈估值与公司质量，选品能力需由其他框架补充。

### 容易混淆的邻近方法论

- `sector-rotation-detector`: 板块强弱排名 ≠ 解释可信度裁决；
- `deep-news`: 找原因 ≠ 让走势裁决原因，先价格后解释，勿倒置。

---

## 相关 skills（阶段 3 填充）

- depends-on: `market-scan`（价格/板块数据）、`deep-news`（解释来源）
- contrasts-with: `narrative-news-check`（新闻叙事核查）
- composes-with: `independent-judgment`（信源过滤 + 价格裁决）、`sector-rotation-detector`

---

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓（verified.md r06：Guiana Gold 接飞刀 / Chester 不跟涨 / TT 操纵烟幕 / "inside buying 没有就是没有"）
- **测试基准**: 6 条（3 should_trigger / 2 should_not_trigger / 1 edge_case），见 test-prompts.json；阶段 4 压力测试复核
- **蒸馏时间**: 2026-08-08
- **蒸馏源**: verified.md r06 + candidates（f08/g07/g08/g09/x08）