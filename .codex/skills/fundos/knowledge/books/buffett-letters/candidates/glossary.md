# 《巴菲特致股东信》关键概念词典（候选）

> 产出：cangjie 蒸馏流水线 · 术语提取器（阶段 1 候选，供阶段 1.5 确认）
> 输入：BOOK_OVERVIEW.md + 精选 12 封信（1977/1979/1984/1987/1989/1993/1997/2005/2008/2016/2022/2024，chunks/sub_01–sub_14）
> 说明：source_quote 全部取自原文分块原文，未改写；引号/撇号统一为 ASCII。选集内未出现的概念（如 owner earnings，原文在 1983 年信，不在本选集）不予收录。

- id: g01
  title: 内在价值 (Intrinsic Value)
  type: term
  source_chapter: 1989
  source_quote: |
    "What counts, however, is intrinsic value - the figure indicating what all of our constituent businesses are rationally worth. With perfect foresight, this number can be calculated by taking all future cash flows of a business - in and out - and discounting them at prevailing interest rates. So valued, all businesses, from manufacturers of buggy whips to operators of cellular phones, become economic equals."
  summary: |
    - 定义：把企业剩余寿命内全部未来现金流按利率折现，得到"企业理性上值多少钱"的估值；巴菲特认为这才是真正该跟踪的业绩标尺。
    - 与常识差异：账面价值是会计口径（已投入资本+留存收益），内在价值是"还能取出的现金的现值"，两者在多数公司几乎无关（1993 年信明示）。
    - 关键性质：计算主观、无法精确，只能给大致区间；但长期看市场价格会与内在价值"殊途同归"（1993）。
    - 用途：回购是否划算（1984）、浮存金业务估值（1997）、透视盈余增速目标（1993）都以此为准绳。
    - 下游用法：估值类 skill 用"价格 vs 内在价值区间"判断贵贱，而不是用净值涨跌代替。
  tags: [term, core-concept, valuation]

- id: g02
  title: 浮存金 (Insurance Float)
  type: term
  source_chapter: 1993
  source_quote: |
    "To oversimplify the matter somewhat, the total of the funds prepaid by policyholders and the funds earmarked for incurred-but-not-yet-paid claims is called 'the float.' In the past, the industry was able to suffer a combined ratio of 107 to 111 and still break even from its insurance writings because of the earnings derived from investing this float."
  summary: |
    - 定义：投保人预付的保费加已发生未赔付的准备金，合计称"浮存金"，保险公司可先拿来投资，属于"别人的钱、自己用"。
    - 与常识差异：浮存金不是股东资金，但成本可能是负的——承保盈利时等于别人倒贴钱让你用钱；2008 年伯克希尔 $58.5B 浮存金成本低于零。
    - 关键风险：利率下行会稀释浮存金价值（1993 年巴菲特明确提示）；评估财险公司必须把承保结果与浮存金可赚的无风险收益合并看。
    - 无法复制的结构：浮存金是伯克希尔的独特低成本杠杆，普通散户/基金无法复制（BOOK_OVERVIEW 批判字段）。
    - 下游用法：分析"低息借款/垫资"类金融产品时，先问资金成本是否为负、来源是否稳定。
  tags: [term, insurance, leverage]

- id: g03
  title: 护城河 (Moat)
  type: term
  source_chapter: 1997
  source_quote: |
    "Moreover, both Coke and Gillette have actually increased their worldwide shares of market in recent years. The might of their brand names, the attributes of their products, and the strength of their distribution systems give them an enormous competitive advantage, setting up a protective moat around their economic castles."
  summary: |
    - 定义：品牌力、产品特性、分销体系等带来的持久竞争优势，像护城河一样保护企业的"经济城堡"。
    - 与常识差异：护城河不是市场份额本身，而是让对手难以跨越的结构性壁垒；2005/2008 年巴菲特强调要"加宽护城河"以维持持久竞争优势。
    - 实例对照：Coke/Gillette 全球份额持续扩大；而商品型公司"每日无保护作战"，Peter Lynch 警告"竞争对财富有害"。
    - 风险观：护城河强的公司 beta 未必低，用价格波动衡量风险会低估竞争优势的价值（1997 年原文质疑）。
    - 下游用法：选资产前先问"护城河是什么、能否持久"；GEICO 式低成本护城河（2016）是最好样板。
  tags: [term, competitive-advantage, business-quality]

