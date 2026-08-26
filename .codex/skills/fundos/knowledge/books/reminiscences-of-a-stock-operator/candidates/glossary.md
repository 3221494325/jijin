# 关键概念词典候选 — Reminiscences of a Stock Operator（股票大作手回忆录）

> 提取器：glossary-extractor（cangjie 蒸馏流水线）
> 依据文本：Project Gutenberg #60979 版本，9 个 chunk（part_01–part_09）
> 说明：每条 quote 均为书中原文（保留原文拼写与标点）；summary 为中文解释，含"作者用法 vs 常识"差异。

---

- id: g01
  title: bucket shop（投机行）
  type: term
  source_chapter: 第 1 章（part_01）
  source_quote: |
    "You know how they traded in bucket shops. You gave your money to a clerk and told him what you wished to buy or sell. He looked at the tape or the quotation board and took the price from there--the last one, of course. He also put down the time on the ticket so that it almost read like a regular broker's report."
  summary: |
    投机行是一种"伪券商"：客户交现金给店员、报出想买/卖的股票，店员照纸带或报价板上的"最后成交价"开票，不真正在交易所撮合，本质是客户与庄家对赌价格波动的赌场（部分经营棉花/小麦等品种）。作者用法与常识差异：它不是"地下赌场"的比喻，而是一种当时合法泛滥的商业模式；它"从不追加保证金"、涨跌停限制利润、靠客户爆仓赚钱（"Their profit lies in your being wiped"）。作者少年时代在投机行靠纸带阅读百战百胜，但换到正规券商后同样方法大败——这是全书第一个关键转折，说明"赌波动"与"做交易"是两回事。
  tags: [term, core-concept, 交易场所, 历史背景]

- id: g02
  title: tape reading（纸带阅读）
  type: term
  source_chapter: 第 1 章、第 3 章（part_01）
  source_quote: |
    "A battle goes on in the stock market and the tape is your telescope. You can depend upon it seven out of ten cases. ... It seems so obvious now that tape reading is not enough, irrespective of the brokers' execution, that I wonder why I didn't then see both my trouble and the remedy for it."
  summary: |
    纸带阅读指通过行情纸带（ticker tape）上逐笔价格与成交的细微变化判断买卖力量强弱（"买盘只比卖盘强一点点"），作者称之为"望远镜"，七成可靠。它与常识差异：它不是"看图猜涨跌"，而是读"买盘与卖盘的战斗"；更关键的是作者反复强调"tape reading is not enough"——纸带永远滞后于真实成交（1901 年 5 月 9 日北太平洋轧空事件中纸带落后 20 多点、执行又慢，导致他爆仓）。纸带只能告诉你"何时开始"（时机），不能告诉你"整个大趋势"。下游 skill 若把 tape reading 译成"技术分析"会失真。
  tags: [term, core-concept, 技术分析, 交易时机]

- id: g03
  title: line of least resistance（最小阻力线）
  type: term
  source_chapter: 第 10 章、第 14 章（part_04、part_06）
  source_quote: |
    "The speculator is not an investor. His object is not to secure a steady return on his money at a good rate of interest, but to profit by either a rise or a fall in the price of whatever he may be speculating in. Therefore the thing to determine is the speculative line of least resistance at the moment of trading; and what he should wait for is the moment when that line defines itself, because that is his signal to get busy."
  summary: |
    最小阻力线是作者最核心的进场理论：不预测价格，而是判断"此刻阻力最小的方向"，等该方向自己确认（价格突破旧屏障、120 处买压盖过卖压、130 处卖压盖过买压）再行动。与常识差异：①它不是均线/通道之类指标，而是"买卖双方力量对比"的状态；②它不要求抄底逃顶（"buy as cheap as possible"是错的），要求"在正确的时间"行动；③连"意外事件"（accidents）也只会帮到基于最小阻力线建仓的头寸。全书出现 20+ 次（part_04 12 次），第 14 章小麦/棉花战役再次印证其价值。
  tags: [term, core-concept, 交易系统, 时机选择]

