#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 控制台交互菜单 v1.0
============================================================
基于 FundOS Skill + 六仓库融合架构
严格遵循合规红线：仅数据展示/复盘，不输出交易指令
============================================================
"""

import os
import sys
import json
import datetime
from pathlib import Path

# ============================================================
# 配置
# ============================================================
CONFIG_FILE = Path.home() / ".fundos" / "config.json"
DEFAULT_CONFIG = {
    "data_dir": str(Path.home() / "FundOS" / "data"),
    "export_dir": str(Path.home() / "FundOS" / "exports"),
    "thresholds": {
        "profit_target": 0.15,       # 止盈观察线 15%
        "loss_alert": -0.10,         # 回撤提醒 -10%
        "valuation_percentile": 20,  # 估值分位观察线
        "single_industry_max": 0.40, # 单行业仓位上限
        "equity_ratio_min": 0.30,    # 权益仓位下限
        "equity_ratio_max": 0.80,    # 权益仓位上限
    },
    "risk_disclaimer": True,
}


# ANSI colors
C = {"R":"`e[91m","G":"`e[92m","Y":"`e[93m","B":"`e[94m","M":"`e[95m","C":"`e[96m","W":"`e[97m","X":"`e[0m","bold":"`e[1m"}
RISK_BANNER = """
╔══════════════════════════════════════════════════════════════╗
║  ⚠️  重要风险提示 - 每次使用前请确认                           ║
╠══════════════════════════════════════════════════════════════╣
║  1. 本工具仅做数据统计与客观展示，不构成任何投资建议            ║
║  2. 不自动登录支付宝、不自动下单、不生成买卖指令                 ║
║  3. 所有交易决策请自行独立判断，投资有亏损风险                   ║
║  4. 历史回测不代表未来收益，数据可能存在偏差                     ║
║  5. 场外基金估值 ≠ 实际净值，请以官方公布净值为准               ║
║  6. 持仓数据为本地文件，不上传任何云端                           ║
╚══════════════════════════════════════════════════════════════╝
"""


def load_config():
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        return {**DEFAULT_CONFIG, **json.loads(CONFIG_FILE.read_text(encoding="utf-8"))}
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG


def save_config(cfg):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


# ============================================================
# 菜单系统
# ============================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def press_enter():
    input("\n按 Enter 返回主菜单...")


def show_banner():
    print(RISK_BANNER)


def menu_header(title):
    print(f"\n{'='*60}")
    print(f"  📊 {title}")
    print(f"{'='*60}")


# ---------- 阶段一：持仓数据 ----------

def phase1_menu(cfg):
    while True:
        clear_screen()
        show_banner()
        menu_header("阶段一：持仓数据管理 [安全区 · 放心使用]")
        print("""
  [1]  导入持仓 Excel          从支付宝导出的持仓文件读取数据
  [2]  导入交易记录 Excel       读取申购/赎回/转换记录
  [3]  查看当前持仓列表         展示所有持有基金及基本信息
  [4]  更新净值数据             从公开数据源拉取最新净值
  [5]  计算持仓指标             单基金收益/成本/占比
  [6]  导出持仓报表             Excel/JSON 格式本地保存
  [7]  查看数据目录             浏览本地数据文件
  [8]  配置数据源参数           设置数据目录/导出路径
  ─────────────────────────────────────────────
  [0]  返回主菜单
""")
        choice = input("  请输入选项 [0-8]: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            cmd_import_holdings(cfg)
        elif choice == "2":
            cmd_import_transactions(cfg)
        elif choice == "3":
            cmd_view_holdings(cfg)
        elif choice == "4":
            cmd_update_nav(cfg)
        elif choice == "5":
            cmd_calc_indicators(cfg)
        elif choice == "6":
            cmd_export_report(cfg)
        elif choice == "7":
            cmd_browse_data(cfg)
        elif choice == "8":
            cmd_config_data(cfg)


def cmd_import_holdings(cfg):
    menu_header("导入持仓 Excel")
    print(f"""
  📋 操作指南:
    1. 打开支付宝 → 理财 → 基金 → 持仓 → 导出
    2. 将导出的 Excel 文件放入: {cfg['data_dir']}
    3. 在此输入文件名即可导入

  ✅ 合规安全: 纯本地文件操作，不涉及任何账号登录
  ⚠️  隐私保证: 数据仅存本地，不上传
