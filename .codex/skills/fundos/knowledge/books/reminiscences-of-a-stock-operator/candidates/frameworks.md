# 候选框架单元 — Reminiscences of a Stock Operator（股票大作手回忆录）

> 提取器：framework-extractor（cangjie 蒸馏流水线）
> 输入：BOOK_OVERVIEW.md + chunks/part_01.txt ~ part_09.txt（全 9 块已扫描）
> 用途：面向基金持仓管理的可迁移决策框架 / 思维模型 / 推理方法
> 说明：全部条目均出自书中原文（英文 quote 为原书文字），无虚构；阶段 1.5 将做三重验证与去重。

- id: f01
  title: 最小阻力线（趋势跟随）
  type: framework
  source_chapter: 第10-11章 / part_04 chunk
  source_quote: |
    "For purposes of easy explanation we will say that prices, like everything else, move along the line of least resistance. They will do whatever comes easiest, therefore they will go up if there is less resistance to an advance than to a decline; and vice versa. Nobody should be puzzled as to whether a market is a bull market or a bear market after it fairly starts."
  summary: |
    不要预测价格目标或猜顶猜底，而是判断价格沿哪个方向运行"最省力"：
    上涨阻力小就顺势做多，下跌阻力小就顺势做空，阻力相当就是震荡观望。
    判定依据来自市场自身行为（价格与成交的配合），而非个人观点、估值或消息。
    对基金持仓管理：先定大方向（多/空/震荡），只沿最小阻力方向配置仓位；
    方向一旦确立（趋势明显展开）就不必困惑于"该买该卖"；
    价格高低本身不构成买卖理由，趋势位置才是。
  tags: [trend-following, line-of-least-resistance, mental-model]

- id: f02
  title: 关键点（等待最小阻力线自我定义）
  type: framework
  source_chapter: 第11章 / part_04 chunk
  source_quote: |
    "Therefore the thing to determine is the speculative line of least resistance at the moment of trading; and what he should wait for is the moment when that line defines itself, because that is his signal to get busy. ... In other words, by crossing $1.20 the line of least resistance of wheat prices was established."
  summary: |
    关键点不是某个预测出来的价位，而是市场行为"自我定义方向"的那个时刻：
    例如小麦突破 $1.20 之后，最小阻力线才被确立，此后价格顺势而行。
    在此之前不行动、不预判、不抢跑；等到信号出现才动手。
    书中反面教训：他因急于抢跑棉花、试图"帮市场一把"，错过了整段行情。
    对基金：用明确的突破/确认信号代替主观抄底摸顶；
    宁可错过也不做错，让市场走出来之后再加注，
    避免"判断对了但时机错了"这一最典型的亏损模式。
  tags: [timing, entry-signal, pivotal-point]

- id: f03
  title: 试探仓与金字塔加仓
  type: framework
  source_chapter: 第11章 / part_04 chunk
  source_quote: |
    "He should accumulate his line on the way up. Let him buy one-fifth of his full line. If that does not show him a profit he must not increase his holdings because he has obviously begun wrong; he is wrong temporarily and there is no profit in being wrong at any time. ... Suppose the line of least resistance indicated a bull movement. Well, I would buy ten thousand bales. After I got through buying that, if the market went up ten points over my initial purchase price, I would take on another ten thousand bales."
  summary: |
    建仓分步验证：先买计划仓位的五分之一（或首批试探仓），
    只有价格证明方向正确（出现浮盈）才允许加仓；
    首仓浮亏即说明开始就错了，绝不加仓摊平，立即退出。
    加仓幅度随盈利扩大而递增（涨 10 点加 10 千，涨 20 点加 20 千），
    使总仓位始终朝最小阻力方向累积。
    试探阶段的亏损被视作"检验成本"：只要最终在正确时点重仓，
    试探费很快被大行情赚回——"在正确的时间正确"永远值得。
    对基金：把建仓拆成"验证-确认-加码"三段，用市场验证代替个人自信。
  tags: [pyramiding, position-sizing, testing]

