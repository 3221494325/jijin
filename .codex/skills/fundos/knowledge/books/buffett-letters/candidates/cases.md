# 案例提取产出 — 《巴菲特致股东信》(Berkshire Hathaway Shareholder Letters)
# 流水线: cangjie-skill case-extractor | 日期: 2026-08-08
# 信件范围: 1977 / 1979 / 1984 / 1987 / 1989 / 1993 / 1997 / 2005 / 2008 / 2016 / 2022 / 2024
# 用途: 阶段 1.5 V1 跨域验证 + 阶段 2 A1 (Past Application) 素材

- id: c01
  title: 1987 年 10 月暴跌：波动是机会，但机会稍纵即逝
  type: case
  source_chapter: 1987 年信（chunks sub_03 / sub_04）
  source_quote: |
    "During 1987 the stock market was an area of much excitement but little net
    movement... Mr. Market was on a manic rampage until October and then experienced
    a sudden, massive seizure... During the break in October, a few stocks fell to
    prices that interested us, but we were unable to make meaningful purchases before
    they rebounded. At yearend 1987 we had no major common stock investments (that is,
    over $50 million) other than those we consider permanent or arbitrage holdings."
  summary: |
    问题：1987 年 10 月美股突然暴跌，市场把"波动"当作风险；大量机构用"组合保险"
    （实质是下跌自动止损）放大抛压，把波动变成踩踏。
    处理：伯克希尔坚持以"企业分析师"而非"市场分析师"的视角持股；暴跌期间少数股票
    跌到了感兴趣的价格，但反弹太快，未能形成有意义的买入（诚实承认"没买到"）。
    结论：波动带来的折价是投资者的朋友，前提是投资者不被财务或心理压力逼着
    在不利时点卖出；对真投资者，暴涨暴跌的市场反而提供更多机会。
    结果：年末组合除永久持仓与套利外无重大新增；教训是"机会可能只存在几天"，
    想抓恐慌必须事先有准备与弹药。
  bound_to:
    - 市场先生 / 波动与风险观
    - 恐慌买入框架（机会窗口极短，需预先准备）
  outcome: |
    1987 年全年伯克希尔账面价值 +19.5%；暴跌未造成永久损失，反而确立了
    "波动≠风险、被迫卖出才是风险"的长期框架。
  tags: [case, 1987, 市场暴跌, 波动与风险, 准备与纪律]

- id: c02
  title: 2008 危机中"别人恐惧我贪婪"：$145 亿买入 Wrigley / Goldman / GE
  type: case
  source_chapter: 2008 年信（chunks sub_10）
  source_quote: |
    "pessimism is your friend, euphoria the enemy... we made purchases totaling
    $14.5 billion in fixed-income securities issued by Wrigley, Goldman Sachs and
    General Electric. We very much like these commitments, which carry high current
    yields... But in each of these three purchases, we also acquired a substantial
    equity participation as a bonus. To fund these large purchases, I had to sell
    portions of some holdings that I would have preferred to keep (primarily Johnson
    & Johnson, Procter & Gamble and ConocoPhillips)... We never want to count on the
    kindness of strangers in order to meet tomorrow's obligations."
  summary: |
    问题：2008 年金融危机，信贷冻结、市场从"低估风险"转向"过度定价风险"，
    连优质公司也拿不到正常条款的融资。
    处理：抓住"正常市场拿不到的条款"——买入 Wrigley、Goldman Sachs、General
    Electric 合计 $145 亿固收，高当期收益率，且每笔都附带可观股权参与权（bonus）；
    为筹资卖出本不想卖的 J&J、P&G、ConocoPhillips 部分持仓；同时承诺"永远
    保持超额现金，不指望陌生人的善意"。
    结果：三笔投资自身收益率即令人满意，股权部分提供额外上行；并借机警告：
    长期持现金与长期国债在近零利率下是"几乎肯定错误"的政策（"cash is king"
    是自欺，购买力会被通胀侵蚀）。
  bound_to:
    - 恐慌买入框架（危机中条款优于平时）
    - 现金管理 / 流动性底线
  outcome: |
    2008 年伯克希尔账面价值 -9.6%（远好于标普 -37%）；这些危机条款后来
    贡献了可观的股息与资本利得，"卖次优换最优"成为再平衡范本。
  tags: [case, 2008, 金融危机, 恐慌买入, 现金管理]

