# FundOS 项目总档案（交接文档 / PROJECT_HANDOVER）

> 目的：任何 Agent（或未来的你）接手本项目时，从这一份文档出发即可了解全貌、找到任何东西、安全地运维或彻底清除。
> 最后更新：2026-08-30。配套文档：[CHANGELOG.md](CHANGELOG.md)（每次更新做了什么）、[AGENTS.md](AGENTS.md)（Agent 行为规范）、[ARCHITECTURE.md](ARCHITECTURE.md)（架构与数据源矩阵）。

---

## 一、这个项目是什么

**FundOS**：个人基金持仓管理系统（仅服务 `D:\基金项目`，不外传）。核心目标：帮持有人从亏损转向盈利，输出可执行的操作思路（决策框架+分批节奏+风控边界），**不承诺收益、不给必涨必跌**。

三大组成部分：
1. **技能库**（`.codex/skills/fundos/`）：总裁人格 + 22 个蒸馏技能（Livermore/Buffett/Mackay），Agent 分析时按 description 触发；
2. **引擎**（根目录 Python 脚本）：配置层→数据层→分析层→指南引擎→LLM 层→编排层→可视化面板；
3. **自动化**：工作日 09:00 晨报 / 15:30 触发警报 / 20:30 晚报（弹窗+可选微信），看板登录常驻，错过的时点开机补跑。

当前持仓 9 只基金（科技/AI 6 只 + QDII 3 只 + 绿电 1 只口径分类，A/C 分开计），权威数据源是 `portfolio_snapshot.json`（用户手工确认更新）。

---

## 二、文件地图（什么东西保存在哪）

### 2.1 根目录代码（引擎，全部可重建，删除前先看依赖）

| 文件 | 职责 | 备注 |
|---|---|---|
| `fundos_config.py` | **唯一事实来源**：9 只持仓元数据、成本净值(cost_nav)、阈值、路径、板块映射 | 新增持仓/改成本只改这里，并按文件内注释重推 cost_nav |
| `fundos_data.py` | 数据层：重试退避/多源回退(lsjz→pingzhongdata→akshare)/HTTP缓存/净值与板块归档/汇率 | 所有取数必走这里，禁止裸 except |
| `fundos_core.py` | 持仓诊断（盈亏/占比/阈值/QDII美股代理+汇率估值） | 每日分析第2步 |
| `fundos_analytics.py` | 组合风险分析：回撤/夏普/波动/相关性/风险贡献/HHI/净值分位/XIRR | 输出 fund_analytics_* |
| `fundos_advisor.py` | **操作指南规则引擎**（环境/分级指令/单基金建议/禁止清单） | 纯函数可单测；dashboard 与 AI 共用 |
| `fundos_llm.py` | 大模型接入（OpenAI兼容，默认智谱GLM）；配置优先级 env > data/llm/config.json | 未配置自动降级纯规则 |
| `setup_llm.py` | 免费大模型一键接入向导（智谱/硅基流动/魔搭预设+连通性验证） | `python setup_llm.py --status` 查看 |
| `backtest.py` | 策略回测：触发线规则 vs 死扛；--aip 定投对照 | 输出 fund_backtest_* |
| `market_scan.py` | 全市场224板块扫描+主线连续性+轮动打分 | 输出 market_sector_scan.md |
| `daily_check.py` | 盘后净值+止损/止盈/换A触发线复核（9只，原子写入） | 触发线规则的定义处 |
| `volatility_aug.py` | 单基金波动率/最大回撤预估 | |
| `fund_engine.py` | 总编排（Phase1并行扫描/盘后/新闻→Phase2诊断→Phase3分析）；`run --offline` | 输出 fund_engine_report.md + 总裁批示 |
| `deep_news.py` / `news_engine.py` | 旧新闻引擎（利好利空三层拆解/情报日报） | 仍可用；六维主力在 news_fetch_v2 |
| `news_fetch_v2.py` | **六维新闻引擎 v2.1**（在 `.codex/skills/fundos/scripts/`）：已验证四源+当日归档+情绪分类+直连快讯 | 含 classify_sentiment_v2 / compute_sentiment_index / archive_news / day_summary |
| `portfolio_data.py` | 快照加载器（daily_check_result 优先，回退快照） | |
| `trade_journal.py` | 操作留痕/复盘（add/view/review） | 数据 trade_journal.json |
| `daily_update.py` | 手动输入当日涨跌幅 | 数据 manual_updates.json |
| `auto_pipeline.py` | 三时点流水线 + install/uninstall/status/catchup | 系统级注册见第四节 |
| `notify.py` | Windows toast（可点击打开看板）+ Server酱微信 + 日志 | |
| `dashboard.py` + `dashboard.html` | 可视化面板（本地 HTTP 服务 :8899，报纸风模板与代码分离） | 模板改 dashboard.html 即可，无需改 py |
| `fundos_console_v2.py` | 交互控制台（[10] 可启动面板） | |
| `tests/test_fundos.py` | 42 项单元测试 | `python tests/test_fundos.py` |
| `_archive/` `_备份_*` | 历史归档（可整体忽略） | |

