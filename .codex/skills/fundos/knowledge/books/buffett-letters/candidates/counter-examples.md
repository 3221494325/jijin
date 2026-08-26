# 反例提取器输出：巴菲特致股东信（12 封精选）

> 流水线：cangjie-skill · extractor: counter-example-extractor
> 输入：1977/1979/1984/1987/1989/1993/1997/2005/2008/2016/2022/2024 共 12 封信件（chunks/sub_01.txt – sub_14.txt，逐块扫描）
> 用途：阶段 2 的 B（Boundary）段核心素材；约束正面 skill 的适用边界
> 产出：10 条反例候选（x01–x10），全部原文引用、可回查核验

## 信件覆盖核对

| 信件年份 | 所在 chunk | 关联候选 |
|---|---|---|
| 1977 | sub_01（含 1979） | x04 辅助（纺织预测失误） |
| 1979 | sub_01 | x10（主） |
| 1984 | sub_02 | x09（主） |
| 1987 | sub_03 | x10 辅助（全债券组合"清零"风险） |
| 1989 | sub_04 + sub_05 | x02（主）、x05（主）、x08 辅助 |
| 1993 | sub_06 | x01（主）、x08（主） |
| 1997 | sub_07 | x04 辅助、x05 辅助（鸭子比喻） |
| 2005 | sub_08 + sub_09 | x07（主） |
| 2008 | sub_10 + sub_11（1–265 行） | x03（主）、x06（主） |
| 2016 | sub_11（266 行起）+ sub_12 | x04 辅助（naysayers 一段） |
| 2022 | sub_12（747 行起）+ sub_13（1–369 行） | x04（主）、x01 辅助（芒格论杠杆） |
| 2024 | sub_13（370 行起）+ sub_14 | x06/x08/x09/x10 辅助 |

> 说明：sub_10 与 sub_11 的 2008 部分、sub_11 的个别 2016 行在源文本中丢失了空格，引用处已按原词还原空格；核验时按"去全部空白后逐字包含"比对。

## 候选列表

- id: x01
  title: 杠杆：99:1 的好概率也不赌
  type: counter-example
  source_chapter: 1993 年致股东信（sub_06 · Mistakes of the First Twenty-five Years 一节）
  source_quote: |
    "We wouldn't have liked those 99:1 odds - and never will. A small chance
    of distress or disgrace cannot, in our view, be offset by a large chance of
    extra returns. If your actions are sensible, you are certain to get good
    results; in most such cases, leverage just moves things along faster.
    Charlie and I have never been in a big hurry: We enjoy the process far more
    than the proceeds - though we have learned to live with those also."
  summary: |
    失败模式：用借来的钱放大组合，即使"大概率赚钱"，也把不可逆的破产/出局风险放进了组合。
    书中何时出现：1993 年信回顾 25 年错误时承认，更高但仍属常规的杠杆比率本可带来明显更高的账面回报（他估计有 99% 概率只有好处），但他明确拒绝这种 99:1 的赔率。
    后果：一旦那 1% 的"外部或内部冲击"发生，常规负债率也会把公司从"暂时痛苦"拖到"违约"；伯克希尔因此刻意保持极低杠杆，用"慢慢变富"换"永不出局"。
    2022 年信借芒格之口重申："投资没有 100% 确定的事，所以杠杆是危险的——一串漂亮的数字乘以零，永远等于零。"
    对基金持仓管理的含义：带杠杆的基金/持仓在极端行情中可能被强平归零，属于不可逆风险；再高的期望收益都不该用本金清零去交换。
  failure_mode: |
    用杠杆放大收益的同时放大"出局"概率，把尾部风险当成可忽略项。
  mechanism: |
    杠杆的期望为正不等于风险可控：1% 的冲击（流动性冻结、暴跌、追缴保证金）足以把常规杠杆变成永久性资本损失；损失是乘数式的（"乘以零等于零"），且时间越长、路径越依赖融资续命。
  warning_signs:
    - 组合层面存在保证金借款或融资买入
    - 产品说明含杠杆倍数或"结构化"放大条款
    - 收益预期建立在"大概率"而非"极端行情下也能活下来"之上
  bound_to:
    - "恐慌买入框架（杠杆下的暴跌加仓会先被强平，越跌越死）"
    - "长期持有与复利（杠杆把时间从朋友变成敌人）"
  tags: [counter-example, leverage, tail-risk, 不做清单]

