# FundOS 系统架构（深度优化设计）

> 基于六仓库技术拆解融合分析，从 P0-P2 优化方向提炼的工程级架构规格。

## 一、部署拓扑

```
┌─────────────────────────────────────────────────────────────┐
│  CDN / Static Hosting                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Web App  │  │ Extension│  │ Doc Site │                  │
│  │(Next.js) │  │(Chrome)  │  │(VitePress)│                  │
│  └────┬─────┘  └──────────┘  └──────────┘                  │
│       │                                                     │
├───────┼─────────────────────────────────────────────────────┤
│  VPS / Cloud Server                                         │
│  ┌────┴────────────────────────────────────────┐            │
│  │        API Gateway (Go)                     │            │
│  │  ┌──────────┬──────────┬──────────┐        │            │
│  │  │ REST :80 │ gRPC:9090│ MCP :3456│        │            │
│  │  └──────────┴──────────┴──────────┘        │            │
│  └────┬───────────────────────┬───────────────┘            │
│       │                       │                             │
│  ┌────┴────────┐    ┌────────┴────────┐                    │
│  │ Data Hub    │    │  AI Brain (Go)  │                    │
│  │ (Python)    │    │  Agent/Tools    │                    │
│  │ :50051      │    │  :50052         │                    │
│  └────┬────────┘    └─────────────────┘                    │
│       │                                                     │
│  ┌────┴────────┐                                           │
│  │ Quant Engine│                                           │
│  │ (Python)    │                                           │
│  │ :50053      │                                           │
│  └────┬────────┘                                           │
│       │                                                     │
│  ┌────┴────────────────────────────┐                       │
│  │  PostgreSQL  │  Redis  │ MinIO  │                       │
│  └──────────────┴─────────┴────────┘                       │
├─────────────────────────────────────────────────────────────┤
│  Desktop (Local)                                            │
│  ┌──────────────────────────────┐                          │
│  │  Wails App (Go+Vue)          │                          │
│  │  ├── Embedded SQLite (local) │                          │
│  │  └── → API Gateway (remote)  │                          │
│  └──────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## 二、Data Hub — 统一数据总线

### 分层架构

```
┌─────────────────────────────────────────────┐
│              gRPC Server (:50051)            │
│  ┌─────────────────────────────────────┐    │
│  │        Service Layer                 │    │
│  │  FundService / StockService /        │    │
│  │  BondService / FuturesService        │    │
│  └──────────────┬──────────────────────┘    │
│                 │                            │
│  ┌──────────────┴──────────────────────┐    │
│  │        Normalizer Pipeline           │    │
│  │  RawData → CleanData → CanonicalData │    │
│  └──────────────┬──────────────────────┘    │
│                 │                            │
│  ┌──────────────┴──────────────────────┐    │
│  │        Provider Registry             │    │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐       │    │
│  │  │天天│ │东方│ │晨星│ │新浪│  ...   │    │
│  │  │基金│ │财富│ │    │ │    │        │    │
│  │  └────┘ └────┘ └────┘ └────┘       │    │
│  └──────────────┬──────────────────────┘    │
│                 │                            │
│  ┌──────────────┴──────────────────────┐    │
│  │        Infrastructure                │    │
│  │  Cache(Redis) │ RateLimiter │ Proxy  │    │
│  │  CircuitBreaker │ Retry │ Logger    │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Provider接口规范

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass

@dataclass
class ProviderCapability:
    asset_types: list[str]       # ["fund", "stock", "bond", "futures"]
    data_types: list[str]        # ["realtime", "history", "holdings", "profile"]
    rate_limit: int              # requests per minute
    region: str                  # "cn" | "global"

class BaseProvider(ABC):
    @abstractmethod
    async def fetch(self, code: str, data_type: str, **params) -> dict:
        """原始数据获取"""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """连通性检测"""
        ...

    @abstractmethod
    def capability(self) -> ProviderCapability:
        """能力声明"""
        ...

    async def normalize(self, raw: dict, schema: str) -> dict:
        """数据归一化（可覆写）"""
        ...

    async def stream(self, codes: list[str], data_type: str) -> AsyncIterator[dict]:
        """流式数据推送（WebSocket后端）"""
        ...
