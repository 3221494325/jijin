#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 控制台 v2.0 —— 个人基金持仓管理助手
============================================
使用方式: python fundos_console_v2.py
功能:
  [1] 实时行情概览    - 今日指数+基金净值
  [2] 持仓诊断报告    - 完整分析+策略阈值
  [3] 基金对比分析    - 多基金收益对比
  [4] 定投计算器      - AIP模拟
  [5] 新闻资讯        - 板块相关新闻
  [6] 查看使用说明    - 帮助
  [0] 退出
"""
import os, sys, json, time, subprocess
from pathlib import Path
from datetime import datetime

sys.stdout = open(sys.stdout.fileno(), "w", encoding="utf-8", errors="replace")

# ============================================================
# CONFIG
# ============================================================
SKILL_DIR = Path(r"D:\基金项目\.codex\skills\fundos")
SCRIPTS_DIR = SKILL_DIR / "scripts"
PROJECT_DIR = Path(r"D:\基金项目")
FUNDOS_CORE = PROJECT_DIR / "fundos_core.py"

C = {
    "R": "\033[91m", "G": "\033[92m", "Y": "\033[93m",
    "B": "\033[94m", "M": "\033[95m", "C": "\033[96m",
    "W": "\033[97m", "X": "\033[0m", "bold": "\033[1m",
}

BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║     ███████╗██╗   ██╗███╗   ██╗██████╗  ██████╗ ███████╗   ║
║     ██╔════╝██║   ██║████╗  ██║██╔══██╗██╔═══██╗██╔════╝   ║
║     █████╗  ██║   ██║██╔██╗ ██║██║  ██║██║   ██║███████╗   ║
║     ██╔══╝  ██║   ██║██║╚██╗██║██║  ██║██║   ██║╚════██║   ║
║     ██║     ╚██████╔╝██║ ╚████║██████╔╝╚██████╔╝███████║   ║
║     ╚═╝      ╚═════╝ ╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚══════╝   ║
║              个人基金持仓管理助手  v2.0                       ║
╚══════════════════════════════════════════════════════════════╝
"""

RISK_NOTE = """
  ⚠️  风险提示: 本工具仅做数据统计与客观展示
      不自动登录、不自动下单、不输出买卖指令
      所有交易决策请自行独立判断
"""


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(f"\n  {C['Y']}按 Enter 返回主菜单...{C['X']}")


def run_py(script_path, *args):
    """运行Python脚本并显示输出"""
    cmd = f'python "{script_path}" {" ".join(args)}'
    try:
        os.system(f"chcp 65001 > nul && {cmd}")
    except:
        os.system(cmd)


def menu_1_market():
    """实时行情概览"""
    clear()
    print(BANNER)
    print(f"  {C['bold']}{C['C']}[1] 实时行情概览{C['X']}")
    print(f"  {'─'*60}")
    print(f"  {C['Y']}正在获取最新数据...{C['X']}\n")
    
    if FUNDOS_CORE.exists():
        os.system(f'chcp 65001 > nul && set PYTHONUTF8=1 && python "{FUNDOS_CORE}"')
    else:
        print(f"  {C['R']}核心引擎未找到: {FUNDOS_CORE}{C['X']}")
    
    pause()


