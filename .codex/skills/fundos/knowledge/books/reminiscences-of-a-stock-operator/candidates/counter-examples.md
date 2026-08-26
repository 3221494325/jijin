# Counter-Examples 反例候选提取
《股票大作手回忆录》(Reminiscences of a Stock Operator, Edwin Lefèvre)

> 提取器：cangjie-skill / counter-example-extractor
> 提取日期：2026-08-08
> 覆盖范围：正文 9 个 chunk（part_01–part_09）已全部精读，覆盖第 I–XXIV 章全书。
> 用途：作为 skill 阶段 2 的 B（Boundary）段素材，界定"哪些情况下正面规则会失效/被误用"。
> 备注：全局锚点 BOOK_OVERVIEW.md 中文内容已损坏（全部显示为 `?`），仅结构可辨认；本文件引文均直接取自 chunks 英文原文并经 grep 复核，未做转述改写。

---

## 候选清单（10 条）

### x01 套牢不止损：小亏拖成"总截肢"
- **id**: x01
- **title**: 套牢不止损（hope 心理把小亏拖成灭顶之灾）
- **type**: counter-example / 心理陷阱（loss-aversion + hope）
- **source_chapter**: 第十章（Ch X，part_04）；第九章 1907 年恐慌（Ch IX，part_03）
- **source_quote**:
  > "The speculator's chief enemies are always boring from within. It is inseparable from human nature to hope and to fear. In speculation when the market goes against you you hope that every day will be the last day--and you lose more than you should had you not listened to hope. … Finally there came the awful day of reckoning for the bulls and the optimists and the wishful thinkers and those vast hordes that, dreading the pain of a small loss at the beginning, were now about to suffer total amputation--without anaesthetics."
- **summary**:
  - 失败模式：浮亏时用"希望"代替判断，拒绝承认错误、拒绝止损，小亏被拖成大亏。
  - 书中何时出现：这是作者对市场参与者最核心的警告；第十章直接点破"希望与恐惧是投机者两大内在敌人"，第九章以 1907 年 10 月 24 日恐慌收尾，描述"因害怕一开始的小损失，最后遭受无麻醉的总截肢"。
  - 后果：不止损者最终在流动性枯竭时被一次性强平出局，损失远大于当初的小止损；1907 年恐慌中大量 margin 持仓者被逼在无人接盘时割肉。
  - 对基金持仓管理：预设止损/减仓纪律必须在开仓时写死，浮亏超过阈值即执行，不因"明天会反弹"而延期；hope 是仓位管理的最大敌人。
- **tags**: [counter-example, hope-bias, no-stop-loss, loss-aversion, position-management]

---

### x02 听内幕消息/小道消息交易
- **id**: x02
- **title**: 听内幕消息与小道消息（tip 上瘾者必死）
- **type**: counter-example / 行为陷阱（tip-taking）
- **source_chapter**: 第十六章（Ch XVI，part_06）；第二十四章（Ch XXIV，part_09）
- **source_quote**:
  > "It has always seemed to me the height of damfoolishness to trade on tips. … It is not so much greed made blind by eagerness as it is hope bandaged by the unwillingness to do any thinking. … Wall Street professionals know that acting on “inside” tips will break a man more quickly than famine, pestilence, crop failures, political readjustments or what might be called normal accidents."
- **summary**:
  - 失败模式：放弃自己的分析，把决策外包给"内幕消息/可靠来源"，本质是拒绝思考。
  - 书中何时出现：第十六章借 Borneo 股票局、G.O.H. 内幕（消息竟来自交易者自己的岳父，仍亏 3,500 美元）和 Westlake 给 Gates 的 Reading 建议（Gates 反向操作反而赚 6 万）等故事说明 tip 的荒谬；第二十四章直言"靠内幕 tip 破产比饥荒瘟疫更快"。
  - 后果：消息源头越"内部"越不可信；主力正是利用消息制造对手盘，接消息者成为出货对象，亏损无法追责。
  - 对基金持仓管理：以内部消息作为加减仓依据是硬性禁区；投研结论必须来自可复核的公开信息与独立验证，任何"只有我知道"的渠道都应降权处理。
- **tags**: [counter-example, inside-tips, rumor-trading, decision-outsourcing, information-asymmetry]

---

