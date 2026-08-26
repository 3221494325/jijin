# Framework Candidates —《巴菲特致股东信》精选 12 封（1977/79/84/87/89/93/97/05/08/16/22/24）

> 提取器：framework-extractor（cangjie 蒸馏流水线）
> 输入：BOOK_OVERVIEW.md（全局锚点）+ chunks/sub_01.txt ~ sub_14.txt
> 日期：2026-08-08
> 说明：共 10 条候选，全部有原文引文支撑；聚焦对基金持仓管理有用的估值/能力圈/恐慌买入/长期持有/仓位框架。原文引文逐字取自分块文本（≤100 词）。

- id: f01
  title: 内在价值 vs 账面价值：先选对衡量标尺
  type: framework
  source_chapter: 1993 年致股东信（另见 1984/1989/2016）
  source_quote: |
    “Of course, it’s per-share intrinsic value, not book value, that counts. Book value is an
    accounting term that measures the capital, including retained earnings, that has been put
    into a business. Intrinsic value is a present-value estimate of the cash that can be taken
    out of a business during its remaining life. At most companies, the two values are unrelated.”
  summary: |
    估值的第一步是选对标尺：账面价值只记录投入企业的资本（含留存收益），内在价值则是
    “剩余寿命内可取出现金”的现值估计，两者在多数公司几乎无关。伯克希尔反复强调
    “真正起作用的衡量标准是每股内在价值的增长”（1984），账面价值只是“有用但被低估的
    代理指标”。内在价值无法精确计算，只能估计（1984：calculations of intrinsic business
    value are subjective），2016 年补充“长期看股价向内在价值靠拢”。
    对基金持仓：不能以净值增长或每股收益增速论成败，必须回到“底层资产未来能产生多少
    现金”这一层；结论应以区间而非精确数字呈现。
  tags: [valuation, intrinsic-value, book-value, estimation]

- id: f02
  title: 未来现金流折现估值（DCF 思考法，伊索寓言式机会成本）
  type: framework
  source_chapter: 1989 年致股东信
  source_quote: |
    “What counts, however, is intrinsic value - the figure indicating what all of our constituent
    businesses are rationally worth. With perfect foresight, this number can be calculated by
    taking all future cash flows of a business - in and out - and discounting them at prevailing
    interest rates. So valued, all businesses, from manufacturers of buggy whips to operators
    of cellular phones, become economic equals.”
  summary: |
    所有资产的估值本质是同一道算术题：把未来全部现金流入与流出按当前利率折现到现在。
    一旦用这把尺子衡量，“卖鞭子的”与“卖手机的”就变成可比的经济体，差异只来自现金流的
    大小、时间与确定性，而非行业标签或题材。这是“伊索寓言”式机会成本思维的定量版：
    同信还以 a-bird-in-the-bush-may-be-worth-two-in-the-hand 讨论留存收益被优秀管理层
    再投资的价值。对基金：先问“底层资产十年后能赚多少现金、该用什么折现率”，再判断
    价格是否值得；避免用赛道、概念或历史涨幅替代现金流折现。
  tags: [valuation, dcf, cash-flow, opportunity-cost]

- id: f03
  title: 盈余质量分层：受限 vs 非受限盈余（所有者盈余的思想源头）
  type: framework
  source_chapter: 1984 年致股东信（另见 1989）
  source_quote: |
    “The first point to understand is that all earnings are not created equal. In many businesses
    particularly those that have high asset/profit ratios - inflation causes some or all of the
    reported earnings to become ersatz. The ersatz portion - let’s call these earnings
    “restricted” - cannot, if the business is to retain its economic position, be distributed
    as dividends.”
  summary: |
    会计利润并不平等：高资产/利润比的企业里，通胀会把部分报告盈余变成“赝品”，这部分
    受限盈余若被分掉，企业将在单位销量、长期竞争地位或财务实力上退步，因此必须被
    “征用”留存。留存是否合理只有一条规则：每留存 1 美元，须有合理前景（最好有历史
    证据或前瞻分析背书）至少创造 1 美元市值，否则应分给股东。该思想后来被凝练为
    “所有者盈余”（净利润+折旧摊销-维护性资本开支）概念；1989 年又给出“透视盈余”
    （look-through）视角：把被投资方留存经营盈余并入自己的真实盈利能力。
    对基金：评估基金/企业真实产出要扣除维护性资本开支与会计水分，警惕高分红率掩盖
    的受限盈余。
  tags: [valuation, owner-earnings, earnings-quality, capital-allocation]