- id: x02
  title: 会计炼金术：用债务结构把坏生意伪装成好生意
  type: counter-example
  source_chapter: 1989 年致股东信（sub_05 · Zero-Coupon Bonds 一节）
  source_quote: |
    "But in the end, alchemy, whether it is metallurgical or financial, fails.
    A base business can not be transformed into a golden business by tricks of
    accounting or capital structure. The man claiming to be a financial alchemist
    may become rich. But gullible investors rather than business achievements
    will usually be the source of his wealth."
  summary: |
    失败模式：被"会计/资本结构把戏"制造的账面收益迷惑，把没有真实现金流支撑的高杠杆交易当成好投资。
    书中何时出现：1989 年信批判垃圾债券狂热——零息/实物支付债券让"承诺暂时不用付钱"的公司看起来永不违约；投行发明 EBDIT（忽略折旧与资本开支的"锯短了的尺子"）来证明坏交易也付得起利息。
    后果：账面可凭空创造"收入"，但"炼金术最终失败，基础生意无法靠会计或资本结构把戏变成黄金生意"；赚到钱的是发起人与投行，买单的是轻信的投资人。文中给出防身建议：一旦有人谈 EBDIT、或构造出"当期现金流净额（扣除充足资本开支后）付不起全部利息（含应计）"的资本结构——"拉上钱包拉链"。
    对基金持仓管理的含义：警惕高收益债、结构化产品、困境重组基金里按"不完整现金流口径"计算的收益率；现金流能否覆盖全部利息与真实资本开支是底线检查。
  failure_mode: |
    用会计口径（EBDIT、应计利息、忽略资本开支）高估偿债能力，买入实质是"借新还旧"的资产。
  mechanism: |
    违约可以被推迟但不能被消除；"愚蠢与失败之间的间隔"越长，发起人越能收割费用与佣金，买入者的本金在到期日一次性暴露并归零。
  warning_signs:
    - 产品用 EBITDA/EBDIT 而非自由现金流定价
    - 利息含应计成分或"实物支付"条款
    - 标的依赖再融资而非经营现金流还债
  bound_to:
    - "恐慌买入框架（便宜不等于安全）"
    - "安全边际判断（账面便宜可能是'炼金术'制造的假象）"
  tags: [counter-example, debt, accounting, junk-bond, 陷阱]

- id: x03
  title: 衍生品：无法理解、互相纠缠、市值波动致命的金融武器
  type: counter-example
  source_chapter: 2008 年致股东信（sub_10 末尾 + sub_11 开头 · Derivatives 一节）
  source_quote: |
    "Derivatives contracts, in contrast, often go unsettled for years, or even
    decades, with counterparties building up huge claims against each other.
    'Paper' assets and liabilities - often hard to quantify - become important
    parts of financial statements though these items will not be validated for
    many years. Additionally, a frightening web of mutual dependence develops
    among huge financial institutions. ... Participants seeking to dodge troubles face
    the same problem as someone seeking to avoid venereal disease: It's not just
    whom you sleep with, but also whom they are sleeping with."
  summary: |
    失败模式：持有结构复杂、期限极长、依赖假设模型的衍生品，或买入大量使用衍生品的公司。
    书中何时出现：2008 年信专节讲衍生品：合约多年甚至数十年不清算，"纸面资产/负债"进入报表；巨头之间形成"互相依赖的可怕网络"，风险像性病一样传染——"不只你跟谁睡，还有他们跟谁睡"；对高杠杆+庞大衍生品账本的 CEO，"公司生存第一定律"是"一般般的无能不够，需要令人瞠目结舌的失误"。
    后果：2008 年抵押品追缴要求几乎拖垮多家机构（Constellation Energy 距破产只剩几小时）；模型（Black-Scholes）套用于 100 年期合约会给出荒谬定价；伯克希尔自己只做"先收钱、方向明确"的衍生品，并要求"CEO 必须是首席风险官"。
    对基金持仓管理的含义：避开衍生品暴露重的基金/持仓；用"纸面数字"报净值的模型估值不可轻信。
  failure_mode: |
    高杠杆+衍生品+市值计价三者叠加，流动性冲击时被追缴保证金强平，账面波动与真实损失互相放大。
  mechanism: |
    衍生品账本透明度低、久期长、对手方网络互相传染；模型把短期波动率外推到超长期，定价失真；市价波动引发"纸面巨亏→追缴→贱卖"螺旋。
  warning_signs:
    - 持仓里有自己看不懂的衍生品结构
    - 产品净值依赖模型估值而非市场成交
    - 基金以"杠杆+衍生品对冲"作为卖点
  bound_to:
    - "恐慌买入框架（衍生品在恐慌中先爆仓，加仓前先查对手方风险）"
    - "能力圈判断（看不懂就不碰）"
  tags: [counter-example, derivatives, leverage, model-risk]

