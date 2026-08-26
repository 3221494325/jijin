# Stage 2 共享说明 — 构造 FundOS 蒸馏技能（RIA++）

## 你的任务
为指定的方法论单元构造正式技能。每个技能 = 1 个目录 + 2 个文件：
```
C:\Users\lzf13\.codex\skills\fundos\knowledge\distilled\<slug>\SKILL.md
C:\Users\lzf13\.codex\skills\fundos\knowledge\distilled\<slug>\test-prompts.json
```

## 技能语言与用途
- 全部用**简体中文**写作（引文保留英文原文）。
- 这些技能**只服务于 FundOS 基金项目**（用户个人基金持仓管理，帮用户从亏损转盈利、给出可执行建议）。
- 每个技能必须能回答 FundOS 场景下的实际问题：持仓基金、板块轮动、新闻利好利空、加仓/减仓/止损/换仓、情绪管理。

## 必须遵守的合规规则（硬性）
- 不输出"明天必涨/必跌/必须买/必须卖"式的硬性指令；给"决策框架+观察提醒+操作思路+分批节奏"。
- 引用英文原文时**必须**来自给定源文件，禁止编造；引文 ≤100 词，标注章节出处。
- 不夸大、不保证收益；结尾应有风险提示/免责意识。
- 用户当前持仓 8 只基金（详见 fundos_context.md），触发场景要落到这些真实持仓。

## SKILL.md 结构（严格按模板，删掉注释块）
frontmatter:
- name: <slug>
- description: 必须包含"何时调用 + 何时不调用 + 关键 trigger 信号（中英双写）"；≤300 字；用中文。
- source_book / source_chapter / tags / related_skills（阶段3可先填合理值）

正文六段：
- R 原文（引用，≤100词英文，标注章节）
- I 方法论骨架（5-15行，自己的话）
- A1 书中的应用（1-2个案例：问题→用法→结论→结果）
- A2 触发场景（3个场景 + 语言信号 + 与相邻技能区分）
- E 可执行步骤（3-5步，每步含完成标准/判停条件；要可落地到 FundOS：数据脚本、持仓、纪律阈值）
- B 边界（不适用场景 + 书中失败模式 + 作者盲点/时代局限 + 易混淆概念）

结尾：相关 skills（depends-on / contrasts-with / composes-with）+ 审计信息（V1/V2/V3 ✓）。

## test-prompts.json（严格按模板）
- 至少 3 条 should_trigger + 2 条 should_not_trigger + 1 条 edge_case。
- 全部 should_not_trigger 必须"不应激活本技能"，其中至少 1 条是同书/相邻技能的诱饵（跨技能混淆测试）。
- 提示词用中文，贴近 FundOS 用户真实问法（含持仓基金名、板块名、新闻场景）。

## 参考文件
- SKILL 模板: C:\Users\lzf13\.codex\skills\cangjie-skill\templates\SKILL.md.template
- test 模板: C:\Users\lzf13\.codex\skills\cangjie-skill\templates\test-prompts.json.template
- 风格样板: C:\Users\lzf13\.codex\skills\fundos\knowledge\distilled\sector-rotation-detector.md
- FundOS 语境: C:\Users\lzf13\.codex\skills\fundos\knowledge\stage2_packs\fundos_context.md
- 三本书源文件（引文必须来自这里，禁止编造）:
  - 回忆录: C:\Users\lzf13\.codex\skills\fundos\knowledge\books\reminiscences-of-a-stock-operator\candidates\*.md + verified.md
  - 巴菲特: C:\Users\lzf13\.codex\skills\fundos\knowledge\books\buffett-letters\candidates\*.md + verified.md
  - EPD: C:\Users\lzf13\.codex\skills\fundos\knowledge\books\extraordinary-popular-delusions\candidates\*.md + verified.md

## 编码要求（Windows 关键！）
- 写入文件必须用 Python `open(path, "w", encoding="utf-8")`，**不要**用 PowerShell 重定向或 echo（会变 GBK/乱码）。
- 在你的最终答复中列出你创建的完整文件路径列表。

## 完成标准
- 每个 SKILL.md 结构完整、引文真实、E 段可执行、B 段有反例。
- test-prompts.json 合法 JSON（可 json.load 通过）。
- 完成后回复：创建的文件路径 + 每个技能一句话摘要。