- id: g04
  title: 关键点 / pivotal point（原文用词说明）
  type: concept
  source_chapter: 第 7 章、第 10 章（part_03、part_04）
  source_quote: |
    "what he should wait for is the moment when that line defines itself, because that is his signal to get busy. ... Much depends upon beginning at exactly the right time. It took me years to realize the importance of this. It also cost me some hundreds of thousands of dollars."
  summary: |
    注意：本版原文中并未出现 "pivotal point" 字样（全 9 个 chunk 检索为 0 次），该词出自 Livermore 后来的《How to Trade in Stocks》；本书对应的概念是"最小阻力线自我定义、信号明确的那一刻"，以及"开始于完全正确的时机"。与常识差异：关键点不是"关键价位"（支撑/阻力数字），而是"趋势确认的临界时刻"，早了是逆势、晚了利润已蒸发，作者为此交了"几十万美元学费"。下游 skill 引用 pivotal point 时应指向"线自我定义的时刻"而非"某条价格线"。
  tags: [concept, 术语勘误, 交易时机, 信号确认]

- id: g05
  title: pyramiding（金字塔加仓）
  type: term
  source_chapter: 第 7 章（part_03）
  source_quote: |
    "I don't mean to be understood as advising persistent pyramiding. A man can pyramid and make big money that he couldn't make if he didn't pyramid; of course. ... Suppose a man's line is five hundred shares of stock. I say that he ought not to buy it all at once; not if he is speculating. ... But after the initial transaction, don't make a second unless the first shows you a profit. Wait and watch."
  summary: |
    金字塔加仓＝不在一次买满目标仓位，而是先建小仓，只在"第一笔已经浮盈"时才加第二笔、第三笔（"I must buy on rising scale. I don't buy long stock on a scale down, I buy on a scale up"）。与常识差异：①常识把加仓当"摊低成本"，作者明确反对越跌越买；②加仓不是赌注越下越大，而是"利润证明你对了才加"；③作者同时告诫不要"persistent pyramiding"（连续加仓成瘾），浮亏时唯一正确动作是止损离场。这是与"逢低补仓""向下摊平"完全相反的操作纪律。
  tags: [term, core-concept, 仓位管理, 交易纪律]

- id: g06
  title: sitting tight（拿住大行情）
  type: term
  source_chapter: 第 5 章（part_02）
  source_quote: |
    "It never was my thinking that made the big money for me. It was always my sitting. Got that? My sitting tight! It is no trick at all to be right on the market. You always find lots of early bulls in bull markets and early bears in bear markets. ... Men who can both be right and sit tight are uncommon. I found it one of the hardest things to learn."
  summary: |
    核心论断：大钱不在"个别波动"里，而在"主要趋势"（main movements）里；赚大钱靠的不是想得对，而是拿得住（sitting tight）。书中以老帕特里奇（Turkey/Partridge）反复说"Well, you know this is a bull market!"为例——他拒绝根据一条内幕消息换股，只坚持"现在是牛市"这个大判断。与常识差异：散户认为"高抛低吸赚差价"才算会做，作者认为频繁进出正是穷人做法；"判断正确"到处都是（牛市里人人都是多头），"判断正确+拿住不动"才稀缺。这是全书最著名的心理纪律条目。
  tags: [term, core-concept, 交易心理, 趋势交易]

- id: g07
  title: tips（小道消息 / 荐股）
  type: term
  source_chapter: 第 15 章、第 16 章（part_06）；第 24 章（part_09）
  source_quote: |
    "Tips! How people want tips! They crave not only to get them but to give them. There is greed involved, and vanity. ... the tip-seeker is not really after good tips, but after any tip. ... The raid excuse for losses that unfortunate speculators so often receive from brokers and financial gossipers is really an inverted tip. The difference lies in this: A bear tip is distinct, positive advice to sell short. But the inverted tip--that is, the explanation that does not explain--serves merely to keep you from wisely selling short."
  summary: |
    tips 是本书用得最多的词之一（各 chunk 合计 60+ 次）。作者定义与常识差异：①求 tip 者要的"不是好 tip，而是任何 tip"（贪欲+虚荣驱动）；②"inverted tip（反向消息）"——券商/圈内人解释暴跌的"利空理由"其实常是掩护操纵者吸货的烟雾，反而阻止你聪明地卖空；③第 3 章名言"nobody can give me a tip or a series of tips that will make more money for me than my own judgment"，第 24 章再补一刀："acting on 'inside' tips will break a man more quickly than famine, pestilence..."。tip 在他笔下不是"信息"，而是"让你依赖别人、放弃自己判断"的毒药。
  tags: [term, core-concept, 信息处理, 反人性]