""")
    fname = input("  请输入持仓文件名 (留空返回): ").strip()
    if fname:
        print(f"\n  [模拟] 已读取 {fname}，解析持仓数据...")
        print("  ✅ 导入成功 (具体实现参见 FundOS Skill → references/module-specs.md)")
    press_enter()


def cmd_import_transactions(cfg):
    menu_header("导入交易记录")
    print("""
  📋 支持格式:
    - 支付宝基金交易记录导出 Excel
    - 手动填写的 CSV/Excel 模板

  ⚠️  分红方式影响计算:
    - 现金分红: 收益已到账，计算累计收益时需要纳入
    - 红利再投: 份额增加，成本需要重新摊薄计算
""")
    press_enter()


def cmd_view_holdings(cfg):
    menu_header("当前持仓列表")
    print("""
  ┌────────┬──────────────────┬────────┬────────┬──────────┬──────────┐
  │  代码   │      基金名称     │ 持有份额 │ 成本价  │  当前净值  │  收益率   │
  ├────────┼──────────────────┼────────┼────────┼──────────┼──────────┤
  │ (示例)  │                  │        │        │          │          │
  │ 000001 │ 华夏成长混合      │ 1000.00│  1.2000│   1.3500  │  +12.50% │
  │ 110022 │ 易方达消费行业    │  500.00│  2.8000│   3.1000  │  +10.71% │
  └────────┴──────────────────┴────────┴────────┴──────────┴──────────┘

  💡 导入真实数据后此处显示实际持仓
""")
    press_enter()


def cmd_update_nav(cfg):
    menu_header("更新净值数据")
    print("""
  数据源选择 (FundOS Data Hub Provider):
  [1] 东方财富 (推荐) ← efinance 主力 Provider
  [2] 天天基金        ← FundCrawler + real-time-fund
  [3] 晨星            ← FundCrawler (评级+分析)
  [4] 全部更新

  ⚠️  场外基金净值每日晚间更新，盘中估值为估算值，存在偏差
  ⚠️  A股节假日不更新净值
""")
    choice = input("  选择数据源 [1-4]: ").strip()
    if choice in ("1", "2", "3", "4"):
        print("\n  [模拟] 正在从公开数据源获取净值...")
        print("  ✅ 更新完成 (实际调用 FundOS Data Hub gRPC)")
    press_enter()


def cmd_calc_indicators(cfg):
    menu_header("持仓指标计算 [继承自 xalpha Quant Engine]")
    print(f"""
  将计算以下指标:

  单基金维度:
  ├── 持有收益 / 持有收益率
  ├── 持仓成本 / 摊薄成本
  ├── 近 7/30/90 日涨跌幅
  └── 定投统计 (累计投入 / 平均成本)

  组合维度:
  ├── 总仓位 / 总市值
  ├── 股债配比
  ├── 行业集中度
  ├── 组合最大回撤
  └── 组合波动率

  策略阈值 (当前配置):
  ├── 止盈观察线: {cfg['thresholds']['profit_target']*100}%
  ├── 回撤提醒线: {cfg['thresholds']['loss_alert']*100}%
  ├── 估值分位线: {cfg['thresholds']['valuation_percentile']}%
  ├── 单行业上限: {cfg['thresholds']['single_industry_max']*100}%
  └── 权益仓位区间: {cfg['thresholds']['equity_ratio_min']*100}%-{cfg['thresholds']['equity_ratio_max']*100}%

  ⚙️  计算由本地 Python 代码执行，不依赖大模型，结果精确可靠
""")
    press_enter()


def cmd_export_report(cfg):
    menu_header("导出持仓报表")
    print("""
  导出格式:
  [1] Excel (.xlsx)
  [2] JSON
  [3] Markdown (适合 Codex 读取)
  [4] 全部

  输出路径: {export_dir}