- id: c03
  title: 2008 年公开认错：ConocoPhillips 顶部买入 + 爱尔兰银行 -89%
  type: case
  source_chapter: 2008 年信（chunks sub_10）
  source_quote: |
    "During 2008 I did some dumb things in investments. I made at least one major
    mistake of commission and several lesser ones... I bought a large amount of
    ConocoPhillips stock when oil and gas prices were near their peak... the terrible
    timing of my purchase has cost Berkshire several billion dollars... During 2008,
    I spent $244 million for shares of two Irish banks that appeared cheap to me.
    At yearend we wrote these holdings down to market: $27 million, for an 89% loss."
  summary: |
    问题：2008 年巴菲特犯下"主动错误"：在油价峰值附近重仓买入 ConocoPhillips；
    又以"看起来便宜"为由用 $244M 买入两只爱尔兰银行股——把"便宜"误当成安全边际，
    却超出能力圈、且未预见能源价格与欧债风险。
    处理：在年报中主动、完整披露错误（major mistake of commission），说明成因
    （未预见油价暴跌、时点极差），并按市价立即减记，不掩盖、不拖延。
    结果：ConocoPhillips 造成数十亿美元损失；爱尔兰银行当年减记 89%（$244M→$27M）
    且之后继续下跌；成为"不懂不买、错后立刻认错纠正"的反面教材。
  bound_to:
    - 能力圈边界（便宜≠懂）
    - 错误处理：承认、计量、及时纠正（拒绝 thumb-sucking）
  outcome: |
    事后伯克希尔仍持有其认为"油价长期更高"的判断，但承认时点错误；
    该案例与其 2005 年"问题出现就要立刻行动"的教训一脉相承。
  tags: [case, 2008, 认错, 能力圈, 仓位管理]

- id: c04
  title: 2005 年衍生品退场：Gen Re 23,218 份合约的漫长清仓
  type: case
  source_chapter: 2005 年信（chunks sub_08 / sub_09）
  source_quote: |
    "We lost $104 million pre-tax last year in our continuing attempt to exit Gen
    Re's derivative operation. Our aggregate losses since we began this endeavor
    total $404 million. Originally we had 23,218 contracts outstanding. By the start
    of 2005 we were down to 2,890... Reducing our inventory to 741 contracts last
    year cost us the $104 million mentioned above... one of the contracts we
    liquidated in 2005 had a term of 100 years!"
  summary: |
    问题：1998 年收购 General Re 时，明知其衍生品交易台是"问题"，却想"无痛退出"
    而拖延数年（想卖给别人），期间还不断新增合约；衍生品期限长、变量多、难以
    公允估值，与金融市场的风险高度相关。
    处理：最终决定亲手清仓——23,218 份合约逐年压缩到 741 份，累计亏损 $404M；
    事后明确承担"拖延（dithering / thumb-sucking）"的责任，并确立
    "问题出现，无论多不舒服，行动的时间就是现在"。
    结果：在良性市场、无融资压力下完成退出已属幸运；巴菲特以"金丝雀"自喻，
    警告全球衍生品规模仍在膨胀、估值依赖"想象"，并坚持复杂衍生品不进伯克希尔。
  bound_to:
    - 不做清单（不碰看不懂的复杂结构与对手盘风险）
    - 错误处理：立刻纠正，拖延放大成本
  outcome: |
    伯克希尔此后只保留自认为"定价错误"的少量衍生品（如股指卖出期权），
    且坚持对手方先付款、无抵押风险的条款；2008 年信中重申
    "Derivatives are dangerous"。
  tags: [case, 2005, 衍生品, 风险控制, 不做清单]

- id: c05
  title: 1979 年十五年期债券错误：通胀下长期固收的"确定性亏损"
  type: case
  source_chapter: 1979 年信（chunks sub_01）
  source_quote: |
    "It was a mistake to buy fifteen-year bonds, and yet we did; we made an even
    more serious mistake in not selling them (at losses, if necessary) when our
    present views began to crystallize... We have severe doubts as to whether a very
    long-term fixed-interest bond, denominated in dollars, remains an appropriate
    business contract in a world where the value of dollars seems almost certain to
    shrink by the day."
  summary: |
    问题：1970 年代高通胀（信中测算 14% 通胀下名义 20% 的年化收益税后购买力
    接近归零），伯克希尔的保险资金却持有 15 年期固定利率美元债券——名义收益
    被通胀与税收双重侵蚀。
    处理：承认"买 15 年期债券是错误，更大的错误是该卖没卖"；此后保险组合
    不再净买长期直债，转向可转债（转换权≈把久期缩短到由自己选择的时间点），
    并把资金更偏重股票。
    结果：债券组合浮亏显著低于同业；确立了"绝不给 2010 或 2020 年的钱
    在今天定价"的原则（"Neither a short-term borrower nor a long-term lender be"）。
  bound_to:
    - 不做清单（通胀环境下长久期固定收益）
    - 资产配置：久期与通胀匹配
  outcome: |
    该原则贯穿至今（2008 年信中再次警告长期国债"泡沫"、2022 年后现金
    只买短久期美国国债），证明"固收也有价值毁灭"。
  tags: [case, 1979, 债券, 通胀, 资产配置]

