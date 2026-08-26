# 六大源仓库解剖分析

> 每个源仓库的角色、核心能力、可继承资产、改造策略。

## R1: hzm0321/real-time-fund (基估宝)

```
Stars: 1,614 | Forks: 495 | Lang: JavaScript | 319 files
形态: Next.js Web App + CLI工具
部署: GitHub Pages / Vercel
```

**核心资产** (可直接继承):
- 玻璃拟态 UI 组件体系 (components/ui/ — 基于 shadcn/ui + Radix)
- 持仓管理 + 定投计划引擎 (Zustand stores)
- Supabase 云端同步方案 (冲突处理逻辑完整)
- JSONP 跨域数据方案 (天天基金/腾讯财经直连)
- 前端基金数据处理 lib/utils.js
- CLI 工具 @jigubao/cli (终端+脚本友好)

**改造策略**: 作为 FundOS 的 Web 前端基准，保留UI体系，替换底层数据获取为 API Gateway 调用，新增股票/期货/策略模块。

**侵入度**: 低 (仅修改数据获取层)

---

## R2: refraction-ray/xalpha

```
Stars: 2,655 | Forks: 481 | Lang: Python | 98 files
形态: Python 库 (pip installable)
版本: 0.12.4
```

**核心资产** (可直接继承):
- BTE 动态回测框架 (backtest.py — 完整的事件驱动回测引擎)
- 信息模型体系 (fundinfo / mfundinfo / cashinfo / vinfo — OOP数据抽象)
- 交易模拟 (trade.py / itrade.py)
- 多基金组合 (multiple.py — mul/mulfix 定投/不定额)
- 指标体系 (indicator.py — 夏普/回撤/波动率/信息比率/Alpha/Beta)
- 工具箱 (toolbox.py — IRR/XIRR/费率计算)
- 估值表 (remain.py — 持仓穿透分析)
- 多数据源桥接 (provider.py — 聚宽等第三方)

**改造策略**: 作为 Quant Engine 的内核，保持API兼容，增加 BTE_V2 (benchmark/slippage/commission/ai_interpret)，新增信号引擎层。

**侵入度**: 低 (扩展而非修改核心)

---

## R3: Jerry1014/FundCrawler

```
Stars: 583 | Forks: 162 | Lang: Python | ~30 files
形态: CLI 爬虫工具
架构: 异步引擎 + 策略模式解析器
```

**核心资产** (可直接继承):
- 异步爬虫引擎 (engine.py — asyncio + aiohttp Session复用 + 并发控制)
- Step 策略模式 (page_parser/ — BASIC→STANDARD→FULL三级粒度)
- 天天基金解析器 (tiantian.py — HTML解析 + 字段提取)
- 晨星解析器 (morningstar.py — 评级+风险+业绩)
- FundContext 基金上下文模型
- 进度条+终端交互 (tqdm 闪烁指示器)
- 结果写入器 (CSV输出)

**改造策略**: 引擎核心移植到 Data Hub engine/，解析器移植为 Provider 实现。

**侵入度**: 中 (接口适配为 BaseProvider 模式)

---

## R4: x2rr/funds

```
Stars: 3,194 | Forks: 407 | Lang: Vue | 95 files
形态: Chrome 浏览器扩展
架构: Vue 2 + ECharts + Webpack
```

**核心资产** (可直接继承):
- Chrome Extension 完整工程 (manifest/popup/background)
- ECharts 基金走势可视化
- 基金卡片式 UI 组件
- 天天基金 API 对接 (JSONP)
- 自选基金本地管理 (chrome.storage)
- 节假日数据 (holiday.json)

**改造策略**: 升级到 Vue 3 + Manifest V3，数据源改为 API Gateway，作为 FundOS 轻量入口。

**侵入度**: 低 (数据层替换)

---

## R5: Micro-sheep/efinance

```
Stars: 3,908 | Forks: 739 | Lang: Python | 46 files
形态: Python 库 (pip installable)
版本: 0.5.9
```

**核心资产** (可直接继承):
- 多资产统一接口 (stock/fund/bond/futures 四大模块)
- 东方财富完整数据覆盖 (实时/历史/深度/龙虎榜/资金流)
- 并发引擎 (multitasking + ThreadPoolExecutor + 信号处理)
- 重试机制 (@retry(tries=3))
- 数据清洗 (to_numeric/to_type)
- 公共模块复用 (common/ — get_base_info/get_quote_history 跨资产共享)
- Rich 终端美化输出

**改造策略**: 作为 Data Hub 的主力 Provider，所有 getter 函数改为 Provider 接口模式，归一化到统一 schema，增加 gRPC 服务层。

**侵入度**: 中 (接口改造 + 新增gRPC层)

---

## R6: ArvinLovegood/go-stock

```
Stars: 7,069 | Forks: 1,244 | Lang: Go | 136 files
形态: Desktop App (Wails + NaiveUI)
架构: Go后端 + Vue3前端 + SQLite
```

**核心资产** (可直接继承):
- AI Agent 系统 (agent/ — 意图识别/工具编排/对话记忆/多模型工厂/飞书机器人)
- 100+ 数据工具 API (backend/data/ — 多数据源矩阵)
- 多数据源适配 (东方财富/新浪/通达信/i问财/雪球/Tushare/财联社/华尔街见闻)
- 桌面应用框架 (Wails v2 — Go+Vue 跨平台)
- MCP Server (mcp_server_api.go — AI Agent标准协议)
- 定时任务 (cron)
- 多渠道告警 (钉钉/飞书/Windows通知/macOS通知)
- Markdown→图片 (可视化报告)
- 筹码分布分析
- AI情绪分析 + K线技术解读

**改造策略**: 提取 agent/ + tools/ 为独立 AI Brain 服务，数据获取层迁移到 Data Hub（Go→Python重写），桌面框架保留并接入 API Gateway。

**侵入度**: 高 (大规模模块提取和重写)

---

## 改造侵入度与风险矩阵

| 源仓库 | 侵入度 | 风险 | 改造优先级 |
|--------|:------:|:----:|:----------:|
| real-time-fund (R1) | 低 | 低 | Phase 3 |
| xalpha (R2) | 低 | 低 | Phase 2 |
| FundCrawler (R3) | 中 | 低 | Phase 1 |
| funds (R4) | 低 | 低 | Phase 3 |
| efinance (R5) | 中 | 中 | Phase 1 |
| go-stock (R6) | 高 | 高 | Phase 1 (数据) + Phase 2 (AI) |

**风险缓解策略**: 
- 高侵入度仓库(R6)采用 fork-and-adapt 模式，保留原始仓库独立维护
- 所有改造以 adapter/wrapper 方式实现，不破坏源仓库 API 兼容性
- 渐进式: 先 Data Hub(价值最大)，再 Quant+AI，最后前端统一
