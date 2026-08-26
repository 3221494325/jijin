# FundOS · 基金项目

> 个人基金持仓管理系统。目标：把用户从亏损带向盈利，输出可执行的操作思路（不承诺收益）。

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

## 脚本地图
| 脚本 | 功能 |
|------|------|
| fundos_core.py | 持仓诊断 |
| market_scan.py | 全市场 224 板块扫描 |
| deep_news.py / news_engine.py | 利好利空情报 |
| daily_check.py | 盘后净值 + 触发线复核 |
| daily_update.py | 手动录入涨跌幅 |
| trade_journal.py | 操作记录/复盘 |
| fundos_console_v2.py | 交互控制台 |

## 数据文件
`portfolio_snapshot.json`、`transactions.json`、`trade_journal.json`、`manual_updates.json`、`news_cache.json`、`holdings.xlsx`，以及 `daily_check_YYYY-MM-DD.md` 等日报。

## 红线
- 输出不承诺收益、不给「必涨/必跌」，结尾带免责声明。
- 本技能库只服务本基金项目，与小说/代码等其他领域任务隔离。
- 详细规范见 `AGENTS.md` 与 `ARCHITECTURE.md`。