- id: f04
  title: 止损即认错（亏损不是错误，不认错才是）
  type: framework
  source_chapter: 第12章 / part_04 chunk
  source_quote: |
    "Losing money is the least of my troubles. A loss never bothers me after I take it. I forget it overnight. But being wrong--not taking the loss--that is what does the damage to the pocketbook and to the soul. ... 'I am carrying so much cotton that I can't sleep thinking about it. It is wearing me out. What can I do?' 'Sell down to the sleeping point,' answered the friend."
  summary: |
    把"亏损"与"犯错"分开：已实现的亏损是过去的信息，执行后立即翻篇；
    真正的伤害来自"错了却不肯认、不肯执行离场"——那才是伤钱又伤神。
    配套操作意象是"卖到能睡着的仓位规模"：把持仓降到让自己安心的程度。
    对基金：止损纪律的核心是把"认错"操作化——
    预先设定离场线、达到条件机械执行、事后不纠结不报复性交易；
    仓位大小应服从"持仓不影响决策质量"这一标准，而非收益目标。
  tags: [stop-loss, risk-management, discipline]

- id: f05
  title: 拿住盈利（坐得住）
  type: framework
  source_chapter: 第5章 / part_02 chunk
  source_quote: |
    "It never was my thinking that made the big money for me. It was always my sitting. Got that? My sitting tight! It is no trick at all to be right on the market. You always find lots of early bulls in bull markets and early bears in bear markets. ... Men who can both be right and sit tight are uncommon. I found it one of the hardest things to learn."
  summary: |
    判断正确的人很多，能在正确后拿住头寸的人极少；大钱不是赚在进场时，
    而是赚在持有期。老 Partridge 的回答"如果我卖了就会失去我的位置"，
    把"位置"定义为大趋势中的持仓资格——它比眼前几个点的差价更值钱。
    市场不会打败你，多数人是自己打败自己：因为等不起、拿不住。
    对基金：看对大方向后，用"仓位+持有"表达观点而非频繁交易；
    盈利仓位的最大敌人是落袋为安的冲动和对短期反向的恐慌。
  tags: [holding, patience, trend]

- id: f06
  title: 研判大环境（大钱在大行情，顺大势而为）
  type: framework
  source_chapter: 第8章 / part_03 chunk
  source_quote: |
    "I began to realize that the big money must necessarily be in the big swing. ... my greatest discovery was that a man must study general conditions, to size them so as to be able to anticipate probabilities. In short, I had learned that I had to work for my money."
  summary: |
    大钱来自大行情（big swing），而大行情由一般市场条件
    （general conditions：货币、经济、资金面等整体环境）驱动，
    不是个股消息或庄家操纵所能长期维持的。
    赚钱靠的是研究整体环境、据此推算未来概率，而不是盘感或小道消息。
    对基金：自上而下先定大环境（牛/熊/震荡），再在其中选标的与时机；
    把"顺大势"作为持仓的首要约束——逆环境的重仓是主要亏损来源，
    环境变化时应系统性降杠杆或调方向，而不是跟单一标的死磕。
  tags: [general-conditions, top-down, macro]

- id: f07
  title: 独立判断（不信消息、不把决策外包给他人）
  type: framework
  source_chapter: 第3章+第13章 / part_01+part_05 chunk
  source_quote: |
    "I know from experience that nobody can give me a tip or a series of tips that will make more money for me than my own judgment. It took me five years to learn to play the game intelligently enough to make big money when I was right. ... Instead of standing or falling by my own observation and deductions I was merely playing another man's game."
  summary: |
    依赖别人的消息买入，就得依赖别人卖出——卖点不在自己控制内，
    等于把资金命运交给对方；因此必须建立自己的观察与推理闭环。
    Percy Thomas 事件是反面教材：他听信魅力型权威、放弃自己的推理，
    事后自评"我只是在玩别人的游戏"，为此付出千万级学费。
    对基金：消息、卖方观点、名人判断只能作为输入，
    必须经过自己的验证流程后才可进入决策；
    当外部观点与自身证据冲突时，以证据和价格行为为准。
  tags: [independent-thinking, anti-tip, conviction]