- id: f04
  title: 市场先生：价格是仆人，不是向导
  type: framework
  source_chapter: 1987 年致股东信（另见 1993）
  source_quote: |
    “But, like Cinderella at the ball, you must heed one warning or everything will turn into
    pumpkins and mice: Mr. Market is there to serve you, not to guide you. It is his pocketbook,
    not his wisdom, that you will find useful. If he shows up some day in a particularly foolish
    mood, you are free to either ignore him or to take advantage of him, but it will be disastrous
    if you fall under his influence. Indeed, if you aren’t certain that you understand and can
    value your business far better than Mr. Market, you don’t belong in the game.”
  summary: |
    把市场报价想象成一位躁郁症合伙人的每日报价：情绪亢奋时报高价，沮丧时报低价，且
    不介意被无视，交易完全由你选择；他越狂躁，机会越多（1993 年原文）。关键纪律是
    “服务你而非指导你”：用他的口袋（报价）而不是他的智慧（情绪）做决策，愚蠢报价
    可忽略也可利用，但绝不能受其影响。衍生两条规则：(1) 用企业经营结果而非每日或
    年度报价评判成败——市场短期是投票机、长期是称重机；(2) 若不能比市场先生更懂并
    更准地给企业估值，就不该下场。对基金：净值波动是报价不是价值，回撤本身不是
    卖出理由，反而可能是买点。
  tags: [mental-model, mr-market, market-volatility, emotion]

- id: f05
  title: 安全边际：以买整家企业的标准买碎股
  type: framework
  source_chapter: 1984 年致股东信（另见 1977/1997）
  source_quote: |
    “Simply put, we feel that if we can buy small pieces of businesses with satisfactory
    underlying economics at a fraction of the per-share value of the entire business, something
    good is likely to happen to us - particularly if we own a group of such securities.”
  summary: |
    用“买整家企业”的标准买上市公司的零散股份：当你能以每股整家企业价值的很小一部分
    买入一块好生意时，好事大概率发生，持有一组这样的证券尤甚。这就是安全边际的运作
    机制；1977 年指出“卓越企业的碎股有时相对整买价格出现巨大折价，这种折价只能通过
    买股票间接获得”，1997 年则明确称其为“Ben Graham 认定的明智投资的基石”——同年
    巴菲特警告当时股价已“实质性地侵蚀了安全边际”。对基金：建仓前先问“若这是整家
    公司我愿意付多少”，只在价格显著低于估值时出手；折扣本身是对判断失误的缓冲，
    市场越热安全边际越薄，越应降低仓位而非加码。
  tags: [valuation, margin-of-safety, business-valuation, entry-price]

- id: f06
  title: 能力圈：圈外错过不是罪，圈内犹豫同样致命
  type: framework
  source_chapter: 1989 年致股东信（另见 1987/1977）
  source_quote: |
    “Some of my worst mistakes were not publicly visible. These were stock and business
    purchases whose virtues I understood and yet didn’t make. It’s no sin to miss a great
    opportunity outside one’s area of competence. But I have passed on a couple of really big
    purchases that were served up to me on a platter and that I was fully capable of
    understanding. For Berkshire’s shareholders, myself included, the cost of this thumb-sucking
    has been huge.”
  summary: |
    能力圈框架有两面：圈外机会看不懂，错过不是罪；圈内机会看懂了却因犹豫不敢下手
    （thumb-sucking），代价同样巨大。圈的边界由“能否比市场先生更懂并更准地估值”界定
    （1987 原文），1977 年四重筛选标准的第一条就是“生意要看得懂”，第四条才是“价格
    要有吸引力”——理解先于价格。对基金：只持有自己真正理解底层逻辑的基金/资产；
    不理解的热点宁可错过；同时要区分“圈外不碰”与“圈内不敢下手”，后者同样要治，
    事前制定分批买入计划可对抗犹豫。
  tags: [mental-model, circle-of-competence, discipline, opportunity]

- id: f07
  title: 恐慌买入框架：广泛恐惧是朋友，个人恐惧是敌人
  type: framework
  source_chapter: 2016 年致股东信（另见 2008）
  source_quote: |
    “During such scary periods, you should never forget two things: First, widespread fear is
    your friend as an investor, because it serves up bargain purchases. Second, personal fear
    is your enemy. It will also be unwarranted. Investors who avoid high and unnecessary costs
    and simply sit for an extended period with a collection of large, conservatively-financed
    American businesses will almost certainly do well.”
  summary: |
    恐慌一定会来（“未来岁月会不时出现重大下跌，甚至恐慌，几乎影响所有股票”），且无人
    能预告时点。核心是把“别人的恐惧”与“自己的恐惧”分开：广泛的恐惧是朋友，因为送来
    便宜货；个人的恐惧是敌人，因为没有根据，会导致在底部割肉。执行要点：(1) 平时
    保持弹药——2008 年伯克希尔“永远以远超需要的现金运行，绝不指望陌生人的善意”，
    市场混乱时成为买方（“pessimism is your friend, euphoria the enemy”）；(2) 恐慌时
    用大盆而非小勺接金子（2016：rush outdoors carrying washtubs, not teaspoons）；
    (3) 前提是资产本身没坏，而非基本面恶化。对基金：大跌是分批买入信号而不是清仓
    信号，按计划执行。
  tags: [behavioral, panic, contrarian, buying, liquidity]