### x03 被权威/朋友劝阻而放弃独立判断（Saratoga 联合太平洋事件）
- **id**: x03
- **title**: 听权威朋友劝告、放弃自己的判断（Saratoga UP 多翻空）
- **type**: counter-example / 行为陷阱（authority bias）
- **source_chapter**: 第九章（Ch IX，part_03）
- **source_quote**:
  > "I sold out all my Union Pacific. Of course if it was unwise to be long of it, it was equally unwise not to be short of it. So after I got rid of my long stock I sold four thousand shares short. I put out most of it around 162. … The next day the directors of the Union Pacific Company declared a 10 per cent dividend on the stock."
- **summary**:
  - 失败模式：在自己判断正确时，被"消息灵通且动机善良"的权威人物说服，放弃基于盘面的独立结论，甚至反向开仓。
  - 书中何时出现：萨拉托加度假期间，作者依据盘面看多 Union Pacific 并持续买入；经纪人 Ed Harding 好意来电称"内幕在派发，你正在当接盘侠"，作者顶不住压力清仓并反手做空 4,000 股。
  - 后果：次日 UP 董事会宣布 10% 股息，股价跳涨创历史新高，作者两头挨打，亏掉巨额本金与面子；事后他承认盘面其实一直在说真话。
  - 对基金持仓管理：权威意见只能作为信息输入，不能替代仓位决策；改变原有持仓方向必须有独立证据触发，而非"某大佬/某券商建议"。
- **tags**: [counter-example, authority-bias, abandoning-judgment, reversal-of-position]

---

### x04 被魅力人物说服动摇、失去自信（Percy Thomas 棉花局）
- **id**: x04
- **title**: 被魅力型"专家"说服，从自信变成犹豫（棉花多头陷阱）
- **type**: counter-example / 行为陷阱（persuasion / loss of confidence）
- **source_chapter**: 第十三章（Ch XIII，part_05）
- **source_quote**:
  > "A man cannot be convinced against his own convictions, but he can be talked into a state of uncertainty and indecision, which is even worse, for that means that he cannot trade with confidence and comfort. … I lost my poise; or rather, I ceased to do my own thinking."
- **summary**:
  - 失败模式：自身判断正确时，被口才极佳、数据看似严密的人反复洗脑，从"确定"退化为"不确定"，进而做出与初衷相反的仓位调整。
  - 书中何时出现：第十三章，棉花专家 Percy Thomas（作者自认见过最有魅力的人）用"一万个南方通讯员的独家数据"说服作者，作者本为空头却因恐惧而平仓，随后反手做多棉花。
  - 后果：作者在棉花上巨亏（此役及其后续让其元气大伤，多年后才恢复），且因"不再做自己的思考"失去了交易者的根本能力。
  - 对基金持仓管理：警惕"数据详实但无法复核"的叙事；当外部信息让自己从清晰变模糊时，应视为风险信号，而非加仓理由；决策须回到可验证的基本面/估值框架。
- **tags**: [counter-example, persuasion-bias, loss-of-confidence, narrative-trap]

---

### x05 人情与感恩绑架交易决策（Dan Williamson 事件）
- **id**: x05
- **title**: 人情/感恩绑架交易决策（四年黄金行情被锁死）
- **type**: counter-example / 结构性陷阱（conflict of interest + emotional ties）
- **source_chapter**: 第十四章（Ch XIV，part_05）
- **source_quote**:
  > "my feelings again won over my judgment and I gave in. To subordinate my judgment to his desires was the undoing of me. … Noblesse oblige--but not in the stock market, because the tape is not chivalrous and moreover does not reward loyalty."
- **summary**:
  - 失败模式：因感激/人情/关系而把交易决策权交给他人，放弃自己正确方向的仓位，甚至配合对方节奏操作。
  - 书中何时出现：第十四章，券商 Williamson 曾替作者还债、给信用，随后以"为你好"为名让作者平掉正确的空头、买入 Southern Atlantic 等股票；作者因感恩无法拒绝。
  - 后果：作者不仅亏损 15 万美元并欠券商 15 万，更被当作 Marquand 遗产出货的"烟幕"；此后 1911–1914 四年无行情，他因错过 1907–1910 的大机会而损失"一辈子最大的机会"。
  - 对基金持仓管理：基金内部必须有防火墙：利益相关方（托管人、渠道、大客户、关联方）的意见不得直接驱动调仓；人情往来与持仓决策隔离，防止仓位被"关系"绑架。
