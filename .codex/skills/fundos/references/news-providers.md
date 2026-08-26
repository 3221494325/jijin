# 新闻数据源注册表 (News Provider Registry)

> 继承自 go-stock 的新闻采集模块 (tool_cailianpress_opinion.go / tool_wallstreetcn.go / market_news_api.go / web_search_api.go)

## 注册表

| Provider ID | 名称 | 类型 | 内容 | 采集方式 | 频率限制 | 
|-------------|------|:----:|------|----------|:--------:|
| `cls` | 财联社 | 快讯 | 实时电报/7x24快讯 | API | ~30/min |
| `eastmoney_news` | 东方财富资讯 | 新闻 | 板块新闻/个股公告 | API | ~60/min |
| `wallstreetcn` | 华尔街见闻 | 深度 | 市场分析/专题 | Web | ~20/min |
| `sina_finance` | 新浪财经 | 综合 | 市场资讯/行业新闻 | Web | ~30/min |
| `cailianpress` | 财联社观点 | 观点 | 机构观点/深度 | Web | ~20/min |
| `baidu_finance` | 百度财经 | 综合 | 聚合新闻 | Web | ~30/min |

## 情绪分类规则

基于关键词匹配（简单但实用），不依赖大模型：

```python
POSITIVE = ["利好", "大涨", "突破", "创新高", "增长", "超预期",
            "政策支持", "扶持", "回暖", "反弹", "拉升", "走强",
            "领涨", "净流入", "加速"]
NEGATIVE = ["利空", "大跌", "暴跌", "下挫", "亏损", "不及预期",
            "监管", "处罚", "退市", "风险", "预警", "承压",
            "走弱", "领跌", "净流出", "下滑"]
```

⚠️ 此分类为快速参考，不保证准确性。请阅读原文自行判断。

## 持仓→板块映射

| 你的持仓 | 相关板块 |
|----------|----------|
| 华夏绿色电力ETF | 绿色电力、新能源、光伏、风电、碳中和 |
| 易方达全球成长QDII | QDII、全球市场、美股 |
| 摩根标普500 QDII | 标普500、美股、美联储 |
| 摩根纳斯达克100 QDII | 纳斯达克、美股科技、AI、七巨头 |
| 中欧半导体股票 | 半导体、芯片、集成电路、光刻机 |
| 易方达信息产业混合 | AI、信息技术、数字经济、信创 |
| 易方达科创50联接 | 科创50、科创板、硬科技 |
| 永赢科技智选混合 | AI应用、机器人、自动驾驶、TMT |

## 使用方式

### 命令行
```bash
# 全部板块
python scripts/news_fetch.py

# 指定板块
python scripts/news_fetch.py --sector 半导体

# 导出
python scripts/news_fetch.py --output news_brief.md
```

### Codex 对话
```
"帮我搜半导体板块最新消息"
"生成今天持仓板块新闻简报"
"最近美股有什么利空消息"
"分析AI板块新闻情绪"
```

## 缓存策略

- 本地缓存目录: `~/FundOS/news_cache/`
- 缓存有效期: 30分钟
- 清除缓存: `python scripts/news_fetch.py --clear-cache`

## 继承来源

go-stock 源码中已有的新闻相关模块:
- `backend/data/tool_cailianpress_opinion.go` — 财联社观点采集
- `backend/data/tool_wallstreetcn.go` — 华尔街见闻采集
- `backend/data/market_news_api.go` — 市场新闻API
- `backend/data/web_search_api.go` — 联网搜索

FundOS News Module 将这些 Go 模块的逻辑移植为 Python 实现。