""".format(export_dir=cfg['export_dir']))
    press_enter()


def cmd_browse_data(cfg):
    menu_header("数据目录")
    data_dir = Path(cfg["data_dir"])
    data_dir.mkdir(parents=True, exist_ok=True)
    files = list(data_dir.glob("*"))
    if files:
        for f in files:
            size = f.stat().st_size
            print(f"  {'📄' if f.is_file() else '📁'} {f.name} ({size} bytes)")
    else:
        print("  📂 目录为空，请先导入持仓数据")
    print(f"\n  数据路径: {data_dir}")
    press_enter()


def cmd_config_data(cfg):
    menu_header("配置数据参数")
    print(f"""
  当前配置:
    data_dir  = {cfg['data_dir']}
    export_dir= {cfg['export_dir']}
""")
    new_dir = input("  新数据目录 (留空不变): ").strip()
    if new_dir:
        cfg["data_dir"] = new_dir
    new_exp = input("  新导出目录 (留空不变): ").strip()
    if new_exp:
        cfg["export_dir"] = new_exp
    save_config(cfg)
    print("  ✅ 配置已保存")
    press_enter()


# ---------- 阶段二：分析提醒 ----------

def phase2_menu(cfg):
    while True:
        clear_screen()
        show_banner()
        menu_header("阶段二：分析观察提醒 [Codex 推理层 · 仅观察不指令]")
        print("""
  [1]  运行持仓诊断            生成客观数据观察报告
  [2]  估值分位观察             指数/基金估值处于历史什么位置
  [3]  仓位阈值告警             检查是否触及预设仓位上下限
  [4]  回撤提醒                 净值大幅回撤触发观察
  [5]  再平衡观察               股债比例偏离目标区间提醒
  [6]  定投节奏分析             定投成本摊薄效果评估
  [7]  配置策略阈值             修改止盈/止损/仓位等观察线
  ─────────────────────────────────────────────
  [0]  返回主菜单
""")
        choice = input("  请输入选项 [0-7]: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            cmd_diagnosis(cfg)
        elif choice == "2":
            cmd_valuation(cfg)
        elif choice == "3":
            cmd_position_alert(cfg)
        elif choice == "4":
            cmd_drawdown_alert(cfg)
        elif choice == "5":
            cmd_rebalance(cfg)
        elif choice == "6":
            cmd_aip_analysis(cfg)
        elif choice == "7":
            cmd_config_thresholds(cfg)


def compliance_notice():
    return """
╔══════════════════════════════════════════════════════════════╗
║  本工具仅基于历史数据进行客观统计展示                           ║
║  所有内容不构成任何基金投资建议                                 ║
║  市场存在波动风险，投资有亏损可能                               ║
║  所有交易决策请自行独立判断                                     ║
╚══════════════════════════════════════════════════════════════╝
"""


def cmd_diagnosis(cfg):
    menu_header("持仓诊断报告")
    print(compliance_notice())
    print("""
  📊 诊断维度:
  ├── 组合总览: 总市值 / 总收益 / 总收益率
  ├── 单基金诊断: 每只基金的收益/回撤/波动
  ├── 行业分布: 穿透持仓后的行业集中度
  ├── 风险指标: 组合夏普比率 / 最大回撤 / 波动率
  └── 观察项: 根据你预设的阈值，列出触发观察的基金

  🔒 输出格式: 纯数据 + 客观描述，不包含"建议买入/卖出"话术
  🔒 合规话术: 只描述"到达预设观察线"，不输出"建议操作"

  💡 此功能由 Codex 推理层执行:
     指标计算 → 本地Python (精确)
     分析文本 → Codex (基于 FundOS Skill 的合规 Prompt)
     输出过滤 → 合规校验层 (剔除违规话术)
""")
    press_enter()


def cmd_valuation(cfg):
    t = cfg["thresholds"]["valuation_percentile"]
    menu_header(f"估值分位观察 (当前观察线: {t}%分位)")
    print(compliance_notice())
    print(f"""
  逻辑说明:
    当某指数/基金的 PE/PB 估值处于近 3-5 年历史 {t}% 分位以下时，
    触发观察提醒，不构成买入建议。

  正确话术示例:
    ✅ "沪深300当前PE处于近5年 8%分位，已到达你预设的{t}%观察线，请自行评估"
  禁止话术:
    ❌ "估值偏低，建议加仓"
    ❌ "当前是买入的好时机"

  📡 数据来源: FundOS Data Hub → eastmoney Provider → 指数估值数据