- id: x04
  title: 预测市场与经济：比无用更糟
  type: counter-example
  source_chapter: 2022 年致股东信（sub_13 · Some Surprising Facts About Federal Taxes 一节）
  source_quote: |
    "Though economists, politicians and many of the public have opinions about the
    consequences of that huge imbalance, Charlie and I plead ignorance and firmly
    believe that near-term economic and market forecasts are worse than useless."
  summary: |
    失败模式：按短期经济/市场预测做择时或调仓，把决策建立在"没人真懂、但都敢讲"的预测上。
    书中何时出现：2022 年信谈财政赤字时说：对巨额失衡的后果各界各有意见，但"查理和我承认无知，并坚信短期经济与市场预测比无用更糟"。早在 1977 年信他就自嘲纺织业务"连续两年错误地预测了更好的结果——这也许说明了我们的预测能力、纺织业的天性，或两者兼有"。
    后果：预测错误会在最差时点买卖（2008 年他买 ConocoPhillips 的时机错误即实例）；2016 年信提醒"靠兜售悲观预测为生的人，如果按自己兜售的胡说行事，上帝也救不了他们"。1997 年信给出替代方案："何必在干草堆里找针？"——只投自己能评估长期经济的"简单案例"。
    对基金持仓管理的含义：不做择时；把精力放在估值区间与纪律执行上；警惕任何"精确点位/时间窗口"的预测型话术。
  failure_mode: |
    用不可靠的预测代替估值与纪律，导致追高杀低、频繁调仓。
  mechanism: |
    短期预测本质是零信息优势的猜测；人脑对"听起来专业"的预测过度置信，预测失败后又会用新预测自我确认，形成追涨杀跌循环。
  warning_signs:
    - 决策理由里有"我认为年底前会……"
    - 组合因宏观观点变化而频繁调整
    - 迷信机构点位/时间预测
  bound_to:
    - "恐慌买入框架（规则型分批 vs 预测型加仓/减仓）"
    - "长期定投纪律（定投正是对'预测无用'的制度性承认）"
  tags: [counter-example, forecast, market-timing, 认知偏误]

- id: x05
  title: 情绪传染：让市场先生当向导，而不是仆人
  type: counter-example
  source_chapter: 1989 年致股东信（sub_04 · Mr. Market 一节）
  source_quote: |
    "Mr. Market is there to serve you, not to guide you. It is his pocketbook,
    not his wisdom, that you will find useful. If he shows up some day in a
    particularly foolish mood, you are free to either ignore him or to take
    advantage of him, but it will be disastrous if you fall under his influence.
    Indeed, if you aren't certain that you understand and can value your business
    far better than Mr. Market, you don't belong in the game."
  summary: |
    失败模式：把市场报价/群体情绪当作决策依据——涨时亢奋追高、跌时恐慌割肉，即追热门与跟风。
    书中何时出现：1989 年信引用格雷厄姆的"市场先生"寓言：报价来自一位"有无法治愈的情绪病"的合伙人，兴奋时报高价、抑郁时报低价；"他是来服务你的，不是来指导你的——用他的钱包，而不是他的智慧"，一旦受他影响就"必遭灾难"。1997 年信再加比喻：牛市里"要避免像大雨后得意洋洋的鸭子那样犯错"，误以为自己的划水技术让水位上升。
    后果：把情绪当信息，会在顶部接盘、在底部交出筹码；1989 年信还指出专业机构同样被"市场中超级易传染的情绪"左右，用巨额资金非理性投机，把波动放大给所有人。
    对基金持仓管理的含义：跟风追热门基金/行业是典型的情绪驱动；正确姿势是让"报价服务你"——用恐慌与狂热反向布局。
  failure_mode: |
    群体情绪通过报价传染给个人，形成"追高→套牢→割肉→再追高"的损耗循环。
  mechanism: |
    报价的波动被大脑当成"事实更新"，贪婪/恐慌信号压过估值判断；机构化运作放大而非消除这种情绪。
  warning_signs:
    - 决策理由主要是"最近涨得好/大家都在买"
    - 净值大跌时第一反应是卖出而非检视逻辑
    - 用新闻热度代替基本面研究
  bound_to:
    - "恐慌买入框架（反向利用恐慌）"
    - "不做清单（不追热点、不满仓单一行业）"
  tags: [counter-example, market-sentiment, herd, 行为偏误]

