# FundOS 项目架构

> 个人基金持仓管理系统。目标：把用户从亏损带向盈利，输出可执行的操作思路。
> 人格：**总裁**（见 [persona.md](.codex/skills/fundos/persona.md)）。所有基金分析按「总裁批示」格式输出。

## 一、总览

FundOS = **总裁人格技能库**（决策框架）+ **数据脚本**（实时行情/诊断/新闻）+ **数据文件**（持仓/流水/复盘）。

```
D:\基金项目\
├── .codex\skills\fundos\      # 项目级技能库（仅本项目加载）
│   ├── SKILL.md               # 技能主入口（总裁人格 + 22 技能 + 工作流）
│   ├── persona.md             # 总裁人格定义（六条铁律 + 批示格式）
│   ├── QUICKSTART.md          # 5 分钟上手
│   ├── knowledge\             # 知识库
│   │   ├── INDEX.md           # 22 技能索引 + 关系图
│   │   ├── DIGEST.md          # 精华导读（含巴菲特 2025-26 附录）
│   │   ├── GLOSSARY.md        # 术语词典
│   │   ├── books\             # 三本书语料（巴菲特/大众幻想/回忆录）
│   │   ├── distilled\         # 22 个蒸馏技能（各含 SKILL.md + test-prompts.json）
│   │   ├── experience\        # 实战经验沉淀（lessons.md）
│   │   ├── _archive\          # 旧阶段蒸馏包（stage2_packs）
│   │   └── .archived\         # 改动前快照（20260821 吞噬前）
│   ├── references\            # 分析框架/数据源/API/合规/架构
│   │   └── investment-framework.md   # 2026-08-21 蒸馏（8维打分/股息/风险信号）
│   ├── scripts\               # 技能侧工具（报告/新闻/净值/调度）
│   ├── reports\               # 审计/吞噬报告（2026-08-21_ingestion.md）
│   └── agents\                # Agent 配置
├── _archive\                  # 冗余文件归档（非删除，可回溯）
│   ├── scripts\               # 被取代/用过时代码的脚本（旧控制台、live_*、weekend_news* 等）
│   ├── reports\               # 历史日报/方案报告（daily_check_*、financial_news_* 等）
│   └── data\                  # 过期数据文件（weekend_news.json、news_result.json）
├── fundos_console_v2.py       # 交互控制台（[1]行情 [2]诊断 [5]新闻 [7]扫描 [8]记录 [9]技能库）
├── fundos_core.py             # 持仓诊断（盈亏/占比/阈值）
├── market_scan.py             # 全市场 224 板块扫描（新浪源）
├── deep_news.py               # 深度利好利空情报
├── news_engine.py             # 日常情报日报
├── daily_check.py             # 每日盘后净值+触发线复核
├── daily_update.py            # 手动录入涨跌幅
├── trade_journal.py           # 操作记录/复盘（add/view/review）
├── *.json                     # 持仓/交易/复盘/净值数据
├── *.md                       # 每日检查/新闻/扫描/方案报告
└── AGENTS.md                  # 项目级 Agent 规范
```

## 二、技能库（knowledge/distilled — 22 技能）

| 来源 | 技能 |
|------|------|
| 《股票大作手回忆录》Livermore（7） | trend-following-minimum-resistance / right-side-entry-pyramid / stop-loss-admission / hold-winners / independent-judgment / price-action-first / emotion-discipline-system |
| 《巴菲特致股东信》Buffett（8） | intrinsic-value-ruler / margin-of-safety / mr-market-panic-buying / circle-of-competence / hold-three-conditions / position-size-framework / do-not-list / timely-correction |
| 《大众幻想》Mackay（5） | mania-cycle-map / narrative-news-check / mass-participation-top / herd-contagion-check / leverage-amplifier |
| 实战蒸馏（1） | sector-rotation-detector（主线轮动） |
| 人格技能（1，2026-08-21） | buffett-perspective（巴菲特视角） |

每个技能目录含：`SKILL.md`（frontmatter + 方法论 + 触发/边界/审计）+ `test-prompts.json`（触发测试）。

## 三、数据脚本职责

| 脚本 | 功能 | 数据源 |
|------|------|--------|
| fundos_core.py | 组合诊断（盈亏/占比/阈值/板块敞口） | 天天基金净值 + 新浪指数 |
| market_scan.py | 全市场 224 板块排名，识别主线 | 新浪板块/概念 |
| deep_news.py | 利好利空三层拆解 | 同花顺/见闻/东财 |
| daily_check.py | 盘后净值复核 + 止损/止盈/换A 触发线 | 天天基金 lsjz/f10 |
| trade_journal.py | 操作记录/复盘 | 本地 JSON |
| fundos_console_v2.py | 交互控制台（聚合以上） | — |

## 四、数据文件

| 文件 | 内容 |
|------|------|
| portfolio_snapshot.json | 最新持仓快照 |
| transactions.json | 买卖流水 |
| trade_journal.json | 操作/批示留痕（逐条复盘） |
| manual_updates.json | 手动涨跌幅（优先于指数映射） |
| news_cache.json / news_result.json | 新闻缓存/结果 |
| daily_check_YYYY-MM-DD.md | 每日盘后检查报告 |
| deep_news_report.md / market_sector_scan.md | 新闻 / 板块扫描报告 |

## 五、强制工作流（每次分析必走）

```
1. market_scan.py   → 全市场主线（先看全局，避免持仓锚定）
2. fundos_core.py   → 组合诊断（盈亏/占比/阈值）
3. deep_news.py     → 利好利空三层拆解（如涉新闻）
4. 总裁批示输出     → 形势/体检/指令/风控/免责
5. trade_journal.py → 留痕复盘
```

## 六、数据源矩阵

| 数据 | 来源 | 状态 |
|------|------|------|
| 基金净值 | api.fund.eastmoney.com/f10/lsjz | ✅ 稳定 |
| A股/全球指数 | hq.sinajs.cn | ✅ 稳定 |
| 行业/概念板块 | vip.stock.finance.sina.com.cn | ✅ 稳定 |
| 新闻快讯 | 同花顺/华尔街见闻/新浪 | ✅ 稳定 |
| 东财搜索 | search-api-web.eastmoney.com | ⚠️ 限流 |
| 东财 push2 | push2.eastmoney.com | ❌ 避免使用 |

## 七、近期变更（2026-08-21）

- 吞噬融合三包：`buffett-perspective`（并入基金项目）、`stock-analysis-6-2-0`（蒸馏方法论 → references/investment-framework.md）、`stock-watcher`（不吸收）。
- 技能数 21 → 22；规范化 `sector-rotation-detector` 为目录结构。
- 归档孤儿脚本 `fix_ch4v2.py` / `style_rule.py` → `C:\Users\lzf13\.codex\skills\_archive\`。
- 修复控制台技能库菜单的过期索引路径与计数。
- 清理冗余：归档旧版 `fundos_console.py`、5 个 `live_*`/`today_nav`/`sector_live`（用过时错误代码）、3 个 `weekend_news*.py`、2 个一次性 `save_*` 脚本、16 份历史报告到 `_archive\`。
- 完整留痕：[reports/2026-08-21_ingestion.md](.codex/skills/fundos/reports/2026-08-21_ingestion.md)。
