# FundOS 金融知识蒸馏体系

> 基于 cangjie-skill (RIA-TV++ 方法论) 的长期蒸馏机制。
> 目标：把金融分析知识 + 实战经验，逐步蒸馏成完整的金融分析师人格。

## 目录结构

```
knowledge/
├── books/           # 书籍/课程/长内容蒸馏（每本一个子目录）
│   └── <书名>/      # SKILL.md + INDEX.md + DIGEST.md + test-prompts.json
├── experience/      # 实战经验蒸馏（每次分析后沉淀）
│   ├── lessons.md   # 经验教训库（判断对/错记录）
│   └── <date>.md    # 每日分析复盘
├── distilled/       # 已蒸馏完成、可被调用的原子技能
└── GLOSSARY.md      # 金融术语词典（累计）
```

## 蒸馏流程

### A. 内容蒸馏（书籍/课程）
用 cangjie-skill 的 RIA-TV++ 流水线：
1. 用户提供内容文本（PDF/EPUB/TXT/字幕）
2. 5个提取器并行提取（框架/原则/案例/反例/术语）
3. 三重验证筛选
4. RIA++ 构造原子技能
5. Zettelkasten 链接 + 压力测试
6. 安装到 `distilled/` 供 FundOS 调用

### B. 经验蒸馏（实战复盘）
每次分析后自动执行：
1. 记录：判断依据 + 结果（对/错）
2. 归纳：什么信号有效、什么判断失误
3. 沉淀：提炼成经验单元写入 `experience/lessons.md`
4. 定期：经验成熟后升级为正式技能到 `distilled/`

## 当前状态（2026-08-08）

- [x] 引进 cangjie-skill (v1.0)
- [x] 建立知识库结构
- [x] 三本书完整蒸馏（回忆录7 + 巴菲特8 + EPD5 = 20 技能）
- [x] 实战技能 1 个（sector-rotation-detector）
- [x] 总裁人格（persona.md）已挂载
- [x] 技能库已迁移为项目级（D:\基金项目\.codex\skills\fundos），仅本基金项目可调用
- [ ] 持续：经验蒸馏 10+ 条后升级更多实战技能

## 调用方式

- 蒸馏一本书: 对 Codex 说 "蒸馏《书名》成skill" + 提供文件路径
- 复盘一次分析: 说 "复盘本周分析"
- 查看经验库: 说 "查看经验教训"