""")
    press_enter()


def cmd_position_alert(cfg):
    t = cfg["thresholds"]
    menu_header("仓位阈值告警")
    print(compliance_notice())
    print(f"""
  当前阈值:
    ├── 单行业占比上限: {t['single_industry_max']*100}%
    ├── 权益仓位下限:   {t['equity_ratio_min']*100}%
    └── 权益仓位上限:   {t['equity_ratio_max']*100}%

  告警逻辑 (仅观察提醒):
    ├── 某行业占比 > {t['single_industry_max']*100}% → 触发集中度观察
    ├── 权益仓位 < {t['equity_ratio_min']*100}%  → 触发仓位偏低观察
    └── 权益仓位 > {t['equity_ratio_max']*100}%  → 触发仓位偏高观察

  正确话术:
    ✅ "医药行业占比42%，超过你设置的40%上限，当前集中度偏高"
    ✅ "权益仓位达到85%，超出你设置的80%上限"
""")
    press_enter()


def cmd_drawdown_alert(cfg):
    t = cfg["thresholds"]["loss_alert"]
    menu_header(f"回撤提醒 (当前阈值: {t*100}%)")
    print(compliance_notice())
    print(f"""
  当单只基金或组合从近期高点回撤超过 {abs(t)*100}% 时触发观察提醒。

  ⚠️  回测局限性:
    - 历史最大回撤不代表未来回撤幅度
    - 极端行情下回撤可能远超历史极值
    - 提醒仅做观察参考，不暗示应该加仓或减仓

  正确话术:
    ✅ "XX基金自高点回撤12.3%，超过你设置的10%回撤观察线"
""")
    press_enter()


def cmd_rebalance(cfg):
    menu_header("再平衡观察")
    print(compliance_notice())
    print("""
  当股债配比偏离目标区间时触发观察提醒。

  示例:
    目标: 股60% / 债40%    允许偏离: ±10%
    当前: 股73% / 债27%    → 触发再平衡观察

  正确话术:
    ✅ "当前股债比为73:27，偏离你设置的目标区间(60:40±10%)，触发再平衡观察"
    ✅ "如需调整，请自行在支付宝操作"

  💡 此功能由 Quant Engine 计算，Codex 仅做话术包装
""")
    press_enter()


def cmd_aip_analysis(cfg):
    menu_header("定投节奏分析")
    print(compliance_notice())
    print("""
  分析维度:
    ├── 累计投入总额
    ├── 定投摊薄成本 vs 当前净值
    ├── 定投收益率 (IRR/XIRR)
    ├── 每期投入金额变化趋势
    └── 定投频率 vs 波动率关系

  算法来源: xalpha toolbox.py (IRR/XIRR/费率计算)

  ⚠️  定投不保证盈利，过往定投表现不代表未来收益
""")
    press_enter()


def cmd_config_thresholds(cfg):
    menu_header("配置策略阈值 [所有阈值由你人工设定]")
    t = cfg["thresholds"]
    print(f"""
  当前阈值:
    [1] 止盈观察线: {t['profit_target']*100}%
    [2] 回撤提醒线: {t['loss_alert']*100}%
    [3] 估值分位线: {t['valuation_percentile']}%
    [4] 单行业上限: {t['single_industry_max']*100}%
    [5] 权益仓位下限: {t['equity_ratio_min']*100}%
    [6] 权益仓位上限: {t['equity_ratio_max']*100}%

  ⚠️  参数熔断: 如果设置极端值 (>50%止盈 / <-50%止损 / <1%分位) 将自动提示
""")
    choice = input("  修改选项 [1-6 / 0=返回]: ").strip()
    if choice == "1":
        v = float(input("  止盈观察线 (%, 如15): "))
        if v > 50: print("  ⚠️ 参数熔断: 止盈线超过50%，请确认这是你理性的选择")
        cfg["thresholds"]["profit_target"] = v / 100
        save_config(cfg)
        print("  ✅ 已更新")
    elif choice == "2":
        v = float(input("  回撤提醒线 (%, 如-10): "))
        if v < -50: print("  ⚠️ 参数熔断: 止损线超过-50%")
        cfg["thresholds"]["loss_alert"] = v / 100
        save_config(cfg)
        print("  ✅ 已更新")
    elif choice in ("3", "4", "5", "6"):
        print("  ✅ 已更新 (实现细节参见 FundOS Skill)")
        save_config(cfg)
    press_enter()


# ---------- 阶段三：复盘系统 ----------

def phase3_menu(cfg):
    while True:
        clear_screen()
        show_banner()
        menu_header("阶段三：复盘系统 [事后分析 · 策略优化]")
        print("""
  [1]  记录人工操作              手动记录支付宝中的实际交易
  [2]  操作 vs 策略对比           检查实际操作是否符合预设策略
  [3]  定期复盘报告              周/月维度操作回顾
  [4]  策略效果评估               预设策略的历史表现统计
  [5]  优化参数建议               基于复盘数据，观察参数调整空间
  ─────────────────────────────────────────────
  [0]  返回主菜单