def menu_2_diagnosis():
    """持仓诊断报告"""
    clear()
    print(BANNER)
    print(f"  {C['bold']}{C['C']}[2] 持仓诊断报告{C['X']}")
    print(f"  {'─'*60}")
    
    # Check for Excel file
    desktop = Path.home() / "Desktop"
    excel_files = list(desktop.glob("基金持仓*.xlsx"))
    
    if excel_files:
        hf = excel_files[0]
        print(f"  {C['G']}✅ 找到持仓文件: {hf.name}{C['X']}\n")
        
        # Run portfolio report
        report_script = SCRIPTS_DIR / "portfolio_report.py"
        if report_script.exists():
            print(f"  {C['Y']}📊 正在生成诊断报告...{C['X']}\n")
            os.system(f'chcp 65001 > nul && set PYTHONUTF8=1 && python "{report_script}" --holdings "{hf}" --output "D:\\基金项目\\diagnosis_report.md"')
            print(f"\n  {C['G']}✅ 报告已保存: D:\\基金项目\\diagnosis_report.md{C['X']}")
            
            # Also run core analysis
            if FUNDOS_CORE.exists():
                print(f"\n  {C['Y']}📊 实时分析补充...{C['X']}\n")
                os.system(f'chcp 65001 > nul && set PYTHONUTF8=1 && python "{FUNDOS_CORE}"')
        else:
            print(f"  {C['R']}报告脚本未找到{C['X']}")
    else:
        print(f"  {C['Y']}⚠️ 未找到持仓Excel文件{C['X']}")
        print(f"  {C['W']}请将支付宝导出的持仓Excel放到桌面{C['X']}")
        print(f"\n  {C['Y']}使用在线数据运行核心分析...{C['X']}\n")
        if FUNDOS_CORE.exists():
            os.system(f'chcp 65001 > nul && set PYTHONUTF8=1 && python "{FUNDOS_CORE}"')
    
    pause()


def menu_3_compare():
    """基金对比分析"""
    clear()
    print(BANNER)
    print(f"  {C['bold']}{C['C']}[3] 基金对比分析{C['X']}")
    print(f"  {'─'*60}")
    print(f"  {C['Y']}对比基金近1月/3月/6月/1年收益...{C['X']}\n")
    
    compare_script = SCRIPTS_DIR / "fund_compare.py"
    if compare_script.exists():
        os.system(f'chcp 65001 > nul && set PYTHONUTF8=1 && python "{compare_script}"')
    else:
        print(f"  {C['R']}对比脚本未找到{C['X']}")
    
    pause()


def menu_4_aip():
    """定投计算器"""
    clear()
    print(BANNER)
    print(f"  {C['bold']}{C['C']}[4] 定投计算器{C['X']}")
    print(f"  {'─'*60}")
    print()
    
    aip_script = SCRIPTS_DIR / "aip_calc.py"
    if aip_script.exists():
        os.system(f'chcp 65001 > nul && set PYTHONUTF8=1 && python "{aip_script}"')
    else:
        print(f"  {C['R']}定投脚本未找到{C['X']}")
    
    pause()


def menu_5_news():
    """新闻资讯"""
    clear()
    print(BANNER)
    print(f"  {C['bold']}{C['C']}[5] 新闻资讯{C['X']}")
    print(f"  {'─'*60}")
    print(f"\n  {C['Y']}📰 尝试获取板块相关新闻...{C['X']}\n")
    
    news_script = SCRIPTS_DIR / "news_fetch_v2.py"
    if news_script.exists():
        os.system(f'chcp 65001 > nul && set PYTHONUTF8=1 && python "{news_script}"')
    else:
        # Try v1
        news_script = SCRIPTS_DIR / "news_fetch.py"
        if news_script.exists():
            os.system(f'chcp 65001 > nul && set PYTHONUTF8=1 && python "{news_script}"')
        else:
            print(f"  {C['R']}新闻脚本未找到{C['X']}")
            print(f"  {C['W']}提示: 新闻功能依赖网络，Shell环境可能受限{C['X']}")
    
    pause()


def menu_7_market_scan():
    """全市场板块扫描"""
    clear()
    print(BANNER)
    print(f"  {C['bold']}{C['C']}[7] 全市场板块扫描{C['X']}")
    print(f"  {'─'*60}")
    print(f"  {C['Y']}扫描全市场224个板块，识别主线方向...{C['X']}\n")
    scan_script = Path(r"D:\基金项目\market_scan.py")
    if scan_script.exists():
        os.system(f'chcp 65001 > nul && set PYTHONUTF8=1 && python "{scan_script}"')
    else:
        print(f"  {C['R']}扫描脚本未找到: {scan_script}{C['X']}")
    pause()