### 2.2 data/ 目录（运行数据，除 config.json 含密钥外均可重建或丢弃）

| 路径 | 内容 | 可否删除 |
|---|---|---|
| `data/nav_history/*.json` | 9 只基金净值历史沉淀（全量，分析/回测的底座） | ⚠️ 可重建但会重新拉取，建议保留 |
| `data/board_history/*.json` | 每日板块快照（主线连续性/轮动打分依赖，**过去的日子无法重抓**） | ⚠️ 建议保留 |
| `data/news_history/news_YYYY-MM-DD.json` | 当日快讯归档（去重，上限800条/天） | 可删（历史新闻） |
| `data/sentiment_history/*.json` | 日度情绪指数序列 | 可删 |
| `data/state/auto_state.json` | 流水线执行状态（catchup 防重复依赖） | 可删（会重跑当天时点） |
| `data/cache/*.json` | HTTP 短期缓存（TTL 自动过期） | ✅ 随便删，自动重建 |
| `data/logs/*.log` | 运行日志（auto_YYYY-MM-DD.log / dashboard_stdout.log） | 可删 |
| `data/static/echarts.min.js` | 本地图标库（1MB） | 删了会回退 CDN |
| `data/llm/config.json` | **⚠️ 敏感：大模型 API 密钥（智谱）** | 删除前先去平台吊销密钥 |
| `data/llm/last_brief.json` | AI 研判缓存（含指纹） | 可删（按钮重新生成） |

### 2.3 根目录数据/报告文件（用户资产 + 生成物）

| 文件 | 性质 |
|---|---|
| `portfolio_snapshot.json` | **权威持仓**（用户手工确认；2026-08-26 版）。更新它之后必须按 fundos_config 注释重推 cost_nav |
| `transactions.json` | 交易流水（2026-08-08 重建版，XIRR 用；未含其后的转A/赎回调账） |
| `trade_journal.json` | 操作留痕 38+ 条（复盘资产） |
| `manual_updates.json` | 手动录入涨跌幅（7-31 一批） |
| `daily_check_result.json` | 盘后检查结果（诊断/分析的数据入口，原子写入） |
| `news_result.json` / `news_cache.json` | 六维新闻引擎输出/旧缓存 |
| `daily_check_*.md`、`fundos_morning_*.md`、`fundos_evening_*.md` | 每日报告（可删，纯生成物） |
| `fund_analytics_report.md/.json`、`fund_backtest_report.md/.json`、`fund_engine_report.md/.json`、`fund_engine_runs.jsonl`、`fund_engine_audit.md`、`fundos_presidential_brief.md`、`market_sector_scan.md`、`deep_news_report.md`、`fund_news_report.md`、`daily_briefing.md` | 各引擎生成物（可删可重生） |
| `holdings.xlsx` | 支付宝导出的原始持仓 Excel |
| `bugfix_run.log`、`phase3/4_run.log`、`latest_run.log`、`备份差异报告_*.md`、`项目文件盘点.md`、`总裁批示_2026-08-22.md`、`PROJECT_ORIGIN.md` | 历史遗留（可归档） |

