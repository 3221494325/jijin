# -*- coding: utf-8 -*-

"""

FundOS Portfolio Report Generator v1.0

=======================================

整合: 持仓数据 + 净值计算 + 指标分析 + 新闻交叉 + 观察提醒



用法:

  python portfolio_report.py                                # 全量报告

  python portfolio_report.py --holdings 持仓.xlsx           # 指定持仓文件

  python portfolio_report.py --with-news news.md            # 包含新闻分析

  python portfolio_report.py --output report.md             # 指定输出

  python portfolio_report.py --format console               # 仅控制台输出

"""



import argparse, json, sys, io, os

from datetime import datetime

from pathlib import Path

from typing import Optional



try:

    import openpyxl

except ImportError:

    print("请安装: pip install openpyxl")

    sys.exit(1)



# ============================================================

# 配置

# ============================================================

CONFIG_DIR = Path.home() / ".fundos"

CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {

    "thresholds": {

        "profit_alert": 0.15,        # 止盈观察线 15%

        "loss_alert": -0.10,         # 回撤观察线 -10%

        "valuation_percentile": 20,  # 估值分位观察线

        "single_fund_max_ratio": 0.30,  # 单基持仓上限

        "equity_ratio_min": 0.30,    # 权益仓位下限

        "equity_ratio_max": 0.80,    # 权益仓位上限

    },

    "risk_disclaimer": True,

}



def load_config():

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if CONFIG_FILE.exists():

        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

        return {**DEFAULT_CONFIG, **cfg}

    save_config(DEFAULT_CONFIG)

    return DEFAULT_CONFIG



def save_config(cfg):

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")



# ============================================================

# 持仓数据读取

# ============================================================

FUND_SECTORS = {

    "华夏中证绿色电力": {"sector": "绿色电力", "type": "股票指数", "region": "A股", "risk": "中高"},

    "易方达全球成长": {"sector": "QDII混合", "type": "混合", "region": "全球", "risk": "高"},

    "摩根标普500": {"sector": "QDII指数", "type": "股票指数", "region": "美股", "risk": "中高"},

    "摩根纳斯达克100": {"sector": "QDII指数", "type": "股票指数", "region": "美股", "risk": "高"},

    "中欧半导体": {"sector": "半导体", "type": "股票", "region": "A股", "risk": "高"},

    "易方达信息产业": {"sector": "信息技术", "type": "混合", "region": "A股", "risk": "中高"},

    "易方达科创50": {"sector": "科创板", "type": "股票指数", "region": "A股", "risk": "高"},

    "永赢科技智选": {"sector": "科技", "type": "混合", "region": "A股", "risk": "高"},

}



def read_holdings(filepath: str) -> list:

    """读取支付宝导出的持仓Excel"""

    wb = openpyxl.load_workbook(filepath, data_only=True)

    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))

    

    funds = []

    total_amount = 0

    total_return = 0

    cumulative_return = 0

    

    for row in rows[1:]:  # 跳过表头

        name = str(row[0]).strip() if row[0] else ""

        if not name or len(name) < 4 or name.startswith('总') or '累计' in name or '昨日' in name or name.replace('.','').replace('-','').isdigit():

            # 汇总行

            if "总金额" in name or "总" in name:

                pass

            continue

        

        amount_str = str(row[1]).replace("元", "").replace(",", "").strip() if len(row) > 1 and row[1] else "0"

        daily_str = str(row[2]).replace("元", "").replace("+", "").replace(",", "").strip() if len(row) > 2 and row[2] else "0"

        return_str = str(row[3]).replace("元", "").replace("+", "").replace(",", "").strip() if len(row) > 3 and row[3] else "0"

        return_pct_str = str(row[4]).replace("%", "").strip() if len(row) > 4 and row[4] else "0"

        

        try:

            amount = float(amount_str)

            daily = float(daily_str)

            ret = float(return_str)

            ret_pct = float(return_pct_str) / 100

        except ValueError:

            continue

        

        # 匹配基金属性

        info = {}

        for key, val in FUND_SECTORS.items():

            if key in name:

                info = val

                break

        

        funds.append({

            "name": name,

            "amount": amount,

            "daily_return": daily,

            "total_return": ret,

            "return_pct": ret_pct,

            "sector": info.get("sector", "未知"),

            "type": info.get("type", "未知"),

            "region": info.get("region", "未知"),

            "risk": info.get("risk", "未知"),

        })

        total_amount += amount

        total_return += ret

    

    # 处理汇总行

    for row in rows[1:]:

        name = str(row[0]).strip() if row[0] else ""

        if "累计收益" in name:

            try:

                cumulative_return = float(str(row[1]).replace("元", "").replace(",", "").strip())

            except:

                pass

    

    return {

        "funds": funds,

        "total_amount": total_amount,

        "total_return": total_return,

        "cumulative_return": cumulative_return,

        "fund_count": len(funds),

    }



