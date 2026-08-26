# 原则提取候选 · 《股票大作手回忆录》

- 提取器: cangjie-skill / principle-extractor
- 输入: BOOK_OVERVIEW.md + chunks/part_01.txt ~ part_09.txt
- 覆盖范围: 全部 9 个 chunk 均已精读（第 I-XXIV 章，正文 24 章完整覆盖）
- 筛选聚焦: 基金持仓管理（止损、止盈、分批、等待、不预测、不追消息、认识自己）
- 引用均为书中英文原文（每条 <=100 词），summary 为中文自述

## 候选清单

- id: p01
  title: 市场只有一边——正确的一边
  type: maxim
  source_chapter: 第 III 章（part_01）
  source_quote: |
    "But there is only one side to the stock market; and it is not the bull
    side or the bear side, but the right side."
  summary: |
    全书最著名的断言：市场不分成多空两个阵营，只分成对与错。
    判断依据不是立场、仓位或情绪，而是对基本条件的解读。
    对基金而言，意味着不因持仓而预设方向，不因浮盈浮亏而站队，
    只跟随条件指向的那一边；错了就站到另一边，而不是死守原方向。
  tags: [principle, direction, bias-free]

- id: p02
  title: 顺势而为：牛市做多，熊市做空
  type: principle
  source_chapter: 第 VIII 章（part_03）
  source_quote: |
    "Obviously the thing to do was to be bullish in a bull market and bearish
    in a bear market. Sounds silly, doesn't it? But I had to grasp that
    general principle firmly before I saw that to put it into practice really
    meant to anticipate probabilities."
  summary: |
    方向判断优先于个股选择：整个市场沿主流运行，个股多数跟随大势。
    操作上与趋势同向，把顺势落实为对概率的预先判断，而不是事后解释。
    基金持仓管理应首先回答"现在是什么市场"，再决定仓位方向和暴露度，
    避免在大趋势中逆势重仓。
  tags: [principle, trend, position-sizing]

- id: p03
  title: 看对方向不算赢，拿得住头寸才算（坐得住）
  type: principle
  source_chapter: 第 V 章（part_02，帕特里奇/老火鸡段落）
  source_quote: |
    "It never was my thinking that made the big money for me. It was always my
    sitting. Got that? My sitting tight! It is no trick at all to be right on
    the market. ... Men who can both be right and sit tight are uncommon. I
    found it one of the hardest things to learn. But it is only after a stock
    operator has firmly grasped this that he can make big money."
  summary: |
    看对方向的人很多，但看得对又拿得住的人极少。
    许多人因不耐烦或怀疑，在大行情启动前就下车，等于白看对。
    老火鸡的"这是牛市"就是在提示：大钱来自坐住不动，而非频繁进出。
    对基金而言，盈利头寸要敢于持有，用趋势终结信号而非短期波动决定离场。
  tags: [principle, patience, holding]

- id: p04
  title: 大钱在大行情：不要试图抓住每次波动
  type: principle
  source_chapter: 第 V 章（part_02）
  source_quote: |
    "Disregarding the big swing and trying to jump in and out was fatal to me.
    Nobody can catch all the fluctuations. In a bull market your game is to
    buy and hold until you believe that the bull market is near its end."
  summary: |
    试图抓住每一次涨跌的人终会被反复打脸；利润来自大波段而非小差价。
    牛市中的正确做法是买入并持有到趋势接近终结，中途不折腾。
    这直接支撑基金"让利润奔跑"的持有纪律：不为蝇头小利提前兑现核心仓位，
    同时明确离场条件——趋势反转而非短期回调。
  tags: [principle, big-swing, hold]

- id: p05
  title: 止损要快：认定错了就立刻离场
  type: rule
  source_chapter: 第 IX 章（part_03，Anaconda 案例）
  source_quote: |
    "the only thing to do when a man is wrong is to be right by ceasing to be
    wrong. ... When you want to get out, get out."
  summary: |
    判断错误后唯一正确的动作是停止错误——立刻离场，而不是等反弹、等回本。
    卖出时不与价格讨价还价，不用限价单拖延（想走就走）。
    对基金而言，止损纪律要预先设定并机械执行：先保本金，再谈盈利；
    犹豫与侥幸是亏损放大的根源。
  tags: [rule, stop-loss, discipline]

- id: p06
  title: 卖掉亏损的、拿住盈利的；绝不摊平亏损
  type: rule
  source_chapter: 第 XIII 章（part_05，Percy Thomas 棉花教训）
  source_quote: |
    "Of all speculative blunders there are few greater than trying to average
    a losing game. ... Always sell what shows you a loss and keep what shows
    you a profit."
  summary: |
    利弗莫尔在棉花上反向操作——砍盈利、留亏损、越亏越买——几乎破产，
    由此总结出最反直觉的规则：亏损仓位是错误信号，应砍掉；
    盈利仓位是正确信号，应保留。摊平亏损（越跌越买摊低成本）
    是最大的投机错误之一。基金补仓必须有独立依据，
    绝不能以摊低成本为唯一理由。
  tags: [rule, cut-losses, no-averaging]

