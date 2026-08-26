# 模块接口规范 (Module Specifications)

## 一、Data Hub

### 目录结构

```
data-hub/
├── pyproject.toml
├── data_hub/
│   ├── __init__.py
│   ├── server.py              # gRPC server入口
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── crawler.py         # 异步爬虫引擎 (← FundCrawler engine.py)
│   │   ├── normalizer.py      # 数据归一化管道
│   │   ├── cache.py           # Redis缓存层
│   │   ├── limiter.py         # 限流器
│   │   └── ws_broadcaster.py  # WebSocket广播
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py            # BaseProvider抽象类
│   │   ├── registry.py        # Provider注册表
│   │   ├── eastmoney/         # (← efinance)
│   │   │   ├── __init__.py
│   │   │   ├── stock.py
│   │   │   ├── fund.py
│   │   │   ├── bond.py
│   │   │   └── futures.py
│   │   ├── tiantian/          # (← FundCrawler page_parser/tiantian.py)
│   │   │   ├── __init__.py
│   │   │   └── parser.py
│   │   ├── morningstar/       # (← FundCrawler page_parser/morningstar.py)
│   │   │   ├── __init__.py
│   │   │   └── parser.py
│   │   ├── sina/              # (← go-stock sina_kline_api.go)
│   │   ├── tdx/               # (← go-stock tdx_kline_api.go)
│   │   ├── tushare/           # (← go-stock tushare_data_api.go)
│   │   └── xueqiu/            # (← go-stock xueqiu_chromedp.go)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── fund.py            # FundNav, FundEstimate, FundHoldings
│   │   ├── stock.py           # StockQuote, StockKline
│   │   ├── bond.py            # BondQuote
│   │   └── futures.py         # FuturesQuote
│   ├── protos/                # gRPC protobuf定义
│   │   ├── fund.proto
│   │   ├── stock.proto
│   │   ├── bond.proto
│   │   └── futures.proto
│   └── config/
│       ├── default.yaml
│       └── schema.py
└── tests/
```

### gRPC 服务接口

```protobuf
// fund.proto
service FundService {
  rpc GetNavHistory(FundNavRequest) returns (stream FundNav);
  rpc GetEstimate(FundEstimateRequest) returns (FundEstimate);
  rpc GetHoldings(FundHoldingsRequest) returns (FundHoldings);
  rpc SearchFund(SearchRequest) returns (SearchResponse);
  rpc StreamRealtime(stream FundCodeRequest) returns (stream FundRealtime);
}
```

## 二、Quant Engine

### 目录结构

```
quant-engine/
├── pyproject.toml
├── quant/
│   ├── __init__.py
│   ├── backtest/              # (← xalpha)
│   │   ├── __init__.py
│   │   ├── environment.py     # BTE基类 + BTE_V2
│   │   ├── fund.py            # fundinfo类 (← xalpha info.py)
│   │   ├── trade.py           # 交易模拟 (← xalpha trade.py)
│   │   ├── portfolio.py       # 多基金组合 (← xalpha multiple.py)
│   │   ├── policy.py          # 策略基类 (← xalpha policy.py)
│   │   └── evaluate.py        # 评价函数 (← xalpha evaluate.py)
│   ├── indicators/            # 指标体系
│   │   ├── __init__.py
│   │   ├── risk.py            # 风险指标 (← xalpha indicator.py)
│   │   └── flow.py            # 资金流指标 (← go-stock)
│   ├── signals/               # ★ 信号引擎
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── ma_cross.py        # 均线交叉
│   │   ├── rsi.py             # RSI超买超卖
│   │   ├── macd.py            # MACD金叉死叉
│   │   ├── volume.py          # 量价信号
│   │   └── composite.py       # 多因子合成
│   ├── models/                # ★ 统一信息模型
│   │   ├── __init__.py
│   │   ├── fund.py
│   │   ├── stock.py
│   │   └── portfolio.py
│   └── config/
│       └── default.yaml
└── tests/
```

### 策略编写接口