# ============================================================

# 风险分析

# ============================================================

def analyze_risk(holdings: dict, config: dict) -> dict:

    """风险指标计算"""

    funds = holdings["funds"]

    total = holdings["total_amount"]

    

    if total == 0:

        return {}

    

    # 区域分布

    regions = {}

    for f in funds:

        r = f["region"]

        regions[r] = regions.get(r, 0) + f["amount"]

    

    # 行业集中度

    sectors = {}

    for f in funds:

        s = f["sector"]

        sectors[s] = sectors.get(s, 0) + f["amount"]

    

    # QDII占比

    qdii_total = sum(f["amount"] for f in funds if "QDII" in f["type"] or f["region"] == "美股")

    qdii_ratio = qdii_total / total

    

    # 科技/AI占比

    tech_total = sum(f["amount"] for f in funds if f["sector"] in ["半导体", "科技", "信息技术", "科创板"])

    tech_ratio = tech_total / total

    

    # 最大单基占比

    max_fund = max(funds, key=lambda f: f["amount"])

    max_fund_ratio = max_fund["amount"] / total

    

    # 亏损基金

    losing_funds = [f for f in funds if f["return_pct"] < 0]

    # 亏损>10%的

    deep_loss = [f for f in funds if f["return_pct"] < -0.10]

    # 亏损>20%的

    severe_loss = [f for f in funds if f["return_pct"] < -0.20]

    

    return {

        "regions": regions,

        "sectors": sectors,

        "qdii_ratio": qdii_ratio,

        "tech_ratio": tech_ratio,

        "max_fund": max_fund,

        "max_fund_ratio": max_fund_ratio,

        "losing_count": len(losing_funds),

        "deep_loss": deep_loss,

        "severe_loss": severe_loss,

        "total_return_pct": holdings["total_return"] / (total - holdings["total_return"]) if (total - holdings["total_return"]) != 0 else 0,

    }



# ============================================================

# 观察提醒生成

# ============================================================

def generate_alerts(holdings: dict, risk: dict, config: dict) -> list:

    """基于预设阈值生成客观观察提醒"""

    alerts = []

    t = config["thresholds"]

    

    # 止盈观察

    for f in holdings["funds"]:

        if f["return_pct"] >= t["profit_alert"]:

            alerts.append({

                "level": "info",

                "fund": f["name"],

                "msg": f'持有收益率 {f["return_pct"]*100:.1f}%，到达你预设的 {t["profit_alert"]*100:.0f}% 止盈观察线，触发观察提醒',

            })

    

    # 亏损观察

    for f in holdings["funds"]:

        if f["return_pct"] <= t["loss_alert"]:

            alerts.append({

                "level": "warning",

                "fund": f["name"],

                "msg": f'持有收益率 {f["return_pct"]*100:.1f}%，超过你设置的 {abs(t["loss_alert"])*100:.0f}% 回撤观察线',

            })

    

    # 单基集中度

    if risk["max_fund_ratio"] > t["single_fund_max_ratio"]:

        alerts.append({

            "level": "info",

            "fund": risk["max_fund"]["name"],

            "msg": f'单基占比 {risk["max_fund_ratio"]*100:.1f}%，超过你设置的 {t["single_fund_max_ratio"]*100:.0f}% 单基上限',

        })

    

    # QDII集中度

    if risk["qdii_ratio"] > 0.40:

        alerts.append({

            "level": "info",

            "fund": "组合整体",

            "msg": f'QDII/海外资产占比 {risk["qdii_ratio"]*100:.0f}%，汇率和政策风险敞口较大',

        })

    

    # 科技集中度

    if risk["tech_ratio"] > 0.50:

        alerts.append({

            "level": "info",

            "fund": "组合整体",

            "msg": f'科技/AI/半导体占比 {risk["tech_ratio"]*100:.0f}%，行业集中度较高',

        })

    

    # 深度亏损

    for f in risk["deep_loss"]:

        alerts.append({

            "level": "warning",

            "fund": f["name"],

            "msg": f'亏损 {abs(f["return_pct"])*100:.1f}%，请关注该基金的基本面变化',

        })

    

    # 严重亏损

    for f in risk["severe_loss"]:

        alerts.append({

            "level": "critical",

            "fund": f["name"],

            "msg": f'亏损 {abs(f["return_pct"])*100:.1f}%，大幅亏损，请自行评估是否持续关注',

        })

    

    return alerts