- id: g08
  title: inside information / inside buying（内幕信息与内幕买盘）
  type: term
  source_chapter: 第 17 章、第 24 章（part_07、part_09）
  source_quote: |
    "I am a trader and therefore looked for one sign: Inside buying. There wasn't any. I didn't have to know why the insiders did not think enough of their own stock to buy it on the decline. It was enough that their market plans plainly did not include further manipulation for the rise. That made it a cinch to sell the stock short."
  summary: |
    内幕信息在书中有两种用法：①"打听来的秘密"——第 24 章指出价值创造的信息被刻意对公众保密，insiders 悄悄扫货（"the value-making information is carefully kept from the public"），且"acting on inside tips will break a man"；②"内幕买盘/卖盘作为读盘信号"——圭亚那金矿案例中作者不看新闻，只盯一个信号：insiders 在自己股票下跌时买不买？"Inside buying. There wasn't any." 据此果断做空，随后传来矿脉变废的消息。与常识差异：普通投资者想"拿到内幕"，作者想的是"用行为推断内幕、并知道内幕消息本身不可依赖"。
  tags: [term, core-concept, 内幕交易, 信号解读]

- id: g09
  title: manipulation / pool（操纵与集团 / 做庄）
  type: term
  source_chapter: 第 17 章、第 18 章（part_07）
  source_quote: |
    "the strength of TT was merely a smoke-screen--a manipulated advance obviously designed to facilitate inside liquidation in Equatorial Commercial, which was largest holder of TT stock. ... The moment the insiders took away their support the price of TT declined."
  summary: |
    manipulation 指大资金集团（pool）有计划地抬拉/打压某只股票以出货或进货；全书后半部（part_07 出现 33 次）反复拆解其手法。TT 案例：热带贸易强势上涨只是"烟幕"，用来掩护关联方在 Equatorial 上出货，支撑一撤价格即跌。作者同时指出（第 19 章）老式操纵手法大多已过时甚至违法（"most of the tricks, devices and expedients of bygone days are obsolete and futile; or illegal and impracticable"）。与常识差异：普通人以为操纵=单边拉升骗散户接盘，作者展示的是"跨股票联动、用一只股票掩护另一只出货"的结构化骗局，以及操纵者的对手盘（公众）必然亏损的结构性原因。
  tags: [term, core-concept, 市场结构, 庄家行为]

- id: g10
  title: short selling（卖空）
  type: term
  source_chapter: 第 3 章、第 8 章（part_01、part_03）
  source_quote: |
    "You ought to have seen that cornered stock, that it was sure suicide to go short of, take a headlong dive when those competitive orders struck it. I let 'em have a few thousand more. The price was 111 when I started selling it. Within a few minutes I took in my entire short line at 92."
  summary: |
    卖空在书中是日常工具而非道德争议：牛市末期"making money when I bought and chipping it out when I sold short"（第 3 章）；第 8 章雷丁铁路被轧空（cornered）的故事则演示卖空的对称风险——所有人都说"做空它等于自杀"时，作者用两笔对敲单击穿空头挤压，111 做空、92 平仓。与常识差异：①作者视做空为与做多完全对称的投机方向（"profit by either a rise or a fall"），没有"做空不道德"的道德包袱；②同时他尊重轧空风险——被 cornered 的股票空头会集体爆仓，卖空者必须懂"对手盘是集团"的力量。注意：本书并未系统论证卖空制度（那是他后期著作的内容）。
  tags: [term, core-concept, 做空, 风险对称]

- id: g11
  title: stop-loss order（止损单）
  type: term
  source_chapter: 第 2 章、第 10 章（part_01、part_04）
  source_quote: |
    "For one thing the automatic closing out of your trade when the margin reached the exhaustion point was the best kind of stop-loss order. You couldn't get stung for more than you had put up and there was no danger of rotten execution of orders, and so on."
  summary: |
    止损在书中不是"技术指标"，而是生存纪律。第 2 章指出投机行的优点：保证金耗尽自动平仓"是最佳止损单"，最多亏完本金、绝无劣质执行；第 10 章职业赌徒 Pat Hearne 的做法是"每次买入后在上方 1 个点设止损，随价格上涨上移止损，回撤 1% 即离场"——"professional gambler is not looking for long shots, but for sure money"。与常识差异：①常识把止损当成"防止更大亏损的保险"，作者强调止损必须与仓位/保证金联动（bucket shop 模式是强制止损）；②Hearne 的"移动止损锁浮盈"在 1920 年代已出现，说明"让利润奔跑、截断亏损"并非现代发明。作者在别处提醒：止损不能制造犹豫（"That should not breed indecision"）。
  tags: [term, core-concept, 风控, 交易纪律]