def menu_8_journal():
    """操作记录"""
    clear()
    print(BANNER)
    print(f"  {C['bold']}{C['C']}[8] 操作记录/复盘{C['X']}")
    print(f"  {'─'*60}")
    print("""
  请选择:
  [a] 记录新操作/建议
  [b] 查看历史记录
  [c] 复盘待办
  [0] 返回
""")
    choice = input("  输入 [a/b/c/0]: ").strip().lower()
    j = Path(r"D:\基金项目\trade_journal.py")
    if choice in ("a", "b", "c"):
        cmd = {"a": "add", "b": "view", "c": "review"}[choice]
        if j.exists():
            os.system(f'chcp 65001 > nul && set PYTHONUTF8=1 && python "{j}" {cmd}')
    pause()


def menu_9_skills():
    """蒸馏技能库"""
    clear()
    print(BANNER)
    print(f"  {C['bold']}{C['C']}[9] 蒸馏技能库 (金融分析师知识库){C['X']}")
    print(f"  {'─'*60}")
    dist = Path(r"D:\基金项目\.codex\skills\fundos\knowledge\distilled")
    skills = sorted([d for d in dist.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])
    if not skills:
        print(f"\n  {C['R']}未找到蒸馏技能目录: {dist}{C['X']}")
    else:
        print(f"\n  {C['Y']}📚 已蒸馏 {len(skills)} 个技能（Livermore/Buffett/Mackay 三本经典）:{C['X']}\n")
        for i, d in enumerate(skills, 1):
            txt = (d / "SKILL.md").read_text(encoding="utf-8")
            desc = ""
            if "description:" in txt:
                parts = txt.split("description:", 1)[1]
                for ln in parts.splitlines():
                    s = ln.strip()
                    if s.startswith("source_book") or s.startswith("tags") or s.startswith("related") or s.startswith("---"):
                        break
                    if s and s != "|":
                        desc = s.rstrip("。").rstrip(".")
                        break
            print(f"  {C['G']}[{i:02d}]{C['X']} {C['bold']}{d.name}{C['X']}")
            if desc:
                print(f"      {C['W']}{desc[:110]}{C['X']}")
        print(f"\n  {C['Y']}🔗 完整索引: D:\\基金项目\\.codex\\skills\\fundos\\knowledge\\INDEX.md{C['X']}")
        print(f"  {C['Y']}📖 精华导读: D:\\基金项目\\.codex\\skills\\fundos\\knowledge\\DIGEST.md{C['X']}")
        print(f"  {C['Y']}📕 术语词典: D:\\基金项目\\.codex\\skills\\fundos\\knowledge\\GLOSSARY.md{C['X']}")
        print(f"\n  {C['W']}提示: 在 Codex 中直接问 FundOS 相关问题，会按 description 自动匹配技能{C['X']}")
    pause()