- id: x06
  title: 拖延纠错：拇指吮吸（thumb-sucking）是最重的罪
  type: counter-example
  source_chapter: 2008 年致股东信（sub_10 · 2008 Performance 一节）＋2024 年致股东信（sub_13 · Mistakes – Yes, We Make Them at Berkshire 一节）
  source_quote: |
    "During 2008 I did some dumb things in investments. I made at least one major
    mistake of commission and several lesser ones that also hurt. I will tell you
    more about these later. Furthermore, I made some errors of omission, sucking
    my thumb when new facts came in that should have caused me to re-examine my
    thinking and promptly take action."
  summary: |
    失败模式：发现持仓逻辑被新事实否定后不立即行动、拖延纠错，让小错拖成大错。
    书中何时出现：2008 年信坦诚"我在投资上做了些蠢事"，至少一个"作为之错"（无人怂恿、全凭自己，在油气价格接近顶部时大笔买入 ConocoPhillips，随后"目前为止我错得彻底"），加上若干"不作为之错"——"新事实出现、本应让我重新检视想法并立即行动时，我在吮吸拇指"。2024 年信把这条升为原则："最重的罪是拖延纠错，即芒格说的'拇指吮吸'——问题不会因为被希望消失而消失，它们需要行动，无论多不舒服。"
    后果：错误拖得越久，退出成本越高；2024 年信承认伯克希尔体量变大后"纠错灵活性在变小"。对基金持仓管理：止损/换仓/减仓前的"再想想"，往往就是账户持续失血的原因。
    含义：设定明确的纠错触发条件（逻辑破坏、事实证伪），把"卖"变成与"买"同样严肃的纪律动作。
  failure_mode: |
    情绪上不愿认错（沉没成本+自我确认），把"再等等"合理化，导致小错累积成大错。
  mechanism: |
    损失厌恶与承诺一致性让投资者拖延卖出；新事实被选择性忽略；时间把可逆的小错变成不可逆的大错。
  warning_signs:
    - 心里反复想着"再观察一个季度"
    - 为已有持仓寻找新理由的频率上升
    - 买入逻辑已失效却不更新或减仓
  bound_to:
    - "长期持有（长期≠不纠错，持有的前提是逻辑未破坏）"
    - "仓位上限（纠错成本与仓位成正比）"
  tags: [counter-example, disposition-effect, thumb-sucking, 卖出纪律]

- id: x07
  title: 频繁交易与费用：Gotrocks 家族的 Helper 们
  type: counter-example
  source_chapter: 2005 年致股东信（sub_09 · How to Minimize Investment Returns 一节）
  source_quote: |
    "the most that owners in aggregate can earn between now and Judgment Day is
    what their businesses in aggregate earn. ... Indeed, owners must earn less
    than their businesses earn because of 'frictional' costs. ... The more that
    family members trade, the smaller their share of the pie and the larger the
    slice received by the Helpers. This fact is not lost upon these broker-Helpers:
    Activity is their friend and, in a wide variety of ways, they urge it on."
  summary: |
    失败模式：通过频繁买卖"打败亲戚/打败市场"，把本属于所有者的企业盈利转移给中介（佣金、管理费、业绩提成、咨询费）。
    书中何时出现：2005 年信用"Gotrocks 家族"寓言：全美公司本由一家人拥有、按企业整体盈利同步变富；"快嘴 Helper"劝他们互相交易——"交易越多，家族分到的饼越小，Helper 拿到的越多；活动是他们的朋友"。随后又出现第二、三、四层 Helper（基金经理、顾问、对冲基金/私募），层层加码收费。
    后果：费前收益归企业，费后收益归投资者自己；文中估计如今摩擦成本可能高达美国企业盈利的 20%，即投资者整体只能拿到约 80%——"坐着不动、谁都不听"反而更好。2016 年信同样建议"避开高而不必要的成本，然后长时间静坐"。
    对基金持仓管理的含义：换手率与费率是确定性损耗；选基金先看费后长期业绩与换手率，警惕"高额业绩提成+固定费用"结构。
  failure_mode: |
    用交易活动本身替代投资判断，费用与税负持续侵蚀复利。
  mechanism: |
    交易是零和搬家（A 赚的来自 B 亏的），减去摩擦成本后整体必为负和；中介有动力鼓励更多活动，因为"活动是他们的朋友"。
  warning_signs:
    - 组合年换手率很高
    - 基金费率+申赎成本占比显著
    - 依据短期排名反复换基金
  bound_to:
    - "长期持有与复利（费用在复利公式里是指数损耗）"
    - "普通人配置降级方案（低费率宽基指数是对抗 Helper 的最优解）"
  tags: [counter-example, fees, churn, frictional-cost]