- id: g12
  title: margin（保证金 / 杠杆）
  type: term
  source_chapter: 第 1 章、第 2 章（part_01）
  source_quote: |
    "You know they'd expect you to keep up a 10 per cent margin, and that means one thousand dollars on one hundred shares. ... Of course, the bucket shops never ask for more margin. The thinner the shoestring the better for them, for their profit lies in your being wiped."
  summary: |
    保证金即杠杆：正规券商 10%（100 股需 1000 美元，第 2 章），投机行低至 1 个点（"one-point margins"），且"从不追加保证金"——因为投机行的利润正来自客户爆仓（"the thinner the shoestring the better for them, for their profit lies in your being wiped"）。与常识差异：①现代语境中 margin 只是券商风控参数，书中 margin 直接决定游戏性质——投机行用极低保证金把客户变成"赌波动"的对手盘，作者在正规券商因保证金高而无法像投机行那样快速进出，反而被迫学会真正的投机；②"margin call 追加保证金"在投机行不存在，爆仓即自动平仓（见 g11）。杠杆大小=游戏类型的分水岭。
  tags: [term, core-concept, 杠杆, 市场结构]

- id: g13
  title: sucker（韭菜 / 冤大头公众）
  type: term
  source_chapter: 第 2 章、第 7 章（part_01、part_03）
  source_quote: |
    "D'yeh see them? ... There's three hundred of 'em! Three hundred suckers! They feed me and my family. See? Three hundred suckers! Then yeh come in, and in two days yeh cop more than I get out of the three hundred in two weeks. That ain't business, kid--not for me!"
  summary: |
    sucker 是投机行老板 Dolan 对客户的称呼（"三百个冤大头养活我全家"），作者借用它定义"公众"的结构性位置：被 tips、操纵、保证金制度反复收割的群体。第 7 章补充公众画像——"He wants to get something for nothing. He does not wish to work. He doesn't even wish to have to think."；第 3 章还区分"plain fool（处处做错的蠢人）"与"Wall Street fool（认为自己必须天天交易的华尔街蠢人）"。与常识差异：sucker 不是"新手"或"穷人"的代称，而是"想要不劳而获、拒绝思考、依赖他人建议"的行为模式；作者认为即使聪明人，只要行为符合这个模式就是 sucker。
  tags: [term, core-concept, 散户行为, 市场参与者]

- id: g14
  title: "nothing new in Wall Street"（华尔街没有新鲜事）
  type: maxim
  source_chapter: 第 1 章（part_01）
  source_quote: |
    "Another lesson I learned early is that there is nothing new in Wall Street. There can't be because speculation is as old as the hills. Whatever happens in the stock market to-day has happened before and will happen again. I've never forgotten that. I suppose I really manage to remember when and how it happened. The fact that I remember that way is my way of capitalizing experience."
  summary: |
    全书第一原则：行情没有新鲜事，今天发生的一切都发生过、还会再发生；投机的关键是记住"何时、如何"发生过，从而把经验资本化（capitalizing experience）。与常识差异：①这不是"历史会重演"的宿命论口号，而是一套方法论的起点——少年时代他用小本子记录"hit and miss"，专门验证自己的观察是否准确（是否 right）；②他强调的是"重复模式"（repetitions and parallelisms of behaviour）与"先例"（precedents），即行为模式可学习，而非价格点位会精确复现。这条是所有交易类 skill 引用本书时的总纲。
  tags: [maxim, core-concept, 交易哲学, 经验主义]

---

## 覆盖范围与核验说明

- **覆盖范围**：本提取基于 Gutenberg #60979 文本的 9 个 chunk。part_01–part_06（第 1–17 章）为逐块精读；part_07–part_09（第 18–24 章）以关键术语定位方式通读相关段落（manipulation/pool、inside、tips、第 24 章结尾总结），未做到逐句精读。
- **原文勘误（重要）**：全文中未出现 "pivotal point" 字样（见 g04），亦未出现 "watered stock" 字样。用户示例中的这两项均无法以原文 quote 支撑，故前者改为"概念条目+用词勘误"，后者未收录（避免编造）。
- **词频佐证**（供后续 skill 参考）：line of least resistance 全书 21 次（part_04 12 次）；tips 60+ 次；manipulation 50+ 次（part_07 33 次）；margin 50+ 次；bucket shop 70+ 次；tape reading 15+ 次；pyramid 6 次；stop-loss 3 次（概念另见"自动平仓"与 Hearne 案例）。
- **章号映射**：part_01=第 1–3 章；part_02=第 4–6 章；part_03=第 7–9 章；part_04=第 10–12 章；part_05=第 13–14 章；part_06=第 15–17 章；part_07=第 18–21 章；part_08=第 22–23 章；part_09=第 24 章（及结尾 Transcriber's Notes）。