### 2.4 技能库（`.codex/skills/fundos/`）

`SKILL.md`（入口）/ `persona.md`（总裁人格六铁律+批示格式）/ `knowledge/`（INDEX+DIGEST+GLOSSARY+22技能蒸馏+books语料）/ `references/`（API契约/数据源注册表/合规）/ `scripts/`（aip_calc、portfolio_report、scheduler 等）/ `reports/`（吞噬留痕）。
**只服务本项目**；其中的 `scripts/news_fetch_v2.py` 是六维新闻引擎本体。

---

## 三、数据流（一分钟看懂引擎怎么转）

```
盘后 15:30: daily_check.py ──触发线──▶ daily_check_result.json（原子写）
全天:      dashboard.py ◀── fundos_data(缓存/归档) ◀── 东财lsjz/新浪/见闻/同花顺
           dashboard → news_fetch_v2 直连快讯 → data/news_history/ 当日归档
20:30:     fund_engine.py run → 并行(扫描/盘后/新闻) → 诊断 → 分析 → fundos_advisor 规则指南
           → fundos_llm(LLM叙事,可选) → 晚报+弹窗/微信
分析:      fundos_analytics / backtest 读 data/nav_history/ 沉淀
人工:      portfolio_snapshot.json（用户确认更新）→ 重推 fundos_config cost_nav
```

---

## 四、系统级配置（删项目必须清理的东西）

| 项 | 位置 | 清理方法 |
|---|---|---|
| 计划任务 ×3 | `FundOS-Morning`(工作日09:00) / `FundOS-Afternoon`(15:30) / `FundOS-Evening`(20:30)，PowerShell 注册，带 StartWhenAvailable+WakeToRun | `schtasks /Delete /TN FundOS-Morning /F`（另两个同理）或 `python auto_pipeline.py uninstall` |
| 登录自启动 ×2 | HKCU\Software\Microsoft\Windows\CurrentVersion\Run 下 `FundOS-Catchup`（补跑）、`FundOS-Dashboard`（pythonw 常驻看板） | `reg delete` 对应键，或 uninstall |
| 桌面快捷方式 | `Desktop\FundOS看板.url` | 直接删除 |
| 看板服务 | pythonw 常驻进程（127.0.0.1:8899） | `taskkill` 对应 PID 或重启后不启动 |

**一键清理前两项**：`python auto_pipeline.py uninstall`。

---

## 五、外部账户与凭证

| 服务 | 用途 | 凭证位置 | 状态 |
|---|---|---|---|
| 智谱 BigModel (open.bigmodel.cn) | AI 总裁研判（glm-4-flash-250414，永久免费档） | `data/llm/config.json` 的 api_key 字段 | ✅ 已配置（2026-08-30 验证连通） |
| Server酱 (sct.ftqq.com) | 微信推送（晚报/警报） | 环境变量 `FUNDOS_SCT_KEY` | ⬜ 未配置（不配置只用弹窗） |
| 新浪/东财/同花顺/见闻 | 行情与新闻数据源 | 无需凭证 | ✅ 免费公开接口 |

⚠️ **安全提醒**：智谱密钥曾出现在对话记录中，接管后建议去 open.bigmodel.cn 用户中心轮换，并重跑 `python setup_llm.py --provider bigmodel --key 新密钥`。

---

## 六、运维手册（常用命令）