```

### 源仓库代码继承映射

| Data Hub 模块 | 继承自 | 继承方式 |
|---------------|--------|----------|
| `providers/eastmoney/` | efinance stock/fund/bond/futures getter | 直接移植+接口适配 |
| `providers/tiantian/` | FundCrawler page_parser/tiantian.py | 移植解析逻辑 |
| `providers/morningstar/` | FundCrawler page_parser/morningstar.py | 移植解析逻辑 |
| `providers/sina/` | go-stock sina_kline_api.go | Python重写 |
| `providers/tdx/` | go-stock tdx_kline_api.go | Python重写 |
| `providers/tushare/` | go-stock tushare_data_api.go | Python重写 |
| `engine/async_crawler.py` | FundCrawler engine.py | 移植异步引擎 |
| `engine/normalizer.py` | — | 全新设计 |
| `engine/cache_layer.py` | — | 全新设计 |

## 三、Quant Engine — 量化分析引擎

### 模块结构

```
quant-engine/
├── backtest/           # ← 移植自 xalpha
│   ├── environment.py  # BTE基类 + GlobalRegister
│   ├── fund.py         # fundinfo/mfundinfo/cashinfo
│   ├── trade.py        # trade/itrade
│   ├── portfolio.py    # mul/mulfix
│   └── policy.py       # 策略基类
├── indicators/         # ← 移植自 xalpha indicator.py
│   ├── risk.py         # 夏普/回撤/波动率
│   ├── performance.py  # Alpha/Beta/信息比率
│   └── flow.py         # ← 移植自 go-stock 资金流分析
├── signals/            # ★ 全新模块
│   ├── base.py         # 信号基类
│   ├── technical.py    # 技术指标信号
│   ├── fundamental.py  # 基本面信号
│   ├── sentiment.py    # 情绪信号（从AI Brain获取）
│   └── composite.py    # 多因子合成
├── models/             # ★ 全新模块
│   ├── fund.py         # 基金统一信息模型
│   ├── stock.py        # 股票统一信息模型
│   └── portfolio.py    # 组合统一模型
└── registry/           # ★ 全新模块
    └── strategy_registry.py
```

### BTE增强设计（P0优化）

```python
class BTE_V2(BTE):  # 继承 xalpha 原始 BTE
    """增强版回测引擎"""

    def __init__(self, start, end=None, totmoney=1000000,
                 benchmark: str = "000300",  # ★ 新增：基准指数
                 commission: float = 0.0001, # ★ 新增：手续费率
                 slippage: float = 0.001,    # ★ 新增：滑点
                 **kws):
        super().__init__(start, end, totmoney, **kws)
        self.benchmark = benchmark
        self.commission = commission
        self.slippage = slippage

    def run(self, date):
        """子类实现策略逻辑"""
        pass

    def summary(self) -> dict:
        """★ 新增：回测摘要报告（自动生成）"""
        return {
            "total_return": ...,
            "annual_return": ...,
            "sharpe": ...,
            "max_drawdown": ...,
            "win_rate": ...,
            "benchmark_return": ...,
            "excess_return": ...,  # Alpha
        }

    async def ai_interpret(self) -> str:
        """★ 新增：AI解读回测结果（调用AI Brain）"""
        ...
```

## 四、AI Brain — AI分析大脑

### 继承自 go-stock backend/agent + backend/data

```
ai-brain/
├── agent/
│   ├── orchestrator.go    # ← 移植 agent.go
│   ├── intent.go          # ← 移植 agent_intent
│   ├── memory.go          # ← 移植 chat_memory.go
│   ├── factory.go         # ← 移植 chat_model_factory.go
│   └── trace.go           # ← 移植 agent_trace.go
├── tools/                 # ← 移植 backend/data tool_*.go
│   ├── registry.go        # ← 移植 tool_registry.go
│   ├── finance/           # 金融工具集
│   │   ├── kline.go
│   │   ├── market_data.go
│   │   ├── fund_data.go   # ★ 新增：基金数据工具
│   │   ├── sentiment.go   # ← 移植
│   │   ├── chip.go        # ← 移植筹码分布
│   │   └── backtest.go    # ★ 新增：回测工具（调用Quant Engine）
│   ├── notification/      # 通知工具集
│   │   ├── dingtalk.go    # ← 移植
│   │   ├── feishu.go      # ← 移植
│   │   └── email.go       # ★ 新增
│   └── search/            # 搜索工具集
│       ├── web_search.go  # ← 移植
│       └── stock_search.go# ← 移植
├── mcp/                   # ← 移植 MCP Server
│   └── server.go
└── cron/                   # ← 移植 cron_task_api.go
    └── scheduler.go