# ============================================================

# 报告生成

# ============================================================


def parse_news_file(filepath: str) -> dict:
    """Parse news.md, extract fund-specific news with sentiment"""
    try:
        text = Path(filepath).read_text(encoding="utf-8")
    except:
        return {"fund_news": {}, "overall_sentiment": "N/A"}
    
    fund_news = {}
    current_fund = None
    overall = {"up": 0, "down": 0, "neutral": 0}
    
    for line in text.split("\n"):
        line = line.strip()
        # Detect fund section
        if line.startswith("### "):
            current_fund = line[4:].strip()
            fund_news[current_fund] = {"up": 0, "down": 0, "neutral": 0, "items": []}
        # Detect news items
        elif current_fund and line.startswith("- ") and ("UP" in line or "DOWN" in line or "up" in line or "down" in line or "偏多" in line or "偏空" in line):
            # Extract basic info
            item = {"line": line}
            if "UP" in line or "偏多" in line or "up" in line:
                fund_news[current_fund]["up"] += 1
                overall["up"] += 1
                item["sentiment"] = "up"
            elif "DOWN" in line or "偏空" in line or "down" in line:
                fund_news[current_fund]["down"] += 1
                overall["down"] += 1
                item["sentiment"] = "down"
            else:
                fund_news[current_fund]["neutral"] += 1
                overall["neutral"] += 1
                item["sentiment"] = "neutral"
            fund_news[current_fund]["items"].append(item)
    
    return {"fund_news": fund_news, "overall": overall}