- id: c06
  title: 1984 年按比例回购：GEICO / General Foods 的"回购≈分红"
  type: case
  source_chapter: 1984 年信（chunks sub_02）
  source_quote: |
    "(1) in mid-1983 GEICO made a tender offer to buy its own shares; (2) at the
    same time, we agreed by written contract to sell GEICO an amount of its shares
    that would be proportionately related to the aggregate number of shares GEICO
    repurchased via the tender... we delivered 350,000 shares to GEICO, received
    $21 million cash, and were left owning exactly the same percentage of GEICO that
    we owned before the tender... In 1984, we had a virtually identical transaction
    with General Foods... our ownership remained at exactly 8.75%."
  summary: |
    问题：1980 年代 GEICO 与 General Foods 都在以远低于内在价值的价格回购股票；
    伯克希尔若坐视不动，持股比例会被稀释，但直接卖出又承担资本利得税。
    处理：与两家公司签订书面合约、按比例参与回购——GEICO 交割 350,000 股
    收回 $21M、General Foods 收回 $21.84M，两家持股比例分别保持不变，且税务上
    按股息处理；同时公开支持"价格远低于价值时的回购"，痛斥 greenmail。
    结果：GEICO、Washington Post、General Foods 三大持仓都靠低价回购
    "用 $1 换回 $2 现值"，显著增厚每股价值；管理层是否在折价时回购成为
    评估股东友好度的关键信号。
  bound_to:
    - 资本配置：回购 vs 分红（关键在价格）
    - 持仓管理：以股东身份参与上市公司回购
  outcome: |
    该框架延续至 2016/2022 年信（回购必须低于内在价值、价值增值定价），
    成为基金评估持仓公司治理与资本回报的重要标尺。
  tags: [case, 1984, 回购, 资本配置, 股东价值]

- id: c07
  title: 2022 年回购与现金：1.2% 回购 + "永远留一船现金"
  type: case
  source_chapter: 2022 年信（chunks sub_13）
  source_quote: |
    "A very minor gain in per-share intrinsic value took place in 2022 through
    Berkshire share repurchases... At Berkshire, we directly increased your interest
    in our unique collection of businesses by repurchasing 1.2% of the company's
    outstanding shares... Every small bit helps if repurchases are made at
    value-accretive prices. Just as surely, when a company overpays for repurchases,
    the continuing shareholders lose... As for the future, Berkshire will always
    hold a boatload of cash and U.S. Treasury bills... We will also avoid behavior
    that could result in any uncomfortable cash needs at inconvenient times,
    including financial panics and unprecedented insurance losses."
  summary: |
    问题：2022 年市场围绕回购争论激烈（"回购伤害股东/国家"论调流行）；同时
    伯克希尔手握巨额现金，面临"留多少、投什么"的资本配置问题。
    处理：当年按"价值增值价格"回购 1.2% 流通股，并说明数学——回购是否有利
    完全取决于价格；苹果、美国运通的自有回购也让伯克希尔持股比例无成本上升；
    同时承诺永远持有"一船现金与美国国债"，避免在金融恐慌或保险巨灾时
    出现任何不适的现金需求，CEO 兼任首席风险官。
    结果：每股内在价值小幅增厚；现金被视为"永不求人、永不被迫卖出"的保障，
    而非收益率目标；2022 年还以现金收购 Alleghany 补充保险浮存金。
  bound_to:
    - 回购的定价纪律（低于内在价值才买）
    - 现金管理与流动性底线
  outcome: |
    2022 年经营利润创新高（$30.8B）；此后（2024 年信）重申"宁可持币，
    也绝不在恐慌时缺钱"，现金主要配置在短久期美国国债上。
  tags: [case, 2022, 回购, 现金管理, 资本配置]

- id: c08
  title: 指数基金赌局（The Bet）：五只 FOF 十年跑不赢 Vanguard 标普指数
  type: case
  source_chapter: 2016 年信（chunks sub_12，赌局于 2005 年提出、2007 年立约）
  source_quote: |
    "I publicly offered to wager $500,000 that no investment pro could select a set
    of at least five hedge funds... that would over an extended period match the
    performance of an unmanaged S&P-500 index fund charging only token fees... For
    Protégé Partners' side of our ten-year bet, Ted picked five funds-of-funds whose
    results were to be averaged and compared against my Vanguard S&P index fund...
    I estimate that over the nine-year period roughly 60% – gulp! – of all gains
    achieved by the five funds-of-funds were diverted to the two levels of managers."
  summary: |
    问题：主动管理（对冲基金及其 FOF）的高额费用是否值回票价？2005 年巴菲特
    提出"专业主动管理整体跑不赢躺平的散户"，2007 年与 Protégé 的 Ted Seides
    立下 $500,000 十年赌约。
    处理：赌约设计——5 只 FOF（内含 100+ 只对冲基金、叠加两层费用）对比一只
    低费率 Vanguard S&P 500 指数基金，2008-2017 计收益。
    结果：前九年指数基金累计 +85.4%（年化 7.1%），5 只 FOF 仅 +2.9% 至 +62.8%；
    约 60% 的 FOF 收益被两层管理费吃掉（"Fees never sleep"）；证明
    "低成本指数对绝大多数人是更优解"。
  bound_to:
    - 指数基金 vs 主动管理（费率是第一道筛子）
    - 普通投资者降级方案
  outcome: |
    2017 年赌约到期时指数基金完胜（本信未含终局数据，仅至 2016 年）；
    该案例成为基金行业"费率拖累净收益"的最有力实证。
  tags: [case, 2016, 指数基金, 费率, 主动vs被动]