- id: f08
  title: 回购决策框架：回购是否增值完全取决于价格
  type: framework
  source_chapter: 2016 年致股东信（另见 1984/2022）
  source_quote: |
    “For continuing shareholders, however, repurchases only make sense if the shares are bought
    at a price below intrinsic value. When that rule is followed, the remaining shares
    experience an immediate gain in intrinsic value. Consider a simple analogy: If there are
    three equal partners in a business worth $3,000 and one is bought out by the partnership
    for $900, each of the remaining partners realizes an immediate gain of $50. If the exiting
    partner is paid $1,100, however, the continuing partners each suffer a loss of $50.”
  summary: |
    回购对继续持有者是否增值，完全取决于成交价与内在价值的关系（purchase-price
    dependent）。三人合伙算术：价值 3000 的生意花 900 买走三分之一股份（低于其 1000 的
    价值），剩下两人各赚 50；付 1100 则各亏 50，增益流向卖家和高价回购的“热情投行家”。
    1984 年先例：“当优秀企业股价远低于内在价值时，没有任何替代行动能像回购一样确定地
    惠及股东”；2022 年延续：“股价数量减少，你对企业的权益就上升——只要按增值价格
    回购”。对基金：看到公司回购或基金份额变动时，先核对价格与内在价值的关系再判断
    利好利空；自己加仓/赎回也应按同一原则。
  tags: [buyback, capital-allocation, price-vs-value, share-count]

- id: f09
  title: 长期持有与复利：持有到“永远”的三条件
  type: framework
  source_chapter: 1987 年致股东信（另见 1989/2022/2016）
  source_quote: |
    “We need to emphasize, however, that we do not sell holdings just because they have
    appreciated or because we have held them for a long time. (Of Wall Street maxims the most
    foolish may be “You can’t go broke taking a profit.”) We are quite content to hold any
    security indefinitely, so long as the prospective return on equity capital of the underlying
    business is satisfactory, management is competent and honest, and the market does not
    overvalue the business.”
  summary: |
    “永远持有”不是口号而是带条件的三条纪律：企业潜在资本回报仍令人满意、管理层称职
    诚实、市场没有高估——三条同时成立就无限期持有，任一条被破坏才考虑卖出。卖出的
    理由从来不是“涨多了”或“拿久了”，“You can’t go broke taking a profit”被巴菲特
    称为华尔街最蠢的格言。1989 年补充：“时间是优秀企业的朋友、平庸企业的敌人”；
    2022 年以可口可乐为例：1994 年花 13 亿美元买入后，只需兑现季度股息支票，股息从
    7500 万涨到 7.04 亿美元。边界（2016）：对上市证券从未承诺“永远持有”，一切以
    估值为准。对基金：长期持有不等于死拿，用三条件做年度体检。
  tags: [long-term, compounding, holding-period, sell-discipline]

- id: f10
  title: 仓位框架：分散还是集中，取决于你知道多少
  type: framework
  source_chapter: 1993 年致股东信
  source_quote: |
    “By periodically investing in an index fund, for example, the know-nothing investor can
    actually out-perform most investment professionals. Paradoxically, when “dumb” money
    acknowledges its limitations, it ceases to be dumb. On the other hand, if you are a
    know-something investor, able to understand business economics and to find five to ten
    sensibly-priced companies that possess important long-term competitive advantages,
    conventional diversification makes no sense for you. It is apt simply to hurt your results
    and increase your risk.”
  summary: |
    仓位结构取决于认知水平，而不是别人的分散教条：不懂具体生意的“know-nothing”
    投资者应分散持有大量股票并拉长买入间隔，定期投资低成本指数基金甚至能跑赢大多数
    专业人士——“愚蠢的钱承认局限就不再愚蠢”；看得懂生意的“know-something”投资者，
    能找到 5-10 个合理价格且具长期竞争优势的公司时，传统分散只会摊薄收益、增加风险，
    应把钱加到最懂、风险最小的前几个选择上，而不是投到“第 20 喜欢”的标的。同年另一
    段给出理论基础：“组合集中可能降低风险——如果它提高你思考生意的强度与买入前的
    舒适度门槛”；风险的正确定义是购买力损失而非价格波动。对基金：要么认命买宽基
    指数定投，要么在能力圈内集中持有，警惕伪分散。
  tags: [position-sizing, diversification, concentration, index-fund, risk]