def menu_6_help():
    """使用说明"""
    clear()
    print(BANNER)
    print(f"  {C['bold']}{C['C']}[6] 使用说明{C['X']}")
    print(f"  {'─'*60}")
    print(f"""
  {C['bold']}FundOS 是什么？{C['X']}
  ┌─────────────────────────────────────────────────────────┐
  │ 个人基金持仓管理助手。帮你管理从支付宝导出的基金持仓，    │
  │ 自动计算收益/成本/占比/风险评估，基于策略阈值生成观察提醒  │
  └─────────────────────────────────────────────────────────┘

  {C['bold']}使用流程{C['X']}
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │  ① 导出数据                                              │
  │     支付宝 → 我的 → 总资产 → 基金 → 导出Excel             │
  │     把文件放到桌面                                        │
  │                                                         │
  │  ② 查看行情 [菜单 1]                                     │
  │     一键获取今日指数+所有基金最新净值                      │
  │     数据来源: 东方财富 + 新浪财经                          │
  │                                                         │
  │  ③ 持仓诊断 [菜单 2]                                     │
  │     完整的持仓分析: 盈亏/占比/风险分层/策略阈值            │
  │     客观观察提醒 (不是买卖建议！)                          │
  │                                                         │
  │  ④ 基金对比 [菜单 3]                                     │
  │     对比持仓基金的近1月/3月/6月/1年收益                    │
  │     识别哪些基金表现好/差                                 │
  │                                                         │
  │  ⑤ 定投计算 [菜单 4]                                     │
  │     模拟定投效果，规划定投策略                             │
  │                                                         │
  │  ⑥ 新闻资讯 [菜单 5]                                     │
  │     获取板块相关新闻 (网络受限时可能不可用)                │
  │                                                         │
  └─────────────────────────────────────────────────────────┘

  {C['bold']}关于今日预估涨跌{C['X']}
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │  场外基金没有实时净值，本工具用指数映射估算:               │
  │                                                         │
  │  • A股基金: 用科创50/创业板指数涨幅 × 关联权重估算         │
  │  • QDII基金: 净值滞后1-2天，无法实时估算                  │
  │  • 实际净值以基金公司约20:00公布为准                       │
  │                                                         │
  │  精确的今日净值请参考你的 养基宝/支付宝 App                │
  │                                                         │
  └─────────────────────────────────────────────────────────┘

  {C['bold']}数据源说明{C['X']}
  ┌─────────────────────────────────────────────────────────┐
  │  • 基金净值: 东方财富 f10/lsjz API (历史净值)             │
  │  • 市场指数: 新浪财经 hq.sinajs.cn (实时)                 │
  │  • 基金估值: fundgz API 已失效，使用指数映射替代           │
  │  • 持仓数据: 你手动导出的 Excel                            │
  └─────────────────────────────────────────────────────────┘

  {C['bold']}常见问题{C['X']}
  ┌─────────────────────────────────────────────────────────┐
  │ Q: 为什么全球成长的数据是几天前的？                        │
  │ A: QDII基金净值滞后1-2天，这是正常的                       │
  │                                                         │
  │ Q: 今日预估涨跌准确吗？                                   │
  │ A: 是指数映射的粗略估算，实际会有偏差，仅供参考             │
  │                                                         │
  │ Q: 为什么不能给我买卖建议？                                │
  │ A: 合规要求。本工具只做客观展示+阈值观察，决策你自己做      │
  └─────────────────────────────────────────────────────────┘
""")
    pause()


def menu_0_exit():
    """退出"""
    clear()
    print(f"\n  {C['G']}👋 FundOS 已退出。祝你投资顺利！{C['X']}\n")
    sys.exit(0)


def main_menu():
    """主菜单"""
    menu_items = {
        "1": ("实时行情概览", menu_1_market, "今日指数 + 基金最新净值"),
        "2": ("持仓诊断报告", menu_2_diagnosis, "完整分析 + 策略阈值检查"),
        "3": ("基金对比分析", menu_3_compare, "近1月/3月/6月/1年比较"),
        "4": ("定投计算器",   menu_4_aip,     "模拟定投效果"),
        "5": ("新闻资讯",     menu_5_news,    "板块相关新闻 (网络受限)"),
        "6": ("使用说明",     menu_6_help,    "帮助文档"),
        "7": ("全市场扫描",   menu_7_market_scan, "224板块找主线"),
        "8": ("操作记录",     menu_8_journal,   "建议留痕+复盘"),
        "9": ("蒸馏技能库",   menu_9_skills,    "22个分析师技能+导读"),
        "0": ("退出",         menu_0_exit,    ""),
    }
    
    while True:
        clear()
        print(BANNER)
        print(RISK_NOTE)
        print(f"  {'─'*60}")
        
        for key, (name, _, desc) in menu_items.items():
            if key == "0":
                print(f"\n  {C['Y']}[0] 退出{C['X']}")
                continue
            desc_str = f" — {desc}" if desc else ""
            print(f"  {C['G']}[{key}] {name}{C['X']}{C['W']}{desc_str}{C['X']}")
        
        print(f"\n  {'─'*60}")
        print(f"  {C['Y']}📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  "
              f"💡 在Codex中说「分析我的持仓」也可直接调用{C['X']}")
        
        try:
            choice = input(f"\n  {C['bold']}请选择 [0-9]: {C['X']}").strip()
        except (EOFError, KeyboardInterrupt):
            menu_0_exit()
        
        if choice in menu_items:
            menu_items[choice][1]()
        else:
            print(f"\n  {C['R']}无效选项，请重新输入{C['X']}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {C['G']}👋 FundOS 已退出{C['X']}\n")