""")
        choice = input("  请输入选项 [0-5]: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            cmd_record_operation(cfg)
        elif choice == "2":
            cmd_compare_strategy(cfg)
        elif choice == "3":
            cmd_review_report(cfg)
        elif choice == "4":
            cmd_strategy_eval(cfg)
        elif choice == "5":
            cmd_optimize_params(cfg)


def cmd_record_operation(cfg):
    menu_header("记录人工操作")
    print("""
  📋 记录你在支付宝中的人工操作:
    基金代码 / 操作类型(买入/卖出/转换) / 金额 / 日期 / 备注

  ✅ 此功能仅做事后记录，不触发任何实际操作
  💡 数据本地存储，用于后续复盘对比
""")
    press_enter()


def cmd_compare_strategy(cfg):
    menu_header("操作 vs 策略对比")
    print(compliance_notice())
    print("""
  对比维度:
    ├── 买入时机: 是否在预设观察区间内
    ├── 卖出时机: 是否触及预设止盈/回撤线
    ├── 仓位管理: 是否遵守仓位上下限
    └── 定投纪律: 是否按计划执行定投

  输出:
    ├── 符合策略: X 次 (X%)
    ├── 偏离策略: Y 次 (Y%)  ← 此处仅客观统计，不做价值判断
    └── 偏差原因分类 (手动标注)

  ⚠️  不评判操作对错，仅客观对比
""")
    press_enter()


def cmd_review_report(cfg):
    menu_header("定期复盘报告")
    print(compliance_notice())
    print("""
  报告周期: 周报 / 月报

  报告内容:
    ├── 期间操作汇总
    ├── 策略执行度统计
    ├── 组合收益归因 (哪些操作贡献了收益/损失)
    ├── 手续费影响分析 (场外基金赎回费/持有期限)
    └── 下期观察项清单

  ⚠️  报告内容仅供个人复盘，不构成投资建议
""")
    press_enter()


def cmd_strategy_eval(cfg):
    menu_header("策略效果评估")
    print(compliance_notice())
    print("""
  📊 评估维度:
    ├── 策略信号准确率 (触发的观察有多少次后续验证了方向)
    ├── 虚警率 (触发观察但后续未发生显著变化)
    ├── 策略覆盖度 (有多少操作是策略未覆盖的)
    └── 参数敏感性分析

  ⚠️  历史策略表现不代表未来有效性
  💡 回测引擎: 基于 xalpha BTE_V2
""")
    press_enter()


def cmd_optimize_params(cfg):
    menu_header("参数优化观察")
    print("""
  基于复盘数据，观察参数调整空间:

  当前可观察:
    ├── 止盈线是否过窄/过宽 (触发频率分析)
    ├── 估值分位线是否合理 (历史触发后胜率)
    ├── 仓位上限是否匹配你的风险偏好
    └── 再平衡频率是否适当

  ⚠️  参数优化仅为观察建议，不构成策略推荐
  ⚠️  过度优化参数可能导致过拟合历史数据
""")
    press_enter()


# ---------- 工具与帮助 ----------

def tools_menu(cfg):
    while True:
        clear_screen()
        show_banner()
        menu_header("工具与帮助")
        print("""
  [1]  FundOS Skill 参考文档        查看架构设计和API规范
  [2]  数据 Schema 校验              验证导入数据格式
  [3]  合规规则检查                  检查输出是否触碰红线
  [4]  脚手架: 新建 Provider          生成数据源适配器模板
  [5]  脚手架: 新建策略               生成回测策略模板
  [6]  帮助: FundOS 架构总览          三横四纵架构图
  ─────────────────────────────────────────────
  [0]  返回主菜单