- id: p07
  title: 分批建仓：只在首仓盈利后加仓
  type: rule
  source_chapter: 第 VII 章（part_03）
  source_quote: |
    "Remember that stocks are never too high for you to begin buying or too
    low to begin selling. But after the initial transaction, don't make a
    second unless the first shows you a profit. Wait and watch."
  summary: |
    初始仓位小步试探，加仓条件是前一笔已经盈利——用市场的确认来验证判断。
    首仓亏损意味着时机或方向暂时错了，此时应停止加码而不是补仓摊平。
    这正是基金分批建仓的理论原型：金字塔式加仓、右侧确认，
    把大注押在验证过的方向上，小注用于试探。
  tags: [rule, scaling, pyramid]

- id: p08
  title: 等待信号：横盘不预测，等最小阻力线明确
  type: principle
  source_chapter: 第 X 章（part_04）
  source_quote: |
    "In a narrow market, when prices are not getting anywhere to speak of but
    move within a narrow range, there is no sense in trying to anticipate what
    the next big movement is going to be--up or down. The thing to do is to
    watch the market, read the tape to determine the limits of the get-nowhere
    prices, and make up your mind that you will not take an interest until the
    price breaks through the limit in either direction."
  summary: |
    窄幅震荡中无法预测突破方向，硬猜只会两头挨打；
    正确动作是观望并等待价格突破区间边界，让最小阻力线自己显现。
    对基金而言：不预测、只跟随；方向未明时降低操作频率，
    用突破确认替代主观猜测——这是等待与不预测两条原则的合一。
  tags: [principle, patience, no-predict]

- id: p09
  title: 不追消息、不靠 tips：只信自己的判断
  type: principle
  source_chapter: 第 III 章（part_01）
  source_quote: |
    "I don't believe in tips. If I buy stocks on Smith's tip I must sell those
    same stocks on Smith's tip. I am depending on him. ... No, sir, nobody can
    make big money on what someone else tells him to do."
  summary: |
    靠别人的消息买入，就必须靠别人的消息卖出——命运完全交在他人手中。
    没有人能靠别人告诉他的买卖赚大钱；判断必须建立在自己的分析上。
    对基金而言：拒绝把内幕、小道消息、专家荐股作为建仓依据，
    消息最多是背景信息，决策必须回到自身的研究框架与风控规则。
  tags: [principle, no-tips, independent]

- id: p10
  title: 认识自己：战胜希望与恐惧
  type: principle
  source_chapter: 第 X 章（part_04）
  source_quote: |
    "The speculator's chief enemies are always boring from within. It is
    inseparable from human nature to hope and to fear. ... Instead of hoping
    he must fear; instead of fearing he must hope. He must fear that his loss
    may develop into a much bigger loss, and hope that his profit may become a
    big profit."
  summary: |
    亏损时人靠希望死扛导致亏损扩大，盈利时人因恐惧过早离场丢掉利润。
    交易者必须反转本能：该怕的是亏损变大，该盼的是利润变大。
    这是认识自己的核心：基金管理者要把人性弱点前置管理，
    用预设止损、纪律化止盈对抗希望与恐惧，而不是临场靠意志力。
  tags: [principle, psychology, self-knowledge]

- id: p11
  title: 止盈不贪：不卖在最高点，有机会就兑现
  type: rule
  source_chapter: 第 XIV 章 + 第 XVII 章（part_05/part_06）
  source_quote: |
    "Never try to sell at the top. It isn't wise. Sell after a reaction if
    there is no rally. ... Experience has taught me that a man can always find
    an opportunity to make his profits real and that this opportunity usually
    comes at the end of the move."
  summary: |
    卖在最高点既不现实也不明智；真正重要的是在行情终结前让利润落袋。
    纸面利润只有变成现金才算数，兑现窗口通常出现在大行情尾段。
    对基金而言：止盈不必追求卖顶，设定分批兑现计划，
    在流动性好、市场仍活跃时执行，避免趋势反转后利润大幅回吐。
  tags: [rule, take-profit, realize]

- id: p12
  title: 独立判断：人情与说服不能凌驾于自己的判断
  type: principle
  source_chapter: 第 XIII 章（part_05，Williamson 与 Percy Thomas 教训）
  source_quote: |
    "I learned that the weaknesses to which a speculator is prone are almost
    numberless. It was proper for me as a man to act the way I did in Dan
    Williamson's office, but it was improper and unwise for me as a speculator
    to allow myself to be influenced by any consideration to act against my
    own judgment. Noblesse oblige--but not in the stock market, because the
    tape is not chivalrous and moreover does not reward loyalty."
  summary: |
    利弗莫尔两次重大失败——棉花上被 Thomas 说服、被 Williamson 的人情困住——
    都是让别人替自己做判断。受人情、权威、魅力人格影响而违背己见，
    在投机中是致命弱点。对基金而言：决策链路上要隔离外部说服，
    投研结论与执行规则高于情面；尊重他人不等于放弃自己的独立判断。
  tags: [principle, independence, no-influence]

## 覆盖范围说明

- 实际精读: part_01 到 part_09 共 9 个 chunk，第 I-XXIV 章正文完整覆盖，无遗漏
- 引用: 全部取自书中英文原文，每条 <=100 词，未改写
- 筛选方向: 止损（p05/p06）、止盈（p11）、分批（p07）、等待（p08）、
  不预测（p08）、不追消息（p09）、认识自己（p10），另含顺势、坐住、大行情、独立判断等核心原则
