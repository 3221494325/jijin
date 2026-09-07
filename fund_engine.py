#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS unified engine entry point.

This module owns project paths and the shared news contract. Existing scripts
remain adapters; callers should use this entry point for orchestration.
"""
import argparse
import json
import subprocess
import sys
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from portfolio_data import load_portfolio

ROOT = Path(__file__).resolve().parent
NEWS_JSON = ROOT / "news_result.json"
NEWS_MD = ROOT / "fund_news_report.md"
SKILL_INDEX = ROOT / ".codex/skills/fundos/knowledge/INDEX.md"
ENGINE_REPORT = ROOT / "fund_engine_report.md"
ENGINE_JSON = ROOT / "fund_engine_result.json"
SNAPSHOT = ROOT / "portfolio_snapshot.json"
DAILY_RESULT = ROOT / "daily_check_result.json"
DAILY_CHECK = ROOT / f"daily_check_{datetime.now().date().isoformat()}.md"
PRESIDENTIAL_BRIEF = ROOT / "fundos_presidential_brief.md"
RUN_HISTORY = ROOT / "fund_engine_runs.jsonl"
AUDIT_REPORT = ROOT / "fund_engine_audit.md"
ANALYTICS_RESULT = ROOT / "fund_analytics_result.json"


def now_iso():
    return datetime.now(timezone(timedelta(hours=8))).isoformat()


def normalize_news(payload):
    """Convert v1/v2 collector output into one versioned contract."""
    raw = payload.get("news", payload) if isinstance(payload, dict) else payload
    raw = raw if isinstance(raw, list) else []
    items = []
    for item in raw:
        if not isinstance(item, dict) or not item.get("title"):
            continue
        title = str(item["title"]).strip()
        content = str(item.get("content", "")).strip()
        sentiment = item.get("sentiment", "⚪中性")
        items.append({
            "id": item.get("id") or f"{item.get('source', '')}:{title}",
            "title": title,
            "content": content,
            "source": item.get("source", "unknown"),
            "url": item.get("url", ""),
            "published_at": item.get("published_at") or item.get("date", ""),
            "collected_at": item.get("collected_at") or now_iso(),
            "dimension": item.get("dimension", "快讯"),
            "sentiment": sentiment,
            "sentiment_score": item.get("sentiment_score", 0),
            # Reference-only signal. It must be combined with price and portfolio rules.
            "reference_signal": item.get("reference_signal", sentiment),
        })
    return {
        "schema_version": "fundos.news.v1",
        "collected_at": payload.get("collected_at", now_iso()) if isinstance(payload, dict) else now_iso(),
        "source_status": payload.get("source_status", {}) if isinstance(payload, dict) else {},
        "sentiment_index": payload.get("sentiment_index") if isinstance(payload, dict) else None,
        "news": items,
    }


def save_news(payload):
    normalized = normalize_news(payload)
    NEWS_JSON.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# FundOS 基金新闻情报",
        f"> 采集时间: {normalized['collected_at']}",
        f"> 数据契约: {normalized['schema_version']}",
        "",
        "| 时间 | 来源 | 维度 | 情绪参考 | 标题 |",
        "|---|---|---|---|---|",
    ]
    for item in normalized["news"]:
        title = item["title"].replace("|", r"\|")
        if item["url"]:
            title = f"[{title}]({item['url']})"
        lines.append(f"| {item['published_at']} | {item['source']} | {item['dimension']} | {item['reference_signal']} | {title} |")
    lines.extend(["", "---", "", "新闻情绪和涨跌预测仅作为参考信号，必须与价格行为、持仓结构和风控规则结合。", "", "> 本文件不构成投资建议。"])
    NEWS_MD.write_text("\n".join(lines), encoding="utf-8")
    return normalized


def source_health():
    """Report runtime prerequisites without hiding failures."""
    checks = {"python": sys.executable, "requests": False, "project": str(ROOT), "news_cache": str(NEWS_JSON)}
    try:
        import requests  # noqa: F401
        checks["requests"] = True
    except ImportError:
        pass
    return checks


def load_skills():
    text = SKILL_INDEX.read_text(encoding="utf-8")
    slugs = sorted(set(re.findall(r"(?m)^\| ([a-z][a-z0-9-]+) \|", text)))
    slugs = [slug for slug in slugs if slug != "slug"]
    return {"count": len(slugs), "skills": slugs, "source": str(SKILL_INDEX)}


def dispatch_skills(snapshot, news):
    """Select auditable skills from measurable portfolio/news conditions."""
    holdings = snapshot.get("holdings", [])
    tech_weight = snapshot.get("tech_weight")
    if tech_weight is None:
        # 按板块字段兜底（v1.0 按基金名硬编码集合，改版后即失效）
        tech_weight = sum(f.get("weight", 0) for f in holdings if f.get("sector") == "tech")
    deep_loss = [f for f in holdings if f.get("ret_pct", 0) <= -15]
    winners = [f for f in holdings if f.get("ret_pct", 0) > 0]
    news_items = news.get("news", [])
    triggered = []

    def add(skills, evidence, action, boundary):
        triggered.append({"skills": skills, "evidence": evidence,
                          "action": action, "boundary": boundary})

    add(["sector-rotation-detector", "trend-following-minimum-resistance"],
        "市场扫描已完成，先比较主线与持仓相对强弱",
        "观察主线是否连续，暂不因单日强势追入",
        "至少等待价格和成交连续确认")
    if deep_loss:
        add(["stop-loss-admission", "timely-correction", "emotion-discipline-system"],
            "; ".join(f"{f['name']} {f['ret_pct']:.2f}%" for f in deep_loss),
            "停止摊平，反弹窗口重新评估并分批纠错",
            "不以回本作为唯一卖出条件；接近-25%重新审查逻辑")
    if tech_weight > 40:
        add(["position-size-framework", "right-side-entry-pyramid"],
            f"科技/AI估算仓位 {tech_weight:.1f}% > 40%",
            "科技反弹时优先降集中度，新增只允许右侧确认后分批",
            "单次调整不超过相关仓位20%，不追涨")
    if winners:
        add(["hold-winners", "hold-three-conditions"],
            "; ".join(f"{f['name']} +{f['ret_pct']:.2f}%" for f in winners),
            "先检查底层逻辑和估值，再决定持有或费率换类",
            "不因小幅盈利机械止盈")
    if news_items:
        add(["narrative-news-check", "price-action-first", "independent-judgment"],
            f"采集新闻 {len(news_items)} 条，存在情绪参考信号",
            "新闻只进入观察层，必须等待价格行为确认",
            "新闻情绪不得单独触发买卖")
    return {"tech_weight": round(tech_weight, 2),
            "data_source": snapshot.get("data_source", SNAPSHOT.name),
            "deep_loss": [f.get("name") for f in deep_loss],
            "triggered": triggered}


def load_portfolio_data():
    return load_portfolio()


def write_presidential_brief(outputs, snapshot, news, analytics=None):
    decision = outputs["decision"]
    holdings = snapshot.get("holdings", [])
    total = snapshot.get("total_ret_pct", 0)
    deep = ", ".join(decision["deep_loss"]) or "无"
    lines = [
        "# 总裁批示 | FundOS 基金引擎",
        f"> 批示时间: {now_iso()}",
        f"> 持仓基准: {snapshot.get('date', snapshot.get('as_of', 'unknown'))}",
        "",
        "## 一、形势研判",
        "市场扫描、持仓诊断和新闻采集已经完成。新闻与涨跌预测只作为参考输入，当前优先级仍是价格确认、仓位结构和亏损纪律。",
        "",
        "## 二、持仓体检",
        f"- 组合收益率: {total:+.2f}%",
        f"- 科技/AI估算仓位: {decision['tech_weight']:.1f}%",
        f"- 深度亏损标的: {deep}",
        f"- 盈利标的: {', '.join(f['name'] for f in holdings if f.get('ret_pct', 0) > 0) or '无'}",
    ]
    p = (analytics or {}).get("portfolio", {})
    if p:
        lines.append(
            f"- 组合风险(近120日): 年化波动 {p.get('ann_vol_pct')}% | "
            f"最大回撤 {p.get('max_dd_pct')}% | 夏普 {p.get('sharpe')} | "
            f"HHI {p.get('hhi')}(有效 ~{p.get('effective_funds')}只)")
    lines += ["", "## 三、执行指令", ""]
    for item in decision["triggered"]:
        lines.append(f"- {item['action']}（依据：{item['evidence']}）")
    lines.extend(["", "## 四、风控边界", ""])
    for item in decision["triggered"]:
        lines.append(f"- {item['boundary']}")
    lines.extend([
        "",
        "## 五、复盘条件",
        "- 下次运行重新比较市场主线、持仓相对强弱和新闻事实是否兑现。",
        "- 只有实际交易发生时，才通过 trade_journal.py 单独记录；本次引擎运行不自动生成交易记录。",
        "- 复盘重点：触发条件是否成立、动作是否遵守边界、预测参考信号是否得到价格确认。",
        "",
        "> 免责声明：本批示是基于项目数据的规则化观察，不构成投资建议。基金投资有风险，决策请独立判断。",
    ])
    PRESIDENTIAL_BRIEF.write_text("\n".join(lines), encoding="utf-8")


def append_run_history(outputs):
    record = {
        "run_at": now_iso(),
        "mode": outputs.get("mode"),
        "status": {k: outputs.get(k) for k in ("market_scan", "diagnosis", "daily_check", "news", "analytics")},
        "news_status": outputs.get("news_status", {}),
        "decision": outputs.get("decision", {}),
    }
    with RUN_HISTORY.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def audit_engine():
    """Write a read-only health and provenance audit."""
    portfolio = load_portfolio_data()
    news = json.loads(NEWS_JSON.read_text(encoding="utf-8")) if NEWS_JSON.exists() else {}
    lines = [
        "# FundOS 基金引擎审计报告",
        f"> 审计时间: {now_iso()}",
        "",
        "## 数据来源",
        f"- 持仓来源: {portfolio.get('data_source', 'unknown')}",
        f"- 持仓时间: {portfolio.get('as_of', 'unknown')}",
        f"- 新闻文件: {'存在' if NEWS_JSON.exists() else '缺失'}",
        f"- 新闻条数: {len(news.get('news', []))}",
        "",
        "## 新闻来源状态",
    ]
    for name, status in news.get("source_status", {}).items():
        if isinstance(status, dict):
            error = status.get("error", "") or ""
            lines.append(f"- {name}: {status.get('status', 'unknown')}，{status.get('items', 0)}条，耗时 {status.get('elapsed_ms', 0)}ms" + (f"，错误: {error}" if error else ""))
    lines.extend(["", "## 风险提示", "- 预测和新闻情绪不得单独触发交易。", "- 本审计只读，不修改交易日志，不自动下单。", "- 失败或滞后数据不得标记为实时确认。", "", "> 本报告不构成投资建议。"])
    AUDIT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    return AUDIT_REPORT


def run_script(name, *args):
    path = ROOT / name
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, str(path), *args], cwd=ROOT, text=True, encoding="utf-8", errors="replace", env=env, check=False)


def collect_news(mode):
    path = ROOT / ".codex/skills/fundos/scripts/news_fetch_v2.py"
    result = subprocess.run(
        [sys.executable, str(path), "--mode", mode, "--format", "json"],
        cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        capture_output=True, check=False,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return result.returncode
    try:
        output = result.stdout or ""
        start = output.find("{")
        if start < 0:
            raise ValueError(result.stderr or "empty collector output")
        payload = json.loads(output[start:])
    except (ValueError, json.JSONDecodeError):
        print("news collector returned invalid JSON", file=sys.stderr)
        return 2
    normalized = save_news(payload)
    print(f"saved {len(normalized['news'])} news items to {NEWS_JSON}")
    return 0


def run_engine(mode="quick", offline=False):
    """Run the complete FundOS workflow and persist one report.

    编排（v2.0）:
      Phase1 并行: market_scan / daily_check / news (网络型任务)
      Phase2 串行: fundos_core 诊断（合并 Phase1 刷新的 daily_check_result）
      Phase3 串行: fundos_analytics 组合风险分析（读本地净值沉淀，离线可用）
    """
    outputs = {}
    outputs["mode"] = mode
    outputs["offline"] = offline
    outputs["health"] = source_health()
    outputs["skills"] = load_skills()
    if offline:
        outputs["market_scan"] = outputs["diagnosis"] = -1
        outputs["daily_check"] = outputs["news"] = -1
    else:
        with ThreadPoolExecutor(max_workers=3) as pool:
            f_scan = pool.submit(run_script, "market_scan.py")
            f_check = pool.submit(run_script, "daily_check.py")
            f_news = pool.submit(collect_news, mode)
            outputs["market_scan"] = f_scan.result().returncode
            outputs["daily_check"] = f_check.result().returncode
            outputs["news"] = f_news.result()
        outputs["diagnosis"] = run_script("fundos_core.py").returncode
    outputs["analytics"] = run_script("fundos_analytics.py", "--days", "120").returncode
    analytics = {}
    if ANALYTICS_RESULT.exists():
        try:
            analytics = json.loads(ANALYTICS_RESULT.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            analytics = {}
    outputs["analytics_summary"] = analytics.get("portfolio", {})
    news = json.loads(NEWS_JSON.read_text(encoding="utf-8")) if NEWS_JSON.exists() else {}
    outputs["news_status"] = news.get("source_status", {})
    snapshot = load_portfolio_data()
    outputs["decision"] = dispatch_skills(snapshot, news)
    write_presidential_brief(outputs, snapshot, news, analytics)
    append_run_history(outputs)
    step_label = lambda rc, name: (f"跳过(offline)" if rc == -1 else ("通过" if rc == 0 else "失败"))
    lines = [
        "# FundOS 基金引擎运行报告",
        f"> 运行时间: {now_iso()}",
        f"> 模式: {mode}{' (offline)' if offline else ''}",
        "",
        "## 执行状态",
        "",
        f"- 市场扫描: {step_label(outputs['market_scan'], 'scan')}",
        f"- 持仓诊断: {step_label(outputs['diagnosis'], 'diag')}",
        f"- 新闻采集: {step_label(outputs['news'], 'news')}",
        f"- 盘后净值检查: {step_label(outputs['daily_check'], 'check')}",
        f"- 组合风险分析: {step_label(outputs['analytics'], 'analytics')}",
        f"- 技能注册: {outputs['skills']['count']} 个",
        "",
    ]
    if analytics.get("portfolio"):
        p = analytics["portfolio"]
        lines += [
            "## 组合风险指标 (近120日)",
            "",
            f"- 年化波动: {p.get('ann_vol_pct')}% | 最大回撤: {p.get('max_dd_pct')}% ({p.get('max_dd_window')})",
            f"- 夏普(rf=0): {p.get('sharpe')} | HHI集中度: {p.get('hhi')} (有效基金数 ~{p.get('effective_funds')})",
            "",
        ]
    lines += ["## 新闻来源状态", ""]
    for name, status in outputs["news_status"].items():
        lines.append(f"- {name}: {status.get('status')}，{status.get('items', 0)}条")
    lines.extend(["", "## 技能调度", "",
                  f"- 盘后检查文件: [{DAILY_CHECK.name}]({DAILY_CHECK.name})",
                  f"- 持仓数据基准: {snapshot.get('data_source', SNAPSHOT.name)}",
                  f"- 科技/AI估算仓位: {outputs['decision']['tech_weight']:.1f}%",
                  f"- 深度亏损标的: {', '.join(outputs['decision']['deep_loss']) or '无'}", ""])
    for item in outputs["decision"]["triggered"]:
        lines.append(f"- **{' + '.join(item['skills'])}**")
        lines.append(f"  - 证据: {item['evidence']}")
        lines.append(f"  - 动作: {item['action']}")
        lines.append(f"  - 边界: {item['boundary']}")
    lines.extend(["", "## 规则", "",
                  "新闻情绪和涨跌预测仅作为参考信号；最终判断必须结合市场价格、持仓结构、止损边界和技能规则。",
                  "", "> 本报告不构成投资建议。"])
    ENGINE_REPORT.write_text("\n".join(lines), encoding="utf-8")
    ENGINE_JSON.write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
    return outputs


def main():
    parser = argparse.ArgumentParser(description="FundOS unified engine")
    parser.add_argument("command", choices=["health", "skills", "news", "scan", "diagnose",
                                            "run", "audit", "journal", "analytics"])
    parser.add_argument("--mode", choices=["quick", "full"], default="quick")
    parser.add_argument("--offline", action="store_true",
                        help="跳过网络采集，仅基于本地数据重建批示/报告")
    args, extra = parser.parse_known_args()

    if args.command == "health":
        print(json.dumps(source_health(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "skills":
        print(json.dumps(load_skills(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "news":
        return collect_news(args.mode)
    if args.command == "analytics":
        return run_script("fundos_analytics.py", "--days", "120", *extra).returncode
    if args.command == "scan":
        return run_script("market_scan.py", *extra).returncode
    if args.command == "diagnose":
        return run_script("fundos_core.py", *extra).returncode
    if args.command == "run":
        result = run_engine(args.mode, offline=args.offline)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.offline:
            return 0
        return 0 if all(result.get(k, 1) == 0 for k in ("market_scan", "diagnosis", "daily_check", "news")) else 1
    if args.command == "audit":
        print(audit_engine())
        return 0
    return run_script("trade_journal.py", *extra).returncode


if __name__ == "__main__":
    raise SystemExit(main())