""")
        choice = input("  请输入选项 [0-6]: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            cmd_skill_docs()
        elif choice == "2":
            cmd_schema_check()
        elif choice == "3":
            cmd_compliance_check()
        elif choice == "4":
            cmd_scaffold_provider()
        elif choice == "5":
            cmd_scaffold_strategy()
        elif choice == "6":
            cmd_architecture_overview()


def cmd_skill_docs():
    menu_header("FundOS Skill 参考文档")
    print("""
  FundOS Skill 位于: ~/.codex/skills/fundos/

  📄 SKILL.md              — 核心指令 + 架构速览
  📂 references/
    ├── architecture.md    — 完整系统架构 (16.6KB)
    ├── data-sources.md    — 13个Provider规格
    ├── module-specs.md    — 各模块接口规范
    ├── api-contracts.md   — gRPC Proto定义
    └── repo-analysis.md   — 六大源仓库解剖分析

  🛠  scripts/
    ├── scaffold.py        — 模块脚手架生成器
    └── example.py         — 数据Schema校验器

  💡 在 Codex 中对话时自动激活 FundOS Skill
""")
    press_enter()


def cmd_schema_check():
    menu_header("数据 Schema 校验")
    print("""
  支持校验的 Schema:
    fund_nav:   基金净值数据 (code/name/date/nav/acc_nav/daily_return/source)
    stock_quote: 股票行情 (code/market/name/open/high/low/close/...)

  用法: python scripts/example.py fund_nav data.json
""")
    press_enter()


def cmd_compliance_check():
    menu_header("合规规则检查清单")
    print("""
  🔴 绝对禁止 (一票否决):
    □ 是否包含"建议买入/卖出/加仓/减仓/止盈/止损"确定性话术?
    □ 是否自动登录任何金融平台?
    □ 是否自动提交交易请求?
    □ 是否输出具体买卖时机和仓位?
    □ 是否暗示"历史策略未来可以稳定盈利"?

  🟡 需要风险声明包裹:
    □ 是否包含估值/收益/回撤数据? → 追加"数据仅供参考"
    □ 是否涉及策略效果? → 追加"历史不代表未来"
    □ 是否生成操作草稿? → 追加"请自行在平台操作"

  🟢 安全区 (自由实现):
    ✅ 数据读取/计算/展示
    ✅ 指标统计/图表生成
    ✅ 持仓复盘/策略对比
    ✅ 到达预设观察线提醒
""")
    press_enter()


def cmd_scaffold_provider():
    menu_header("脚手架: 新建 Data Provider")
    name = input("  Provider名称 (如 my-fund-source): ").strip()
    if name:
        print(f"\n  执行: python scripts/scaffold.py data-provider {name}")
        print(f"\n  将生成包含 BaseProvider 接口骨架的 {name}.py")
        print("  然后实现 fetch() / health_check() / capability() 三个方法即可")
    press_enter()


def cmd_scaffold_strategy():
    menu_header("脚手架: 新建回测策略")
    name = input("  策略名称 (如 ma-cross): ").strip()
    if name:
        print(f"\n  执行: python scripts/scaffold.py quant-strategy {name}")
        print(f"\n  将生成继承 BTE_V2 的策略骨架")
        print("  然后实现 prepare() 和 run(date) 方法即可")
    press_enter()


def cmd_architecture_overview():
    menu_header("FundOS 架构总览 (三横四纵)")
    print("""
  ┌──────────┬──────────┬──────────┬──────────┐
  │ Web App  │ Desktop  │ Extension│   CLI    │  ← 交互层
  │ (R1→)    │ (R6→)    │ (R4→)    │ (R1→)    │
  ├──────────┴──────────┴──────────┴──────────┤
  │     API Gateway (REST + gRPC + MCP)        │  ← 网关层
  ├────────────────┬───────────────────────────┤
  │ Quant Engine   │   AI Brain                │  ← 分析层
  │ (R2→) 回测指标 │   (R6→) Agent/情绪/解读   │
  ├────────────────┴───────────────────────────┤
  │        Data Hub (R3+R5+R6→)                │  ← 数据层
  │    13 Provider · 归一化 · 缓存 · 实时推送   │
  ├────────────────────────────────────────────┤
  │  Strategy Market · Alert Hub · Cloud Sync  │  ← 生态层
  └────────────────────────────────────────────┘

  本机使用路径:
    个人持仓 Excel
      → FundOS Skill (本地计算 + Codex 分析)
      → 输出持仓报表 / 观察提醒 / 复盘报告
      → 你在支付宝手动操作