```python
from quant.backtest.environment import BTE_V2

class MyStrategy(BTE_V2):
    def prepare(self):
        """初始化: 设定标的、参数"""
        self.fund = self.add_fund("000001")
        self.ma_short = 5
        self.ma_long = 20

    def run(self, date):
        """每个交易日调用: 策略核心逻辑"""
        nav_history = self.fund.nav_history(until=date)

        if len(nav_history) < self.ma_long:
            return  # 数据不足

        ma5 = nav_history[-self.ma_short:].mean()
        ma20 = nav_history[-self.ma_long:].mean()

        if ma5 > ma20 and self.fund.position == 0:
            self.buy(self.fund, percent=0.5)
        elif ma5 < ma20 and self.fund.position > 0:
            self.sell(self.fund, percent=1.0)

# 运行
s = MyStrategy(start="2024-01-01", end="2025-12-31", totmoney=100000)
s.run_all()
print(s.summary())
print(await s.ai_interpret())  # AI解读
```

## 三、AI Brain

### 目录结构

```
ai-brain/
├── go.mod
├── go.sum
├── main.go
├── agent/
│   ├── orchestrator.go       # (← go-stock agent.go)
│   ├── intent.go             # (← go-stock agent_intent)
│   ├── memory.go             # (← go-stock chat_memory.go)
│   ├── factory.go            # (← go-stock chat_model_factory.go)
│   └── trace.go              # (← go-stock agent_trace.go)
├── tools/
│   ├── registry.go           # (← go-stock tool_registry.go)
│   ├── finance/
│   │   ├── kline.go          # (← go-stock)
│   │   ├── market_data.go    # (← go-stock)
│   │   ├── fund_data.go      # ★ 新增
│   │   ├── sentiment.go      # (← go-stock)
│   │   ├── chip.go           # (← go-stock)
│   │   └── backtest.go       # ★ 新增 (gRPC→Quant Engine)
│   ├── notification/
│   │   ├── dingtalk.go       # (← go-stock)
│   │   ├── feishu.go         # (← go-stock feishu_bot.go)
│   │   └── email.go          # ★ 新增
│   └── search/
│       ├── web_search.go     # (← go-stock)
│       └── stock_search.go   # (← go-stock)
├── mcp/
│   └── server.go             # (← go-stock mcp_server_api.go)
└── cron/
    └── scheduler.go          # (← go-stock cron_task_api.go)
```

### Tool 接口

```go
type Tool interface {
    Name() string
    Description() string
    Parameters() []Parameter
    Execute(ctx context.Context, params map[string]any) (string, error)
}

// 示例: 基金数据分析工具
type FundAnalysisTool struct {
    quantClient QuantEngineClient  // gRPC client
}

func (t *FundAnalysisTool) Name() string { return "fund_analysis" }
func (t *FundAnalysisTool) Description() string {
    return "分析指定基金的全面数据：净值走势、风险指标、持仓分析、同类排名"
}
func (t *FundAnalysisTool) Parameters() []Parameter {
    return []Parameter{
        {Name: "fund_code", Type: "string", Required: true, Description: "6位基金代码"},
        {Name: "analysis_type", Type: "string", Required: false, Description: "nav/risk/holdings/all"},
    }
}
```

## 四、API Gateway

### 端点路由

```
REST (public):
  GET    /api/v1/funds/:code/nav          → Data Hub
  GET    /api/v1/funds/:code/estimate     → Data Hub
  GET    /api/v1/stocks/:code/quote       → Data Hub
  GET    /api/v1/stocks/:code/kline       → Data Hub
  POST   /api/v1/backtest/run             → Quant Engine
  GET    /api/v1/backtest/:id/result      → Quant Engine
  POST   /api/v1/ai/chat                  → AI Brain
  GET    /api/v1/ai/report/:type          → AI Brain
  WS     /ws/realtime                     → Data Hub (streaming)
  WS     /ws/ai/chat                      → AI Brain (streaming)

gRPC (internal):
  fundos.data.v1.FundService              → Data Hub
  fundos.data.v1.StockService             → Data Hub
  fundos.quant.v1.BacktestService         → Quant Engine
  fundos.ai.v1.AgentService               → AI Brain

MCP (AI agent):
  fundos_data_search                      → Data Hub
  fundos_backtest_run                     → Quant Engine
  fundos_sentiment_analysis               → AI Brain
  fundos_kline_interpret                  → AI Brain
  fundos_portfolio_risk                   → AI Brain + Quant Engine
```