- id: c09
  title: 可口可乐三十年：$1.3B 买入后只收股息，2022 年值 $25B
  type: case
  source_chapter: 1989 年信 + 2022 年信（chunks sub_05 / sub_13）
  source_quote: |
    "This Coca-Cola investment provides yet another example of the incredible speed
    with which your Chairman responds to investment opportunities... Only in the
    summer of 1988 did my brain finally establish contact with my eyes... In August
    1994 – yes, 1994 – Berkshire completed its seven-year purchase of the 400 million
    shares of Coca-Cola we now own. The total cost was $1.3 billion... The cash
    dividend we received from Coke in 1994 was $75 million. By 2022, the dividend
    had increased to $704 million... At yearend, our Coke investment was valued at
    $25 billion."
  summary: |
    问题：巴菲特从 1936 年起就亲身验证可口可乐的产品力，却 52 年一股未买，
    把资金投向纺织、铁路、邮票公司等平庸生意（1989 年信自嘲"大脑直到 1988 年
    夏才与眼睛接通"）。
    处理：1988-89 年大举买入（1989 年底持 23,350,000 股、成本 $1,023,920K；
    1994 年完成 400M 股、总成本 $1.3B 的七年建仓）；此后只做一件事——
    收季度股息，不做任何交易。
    结果：股息从 1994 年 $75M 增至 2022 年 $704M，持股价值 $25B（约占净资产
    5%）；2022 年信总结"杂草随重要性枯萎，鲜花绽放"（the weeds wither away
    in significance as the flowers bloom）。
  bound_to:
    - 能力圈（早就懂的生意，晚买也比不买强）
    - 长期持有与复利（盈利+股息驱动，而非交易）
  outcome: |
    美国运通是"同样的故事"（1995 年完成 $1.3B 建仓，股息 $41M→$302M、
    价值 $22B）；两笔合计 40 年维度验证"少数大赢家创造大部分价值"。
  tags: [case, 1989, 2022, 可口可乐, 长期持有, 能力圈]

- id: c10
  title: GEICO 四十年：$6.67 均价买入 → 1996 现金全资 → 成为保险核心引擎
  type: case
  source_chapter: 1987 年信 + 1997 年信 + 2016 年信（chunks sub_04 / sub_07 / sub_11）
  source_quote: |
    "Our GEICO stock was purchased in 1976, 1979 and 1980 at an average of $6.67
    per share, and after-tax operating earnings per share last year were $9.01...
    In 1984... we would far rather have the business value of GEICO increase by X
    during the year, while market value decreases, than have the intrinsic value
    increase by only 1/2 X with market value soaring... At the beginning of 1996,
    we acquired the half of GEICO we didn't already own, a cash transaction that
    changed our holding from a portfolio investment into a wholly-owned operating
    business."
  summary: |
    问题：1970 年代 GEICO 濒临破产、股价暴跌；1984 年股价停滞而企业价值持续
    增长；投资者若只看报价容易误判"没涨=没价值"。
    处理：1976/1979/1980 年以均价 $6.67 买入（伯克希尔 1987 年底账面市值
    已达 $756.9M）；坚持用企业价值而非股价评估（"宁愿价值涨 X 股价跌，
    不愿价值涨 0.5X 股价飞"）；1996 年初用现金买下剩余一半股权，
    从组合投资升级为全资经营。
    结果：低成本直销模式带来 1997 年保费增长 16%、2005 年市占率快速提升、
    2016 年约占行业 12% 份额，成为伯克希尔财产险的"核心引擎"与浮存金主力。
  bound_to:
    - 企业价值 vs 市场报价（持有期的评估标尺）
    - 核心持仓的升级路径：财务投资→战略持有
  outcome: |
    伯克希尔在 GEICO 上的总成本约 $45.7M（1987 年口径），到 1993 年底
    市值 $1.76B；全资后 GEICO 的留存盈利与浮存金持续放大集团价值。
  tags: [case, 1987, 1997, 2016, GEICO, 长期持有, 企业价值]