- id: g04
  title: 透视盈余 (Look-Through Earnings)
  type: term
  source_chapter: 1993
  source_quote: |
    "Over time, our look-through earnings need to increase at about 15% annually if our intrinsic value is to grow at that rate. ... We expect such pleasant outcomes to recur often in the future and therefore believe our look-through earnings to be a conservative representation of Berkshire's true economic earnings."
  summary: |
    - 定义：把报告利润与被投企业未分配的留存收益（扣除假设税）合并，"透视"全资与部分持股企业的真实盈利。
    - 与常识差异：GAAP 利润只计收到手的分红，会严重低估持有大量优质企业股权的真实盈利能力；巴菲特自评透视盈余是"保守代表"。
    - 用法：把透视盈余增速当作内在价值增速的代理指标（目标年增约 15%），并逐年公布测算表。
    - 依据：Cap Cities 案例——持有期间未分配留存收益带来的市值增长远超已收分红（1993）。
    - 下游用法：评估持有很多低分红/不分红资产的组合时，看组合整体盈利能力而非仅看现金分红。
  tags: [term, accounting, valuation]

- id: g05
  title: 回购 (Stock Repurchases)
  type: term
  source_chapter: 1984
  source_quote: |
    "When companies with outstanding businesses and comfortable financial positions find their shares selling far below intrinsic value in the marketplace, no alternative action can benefit shareholders as surely as repurchases."
  summary: |
    - 定义：好企业+财务稳健+股价远低于内在价值时，回购是对不卖出的股东最有利的现金运用方式。
    - 与常识差异：只认可"价格/价值"驱动的回购，明确反对绿票讹诈式回购（"odious and repugnant"，1984）。
    - 双重收益：算术上每股内在价值提升；"示范效应"证明管理层为股东而非自己扩张利益行事，市场会据此上调估值。
    - 2022 再确认：被投公司回购大多因股价被低估；"公司成长+股本缩减=股东好事"。
    - 下游用法：评估红利/回购策略时，以"价格相对内在价值"为条件判断，不无条件点赞。
  tags: [term, capital-allocation, buyback]

- id: g06
  title: 市场先生 (Mr. Market)
  type: term
  source_chapter: 1987
  source_quote: |
    "He said that you should imagine market quotations as coming from a remarkably accommodating fellow named Mr. Market who is your partner in a private business. Without fail, Mr. Market appears daily and names a price at which he will either buy your interest or sell you his. ... Under these conditions, the more manic-depressive his behavior, the better for you."
  summary: |
    - 定义：把每日报价想象成一位躁郁症合伙人——情绪高涨时报高价、沮丧时报低价，买卖与否完全由你决定。
    - 与常识差异：报价是"仆人"不是"向导"；市场波动是他的情绪发作，不是企业的经济命运，价格与价值在短期经常大幅背离。
    - 用法：无视无趣报价；他越狂躁对你越有利，因为你可以利用低价买入、高价卖出。
    - 延续：2008 年"悲观是你的朋友，狂热是敌人"；"价格是你付出的，价值是你得到的"。
    - 下游用法：恐慌/大涨场景 skill 的核心心理锚——大跌执行计划加仓，不被报价牵着走。
  tags: [term, market-psychology, core-concept]

- id: g07
  title: 生意特许权 (Business Franchise)
  type: term
  source_chapter: 1987
  source_quote: |
    "Furthermore, economic terrain that is forever shifting violently is ground on which it is difficult to build a fortress-like business franchise. Such a franchise is usually the key to sustained high returns."
  summary: |
    - 定义：能让企业持续获得高回报的"堡垒型"生意特许权；地形剧烈变动的行业建不起这种优势。
    - 与常识差异：franchise 不是品牌知名度，而是让高回报可持续的生意结构；好生意+合理价 > 烂生意+便宜价（1979）。
    - 实证：25 家连续十年 ROE>20% 的"超级明星"大多业务平淡、少杠杆、少变阵，其中 24 家跑赢 S&P 500。
    - 管理含义：优秀经理"保护特许权、控成本、不分散注意力"。
    - 下游用法：识别"好生意"因子=定价权+稳定+高 ROE，而非追逐热闹题材。
  tags: [term, business-quality, core-concept]

- id: g08
  title: 低成本指数基金 (Low-Cost Index Fund)
  type: term
  source_chapter: 2022
  source_quote: |
    "The bottom line: When trillions of dollars are managed by Wall Streeters charging high fees, it will usually be the managers who reap outsized profits, not the clients. Both large and small investors should stick with low-cost index funds."
  summary: |
    - 定义：主动投资者作为一个整体必然跑输被动投资者——市场平均结果减去成本，低费率指数基金是普通人的最优解。
    - 实证：十年赌约，5 只对冲基金组合平均年化 2.2%，同期 S&P 指数基金 7.1%（2022 年信公布结果）。
    - 与常识差异："聪明人+高成本"输给"什么都不做+低成本"；费用是唯一确定性的胜负手，指数基金是"被动鸭"也能追平市场的工具（1997）。
    - 结论：大小投资者都应坚持低成本指数基金，并致敬 Jack Bogle（低费率指数化先驱）。
    - 下游用法：基金推荐默认方案=宽基低费率指数基金；主动基金须先证明费后超额收益能力。
  tags: [term, index-investing, retail-advice]
