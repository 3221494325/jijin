# Task A — 构造 4 个 FundOS 蒸馏技能

源书: 《股票大作手回忆录》(Reminiscences of a Stock Operator)
注意：r03 与 r04 是姊妹纪律（截断亏损/让利润奔跑），互相 contrasts-with；r02 依赖 r03 的止损前提。

## 你的技能清单（slug → 方法论单元）

- **trend-following-minimum-resistance** ← r01 趋势跟随：最小阻力线与关键点（趋势跟随）
- **right-side-entry-pyramid** ← r02 右侧建仓：试探仓+金字塔加仓，绝不摊平（右侧建仓）
- **stop-loss-admission** ← r03 止损即认错（亏损不是错误，不认错才是）（止损纪律）
- **hold-winners** ← r04 拿住盈利（看对+拿住才赚大钱）（持有盈利）

## 工作步骤
1. 先读 C:\Users\lzf13\.codex\skills\fundos\knowledge\stage2_packs\COMMON.md（共享要求，必读）
2. 读 C:\Users\lzf13\.codex\skills\fundos\knowledge\stage2_packs\fundos_context.md（FundOS 语境）
3. 读你负责的书的 verified.md（单元定义）与 candidates\ 目录（引文来源，禁止编造引文）
4. 为每个技能创建目录并写 SKILL.md + test-prompts.json（UTF-8，用 Python 写文件）
5. 自查：frontmatter description 含"何时调用/何时不调用/trigger 词"；E 段可执行；test JSON 合法

## 输出位置
C:\Users\lzf13\.codex\skills\fundos\knowledge\distilled\<slug>\SKILL.md
C:\Users\lzf13\.codex\skills\fundos\knowledge\distilled\<slug>\test-prompts.json

## 完成回复
列出全部创建的文件绝对路径 + 每个技能一句话摘要。不要修改其他任何文件。