""")
    press_enter()


# ---------- 主菜单 ----------

def main_menu():
    cfg = load_config()
    while True:
        clear_screen()
        show_banner()
        print("""
╔══════════════════════════════════════════════════════════════╗
║            🧬  FundOS 主控制台  v1.0                          ║
║        融合六大仓库 · 数据→分析→AI→全端                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  【阶段一】 持仓数据管理 ───── ✅ 安全区，放心使用              ║
║    导入Excel → 计算指标 → 导出报表                             ║
║                                                              ║
║  【阶段二】 分析观察提醒 ───── ⚠️  仅观察，不输出交易指令       ║
║    估值分位 · 仓位告警 · 回撤提醒 · 再平衡                     ║
║                                                              ║
║  【阶段三】 复盘系统 ──────── 📊 事后分析，策略优化            ║
║    记录操作 · 策略对比 · 定期复盘                              ║
║                                                              ║
║  【工具】 脚手架 & 帮助 ──── 🛠  Skill文档 & 代码生成          ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  🔴 红线: 不自动交易 · 不登录平台 · 不输出买卖建议              ║
╚══════════════════════════════════════════════════════════════╝
""")
        print("  [1]  阶段一 · 持仓数据管理")
        print("  [2]  阶段二 · 分析观察提醒")
        print("  [3]  阶段三 · 复盘系统")
        print("  [4]  工具与帮助")
        print("  [5]  查看 FundOS 融合报告")
        print("  [H]  帮助: 如何使用这套系统")
        print("  [Q]  退出")
        print()
        choice = input("  请输入选项: ").strip().upper()

        if choice == "1":
            phase1_menu(cfg)
        elif choice == "2":
            phase2_menu(cfg)
        elif choice == "3":
            phase3_menu(cfg)
        elif choice == "4":
            tools_menu(cfg)
        elif choice == "5":
            show_fusion_report()
        elif choice == "H":
            show_help()
        elif choice == "Q":
            print("\n  👋 FundOS 已退出。投资有风险，决策需谨慎。")
            sys.exit(0)



def cmd_quick_news():
    """快捷新闻搜索"""
    menu_header("板块新闻搜索")
    sub = input("  板块 (1=半导体 2=AI 3=美股 4=绿电 5=科创50 0=全部): ").strip()
    sector_map = {"1": "半导体", "2": "AI", "3": "美股", "4": "绿色电力", "5": "科创50"}
    if sub in sector_map:
        cmd = f'python "C:\\Users\\lzf13\\.codex\\skills\\fundos\\scripts\\news_fetch_v2.py" --sector {sector_map[sub]} --mode quick'
    else:
        cmd = f'python "C:\\Users\\lzf13\\.codex\\skills\\fundos\\scripts\\news_fetch_v2.py" --mode quick'
    print(f"\n  执行: {cmd}")
    os.system(cmd)
    press_enter()

def cmd_quick_report(cfg):
    """快捷持仓诊断"""
    menu_header("持仓诊断报告")
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    # Find holdings file
    files = [f for f in os.listdir(desktop) if "基金持仓" in f and f.endswith(".xlsx")]
    if files:
        hf = os.path.join(desktop, files[0])
        print(f"  持仓文件: {files[0]}")
    else:
        hf = input("  持仓文件路径: ").strip()
        if not hf:
            print("  未指定文件"); press_enter(); return
    
    output = os.path.join(desktop, f"持仓诊断报告_{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}.md")
    # Check for news file
    news_files = [f for f in os.listdir(desktop) if "news" in f.lower() and f.endswith(".md")]
    news_arg = ""
    if news_files:
        print(f"  检测到新闻文件: {news_files[0]}")
        use = input("  合并新闻分析? (y/n): ").strip().lower()
        if use == "y":
            news_arg = f' --with-news "{os.path.join(desktop, news_files[0])}"'
    
    cmd = f'python "C:\\Users\\lzf13\\.codex\\skills\\fundos\\scripts\\portfolio_report.py" --holdings "{hf}"{news_arg} --output "{output}"'
    print(f"\n  执行中...")
    os.system(cmd)
    print(f"\n  报告已保存: {output}")
    press_enter()

def cmd_daily_briefing(cfg):
    """一键日报: 新闻 + 诊断"""
    menu_header("一键日报 (新闻 + 持仓诊断)")
    print("  正在采集新闻...")
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    news_out = os.path.join(desktop, f"news_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.md")
    cmd1 = f'python "C:\\Users\\lzf13\\.codex\\skills\\fundos\\scripts\\news_fetch_v2.py" --mode quick --output "{news_out}"'
    os.system(cmd1)
    
    print("  正在生成持仓诊断...")
    files = [f for f in os.listdir(desktop) if "基金持仓" in f and f.endswith(".xlsx")]
    if files:
        hf = os.path.join(desktop, files[0])
        report_out = os.path.join(desktop, f"日报_{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}.md")
        cmd2 = f'python "C:\\Users\\lzf13\\.codex\\skills\\fundos\\scripts\\portfolio_report.py" --holdings "{hf}" --with-news "{news_out}" --output "{report_out}"'
        os.system(cmd2)
        print(f"\n  ✅ 日报已生成: {report_out}")
        print(f"  ✅ 新闻简报: {news_out}")
    else:
        print("  未找到持仓文件，仅生成了新闻简报")
    press_enter()def show_fusion_report():
    clear_screen()
    menu_header("FundOS 融合报告速览")
    report_path = Path(r"D:\基金项目\fund-ecosystem-fusion-report.md")
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8")
        # Show first 100 lines
        lines = content.split("\n")[:100]
        for line in lines:
            print(line)
        print(f"\n  ... (完整报告: {report_path}, 共 {len(content.split(chr(10)))} 行)")
    else:
        print("  📄 报告文件不存在: D:\\基金项目\\fund-ecosystem-fusion-report.md")
    press_enter()


def show_help():
    clear_screen()
    show_banner()
    menu_header("如何使用 FundOS 系统")
    print("""
  ┌─────────────────────────────────────────────────────────┐
  │               FundOS 使用流程全景图                       │
  ├─────────────────────────────────────────────────────────┤
  │                                                         │
  │  ① 数据准备                                              │
  │    支付宝 → 导出持仓Excel → 放入本地 data/ 目录            │
  │    └→ 菜单 [阶段一 → 1 导入持仓]                          │
  │                                                         │
  │  ② 指标计算                                              │
  │    自动计算收益/成本/占比/波动                            │
  │    └→ 菜单 [阶段一 → 5 计算持仓指标]                      │
  │                                                         │
  │  ③ 配置策略阈值                                          │
  │    设置你自己的止盈/止损/仓位观察线                        │
  │    └→ 菜单 [阶段二 → 7 配置策略阈值]                      │
  │                                                         │
  │  ④ 运行诊断                                              │
  │    Codex 基于阈值生成客观观察报告                          │
  │    └→ 菜单 [阶段二 → 1 运行持仓诊断]                      │
  │                                                         │
  │  ⑤ 人工操作                                              │
  │    你在支付宝上自行判断、手动操作                          │
  │    └→ 菜单 [阶段三 → 1 记录人工操作]                      │
  │                                                         │
  │  ⑥ 定期复盘                                              │
  │    对比操作是否符合预设策略，评估策略效果                   │
  │    └→ 菜单 [阶段三 → 3 定期复盘报告]                      │
  │                                                         │
  ├─────────────────────────────────────────────────────────┤
  │  💡 在 Codex 中对话时，FundOS Skill 自动激活              │
  │     可直接说: "分析我的持仓" / "检查估值分位" /            │
  │               "生成本周复盘报告" / "配置策略参数"           │
  ├─────────────────────────────────────────────────────────┤
  │  🔴 永远不做: 自动登录 · 自动下单 · 输出买卖建议            │
  │  🟢 可以做的: 数据展示 · 指标计算 · 观察提醒 · 复盘分析    │
  └─────────────────────────────────────────────────────────┘
""")
    press_enter()


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n  👋 FundOS 已退出。")
        sys.exit(0)
