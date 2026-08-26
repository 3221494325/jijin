# 数据源注册表 (Data Source Registry)

## 注册表总览

| Provider ID | 名称 | 资产类型 | 数据粒度 | 源仓库 | 稳定度 |
|-------------|------|----------|----------|--------|:------:|
| `eastmoney` | 东方财富 | 股票/基金/期货/债券 | 实时+历史+深度 | efinance | ⭐⭐⭐⭐⭐ |
| `tiantian` | 天天基金 | 基金 | 净值+估值+持仓 | FundCrawler/R1 | ⭐⭐⭐⭐ |
| `morningstar` | 晨星 | 基金 | 评级+分析 | FundCrawler | ⭐⭐⭐ |
| `sina` | 新浪财经 | 股票 | K线+实时 | go-stock | ⭐⭐⭐⭐ |
| `tdx` | 通达信 | 股票 | K线 | go-stock | ⭐⭐⭐ |
| `tencent` | 腾讯财经 | 股票 | 实时行情 | real-time-fund | ⭐⭐⭐ |
| `xueqiu` | 雪球 | 股票 | 实时+讨论 | go-stock | ⭐⭐⭐ |
| `iwencai` | 同花顺i问财 | 股票 | AI选股 | go-stock | ⭐⭐⭐ |
| `tushare` | Tushare | 股票/基金/期货 | 历史+财务 | go-stock | ⭐⭐⭐⭐ |
| `jqdata` | 聚宽 | 股票/基金 | 历史+财务 | xalpha | ⭐⭐⭐ |
| `cailianpress` | 财联社 | 新闻/舆情 | 实时 | go-stock | ⭐⭐⭐ |
| `wallstreetcn` | 华尔街见闻 | 新闻/舆情 | 实时 | go-stock | ⭐⭐⭐ |
| `cls` | CLS财联 | 市场统计 | 实时 | go-stock | ⭐⭐⭐ |

## Provider 详细规格

### 1. eastmoney (东方财富) ← efinance 核心

```
资产类型: stock, fund, bond, futures
数据类别:
  - stock/realtime: 实时行情 (get_realtime_quotes)
  - stock/kline: K线历史 (get_quote_history)
  - stock/base_info: 基本信息 (get_base_info)
  - stock/billboard: 龙虎榜 (get_daily_bill_board)
  - stock/deal_detail: 分时成交
  - stock/fund_flow: 板块/个股资金流
  - fund/nav: 基金净值历史 (get_quote_history)
  - fund/estimate: 基金实时估值
  - fund/holdings: 基金持仓
  - bond/convertible: 可转债
  - futures/quote: 期货行情
限流: ~100 req/min (需代理池)
架构: requests + multitasking + beautifulsoup + jsonpath
移植要点: 所有getter函数 → BaseProvider接口模式
```

### 2. tiantian (天天基金) ← FundCrawler + real-time-fund

```
资产类型: fund
数据类别:
  - fund/nav: 净值历史
  - fund/estimate: 实时估值 (JSONP接口)
  - fund/holdings: 前10大重仓股
  - fund/manager: 基金经理信息
  - fund/profile: 基金概况
  - fund/feature: 特色数据 (夏普/波动率/最大回撤)
接入方式: HTTP GET + HTML解析 + JSONP
限流: ~50 req/min
移植要点: FundCrawler page_parser/tiantian.py → BaseProvider
          R1的JSONP方案可作为浏览器端直连方案保留
```

### 3. morningstar (晨星) ← FundCrawler

```
资产类型: fund
数据类别:
  - fund/rating: 晨星评级
  - fund/risk: 风险分析
  - fund/performance: 业绩分析
接入方式: HTTP GET + HTML解析
限流: ~20 req/min (较严格)
移植要点: FundCrawler page_parser/morningstar.py → BaseProvider
```

### 4. sina (新浪财经) ← go-stock

```
资产类型: stock
数据类别:
  - stock/kline: K线数据 (日/周/月)
  - stock/realtime: 实时行情
接入方式: HTTP GET + JSON解析
移植要点: Go代码 → Python重写 (sina_kline_api.go → providers/sina.py)
```

### 5. tdx (通达信) ← go-stock

```
资产类型: stock
数据类别:
  - stock/kline: K线数据
接入方式: 自定义二进制协议
移植要点: Go代码 → Python重写 (tdx_kline_api.go → providers/tdx.py)
注意: 通达信使用专有二进制协议，解析复杂度高
```

### 6-8. 其他

tencent (腾讯财经), xueqiu (雪球), iwencai (i问财), tushare, jqdata, cailianpress (财联社), wallstreetcn (华尔街见闻), cls (CLS财联) 均继承自 go-stock 的对应API模块，需要 Go→Python 重写。

## 数据归一化 (Normalizer)

所有 provider 的原始数据归一化到以下统一 schema:

### 基金净值 (fund_nav)

```json
{
  "code": "000001",           // 6位代码
  "name": "华夏成长混合",     // 名称
  "date": "2026-01-15",       // 日期
  "nav": 1.2345,              // 单位净值
  "acc_nav": 3.4567,          // 累计净值
  "daily_return": 0.0123,     // 日涨跌幅 (小数)
  "estimate_nav": 1.2350,     // 估算净值 (可选)
  "estimate_return": 0.0128,  // 估算涨跌幅 (可选)
  "source": "eastmoney"       // 数据来源
}
```

### 股票行情 (stock_quote)

```json
{
  "code": "000001",           // 代码 (深市)/ "600001" (沪市)
  "market": "sz",             // sh/sz/hk/us
  "name": "平安银行",
  "date": "2026-01-15",
  "open": 12.50,
  "high": 12.80,
  "low": 12.30,
  "close": 12.65,
  "volume": 123456789,
  "amount": 1567890123.45,
  "change_pct": 0.0213,
  "source": "eastmoney"
}
```
