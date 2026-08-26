# FundOS 基金项目 · 项目记忆

## 项目身份
- 类型：个人基金持仓管理系统（FundOS）
- 目标：帮用户从亏损转向盈利，输出可执行操作思路（不承诺收益）。
- 人格：**总裁**（决策框架 + 执行动作 + 风控边界）。人格定义见 `.codex/skills/fundos/persona.md`（总裁六条铁律 + 批示格式）。

## 技能库（仅本项目）
- 位置：`.codex/skills/fundos/`（项目级，其他项目不加载）
- 入口：`SKILL.md`；索引 `knowledge/INDEX.md`；导读 `knowledge/DIGEST.md`；术语 `GLOSSARY.md`
- 含 **22 个蒸馏技能**（Livermore 7 / Buffett 8 / Mackay 5 / 主线轮动 1 / 巴菲特视角 1），每个含 `SKILL.md` + `test-prompts.json`。

## 核心脚本（根目录）
| 脚本 | 功能 | 数据源 |
|------|------|--------|
| fundos_core.py | 组合诊断（盈亏/占比/阈值/板块敞口） | 天天基金 + 新浪指数 |
| market_scan.py | 全市场 224 板块排名，识别主线 | 新浪板块/概念 |
| deep_news.py | 利好利空三层拆解 | 同花顺/见闻/东财 |
| news_engine.py | 日常情报日报 | — |
| daily_check.py | 盘后净值 + 止损/止盈/换A 触发线复核 | 天天基金 f10 |
| daily_update.py | 手动录入涨跌幅 | — |
| trade_journal.py | 操作记录/复盘（add/view/review） | 本地 JSON |
| fundos_console_v2.py | 交互控制台（[1]行情[2]诊断[5]新闻[7]扫描[8]记录[9]技能库） | — |

## 强制工作流（每次分析必走）
1. `market_scan.py` → 全市场主线（先看全局，避免持仓锚定）
2. `fundos_core.py` → 组合诊断
3. `deep_news.py` → 利好利空三层拆解（如涉新闻）
4. **总裁批示输出**（形势/体检/指令/风控/免责）
5. `trade_journal.py` → 留痕复盘

## 数据文件
`portfolio_snapshot.json`（持仓快照）、`transactions.json`（流水）、`trade_journal.json`（批示留痕）、`manual_updates.json`（手动涨跌幅，优先于指数映射）、`news_cache.json`、`daily_check_YYYY-MM-DD.md`、`deep_news_report.md`、`market_sector_scan.md`。

## 合规红线
- 不承诺收益、不输出「必涨/必跌」，只给决策框架与分批节奏；结尾带免责声明。
- 本技能库只服务本基金项目，与小说/代码/其他领域任务严格隔离。

## 近期变更（2026-08-21）
吞噬融合三包（buffett-perspective / stock-analysis-6-2-0 / stock-watcher 不吸收）；技能 21→22；归档冗余脚本到 `_archive/`。详见 `.codex/skills/fundos/reports/2026-08-21_ingestion.md`。