- **tags**: [counter-example, gratitude-bias, conflict-of-interest, independence-of-judgment]

---

### x06 过早止盈：恐惧兑现小利润，卖飞大行情
- **id**: x06
- **title**: 过早止盈（"4 点利润"保守主义卖飞牛市）
- **type**: counter-example / 行为陷阱（fear-driven profit-taking）
- **source_chapter**: 第五章（Ch V，part_02）；第十章（Ch X，part_04）
- **source_quote**:
  > "They say you never grow poor taking profits. No, you don't. But neither do you grow rich taking a four-point profit in a bull market. Where I should have made twenty thousand dollars I made two thousand. … Fear keeps you from making as much money as you ought to."
- **summary**:
  - 失败模式：在趋势仍然成立时，因恐惧回吐而急于兑现小利润，结果"卖飞"主升段，收益与判断正确程度严重不匹配。
  - 书中何时出现：第五章，作者在牛市启动即看多并买入，却听信"老成持重"的建议"先落袋、回调再买"，结果回调永不出现，股票继续上涨 10 点；作者自评"该赚 2 万只赚 2 千"。
  - 后果：判断 100% 正确，盈利却只有应得的一成；同时养成"追高买回"的坏习惯，成本更高、心态更差。
  - 对基金持仓管理：止盈不应是固定点数，而应基于趋势/估值是否仍在；浮盈回撤应设"移动止盈保护线"而非"到点就跑"，避免把主升浪让给市场。
- **tags**: [counter-example, premature-profit-taking, fear-bias, trend-following]

---

### x07 时机未到急于重仓（sprinting too soon）
- **id**: x07
- **title**: 方向对但时机早：急于重仓入场被反向轧
- **type**: counter-example / 行为陷阱（premature entry / over-eagerness）
- **source_chapter**: 第七章（Ch VII，part_03）
- **source_quote**:
  > "So much for sprinting too soon! I was too eager to prove to myself that I had seen real dollars and not a mirage. … I should have walked and not sprinted. … even when one is properly bearish at the very beginning of a bear market it is well not to begin selling in bulk until there is no danger of the engine back-firing."
- **summary**:
  - 失败模式：方向判断正确，但入场时机过早、仓位过重，在行情启动前先被反向波动打死。
  - 书中何时出现：第七章，作者在 1906 年正确预判熊市即将到来，却在下跌尚未确认时"全力冲刺"重仓做空，结果先被一波反弹轧空，爆仓后行情才真正开始。
  - 后果：作者在黎明前倒下，错过了自己看得最准的一轮大跌；他总结出"熊市开头也不要在引擎回火风险消失前成批卖出"。
  - 对基金持仓管理：方向正确不等于立即满仓；分批建仓 + 等待趋势确认（如跌破关键均线/支撑）可避免"对方向、错时机"的仓位被清理。
- **tags**: [counter-example, premature-entry, timing-error, position-sizing]

---

### x08 下跌途中接"便宜盘"、买入不跟涨的弱者
- **id**: x08
- **title**: 接飞刀：在下跌途中买"看起来很便宜"的股票
- **type**: counter-example / 行为陷阱（value trap / catching falling knife）
- **source_chapter**: 第十七章（Ch XVII，part_06）；第十八章（Ch XVIII，part_07）；第二十三章（Ch XXIII，part_08）
- **source_quote**:
  > "outsiders, who did not know, were now buying because having sold at 45 and higher the stock looked cheap at 35 and lower. The dividend was still being paid. The stock was a bargain. … Experiences had taught me to beware of buying a stock that refuses to follow the group-leader."
- **summary**:
  - 失败模式：不看"股票是否在正常做它该做的事"，只看价格跌幅/估值便宜，在弱势股下跌途中买入；或买入同板块中拒绝跟涨的"落后股"，赌补涨。
  - 书中何时出现：第十八章 Guiana Gold 从 45 跌到 35 时，不知情的散户认为"便宜、还有分红"而买入，实则内盘主力正在出货；第十七章 Chester 在汽车股普涨时拒不跟涨，散户按"板块补涨逻辑"买入后被闷杀；第二十三章 Consolidated Stove 公众 50 抢购、37 无人问津。
  - 后果：Guiana 随后因"打到的全是废石"破位崩盘；Chester 内部人一直在卖；Stove 跌破银行质押线，接盘者深度套牢。散户接的每一笔"便宜货"都是主力在派发。
  - 对基金持仓管理：下跌中加仓必须有"基本面恶化被排除"的独立证据，不能仅因"便宜"接盘；同板块最弱个股（不跟涨、无内盘支撑）应视为预警，而非补涨机会。