```

### 关键优化：基金AI分析（go-stock当前缺失）

go-stock 仅有 `fund_data_api.go` 和 `fund_kline_api.go`（基础数据），缺失：

1. **基金工具链**: `tool_fund_portfolio.go` — 基金组合分析
2. **基金经理分析**: `tool_fund_manager.go` — 经理历史业绩/风格漂移
3. **基金对比**: `tool_fund_compare.go` — 多基金横向对比
4. **定投计算器**: `tool_fund_aip.go` — 定投收益模拟

## 五、交互层设计

### Web App (← real-time-fund)

```
web/
├── app/                  # Next.js App Router
│   ├── (dashboard)/      # 仪表盘
│   │   ├── funds/        # 基金列表/详情
│   │   ├── stocks/       # ★ 新增：股票模块
│   │   ├── portfolio/    # ★ 增强：统合持仓（基金+股票+期货）
│   │   └── strategy/     # ★ 新增：策略管理/回测
│   ├── api/              # BFF层 → API Gateway
│   └── layout.tsx
├── components/
│   ├── ui/               # shadcn/ui (保留R1)
│   ├── fund/             # 基金组件（保留R1）
│   ├── stock/            # ★ 新增：股票组件
│   └── ai/               # ★ 新增：AI对话面板
├── stores/               # Zustand stores (保留R1模式)
└── hooks/                # React hooks
```

**保留R1的**: 玻璃拟态UI、持仓管理、定投计划、分组管理、Cloud Sync、拖拽排序、明暗主题、CLI工具

**新增**: 股票/期货行情组件、AI分析面板、策略回测界面、统合持仓视图

## 六、数据流（请求→响应完整链路）

```
用户请求: "分析我的基金组合风险"

Web App → API Gateway (REST /api/portfolio/risk)
  → AI Brain: 解析意图 "portfolio_risk_analysis"
    → AI Brain: 调用 tool_portfolio_risk(params)
      → Quant Engine: 获取持仓数据
        → Data Hub: cache_hit? Redis → 命中返回
        → Data Hub: cache_miss? Provider.fetch() → normalize → cache
      ← Quant Engine: 计算风险指标 (夏普/回撤/相关性矩阵)
    ← AI Brain: LLM解读 → 自然语言风险报告 + 优化建议
  ← API Gateway: { report: "...", metrics: {...}, suggestions: [...] }
← Web App: 渲染风险报告卡片 + ECharts可视化 + AI解读面板
```

## 七、渐进式实施路线

### Phase 1 (Q3 2026): Data Hub MVP

- [ ] 移植 efinance stock+fund getter 为 provider 模式
- [ ] 移植 FundCrawler 异步引擎 + 天天/晨星解析器
- [ ] 移植 go-stock 的 sina/tdx/tushare provider
- [ ] 实现 normalizer pipeline (东方财富schema → 统一schema)
- [ ] Redis缓存层 + 限流器
- [ ] gRPC server 骨架
- [ ] WebSocket实时推送通道

### Phase 2 (Q4 2026): Quant Engine + AI Foundation

- [ ] 移植 xalpha 回测引擎 + 所有信息模型
- [ ] BTE_V2 增强（benchmark/commission/slippage/ai_interpret）
- [ ] 信号引擎（技术面+基本面+情绪面）
- [ ] AI Brain 移植 go-stock agent 核心
- [ ] 新增基金分析 tool chain
- [ ] fund_data_hub gRPC client for Quant Engine
- [ ] backtest_results → AI interpret pipeline

### Phase 3 (Q1 2027): Unified Frontend + Desktop

- [ ] Web App 移植 R1 并新增股票/期货/策略模块
- [ ] Desktop (Wails) 统一UI
- [ ] Extension 升级
- [ ] MCP Server 全能力暴露
- [ ] 统合持仓视图（跨资产）

### Phase 4 (Q2 2027): Ecosystem

- [ ] 策略市场 (分享/订阅/排行榜)
- [ ] 信号订阅 + 多渠道告警
- [ ] 知识图谱（基金←经理←重仓股←行业←概念）
- [ ] 多Agent协作分析
- [ ] LLM策略生成器
