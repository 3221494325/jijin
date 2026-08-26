# 案例提取：Reminiscences of a Stock Operator（《股票大作手回忆录》）

- 提取器：case-extractor（cangjie 流水线阶段 1）
- 输入：BOOK_OVERVIEW.md（原文件中文已损坏为“?”，结构信息仍可辨认）；正文 9 个分块 part_01-09（约 59 万字符，已全部精读）
- 覆盖范围：第 I–XXIV 章（part_01→I-III；part_02→IV-VI；part_03→VII-IX；part_04→X-XII；part_05→XIII-XIV；part_06→XV-XVII；part_07→XVIII-XXI；part_08→XXII-XXIII；part_09→XXIV）
- 提取口径：主角 Larry Livingston（原型 Jesse Livermore）亲历的实盘案例，每条绑定方法论主题，聚焦基金持仓管理五大关切：抄底/接刀、止损、拿住盈利、消息陷阱、重仓集中。

## 案例列表（共 10 条）

- id: c01
  title: 投机行天才到纽约折戟：同一套“刮头皮”方法换市场即失效
  type: case
  source_chapter: 第 3 章（part_01）
  source_quote: |
    "On that, my first day as a customer of a reputable Stock Exchange
    house, and only two hours of it at that, I traded in eleven hundred
    shares of stock, jumping in and out. And the net result of the day's
    operations was that I lost exactly eleven hundred dollars. That is to
    say, on my first attempt, nearly one-half of my stake went up the flue."
  summary: |
    问题：15 岁起在投机行靠读盘刮小差价屡战屡胜（首月赚 1,000 美元、20 岁前赚到 1 万美元），
    到纽约正规券商处沿用同一方法，首日两小时进出 1,100 股，净亏 1,100 美元，相当于本金近半。
    处理：把失败归因于“机器不对”而非方法错，继续高频进出，六个月内亏光全部本金并倒欠券商数百美元；
    借 500 美元回投机行重打，靠投机行“即时按报价结算、无冲击成本”的规则优势回血。
    结果：反复破产两次后终于意识到，投机行是“赌波动”，交易所是“吃滑点与自成交冲击”，
    必须从“读下一个报价”转向“预判大势”，这是全书第一课。
  bound_to:
    - 方法-市场匹配
    - 交易成本（滑点与冲击成本）
    - 从小赢大亏到趋势交易
  outcome: 纽约六个月内亏光并欠债；但保住读盘与记忆两项资产，为转向趋势交易埋下伏笔。
  tags: [case, 方法错配, 高频刮头皮, 小赢大亏, 滑点]

- id: c02
  title: 1901-05-09 北方铁路逼空日：看对方向却一天亏光全部本金
  type: case
  source_chapter: 第 3 章（part_01）
  source_quote: |
    "The market fairly boiled, as I had expected... but by the time they
    executed my orders the stocks had broken twenty points more. The tape
    was way behind the market... When I found out that the stocks I had
    ordered sold when the tape said the price was, say, 100 and they got
    mine off at 80... I decided instantly to cover my shorts and go long.
    My brokers bought... They paid an average of fifteen points more than
    I had figured on. A loss of thirty-five points in one day was more
    than anybody could stand."
  summary: |
    问题：1901 年 5 月 9 日北方铁路逼空日，他看空数日、手握近 5 万美元等暴跌捡便宜，
    市场果然暴跌，但他的市价卖单因行情机（ticker）滞后 20-40 点，成交在极低价位。
    处理：看到成交价后认定“市场不会跌穿地板”，瞬间反手做多接刀，结果买入又平均高出 15 点，
    当日单边亏损 35 点，相当于本金 5 万美元全部亏光。
    结果：他承认“盘面读数”不是全部——恐慌日报价滞后、流动性枯竭、追单与接刀双向踩踏；
    事后总结必须同时解决“判断大势”与“执行方式”两个问题，只靠读盘不足以赚钱。
  bound_to:
    - 恐慌日流动性风险
    - 追单与接刀
    - 看对方向不等于做对交易
  outcome: 5 万美元本金一日归零；随后借 500 美元回投机行重来。
  tags: [case, 恐慌日, 追单, 接刀, 滑点, 看对做错]