def generate_report(holdings: dict, risk: dict, alerts: list, config: dict, news_file: str = None, news_data: dict = None) -> str:

    """生成完整的持仓诊断报告（Markdown）"""

    lines = []

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    

    # 头部

    lines.append(f"# 📊 FundOS 持仓诊断报告")

    lines.append(f"> 生成时间: {now}")

    lines.append(f"> 基金数量: {holdings['fund_count']}只")

    lines.append(f"> 数据来源: 支付宝导出Excel")

    lines.append("")

    lines.append("---")

    lines.append("")

    

    # 风险声明

    if config.get("risk_disclaimer", True):

        lines.append("## ⚠️ 风险声明")

        lines.append("")

        lines.append("> **本报告仅基于历史数据进行客观统计展示，所有内容不构成任何基金投资建议。**")

        lines.append("> 市场存在波动风险，投资有亏损可能。所有交易决策请自行独立判断。")

        lines.append("> 报告中的[观察提醒]仅表示数据到达了你预设的阈值，不暗示应进行任何操作。")

        lines.append("")

        lines.append("---")

        lines.append("")

    

    # 一、资产总览

    lines.append("## 一、资产总览")

    lines.append("")

    total = holdings["total_amount"]

    total_ret = holdings["total_return"]

    cum_ret = holdings["cumulative_return"]

    

    lines.append(f"| 指标 | 数值 |")

    lines.append(f"|------|------|")

    lines.append(f"| 当前总市值 | **{total:,.2f} 元** |")

    lines.append(f"| 持有收益 | {total_ret:+,.2f} 元 |")

    lines.append(f"| 持有收益率 | {risk['total_return_pct']*100:+.2f}% |")

    lines.append(f"| 累计收益(含已卖出) | {cum_ret:+,.2f} 元 |")

    lines.append(f"| 亏损基金数 | {risk['losing_count']}/{holdings['fund_count']} 只 |")

    lines.append("")

    

    # 二、持仓明细

    lines.append("## 二、持仓明细")

    lines.append("")

    lines.append("| # | 基金名称 | 持有金额 | 占比 | 收益率 | 昨日 | 板块 | 风险 |")

    lines.append("|---|----------|:--------:|:----:|:------:|:----:|------|:----:|")

    

    for i, f in enumerate(holdings["funds"], 1):

        ratio = f["amount"] / total * 100

        ret_str = f'{f["return_pct"]*100:+.2f}%'

        daily_str = f'{f["daily_return"]:+.2f}'

        ret_mark = "🔴" if f["return_pct"] < -0.05 else ("🟡" if f["return_pct"] < 0 else "🟢")

        lines.append(f"| {i} | {f['name'][:22]} | {f['amount']:,.0f} | {ratio:.1f}% | {ret_mark}{ret_str} | {daily_str} | {f['sector']} | {f['risk']} |")

    

    lines.append("")

    

    # 三、配置分析

    lines.append("## 三、配置分析")

    lines.append("")

    

    # 区域分布

    lines.append("### 区域分布")

    lines.append("")

    for region, amt in sorted(risk["regions"].items(), key=lambda x: -x[1]):

        pct = amt / total * 100

        bar = chr(9608) * int(pct / 5)

        lines.append(f"- {region}: {bar} {pct:.0f}% ({amt:,.0f}元)")

    lines.append("")

    

    # 行业分布

    lines.append("### 行业/板块分布")

    lines.append("")

    for sector, amt in sorted(risk["sectors"].items(), key=lambda x: -x[1]):

        pct = amt / total * 100

        bar = chr(9608) * int(pct / 5)

        lines.append(f"- {sector}: {bar} {pct:.0f}% ({amt:,.0f}元)")

    lines.append("")

    

    # 集中度

    lines.append("### 集中度分析")

    lines.append("")

    lines.append(f"- 单基最大占比: **{risk['max_fund_ratio']*100:.0f}%** ({risk['max_fund']['name'][:20]})")

    lines.append(f"- QDII/海外占比: **{risk['qdii_ratio']*100:.0f}%**")

    lines.append(f"- 科技/AI/半导体占比: **{risk['tech_ratio']*100:.0f}%**")

    lines.append("")

    

    if risk["qdii_ratio"] > 0.40:

        lines.append(f'> ⚠️ QDII占比 {risk["qdii_ratio"]*100:.0f}%，汇率和海外政策风险敞口较大，请自行评估')

    if risk["tech_ratio"] > 0.50:

        lines.append(f'> ⚠️ 科技板块占比 {risk["tech_ratio"]*100:.0f}%，行业集中度高，板块轮动风险需关注')

    lines.append("")

    

    # 四、观察提醒

    lines.append("## 四、观察提醒")

    lines.append("")

    

    if alerts:

        lines.append(f"共 {len(alerts)} 条观察提醒（基于你预设的策略阈值）：")

        lines.append("")

        

        for level_name, level_icon in [("critical", "🔴"), ("warning", "🟠"), ("info", "🟡")]:

            level_alerts = [a for a in alerts if a["level"] == level_name]

            if level_alerts:

                for a in level_alerts:

                    lines.append(f"- {level_icon} **{a['fund'][:20]}**: {a['msg']}")

                lines.append("")

    else:

        lines.append("*当前无触发观察提醒*")

        lines.append("")

    

    # 五、参数配置

    lines.append("## 五、当前策略阈值")

    lines.append("")

    t = config["thresholds"]

    lines.append(f"| 参数 | 当前值 |")

    lines.append(f"|------|:------:|")

    lines.append(f"| 止盈观察线 | {t['profit_alert']*100:.0f}% |")

    lines.append(f"| 回撤观察线 | {t['loss_alert']*100:.0f}% |")

    lines.append(f"| 估值分位观察线 | {t['valuation_percentile']:.0f}% |")

    lines.append(f"| 单基持仓上限 | {t['single_fund_max_ratio']*100:.0f}% |")

    lines.append(f"| 权益仓位区间 | {t['equity_ratio_min']*100:.0f}% - {t['equity_ratio_max']*100:.0f}% |")

    lines.append("")

    lines.append("*修改阈值: python fundos_console.py → [2] → [7]*")

    lines.append("")

    

    # 六、新闻交叉分析（如果有新闻数据）
    if news_data and news_data.get("fund_news"):
        lines.append("## 六、新闻交叉分析")
        lines.append("")
        ov = news_data["overall"]
        lines.append(f"板块新闻情绪汇总: UP={ov.get('up',0)} DOWN={ov.get('down',0)} NEUTRAL={ov.get('neutral',0)}")
        lines.append("")
        for fund_name, finfo in news_data["fund_news"].items():
            if finfo["up"] > 0 or finfo["down"] > 0:
                lines.append(f"### {fund_name[:25]}")
                lines.append(f"UP={finfo['up']} DOWN={finfo['down']} NEUTRAL={finfo['neutral']}")
                for item in finfo["items"][:3]:
                    lines.append(f"- {item['line'][:100]}")
                lines.append("")
        lines.append("---")
        lines.append("")

    # 七、免责

    lines.append("---")

    lines.append("")

    lines.append("## ⚠️ 免责声明")

    lines.append("")

    lines.append("> 本报告由 FundOS 自动生成，仅基于历史数据和公开信息进行客观统计。")

    lines.append("> **不构成任何形式的投资建议、交易指导或市场预测。**")

    lines.append("> 所有[观察提醒]均为预设参数的机械触发，不代表投资信号。")

    lines.append("> 基金投资存在亏损风险，过往业绩和回测结果不预示未来表现。")

    lines.append("> **所有交易决策请自行独立判断，并在支付宝上手动操作。**")

    lines.append("")

    lines.append(f"> *Generated by FundOS v2.0 on {now}*")

    

    return "\n".join(lines)



