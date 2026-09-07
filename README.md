# FundOS · 基金项目

> 个人基金持仓管理系统。目标：把用户从亏损带向盈利，输出可执行的操作思路（不承诺收益）。
> **接手/留档**：先读 [PROJECT_HANDOVER.md](PROJECT_HANDOVER.md)（总档案）与 [CHANGELOG.md](CHANGELOG.md)（更新日志）。

## 核心人格
所有基金分析以 **总裁** 人格输出（先结论后依据、决策框架 + 执行动作 + 风控边界）。人格定义：`.codex/skills/fundos/persona.md`。

## 技能库（仅本项目）
`.codex/skills/fundos/` —— 22 个蒸馏技能（Livermore/Buffett/Mackay/主线轮动/巴菲特视角）。入口 `SKILL.md`，索引 `knowledge/INDEX.md`。

## 每日/每次分析工作流
```
1. market_scan.py   → 全市场主线
2. fundos_core.py   → 组合诊断
3. deep_news.py     → 利好利空三层拆解（如涉新闻）
4. 总裁批示输出      → 形势/体检/指令/风控/免责
5. trade_journal.py → 留痕复盘
```
> 日常自动化（已装计划任务）: `python auto_pipeline.py status` 查看
> 工作日 09:00 晨报 / 15:30 触发警报 / 20:30 晚报（全引擎），弹窗通知；
> 设置环境变量 FUNDOS_SCT_KEY 可加推微信。
> 电脑不常开也没关系：任务带"错过补跑+睡眠唤醒"，登录时 FundOS-Catchup 自动补跑当天遗漏。

## 脚本地图
| 脚本 | 功能 |
|------|------|
| fundos_config.py | 统一配置层（持仓/成本/阈值 单一事实来源） |
| fundos_data.py | 统一数据层（重试/多源回退/净值历史沉淀） |
| fundos_analytics.py | 组合风险分析（回撤/夏普/波动率/风险贡献） |
| fund_engine.py | 总编排引擎（`run --offline` 离线重建批示） |
| fundos_core.py | 持仓诊断（含 QDII 美股代理估值） |
| market_scan.py | 全市场 224 板块扫描 + 主线连续性 |
| deep_news.py / news_fetch_v2.py | 利好利空情报 / 六维新闻 |
| daily_check.py | 盘后净值 + 触发线复核（9只） |
| volatility_aug.py | 单基金波动/回撤预估 |
| daily_update.py | 手动录入涨跌幅 |
| trade_journal.py | 操作记录/复盘 |
| fundos_console_v2.py | 交互控制台（[10] 可一键启动可视化面板） |
| dashboard.py | 可视化面板：http://127.0.0.1:8899（含今日操作指南/AI总裁研判，红涨绿跌） |
| fundos_advisor.py | 操作指南规则引擎（触发线/集中度/禁止清单，dashboard 与批示共用） |
| fundos_llm.py | 大模型接入（环境变量 FUNDOS_LLM_API_KEY 启用，未配置自动降级） |
| tests/test_fundos.py | 单元测试（python tests/test_fundos.py） |

## 数据文件
`portfolio_snapshot.json`、`transactions.json`、`trade_journal.json`、`manual_updates.json`、`news_cache.json`、`holdings.xlsx`，以及 `daily_check_YYYY-MM-DD.md` 等日报。

## 红线
- 输出不承诺收益、不给「必涨/必跌」，结尾带免责声明。
- 本技能库只服务本基金项目，与小说/代码等其他领域任务隔离。
- 详细规范见 `AGENTS.md` 与 `ARCHITECTURE.md`。