- id: c03
  title: “牛市要坐着不动”：看对却拿不住的大钱教训（老火鸡 Partridge）
  type: case
  source_chapter: 第 5 章（part_02）
  source_quote: |
    "It never was my thinking that made the big money for me. It was
    always my sitting. Got that? My sitting tight!... I've known many men
    who were right at exactly the right time... And their experience
    invariably matched mine--that is, they made no real money out of it.
    Men who can both be right and sit tight are uncommon. I found it one
    of the hardest things to learn. But it is only after a stock operator
    has firmly grasped this that he can make big money."
  summary: |
    问题：老火鸡 Partridge 的故事——Elmer 劝他在 Climax Motors 上先止盈、等回调再买回，
    老人拒绝：“如果我卖了，我就失去了我的仓位（position）”；旁观者 Livingston 对号入座：
    自己在牛市起点就看对，却听“老前辈”建议频繁止盈等回调，而回调从不来，对的时候只赚零头。
    处理：把“大钱来自大趋势（main movements）而非单个波动”内化为原则：判断趋势后买入持有，
    直到确认牛市结束，再彻底离场；并戒掉“抓最后一档/第一档”的执念。
    结果：此后他能在空头巨仓浮盈回吐一半时不动摇，靠“坐得住”赚到数百万美元级别利润。
  bound_to:
    - 拿住盈利
    - 趋势交易
    - 避免过早止盈
  outcome: 成为其交易观的转折点；后文多次描述自己“空 10 万股看到必然反弹也不平仓”。
  tags: [case, 拿住盈利, 坐得住, 趋势, 过早止盈]

- id: c04
  title: 1906 年联合太平洋：被“权威朋友”劝出多头、反手做空遭 10% 股息打爆
  type: case
  source_chapter: 第 6 章（part_02/03）
  source_quote: |
    "I sold out all my Union Pacific. Of course if it was unwise to be
    long of it, it was equally unwise not to be short of it. So after I
    got rid of my long stock I sold four thousand shares short. I put out
    most of it around 162. The next day the directors of the Union Pacific
    Company declared a 10 per cent dividend on the stock... the market
    boiled over. Union Pacific led, and on huge transactions made a new
    high-record price."
  summary: |
    问题：Saratoga 度假期间，他从盘面读出联合太平洋（UP）正被“聪明钱”吸筹并一路加仓；
    消息灵通的好友 Ed Harding 打长途警告“内线正在把货倒给你，你是最好骗的”，他动摇。
    处理：不仅清掉多头，还反手在 162 附近做空 4,000 股——“既然不该做多，就该做空”；
    次日 UP 董事会宣布 10% 股息，股价跳涨创历史新高，空头被彻底打爆。
    结果：他承认“我按了他的建议做了”，却无法解释为什么放弃自己多年训练的盘面判断；
    事后第 8 章他总结连续挨打的核心错误是“在熊市一开始就重仓做空，跑得太早”。
  bound_to:
    - 消息陷阱
    - 他人意见 vs 自己体系
    - 反手报复性交易
  outcome: UP 大涨后巨额亏损；并引发其随后“急于证明自己正确”的过早重仓做空，二次受损。
  tags: [case, 消息陷阱, 权威意见, 反手, 内线操纵]

- id: c05
  title: 1907 年初做空 Reading：等待“关键点”确认后的重仓集中做空（111→92）
  type: case
  source_chapter: 第 8 章（part_03）
  source_quote: |
    "I figured that the price held because the Street was afraid to sell
    it. So one day I gave to two brokers each an order to sell four
    thousand shares, at the same time. You ought to have seen that
    cornered stock... take a headlong dive when those competitive orders
    struck it... The price was 111 when I started selling it. Within a few
    minutes I took in my entire short line at 92."
  summary: |
    问题：经历了“熊市初期太早重仓做空被反复打脸”后，他把“开始时机”列为第一课，
    等待确认信号：北太平洋/大北方铁路推出“分期认购”新股的广告，等于银行家公开承认缺钱。
    处理：确认后开始系统性做空（大北方优先股 330 起）；全场皆跌、唯 Reading 因“被逼空”
    传言横盘，他判断是“大众不敢卖”而非真强势——同时向两个经纪人各下 4,000 股卖单试探，
    股价应声跳水，111 起空、几分钟内在 92 全部回补。
    结果：1907 年 2 月清仓兑现（大北方优先股已跌 60-70 点），随后主动离场度假，
    为秋天更大的行情保留资金与仓位空间。
  bound_to:
    - 关键点/时机确认
    - 重仓集中
    - 试探性建仓与加码
  outcome: Reading 空单数分钟内每股约 19 点利润；2 月“cleaned up”，资金规模上台阶。
  tags: [case, 关键点, 重仓集中, 做空, 试探建仓]