# ============================================================

# 控制台输出

# ============================================================

def print_console(holdings, risk, alerts, config):

    """控制台彩色输出"""

    print()

    print("=" * 65)

    print(f"  FundOS 持仓诊断  {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    print("=" * 65)

    

    total = holdings["total_amount"]

    print(f"\n  总市值: {total:,.2f}元  |  持有收益: {holdings['total_return']:+,.2f}")

    print(f"  持有收益率: {risk['total_return_pct']*100:+.2f}%  |  累计: {holdings['cumulative_return']:+,.2f}")

    print()

    

    print(f"  {'基金':<22s} {'金额':>8s} {'占比':>6s} {'收益率':>8s}")

    print(f"  {'-'*22} {'-'*8} {'-'*6} {'-'*8}")

    for f in holdings["funds"]:

        ratio = f["amount"] / total * 100

        ret_str = f'{f["return_pct"]*100:+.2f}%'

        print(f"  {f['name'][:22]:<22s} {f['amount']:>8,.0f} {ratio:>5.1f}% {ret_str:>8s}")

    

    print(f"\n  配置: QDII {risk['qdii_ratio']*100:.0f}% | 科技 {risk['tech_ratio']*100:.0f}%")

    

    if alerts:

        print(f"\n  --- 观察提醒 ({len(alerts)}条) ---")

        for a in alerts:

            icon = {"critical": "!!", "warning": "! ", "info": "i "}[a["level"]]

        print(f"  [{icon}] {a['msg'][:80]}")

    

    print()

    print("=" * 65)

    print("  Disclaimer: 客观数据展示，不构成投资建议")

    print("=" * 65)



# ============================================================

# CLI

# ============================================================

def main():

    parser = argparse.ArgumentParser(description="FundOS Portfolio Report Generator")

    parser.add_argument("--holdings", "-H", help="持仓Excel文件路径")

    parser.add_argument("--with-news", "-N", help="新闻简报MD文件(可选)")

    parser.add_argument("--output", "-o", help="输出文件路径(.md)")

    parser.add_argument("--format", "-f", choices=["markdown", "console"], default="console")

    parser.add_argument("--config", "-c", help="显示/修改当前策略阈值", action="store_true")

    args = parser.parse_args()

    

    config = load_config()

    

    # 显示配置

    if args.config:

        print("\n当前策略阈值:")

        for k, v in config["thresholds"].items():
            
            print(f"  {k}: {v}")

        return

    

    # 找持仓文件

    holdings_file = args.holdings

    if not holdings_file:

        # 自动搜索

        desktop = Path.home() / "Desktop"

        candidates = list(desktop.glob("基金持仓*.xlsx")) + list(desktop.glob("*持仓*.xlsx"))

        if candidates:

            holdings_file = str(candidates[0])
            
            print(f"自动检测到持仓文件: {holdings_file}")

        else:

            print("未找到持仓文件。请指定: --holdings 文件路径")

            print("或放到桌面，文件名包含\"基金持仓\"")

            return

    

    if not Path(holdings_file).exists():

        print(f"文件不存在: {holdings_file}")

        return

    

    # 读取数据

    print("读取持仓数据...")

    holdings = read_holdings(holdings_file)

    

    # 分析

    print("分析风险指标...")

    risk = analyze_risk(holdings, config)

    

    # 生成观察提醒

    print("生成观察提醒...")

    alerts = generate_alerts(holdings, risk, config)

    

    # 输出

    if args.format == "markdown" or (args.output and args.output.endswith(".md")):
        news_data = parse_news_file(args.with_news) if args.with_news else None
        report = generate_report(holdings, risk, alerts, config, args.with_news, news_data)

        if args.output:
            Path(args.output).write_text(report, encoding="utf-8")
            print(f"报告已保存: {args.output}")
        else:
            print(report)
    else:
        print_console(holdings, risk, alerts, config)


if __name__ == "__main__":
    main()