- id: f08
  title: 信息不对称下的价格解读（价格行为优先于解释）
  type: framework
  source_chapter: 第23-24章 / part_09 chunk
  source_quote: |
    "The public should beware of explanations that explain only what unnamed insiders wish the public to believe. ... When a stock keeps on going down you can bet there is something wrong with it, either with the market for it or with the company. ... In a bull market and particularly in booms the public at first makes money which it later loses simply by overstaying the bull market."
  summary: |
    内部人买在沉默中、卖也在沉默中；公开的"解释"多数服务于
    派发或接盘：利多解释帮内部人出货，利空解释劝散户别卖。
    持续下跌极少是"空头袭击"，而是公司或市场本身出了问题；
    持续上涨也无需解释——连续买盘就是最可靠的"利多"。
    对基金：给"匿名来源的解释"大幅降权，
    用价格与成交行为推断真实信息流；
    警惕"利多新闻多到需要解释"的阶段，那通常是派发期，
    以及牛市后期"赚钱却在纸上"的过度停留（overstaying）。
  tags: [information-asymmetry, price-action, skepticism]

- id: f09
  title: 对抗内在敌人（情绪管理制度化）
  type: framework
  source_chapter: 第2章+第11章 / part_01+part_04 chunk
  source_quote: |
    "A stock operator has to fight a lot of expensive enemies within himself. ... There is the plain fool, who does the wrong thing at all times everywhere, but there is the Wall Street fool, who thinks he must trade all the time. No man can always have adequate reasons for buying or selling stocks daily. ... a man has to guard against many things, and most of all against himself--that is, against human nature."
  summary: |
    最大的对手不是市场而是自己：必须每天交易的冲动、
    希望与恐惧、对"每天赚点钱"的执念——这些是昂贵的内部敌人。
    解法不是靠意志硬扛，而是把"只在有充分理由时出手"变成硬条件：
    没有理由就不交易，等待本身也是仓位。
    对基金：把情绪管理制度化——交易清单、冷静期、仓位上限、
    强制复盘；识别自己进入"必须做点什么"的状态时先停手；
    防止把基金当赌场、把操作当情绪出口。
  tags: [emotion, self-discipline, psychology]

- id: f10
  title: 时间要素（市场领先现实 6-9 个月）
  type: framework
  source_chapter: 第8章+第24章 / part_03+part_09 chunk
  source_quote: |
    "There was a vast difference in our appraisal of the element of time. The analysis of the week that had passed was less important to me than the forecast of the weeks that were to come. ... the course of the market is always from six to nine months ahead of actual conditions."
  summary: |
    市场行情总是领先实际经营状况 6-9 个月：
    用当下的业绩数据解释、交易当下的价格，本质上是对错了时间轴。
    "时间要素"是他反复吃亏的原因——诊断正确但时机错误，
    或在正确的方向上下注太早而被震荡洗出局。
    对基金：建立前瞻窗口，研究未来 6-9 个月的基本面演化，
    而不是追当前景气数据；买入决策要问"六个月后逻辑是否仍成立"；
    把"提前量"同时用于进场时机与离场时机两个方向。
  tags: [time-element, forward-looking, leading-indicators]

## 实际覆盖范围说明

- 精读（全文逐段读入）：part_01–part_05（第1-14章）、part_09（第23章末-第24章）。
- 全文扫描 + 框架相关段落提取：part_06–part_08（第15-23章，以操纵/战争行情叙事为主、框架密度低）。
- 9 个 chunk 全部覆盖；关键框架集中段（第2、5、8、10-13、24章）均以原文引文核实。
- 书中无 "pivotal point" 原词（该术语出自 Livermore 后来的著作），故 f02 采用书中原始表述
  "wait for the moment when that line defines itself" 与小麦 $1.20 案例。