- id: c06
  title: 1907-10-24 恐慌日：空头巨仓反手做多，单日净赚超过 100 万美元
  type: case
  source_chapter: 第 9 章（part_03/04）
  source_quote: |
    "When the commission houses found out there was not a cent to be had
    at any price I knew the time had come... at one time there wasn't a
    single bid for Union Pacific. Not at any price!... I made up my mind
    that since it was unwise and unpleasant to continue actively bearish
    it was illogical for me to stay short. So I turned and began to buy...
    It was the day when my winnings exceeded one million dollars. It
    marked the successful ending of my first deliberately planned trading
    campaign."
  summary: |
    问题：1907 年 10 月 24 日，隔夜拆借利率飙到年化 100-150%，经纪行借不到钱、
    联合太平洋竟无人出价，恐慌到极致；他手握巨额空头浮盈，加空单足以把市场砸到停牌。
    处理：判断继续做空“不明智也不愉快”，会拖慢自己预期的复苏，于是反手买入——
    用恐慌日罕见的流动性，把纸面利润全部换成现金（“我买在了底部价格”）。
    结果：当日盈利超过 100 万美元，“做了一天国王”，也是他第一次按完整计划打完的战役。
    对基金的含义：极端流动性枯竭既是兑现窗口也是逆向调仓窗口，但前提是提前有仓位与子弹。
  bound_to:
    - 恐慌日逆向
    - 止盈兑现
    - 流动性枯竭处理
    - 完整战役计划
  outcome: 单日净赚超 100 万美元，成为其交易生涯标志性战役。
  tags: [case, 恐慌日, 逆向, 止盈, 流动性, 1907]

- id: c07
  title: 1908 年棉花：被 Percy Thomas 的“权威内幕数据”说服，放弃自己的空头判断
  type: case
  source_chapter: 第 12 章（part_04/05）
  source_quote: |
    "When he began his talks with me about the cotton situation I not only
    was bearish but I was short of the market. Gradually, as I began to
    accept his facts and figures, I began to fear I had been basing my
    previous position on misinformation. Of course I could not feel that
    way and not cover. And once I had covered because Thomas made me think
    I was wrong, I simply had to go long."
  summary: |
    问题：棉花大佬 Percy Thomas（“我见过最有魅力的人”）带着“南方一万名通讯员的独家数据”
    反复游说，把他从“空头且持有空单”讲到“怀疑自己的信息不可靠”。
    处理：他无法反驳数据真实性，于是“不再用自己的眼睛看市场”，先平掉空单，又因
    “错了就必然反着做”的思维定式反手做多棉花——彻底放弃独立判断。
    结果：第 13 章显示代价惨重，其中一笔收盘前追买的棉花单笔亏约 40 万美元；
    他自嘲“一个人无法被说服去反对自己的信念，却能被谈进犹豫不决的状态，那更糟”。
  bound_to:
    - 消息陷阱
    - 权威人物与独家数据
    - 独立判断
    - 空翻多的立场漂移
  outcome: 棉花头寸累计亏损数十万美元（含一笔 40 万），并连锁拖入 Williamson 人情账户困局。
  tags: [case, 消息陷阱, 权威数据, 独立判断, 棉花]

- id: c08
  title: 1911 年 Williamson 人情账户：恩情绑架+被当挡箭牌，错失一生最大机会
  type: case
  source_chapter: 第 13 章（part_05）
  source_quote: |
    "I couldn't do less than to thank him. And so my feelings again won
    over my judgment and I gave in. To subordinate my judgment to his
    desires was the undoing of me. Gratitude is something a decent man
    can't help feeling, but it is for a fellow to keep it from completely
    tying him up. The first thing I knew I not only had lost all my profit
    but I owed the firm one hundred and fifty thousand dollars besides."
  summary: |
    问题：破产后 Dan Williamson 借他 2.5 万美元本金，三周赚 11.2 万却不让他还钱；
    随后以“我知道这家公司的内情”为由，把他 8,000 股 Chesapeake & Atlantic 空单平掉反手做多，
    他因感恩放弃判断照做，亏损累计到欠券商 15 万美元。
    处理：彻底交权——“别自己交易，我来替你赚回来”，亏损由对方用“编号账户”神秘填补，
    他多年后才醒悟自己被用作掩护内兄 Marquand 遗产出货的“烟幕”。
    结果：1911-1914 四年市场无机会且他深陷债务，错过“一生中最大的机会”；
    他总结“作为投机者，业务就是永远支持自己的判断”，感恩不能成为交易决策的输入。
  bound_to:
    - 委托代理与账户独立
    - 人情绑架
    - 交易决策权归属
    - 机会成本
  outcome: 净亏损+欠债 15 万美元；浪费 1911-1914 四年，1915 年才靠 Bethlehem 翻身。
  tags: [case, 治理, 人情绑架, 委托代理, 机会成本]

