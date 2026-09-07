# FundOS 基金引擎运行报告
> 运行时间: 2026-09-07T20:30:16.302919+08:00
> 模式: quick

## 执行状态

- 市场扫描: 通过
- 持仓诊断: 通过
- 新闻采集: 通过
- 盘后净值检查: 通过
- 组合风险分析: 通过
- 技能注册: 22 个

## 组合风险指标 (近120日)

- 年化波动: 26.82% | 最大回撤: -15.92% (2026-06-30→2026-07-30)
- 夏普(rf=0): 0.1 | HHI集中度: 0.145 (有效基金数 ~6.9)

## 新闻来源状态

- 快讯: ok，170条
- sina_roll: ok，25条
- ths_news: ok，20条
- eastmoney_search: ok，144条
- wallstreetcn_live: ok，30条

## 技能调度

- 盘后检查文件: [daily_check_2026-09-07.md](daily_check_2026-09-07.md)
- 持仓数据基准: daily_check_result.json
- 科技/AI估算仓位: 37.8%
- 深度亏损标的: 全球成长

- **sector-rotation-detector + trend-following-minimum-resistance**
  - 证据: 市场扫描已完成，先比较主线与持仓相对强弱
  - 动作: 观察主线是否连续，暂不因单日强势追入
  - 边界: 至少等待价格和成交连续确认
- **stop-loss-admission + timely-correction + emotion-discipline-system**
  - 证据: 全球成长 -23.05%
  - 动作: 停止摊平，反弹窗口重新评估并分批纠错
  - 边界: 不以回本作为唯一卖出条件；接近-25%重新审查逻辑
- **hold-winners + hold-three-conditions**
  - 证据: 标普500 +1.80%
  - 动作: 先检查底层逻辑和估值，再决定持有或费率换类
  - 边界: 不因小幅盈利机械止盈
- **narrative-news-check + price-action-first + independent-judgment**
  - 证据: 采集新闻 170 条，存在情绪参考信号
  - 动作: 新闻只进入观察层，必须等待价格行为确认
  - 边界: 新闻情绪不得单独触发买卖

## 规则

新闻情绪和涨跌预测仅作为参考信号；最终判断必须结合市场价格、持仓结构、止损边界和技能规则。

> 本报告不构成投资建议。