- **tags**: [counter-example, catching-falling-knife, value-trap, relative-strength]

---

### x09 过度杠杆、重仓赌单一方向：看对也亏光
- **id**: x09
- **title**: 重仓加杠杆赌单一方向（看对方向仍被杠杆清空）
- **type**: counter-example / 结构性陷阱（over-leverage / concentrated bet）
- **source_chapter**: 第三章 1901 年 5 月 9 日（Ch III，part_01）；第九章 1907 年恐慌（Ch IX，part_03）
- **source_quote**:
  > "Everything happened as I had foreseen. I was dead right and--I lost every cent I had! I was wiped out by something that was unusual. … Without money they must sell what stocks they were carrying on margin--sell at any price they could get in a market where buyers were as scarce as money."
- **summary**:
  - 失败模式：用杠杆/保证金重仓押注单一方向，判断正确但经不起执行滑点、流动性枯竭或一次"意外"，账户直接清零。
  - 书中何时出现：1901 年 5 月 9 日，作者准确预判北方太平洋逼空引发的崩盘，重仓做空，但因行情软件滞后、实际成交价差 20–35 点，被迫平空反多，当日亏光全部身家——"看对了却亏光了"；1907 年 10 月 24 日，全市场 margin 持仓者在无钱可借、无人接盘的 Money Post 前被迫任意价格割肉。
  - 后果：杠杆放大的是"容错率归零"的风险：判断正确也无法对抗极端波动与流动性风险；1907 年无数扛 margin 的人一夜破产。
  - 对基金持仓管理：单方向仓位上限 + 杠杆上限必须在事前设定；测算极端场景（跳空、停牌、流动性枯竭）下的最大回撤，确保"判断暂时错误"也不会被迫清仓离场。
- **tags**: [counter-example, over-leverage, concentration-risk, liquidity-risk, forced-liquidation]

---

### x10 频繁进出、过度交易：手续费与情绪双杀
- **id**: x10
- **title**: 频繁进出（in-and-out）：小胜多次、大亏一次
- **type**: counter-example / 行为陷阱（overtrading / churning）
- **source_chapter**: 第三章（Ch III，part_01）；第四章开头（Ch IV，part_02）
- **source_quote**:
  > "I did worse than not see it; I kept on trading, in and out, regardless of the execution. … I got up to fifty thousand dollars and two days later that went. I had no other business and knew no other game. After several years I was back where I began."
- **summary**:
  - 失败模式：沉迷短线进出，交易频率远高于信息优势，赢多次小钱、输一次大的，长期收益被摩擦成本和情绪损耗吞噬。
  - 书中何时出现：第三章，作者初到纽约反复"in and out"，不看执行质量只看波动；第四章开头总结纽约前几年：曾赚到 5 万美元，两天内全部亏光，"几年后又回到原点，甚至更糟"。
  - 后果：作者自述靠"打一枪换一个地方"永远无法积累大钱，最终领悟"投机的大钱来自大趋势中的持仓，而非逐点博弈"。
  - 对基金持仓管理：换手率应有预算与理由门槛（每笔交易需记录触发逻辑）；降低无效交易频率，把资源集中在少数高确信度、可持仓的标的上。
- **tags**: [counter-example, overtrading, churning, turnover-control, transaction-costs]

---

## 反例 → 基金持仓管理映射速查

| 用户关注点 | 对应候选 |
|---|---|
| 套牢不止损 | x01（hope 拖成灭顶）、x10 参考 |
| 追涨杀跌 | x08（下跌接盘/买弱者）、x06（追高买回） |
| 听消息 | x02（内幕 tip）、x03（权威朋友）、x04（魅力专家）、x05（人情关系） |
| 重仓赌单一方向 | x09（杠杆+集中）、x07（过早满仓） |
| 频繁交易 | x10（in-and-out）、x06（过早止盈导致的反复进出） |