- id: c09
  title: 1915 年 Bethlehem Steel：关键点进场，一次翻身（98→114→145）
  type: case
  source_chapter: 第 14 章（part_05）
  source_quote: |
    "I didn't go near Williamson & Brown's... six long weeks of steady
    tape reading... The stock I was most bullish on in those critical days
    of early 1915 was Bethlehem Steel. I was morally certain it was going
    way up, but... I decided to wait until it crossed par... I rushed to
    Williamson & Brown's office and put in an order to buy five hundred
    shares of Bethlehem Steel. The market was then 98. I got five hundred
    shares at 98 to 99. After that she shot right up, and closed that
    night... at 114 or 115... The next day Bethlehem Steel was 145 and I
    had my stake."
  summary: |
    问题：破产 4 年、交易所因一战停市 7 个月后，他只剩 Williamson 给的“500 股额度”，
    且第一单必须盈利，否则再无翻身机会。
    处理：六周不靠近券商办公室、只看盘不动手，等自己最有把握的 Bethlehem Steel 突破 100
    （关键点/面值）——98-99 买入 500 股，当夜收 114-115、次日 145，随即加仓。
    结果：用一次“必胜”的集中一击重获本金，1915 年底账户回到 14 万美元，
    1916 年先做多后做空净赚约 300 万美元。
    教训：资金受限时“时机正确+集中一击”远胜分散试错；关键点突破是最可靠的进场信号之一。
  bound_to:
    - 关键点进场
    - 突破买入
    - 资金受限下的第一仓必胜
    - 自控与等待
  outcome: 500 股→次日 145，重获交易本金，开启 1915-1916 复出。
  tags: [case, 关键点, 突破, 翻身, 自控]

- id: c10
  title: 5 万包棉花空单：等回调再止损，小亏拖成大亏（25 万美元）
  type: case
  source_chapter: 第 17 章（part_06/07）
  source_quote: |
    "Whenever I thought of cotton I just said to myself: 'I'll wait for a
    reaction and cover.' The price would react a little but before I could
    decide to take my loss and cover, the price would rally again, and go
    higher than ever. So I'd decide again to wait a little and I'd go back
    to my stock deal... I had a loss of $250,000 on my 50,000 bales."
  summary: |
    问题：做空 5 万包棉花的同时在股票上大赚，于是“忙得顾不上”处理棉花浮亏：
    每次想平仓就对自己说“等反弹再走”，而反弹永远不够深、价格不断新高。
    处理：拖延到股票头寸了结、去 Hot Springs 度假、脑子空出来，才正面面对棉花问题，
    最终认亏平仓，并靠后面的操作把损失赚了回来。
    结果：单笔浮亏滚到 25 万美元，是典型的“小亏拖成大亏”。
    教训：止损不能依赖“等个好价”；被盈利仓位分散注意力而拖延止损，比方向看错更致命——
    止损规则应无条件执行、与其他持仓表现解耦。
  bound_to:
    - 止损执行
    - 拖延止损
    - 注意力分散
    - 仓位独立管理
  outcome: 25 万美元浮亏最终认亏；作者称靠“经验与记忆”在后续操作中赚回。
  tags: [case, 止损, 拖延, 小亏拖大亏, 棉花]

## 覆盖范围说明

- 已精读全部 9 个分块（part_01-09，约 59 万字符），覆盖第 I-XXIV 章，未编造内容。
- 原书 chunk 内无显式章号，章号依据正文中的罗马数字标题（_IV_、_V_、_IX_ 等）逐一比对得出；
  每条同时标注 chunk 号以便回溯。
- 10 条案例对应五大基金持仓主题：抄底/接刀（c02、c06）、止损（c10、c02）、
  拿住盈利（c03、c05）、消息陷阱（c04、c07、c08）、重仓集中（c05、c06）。
- 说明：BOOK_OVERVIEW.md 的源文件中文已损坏为“?”（写入时编码丢失），
  其结构信息（24 章分段、方法论锚点）与正文核对一致，不影响上述案例归属。