- id: x08
  title: 价值陷阱：便宜买平庸公司（cigar butt）
  type: counter-example
  source_chapter: 1993 年致股东信（sub_06 · Mistakes of the First Twenty-five Years 一节）
  source_quote: |
    "Unless you are a liquidator, that kind of approach to buying businesses is
    foolish. First, the original 'bargain' price probably will not turn out to be
    such a steal after all. In a difficult business, no sooner is one problem
    solved than another surfaces - never is there just one cockroach in the
    kitchen. Second, any initial advantage you secure will be quickly eroded by
    the low return that the business earns ... Time is the friend of the wonderful
    business, the enemy of the mediocre."
  summary: |
    失败模式：因为"便宜"买入基本面平庸/走下坡的公司，误把低估当安全边际。
    书中何时出现：1993 年信复盘"雪茄烟蒂"策略：捡到的烟蒂还能抽最后一口，赚的就是这一口；但"除非你是清算人，这种买法很蠢"——第一，"便宜价"往往并非真便宜，困难企业"一个问题刚解决，另一个就冒出来，厨房里从来不止一只蟑螂"；第二，初始便宜被低回报快速侵蚀，"时间是优秀企业的朋友，是平庸企业的敌人"。1989 年信已总结："要找的是以合理价格买到的优秀企业，而不是以便宜价格买到的平庸企业——拿猪耳朵做不成丝绸钱包"；2024 年信再次承认 1965 年买下伯克希尔纺织厂是"我的错，折磨了我们二十年"——价格看着便宜，生意注定灭亡。
    后果：低估值可能长期不修复（价值陷阱），机会成本巨大（二十年纺织 vs 优秀企业复利）。对基金持仓管理：便宜行业指数/低价基金不自动等于好投资，先看生意质量与资本回报。
  failure_mode: |
    把"价格低"等同于"价值高"，忽视企业质量与资本回报率。
  mechanism: |
    平庸生意的低 ROE 逐年侵蚀初始折价；持续的问题（竞争、需求萎缩）使价值中枢不断下移，低估反而"合理"。
  warning_signs:
    - 买入理由主要是"跌了很多/PE 很低"
    - 行业长期低资本回报
    - 需要"困境反转"才能回本
  bound_to:
    - "恐慌买入框架（恐慌中也要挑好资产，而非随便捡便宜）"
    - "安全边际（安全边际=好生意+好价格）"
  tags: [counter-example, value-trap, cigar-butt, 质量优先]

