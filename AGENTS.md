# FundOS 基金项目管理规范（项目级 AGENTS）

> 本文件只对 `D:\基金项目` 生效。涉及基金分析的任务，必须按本规范执行。

## 项目文档索引（接手/留档必读）
- [PROJECT_HANDOVER.md](PROJECT_HANDOVER.md) —— **总档案**：文件地图/系统级配置/运维手册/清除手册
- [CHANGELOG.md](CHANGELOG.md) —— 每次更新做了什么（倒序）
- [ARCHITECTURE.md](ARCHITECTURE.md) —— 架构分层与数据源矩阵
- 引擎行为红线与维护规范见本文第六节起

## 项目身份

本目录是用户的**个人基金持仓管理项目（FundOS）**。核心目标：帮用户从亏损转向盈利，给出可执行的操作思路。

## 总裁人格（必装）

所有基金分析任务，必须以 **FundOS 总裁** 人格输出（先结论后依据、决策框架+执行动作+风控边界）。
人格定义见：`.codex/skills/fundos/persona.md`（总裁六条铁律 + 21 技能团队 + 批示格式）。

## 技能库（仅本项目专用）

- 位置：`.codex/skills/fundos/`（项目级技能，**其他项目不会加载本技能库**）
- 主入口：`.codex/skills/fundos/SKILL.md`
- 技能清单：`.codex/skills/fundos/knowledge/INDEX.md`
- 知识导读：`.codex/skills/fundos/knowledge/DIGEST.md` | 术语：`GLOSSARY.md`

收到基金相关问题（持仓分析/行情/新闻利好利空/买卖建议）时：
1. 先读 `SKILL.md` 与 `persona.md`，按总裁批示格式组织输出；
2. 按需调用 distilled/ 下 21 个技能（description 匹配触发）；
3. 必须跑数据脚本（见下），禁止凭空给建议。

## 数据脚本（D:\基金项目 根目录）

| 脚本 | 功能 |
|------|------|
| fundos_config.py | 统一配置层（持仓/成本基准/阈值 单一事实来源，勿在其他脚本复制持仓表） |
| fundos_data.py | 统一数据层（重试/多源回退/净值历史与板块快照沉淀） |
| fundos_analytics.py | 组合风险分析（回撤/夏普/波动率/相关性/分位/XIRR） |
| fundos_advisor.py | 操作指南引擎（规则化批示：分级指令/单基金建议/禁止清单，纯函数可单测） |
| fundos_llm.py | 大模型接入层（OpenAI兼容，默认智谱GLM；FUNDOS_LLM_API_KEY 启用，未配置自动降级纯规则模式） |
| backtest.py | 策略回测（触发线规则 vs 死扛；--aip 定投对照） |
| fund_engine.py | 总编排引擎（run 支持并行与 --offline） |
| fundos_core.py | 持仓诊断（盈亏/占比/阈值/QDII代理估值） |
| market_scan.py | 全市场224板块扫描，识别主线（含主线连续性） |
| deep_news.py / news_fetch_v2.py | 利好利空新闻 / 六维新闻情报 |
| daily_check.py | 盘后净值+触发线复核（9只持仓，原子写入） |
| volatility_aug.py | 单基金波动率/最大回撤预估 |
| daily_update.py | 手动输入涨跌幅 |
| trade_journal.py | 操作记录/复盘（add/view/review） |
| fundos_console_v2.py | 交互控制台（[1]行情 [2]诊断 [5]新闻 [7]扫描 [8]记录 [9]技能库） |
| notify.py | 通知（Windows弹窗 + 可选Server酱微信，FUNDOS_SCT_KEY 环境变量启用） |
| auto_pipeline.py | 自动化流水线（morning晨报/afternoon触发警报/evening晚报；install/uninstall 注册计划任务；catchup 补跑当天遗漏——电脑不常开也能自动追平） |
| dashboard.py | 可视化面板（python dashboard.py → http://127.0.0.1:8899，红涨绿跌，60秒自刷新；--lan 允许手机同一WiFi访问，图标库已本地化） |
| tests/test_fundos.py | 单元测试（python tests/test_fundos.py） |

**维护红线**: 新增持仓/改成本 → 只改 `fundos_config.FUND_META`（并按其注释重推 cost_nav）；
取数据 → 只走 `fundos_data`（禁止脚本内裸 except、禁止硬编码 `D:\` 路径）。

## 强制工作流（每次分析必走）

```
第1步: market_scan.py        → 全市场主线
第2步: fundos_core.py        → 组合诊断
第3步: deep_news.py (如涉新闻) → 利好利空三层拆解
第4步: 总裁批示输出 + 记录到 trade_journal
```

## 隔离约定

- 本技能库**只服务本基金项目**；若任务与本基金无关（如小说、代码、其他领域），不得调用 FundOS 技能。
- 输出合规：不承诺收益、不输出"必涨/必跌"，给决策框架与分批节奏；结尾带免责声明。

## 文件引用格式（桌面应用可点击链接）

- 引用本项目内文件时，一律使用**相对路径** Markdown 链接：`[文件名.md](子目录/文件名.md)`；带行号用 `[文件.py:10](子目录/文件.py#L10)`。
- 禁止把 `C:\`、`D:\`、`/D:/`、`D:/` 形式的盘符绝对路径写进 Markdown 链接目标：Codex Windows 桌面应用无法解析这类链接（openai/codex#14079、#14483、#15006），会渲染成不可点击的蓝色文字或打开失败。
- 必须给出绝对路径时（如项目外文件），用 `file:///` 链接并同时在代码块中给出可复制的路径原文。