```
python auto_pipeline.py status     # 全家桶状态：任务注册/看板在线/执行记录
python auto_pipeline.py catchup    # 补跑当天遗漏
python dashboard.py                # 启动看板（自动开浏览器）；--lan 手机访问
python fund_engine.py run          # 手动全链路；--offline 离线重建批示
python daily_check.py              # 盘后触发线复核
python fundos_core.py              # 持仓诊断
python fundos_analytics.py         # 风险分析（回撤/夏普/XIRR）
python backtest.py --aip 200       # 策略回测
python setup_llm.py --test         # 测 LLM 连通
python tests/test_fundos.py        # 42 项单元测试
python trade_journal.py add        # 操作留痕
```

---

## 七、设计决策与红线（改代码前必读）

1. **单一事实来源**：持仓/成本/阈值只改 `fundos_config.py`；改 `portfolio_snapshot.json` 后必须按 config 注释公式重推 cost_nav（ret = value/cost - 1；cost_nav = nav(锚定日)/(1+ret)；锚定日=快照确认时点最近已公布净值日）。
2. **取数只走 `fundos_data`**：禁止裸 except、禁止硬编码盘符路径、禁止在业务脚本复制持仓表。
3. **新闻情绪只进观察层**：任何指令不得仅因新闻触发（price-action-first 硬编码在 fundos_advisor）。
4. **东财搜索必须 urllib 直连**：requests 会规范化 URL 编码导致返回错误维度（news_fetch_v2 有注释）。
5. **净值缓存是全量落盘、读取时按 days 过滤**（曾因写回截断值出过 bug，见 CHANGELOG）。
6. **LLM 不得推翻规则引擎边界**（fundos_llm SYSTEM_PROMPT 硬约束）；未配置密钥时全链路可用。
7. 合规：输出不承诺收益、结尾带免责声明；本库只服务本项目。

---

## 八、已知问题 / 待办

- `transactions.json` 未含 2026-08-08 之后的转A/赎回调账 → 单基金 XIRR 有离群值（组合级可信），补全流水即自愈。
- 情绪指数在 55 阈值附近波动时，AI 研判会标记 stale 提示重生成（设计行为，非 bug）。
- 新浪板块命名会变，`fundos_config.WATCH_BOARDS` 已改关键词包含匹配，仍可能个别板块失配。
- `news_engine.py`/`deep_news.py` 与 news_fetch_v2 功能部分重叠，为保持 AGENTS 工作流兼容暂保留。
- git 仓库仅 2 个历史提交；2026-08-28 起的大版本改动**未提交**（54 个变更/新增文件），接手后建议尽快做一次提交留档。

---

## 九、彻底清除项目手册（按顺序执行）

```bat
:: 1) 注销计划任务与自启动（或 python auto_pipeline.py uninstall）
schtasks /Delete /TN FundOS-Morning /F
schtasks /Delete /TN FundOS-Afternoon /F
schtasks /Delete /TN FundOS-Evening /F
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v FundOS-Catchup /f
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v FundOS-Dashboard /f

:: 2) 杀掉常驻看板进程
taskkill /F /IM pythonw.exe        :: （确认无其他 pythonw 再执行）

:: 3) 删桌面快捷方式
del "%USERPROFILE%\Desktop\FundOS看板.url"

:: 4) 【先做】吊销智谱密钥：open.bigmodel.cn 用户中心 → 删除该 API Key
::    （密钥明文在 data\llm\config.json）

:: 5) 删除项目目录（若需保留资产，先备份以下三件：
::    portfolio_snapshot.json / trade_journal.json / transactions.json，
::    以及 data\nav_history\（重装后免重新拉取））
rmdir /s /q D:\基金项目
```

**给接手 Agent 的话**：本项目行为规范以 `AGENTS.md` 为准（涉及基金分析必须总裁人格输出+免责声明）；改任何引擎代码前先读第七节红线；改完跑 `python tests/test_fundos.py`（42 项全过为底线）；每日自动化的三个时点与补跑逻辑见第四节，不要重复注册。