- id: x09
  title: 管理层不诚实与会计自欺：让尸体自己报死亡证明
  type: counter-example
  source_chapter: 1984 年致股东信（sub_02 · Errors in Loss Reserving 一节）
  source_quote: |
    "Not all reserving errors in the industry have been of the innocent-but-dumb
    variety ... Companies that would be out of business if they realistically
    appraised their loss costs have, in some cases, simply preferred to take an
    extraordinarily optimistic view about these yet-to-be-paid sums ... If
    liabilities of an insurer, correctly stated, would exceed assets, it falls to
    the insurer to volunteer this morbid information. In other words, the corpse
    is supposed to file the death certificate. Under this 'honor system' of
    mortality, the corpse sometimes gives itself the benefit of the doubt."
  summary: |
    失败模式：相信"报喜不报忧"的管理层与财报，或持有靠乐观假设维持账面偿付能力的公司。
    书中何时出现：1984 年信谈保险业损失准备金：错误分两种，一种"无辜但蠢"，另一种是管理层明知资不抵债，却"选择对未付赔偿金采取异常乐观的看法"，或做交易掩盖真实损失。审计师管不了：正确披露负债的责任落在公司自己头上——"尸体本该自己填死亡证明；在这种'荣誉制度'下，尸体有时会给自己疑罪从无"。2024 年信补刀：2019–2023 年他在信中用了 16 次"错误/失误"，"很多大公司那个时段一次都没用过这两个词——除了亚马逊，到处都是愉快的空话和图片"；"一旦你开始糊弄股东，很快就会相信自己的胡话，连自己也一起骗"。
    后果：被掩盖的问题延迟暴露（"你可以破产却依然手头有钱"），最终损失由市场与同业承担。对基金持仓管理：避开"从不认错"的管理层与粉饰口径的报表。
  failure_mode: |
    以管理层陈述/报表表面数字为准，忽视激励结构导致的系统性乐观偏差。
  mechanism: |
    会计确认滞后+管理层自由裁量+审计边界有限，使"乐观假设"能长期自我维持；掩盖期越长，最终一次性爆雷越大。
  warning_signs:
    - 管理层从不公开承认错误
    - 报表口径频繁"创新"或解释含糊
    - 准备金/减值/拨备与同业明显偏离且从不说明
  bound_to:
    - "能力圈判断（管理层诚信是买入前提之一）"
    - "纠错纪律（发现诚信问题立即行动）"
  tags: [counter-example, integrity, accounting, 管理层风险]

- id: x10
  title: 通胀与固定收益：买"确定"的利息，亏确定的购买力
  type: counter-example
  source_chapter: 1979 年致股东信（sub_01 · Inflation 一节）
  source_quote: |
    "Just as the original 3% savings bond, a 5% passbook savings account or an 8%
    U.S. Treasury Note have, in turn, been transformed by inflation into financial
    instruments that chew up, rather than enhance, purchasing power over their
    investment lives, a business earning 20% on capital can produce a negative
    real return for its owners under inflationary conditions not much more severe
    than presently prevail."
  summary: |
    失败模式：把"固定收益/现金类资产"当无风险资产重仓长期持有，忽视通胀对购买力的确定性侵蚀。
    书中何时出现：1979 年信指出：3% 储蓄债券、5% 存折账户、8% 国债都已被通胀"变成吞噬购买力的金融工具"；连 20% 资本回报的生意，在通胀+税负组合下也可能给股东负的真实回报——他把"通胀率+资本转移税负"称为"投资者痛苦指数"。当年他还承认：买 15 年期债券是错误，发现不对后没卖出是更严重的错误。1987 年信补充：恶性通胀下股票也大跌，但"已发行的债券跌得更惨，全债券组合带有小但不可接受的'清零'风险"；2024 年信再次提醒"纸币在财政愚蠢面前会蒸发，固定息票债券对失控货币毫无保护"。
    后果：持有到期"保本"的固定收益，购买力却持续缩水。对基金持仓管理：久期与现金占比必须与通胀预期挂钩，"保本"不等于"保值"。
  failure_mode: |
    把名义上的"确定收益"当成真实收益，忽略通胀与财政风险。
  mechanism: |
    通胀+税负叠加后，名义回报可能低于真实购买力损失；久期越长暴露越大；高通胀下政府有动机用贬值稀释债务。
  warning_signs:
    - 组合现金/短债占比过高且不考虑通胀
    - 只用名义收益率做比较
    - 把"保本"误当"保值"
  bound_to:
    - "长期复利（真实收益=名义收益-通胀）"
    - "能力圈（资产配置要考虑购买力维度）"
  tags: [counter-example, inflation, fixed-income, 购买力风险]

## 备用反例（未入选，供后续扩展）

- 为交易而交易/并购溢价：2005 年信"付收购溢价对任何买家都不合理……只有童话里才有人告诉皇帝他光着身子"；1993 年信"机构强制力"（任何领导人的愚蠢渴望都会被下属的详细回报率研究迅速背书，同行行为被无脑模仿）。
- 回购定价错误：2016 年信"在一个价格上聪明的事，在另一个价格上就是蠢事"（What is smart at one price is stupid at another）。
- 过度分散：1997 年信"对能看懂生意的人，常规分散只会损害结果、增加风险"。
