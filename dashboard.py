#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 可视化面板 v1.0 — 本地网页看板

用法:
  python dashboard.py               # 启动并自动打开浏览器 http://127.0.0.1:8899
  python dashboard.py --port 9000   # 换端口
  python dashboard.py --no-browser  # 不自动开浏览器

内容: 组合总览 / 持仓实时表 / 净值归一走势 / 板块涨跌榜 / 风险指标 /
      情绪指数序列 / 触发警报 / 新闻流。60秒自动刷新（也可点"立即刷新"）。
数据: 全部来自 FundOS 数据层（带缓存，重复刷新几乎零开销）。
"""
import argparse
import hashlib
import json
from datetime import datetime, timedelta
from email.utils import formatdate
import sys
import threading
import time
import webbrowser
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DIRECTIVE_STATE = ROOT / "data" / "state" / "directive_execution.json"
BJ_TZ = ZoneInfo("Asia/Shanghai")
# 版本号单点定义：页面通过 __FUNDOS_BUILD__ 占位符注入，避免前后端各写一份而错位
BUILD_ID = "cockpit-xray-v4"
_directive_state_lock = threading.Lock()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 无控制台启动守卫（pythonw）：先保证 stdout 存在，后续模块的 print 才安全
if __import__("sys").stdout is None:
    _LOGDIR = ROOT / "data" / "logs"
    _LOGDIR.mkdir(parents=True, exist_ok=True)
    __import__("sys").stdout = open(_LOGDIR / "dashboard_stdout.log", "a",
                                    encoding="utf-8", buffering=1)
    __import__("sys").stderr = __import__("sys").stdout

from fundos_config import (  # noqa: E402
    DAILY_RESULT, NEWS_JSON, DATA_DIR, FUND_META, SECTOR_LABEL,
)
import fundos_analytics  # noqa: E402
import fundos_data  # noqa: E402
import fundos_core  # noqa: E402

# 轻量直连快讯（实时新闻流用；引擎的六维全量采集契约不受影响）
_scripts = ROOT / ".codex" / "skills" / "fundos" / "scripts"
if str(_scripts) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_scripts))
try:
    from news_fetch_v2 import collect_direct_news, sentiment_label_cn  # noqa: F401
    HAS_LIVE_NEWS = True
except Exception:  # noqa: BLE001 — 模块缺失时面板仍可运行（新闻回退引擎结果）
    HAS_LIVE_NEWS = False
    def sentiment_label_cn(item):  # type: ignore
        sc = item.get("sentiment_score", 0) or 0
        return "利好" if sc >= 2 else ("利空" if sc <= -2 else "中性")

PORT_DEFAULT = 8899
DATA_TTL = 20       # 秒：聚合数据缓存
LIVE_TTL = 300      # 秒：新闻/板块实时抓取防爬间隔
_cache = {"ts": 0.0, "payload": None, "refreshing": False, "last_error": ""}
_cache_lock = threading.Lock()
_cache_ready = threading.Event()
_live = {"ts": 0.0, "news": [], "news_ok": False}   # 新闻直连缓存
_live_lock = threading.Lock()

BOARD_DIR = DATA_DIR / "board_history"
SENTIMENT_DIR = DATA_DIR / "sentiment_history"

# 法定节假日（A股休市日）。留空表示只按周末判断；遇到长假在此补齐，
# 页面会明确标注"未含节假日表"，不假装知道。
MARKET_HOLIDAYS = set()


def _prev_weekday(day):
    d = day - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def market_clock(now=None):
    """A股交易时段判定 + 最近交易日。

    看板所有"今日/实时"字样都必须过一遍这里，避免周末把上周五的
    指数涨跌标成"今日估算"。
    """
    now = now or datetime.now(BJ_TZ)
    hm = now.hour * 60 + now.minute
    today = now.date()
    is_weekday = today.weekday() < 5
    is_holiday = today.isoformat() in MARKET_HOLIDAYS
    is_trading_day = is_weekday and not is_holiday

    if not is_weekday:
        session, label = "weekend", "休市 · 周末"
    elif is_holiday:
        session, label = "holiday", "休市 · 法定节假日"
    elif hm < 9 * 60 + 30:
        session, label = "pre_open", "盘前"
    elif hm < 11 * 60 + 30:
        session, label = "morning", "盘中 · 早盘"
    elif hm < 13 * 60:
        session, label = "lunch", "午间休市"
    elif hm < 15 * 60:
        session, label = "afternoon", "盘中 · 午盘"
    else:
        session, label = "closed", "已收盘"

    in_session = session in ("morning", "lunch", "afternoon")
    if is_trading_day:
        if hm >= 15 * 60:
            data_day = today
        elif in_session:
            data_day = today
        else:                      # 盘前：上一交易日才是完整数据日
            data_day = _prev_weekday(today)
    else:
        data_day = _prev_weekday(today)

    return {
        "session": session,
        "label": label,
        "is_trading_day": is_trading_day,
        "in_session": in_session,
        "holiday_table": bool(MARKET_HOLIDAYS),
        "today": today.isoformat(),
        "data_day": data_day.isoformat(),
        "data_day_label": ("今日盘中" if in_session else
                           ("今日收盘" if is_trading_day and hm >= 15 * 60
                            else f"最近交易日 {data_day.isoformat()}")),
        "note": ("非交易日：页面数字为上一交易日收盘口径，不是今天的涨跌。"
                 if not is_trading_day else
                 ("盘中数据为实时，估算不等于结算。" if in_session else
                  ("今日已收盘，估算与净值将陆续公布。" if hm >= 15 * 60
                   else "开盘前：数据为上一交易日收盘口径。"))),
    }


# ============================================================
# 数据聚合（全部复用现有引擎与缓存）
# ============================================================
def collect():
    """聚合面板数据。任何子模块失败都不拖垮整体（优雅降级为缺省块）。"""
    now = datetime.now(BJ_TZ)
    payload = {"updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
               "build": BUILD_ID,
               "snapshot_meta": {"source": "local_computer",
                                  "generated_at": now.isoformat(timespec="seconds"),
                                  "timezone": "Asia/Shanghai",
                                  "status": "success"},
               "market": market_clock(now),
               "data_sources": {}}

    # ---- 持仓 + 指数 + 今日估算（fundos_core，净值带10分钟缓存）----
    try:
        snap_date, funds = fundos_core.load_snapshot()
        indices = fundos_core.fetch_indices()
        proxies, fx_chg = fundos_core.fetch_qdii_proxies()
        manual = {}
        manual_path = ROOT / "manual_updates.json"
        if manual_path.exists():
            manual = json.loads(manual_path.read_text(encoding="utf-8")) \
                .get("updates", {}).get(datetime.now(BJ_TZ).strftime("%Y-%m-%d"), {})
        fundos_core.calc_portfolio(funds)
        fundos_core.estimate_today(funds, indices, proxies, manual, fx_chg)
        total_cost = sum(f["cost"] for f in funds)
        total_value = sum(f["value"] for f in funds)
        est_total = sum(f.get("est_value", f.get("value", 0)) for f in funds)
        daily_path = ROOT / "daily_check_result.json"
        daily_checked_at = ""
        if daily_path.exists():
            try:
                daily_checked_at = json.loads(daily_path.read_text(encoding="utf-8")).get("checked_at", "")
            except (OSError, json.JSONDecodeError):
                daily_checked_at = ""
        payload["portfolio"] = {
            "as_of": snap_date, "total_cost": round(total_cost, 2),
            "total_value": round(total_value, 2),
            "total_ret": round(total_value - total_cost, 2),
            "total_ret_pct": round((total_value / total_cost - 1) * 100, 2) if total_cost else 0,
            "est_total_value": round(est_total, 2),
            "est_ret_pct": round((est_total / total_cost - 1) * 100, 2) if total_cost else 0,
            "usdcnh": fundos_data.fetch_fx("fx_susdcnh").get("price") if fx_chg is not None else None,
            "daily_checked_at": daily_checked_at,
        }
        try:
            snapshot_age = (datetime.now(BJ_TZ).date() - datetime.fromisoformat(str(snap_date)[:10]).date()).days
        except (TypeError, ValueError):
            snapshot_age = None
        payload["portfolio"]["snapshot_age_days"] = snapshot_age
        payload["portfolio"]["freshness_status"] = (
            "current" if snapshot_age is not None and snapshot_age <= 7 else "stale"
        )
        payload["holdings"] = [{
            "name": f["name"], "code": f["code"], "sector": f.get("sector", ""),
            "sector_label": SECTOR_LABEL.get(f.get("sector"), f.get("sector") or "未分类"),
            "value": round(f.get("value", 0), 2), "weight": round(f.get("weight", 0), 1),
            "ret_pct": round(f.get("ret_pct", 0), 2),
            "return": round(f.get("return", 0), 2),
            "nav_date": f.get("nav_date", "-"),
            "nav_day_chg": f.get("nav_day_chg", 0),
            "today_est": round(f.get("today_est", 0), 2),
            "today_source": f.get("today_source", ""),
            "freshness": "估算" if f.get("today_source") not in ("", "QDII滞后") else "已公布净值",
        } for f in funds]
        # 盈亏贡献：谁在拖后腿（按金额，不按百分比，避免小仓位放大噪音）
        total_pl = sum(h["return"] for h in payload["holdings"])
        payload["contribution"] = sorted(
            [{"name": h["name"], "code": h["code"], "pl": h["return"],
              "pl_pct_of_total": round(h["return"] / total_pl * 100, 1) if total_pl else 0,
              "value": h["value"]}
             for h in payload["holdings"]],
            key=lambda x: x["pl"])
        payload["contribution_total"] = round(total_pl, 2)
        payload["indices"] = [{"name": v["name"], "price": v["price"],
                               "chg_pct": round(v["chg_pct"], 2)}
                              for v in indices.values()]
        payload["global_indices"] = [{"name": v["name"], "price": v["price"],
                                      "chg_pct": round(v["chg_pct"], 2)}
                                     for v in proxies.values()]
        payload["data_sources"]["portfolio"] = {"status": "ok", "as_of": str(snap_date)}
    except Exception as exc:  # noqa: BLE001 — 面板不能崩
        payload["error_core"] = str(exc)[:200]
        payload["data_sources"]["portfolio"] = {"status": "error", "error": str(exc)[:160]}
        payload["portfolio"], payload["holdings"] = {}, []

    # ---- 风险指标（分析引擎，历史已缓存）----
    try:
        ana = fundos_analytics.analyze(days=120)
        payload["risk"] = ana.get("portfolio", {})
        payload["funds_risk"] = [{
            "code": code, "name": f["name"], "weight": f["weight"],
            "nav_pct": f.get("nav_pct", 0),
            "ann_vol_pct": f["ann_vol_pct"], "max_dd_pct": f["max_dd_pct"],
            "sharpe": f["sharpe"],
        } for code, f in ana.get("funds", {}).items()]
        corr = ana.get("correlation", {})
        payload["corr_top"] = corr.get("top_pairs", [])
        payload["corr_bottom"] = corr.get("bottom_pairs", [])
        payload["tech_cluster_avg"] = corr.get("tech_cluster_avg")
        payload["xirr"] = (ana.get("xirr") or {}).get("portfolio")
        # 绩效面板：组合净值曲线 / 水下曲线 / 月度收益 / 相关性矩阵
        payload["perf"] = {
            "curve": ana.get("curve") or {},
            "monthly": ana.get("monthly") or [],
            "corr_matrix": corr.get("matrix") or {},
            "window_days": ana.get("window_days", 120),
        }
        # XIRR 只在持有期足够长时才有可比性；短窗口年化会放大成无意义数字
        x = ana.get("xirr") or {}
        payload["xirr_note"] = ("资金流水重建，未含结构调账，仅供粗略参考"
                                if x.get("portfolio") is not None else "流水不足，无法计算")
        payload["data_sources"]["analytics"] = {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        payload["error_analytics"] = str(exc)[:200]
        payload["data_sources"]["analytics"] = {"status": "error", "error": str(exc)[:160]}

    # ---- 净值归一走势（近120交易日，本地缓存即时）----
    series, dates = [], None
    for code, meta in FUND_META.items():
        try:
            hist = fundos_data.fetch_fund_nav_history(code, days=120)
        except fundos_data.DataError:
            hist = []
        if len(hist) < 5:
            continue
        d = [r["date"] for r in hist]
        navs = [r["nav"] for r in hist]
        base = navs[0]
        if dates is None or d[-1] > (dates[-1] if dates else ""):
            dates = d
        series.append({"name": meta["name"], "dates": d,
                       "data": [round(v / base, 4) for v in navs]})
    payload["nav_series"] = {"series": series}
    payload["data_sources"]["nav_history"] = {"status": "ok" if series else "empty", "funds": len(series)}

    # ---- 板块榜（实时抓取，fundos_data 自带5分钟缓存防爬） ----
    try:
        ind, con = fundos_data.fetch_sector_boards()
        ind = sorted(ind, key=lambda x: x.get("chg_pct", 0), reverse=True)
        con = sorted(con, key=lambda x: x.get("chg_pct", 0), reverse=True)
        mk = payload["market"]
        payload["boards"] = {
            # 板块数据的日期取自"最近交易日"，不再用抓取时刻冒充行情日期
            "date": (now.strftime("%m-%d %H:%M 实时") if mk["in_session"]
                     else f"{mk['data_day']} 收盘口径"),
            "live": mk["in_session"],
            "fetched_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "industries": [{"name": b["name"], "chg_pct": round(b["chg_pct"], 2),
                            "amount": round(b.get("amount", 0), 1)} for b in ind[:10]],
            "concepts": [{"name": b["name"], "chg_pct": round(b["chg_pct"], 2)} for b in con[:10]],
        }
        payload["data_sources"]["boards"] = {"status": "ok", "as_of": payload["boards"]["date"]}
    except Exception as exc:  # noqa: BLE001
        payload["error_boards"] = str(exc)[:200]
        payload["data_sources"]["boards"] = {"status": "error", "error": str(exc)[:160]}

    # ---- 情绪指数序列 ----
    sentiment = []
    if SENTIMENT_DIR.exists():
        for p in sorted(SENTIMENT_DIR.glob("sentiment_*.json"))[-30:]:
            try:
                blob = json.loads(p.read_text(encoding="utf-8"))
                sentiment.append({"date": blob.get("date", p.stem[-10:]),
                                  "index": blob.get("index", 50)})
            except (OSError, json.JSONDecodeError):
                continue
    payload["sentiment"] = sentiment

    # ---- 新闻流（直连快讯实时抓取，5分钟防爬间隔；失败回退引擎结果） ----
    news = _load(NEWS_JSON)
    live_ok = False
    with _live_lock:
        import time as _t
        if HAS_LIVE_NEWS and (_t.time() - _live["ts"] > LIVE_TTL or not _live["news_ok"]):
            try:
                _live["news"] = collect_direct_news()
                _live["news_ok"] = True
                _live["ts"] = _t.time()
            except Exception:  # noqa: BLE001
                _live["news_ok"] = False
        if _live["news_ok"] and _live["news"]:
            live_ok = True
            news_items = _live["news"]
            news_time = datetime.now(BJ_TZ).strftime("%m-%d %H:%M")
        else:
            news_items = news.get("news", [])
            news_time = (news.get("collected_at") or "")[5:16].replace("T", " ")
    payload["news_live"] = live_ok
    payload["data_sources"]["news"] = {"status": "live" if live_ok else "cache", "as_of": news_time}
    payload["news_time"] = news_time
    payload["news"] = [{"label": sentiment_label_cn(n), "url": n.get("url", ""),
                        "source": n.get("source", ""),
                        "title": n.get("title", ""), "date": n.get("date", "")}
                       for n in news_items[:14]]

    if live_ok:
        try:
            from news_fetch_v2 import compute_sentiment_index
            payload["sentiment_now"] = compute_sentiment_index(_live["news"])
        except Exception:  # noqa: BLE001
            payload["sentiment_now"] = news.get("sentiment_index", {})
    else:
        payload["sentiment_now"] = news.get("sentiment_index", {})
    # ---- 当日新闻归档（快讯是流，不落盘就会被冲掉）+ 全天累计统计 ----
    day_items = []
    try:
        from news_fetch_v2 import archive_news, load_day_archive
        if _live["news_ok"] and _live["news"]:
            day_items = archive_news(_live["news"])
        else:
            day_items = load_day_archive()
    except Exception:  # noqa: BLE001
        try:
            from news_fetch_v2 import load_day_archive
            day_items = load_day_archive()
        except Exception:  # noqa: BLE001
            day_items = []
    try:
        from news_fetch_v2 import day_summary
        payload["news_day"] = day_summary(day_items)
    except Exception:  # noqa: BLE001
        payload["news_day"] = {}

    daily = _load(DAILY_RESULT)
    payload["actions"] = daily.get("actions", [])
    payload["daily"] = {k: daily.get(k) for k in
                        ("total_value", "total_ret_pct", "tech_weight", "qdii_weight")}
    # 盘后核验结论必须带日期：旧结论当成今日提醒是这类看板最容易骗人的地方
    checked_at = str(daily.get("checked_at") or "")
    checked_day = checked_at[:10]
    if checked_day == payload["market"]["data_day"]:
        stale_state, stale_days = "current", 0
    else:
        try:
            stale_days = (datetime.fromisoformat(payload["market"]["data_day"]).date()
                          - datetime.fromisoformat(checked_day).date()).days
        except ValueError:
            stale_days = None
        stale_state = "stale" if checked_day else "missing"
    payload["actions_meta"] = {
        "checked_at": checked_at, "date": checked_day,
        "state": stale_state, "stale_trading_days": stale_days,
        "label": (f"{checked_day} 盘后核验" if checked_day else "未做盘后核验"),
    }

    # ---- 操作指南（规则引擎：确定性、可审计） ----
    try:
        from fundos_advisor import build_guide
        idx688 = next((i["chg_pct"] for i in payload.get("indices", [])
                       if i["name"] == "科创50"), 0)
        nav_pct_map = {fr.get("code"): fr.get("nav_pct", 0)
                       for fr in payload.get("funds_risk", [])}
        sector_news = {}
        if day_items:
            try:
                from news_fetch_v2 import KEYWORD_LAYERS
                for sec, layers in KEYWORD_LAYERS.items():
                    kws = [k.split("+")[0] for k in
                           list(layers.get("core", [])) + list(layers.get("expand", []))]
                    hits = [n for n in day_items
                            if any(k in n.get("title", "") for k in kws)]
                    sector_news[sec] = {
                        "up": sum(1 for n in hits if n.get("score", 0) >= 2),
                        "down": sum(1 for n in hits if n.get("score", 0) <= -2)}
            except Exception:  # noqa: BLE001
                sector_news = {}
        # 行业前瞻输入：今日板块榜（5分钟缓存）+ 近5日板块快照
        industry_in = None
        try:
            ind_today, _con = fundos_data.fetch_sector_boards()
            ind_sorted = sorted(ind_today, key=lambda x: x.get("chg_pct", 0),
                                reverse=True)[:20]
            days = []
            for snap in fundos_data.load_board_history(5):
                ib = sorted(snap.get("industries", []),
                            key=lambda x: x.get("chg_pct", 0), reverse=True)
                days.append([b.get("name") for b in ib[:15]])
            industry_in = {"today": [{"name": b["name"], "chg_pct": b["chg_pct"]}
                                     for b in ind_sorted],
                           "days": days}
        except Exception:  # noqa: BLE001
            industry_in = None
        payload["guide"] = build_guide(
            holdings=payload.get("holdings", []),
            sentiment=payload.get("sentiment_now"),
            nav_pct=nav_pct_map,
            indices={"sh000688": idx688},
            sector_news=sector_news,
            industry=industry_in)
        state = _load_directive_state()
        for directive in payload["guide"].get("directives", []):
            key = _directive_key(directive)
            directive["execution_key"] = key
            directive["execution"] = state.get(key, {"status": "pending"})
            generated = datetime.fromisoformat(payload["guide"]["generated_at"])
            if generated.tzinfo is None:
                generated = generated.replace(tzinfo=BJ_TZ)
            directive["generated_at"] = generated.isoformat(timespec="seconds")
            directive["review_by"] = (generated + timedelta(hours=24)).isoformat(timespec="seconds")
            directive["expired"] = datetime.now(BJ_TZ) > datetime.fromisoformat(directive["review_by"])
            if directive["execution"].get("status") in ("confirmed", "cancelled"):
                directive["execution"]["next_step"] = _directive_next_step(directive)
    except Exception as exc:  # noqa: BLE001
        payload["error_guide"] = str(exc)[:200]

    # ---- 组合体检 X-Ray（静态规则：通过/不通过 + 阈值，不重复 advisor 的动作建议） ----
    try:
        import fundos_xray
        payload["xray"] = fundos_xray.build_xray(
            holdings=payload.get("holdings", []),
            risk=payload.get("risk"),
            correlation={"tech_cluster_avg": payload.get("tech_cluster_avg")},
            portfolio=payload.get("portfolio"),
            data_sources=payload.get("data_sources"),
            market=payload.get("market"))
        payload["data_sources"]["xray"] = {"status": "ok",
                                          "score": payload["xray"]["score"]}
    except Exception as exc:  # noqa: BLE001
        payload["error_xray"] = str(exc)[:200]
        payload["data_sources"]["xray"] = {"status": "error", "error": str(exc)[:160]}

    # ---- 大模型接入层（未配置密钥时优雅降级为纯规则模式） ----
    try:
        import fundos_llm
        payload["llm_status"] = fundos_llm.status()
        d = fundos_llm.digest({"guide": payload.get("guide"),
                               "news": payload.get("news", []),
                               "news_day": payload.get("news_day"),
                               "portfolio": payload.get("portfolio")})
        payload["llm_digest"] = d
        payload["llm_brief"] = fundos_llm.load_cached(d)
    except Exception as exc:  # noqa: BLE001
        payload["llm_status"] = {"configured": False}
        payload["llm_brief"] = None
        payload["error_llm"] = str(exc)[:200]
    return payload


def _directive_key(directive):
    raw = "{}\n{}".format(directive.get("title", ""), directive.get("rule", ""))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_directive_state():
    try:
        return json.loads(DIRECTIVE_STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_directive_state(state):
    DIRECTIVE_STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DIRECTIVE_STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DIRECTIVE_STATE)


def _directive_next_step(directive):
    """Return the follow-up state for the instruction lifecycle."""
    execution = directive.get("execution") or {}
    if execution.get("status") == "cancelled":
        return "本次不执行；等待下一次规则生成或人工复核，不代表已成交。"
    level = directive.get("level")
    if level == "指令":
        return "等待下一次净值与触发线复核；未到条件前不重复操作。"
    if level == "警告":
        return "进入观察，等待市场环境或持仓触发线变化后再复核。"
    return "保留观察，等待价格或独立数据确认后再复核。"


def _load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def get_payload():
    """返回最近快照；过期数据在后台刷新，避免外部源拖住页面请求。"""
    with _cache_lock:
        age = time.time() - _cache["ts"] if _cache["ts"] else None
        payload = _cache["payload"]
        if payload is None and not _cache["refreshing"]:
            _cache["refreshing"] = True
            threading.Thread(target=_refresh_payload, daemon=True, name="fundos-data-refresh").start()
        elif age is None or age > DATA_TTL:
            if not _cache["refreshing"]:
                _cache["refreshing"] = True
                threading.Thread(target=_refresh_payload, daemon=True, name="fundos-data-refresh").start()
        payload = _cache["payload"]
    if payload is not None:
        # 刷新本身要十几秒，超过 TTL 就判 stale 会天天误报；用 3×TTL 才算真陈旧
        return _decorate_payload(payload, stale=age is not None and age > DATA_TTL * 3)
    # 首次访问给数据聚合一个有限窗口；超时也必须返回可识别的降级响应。
    _cache_ready.wait(timeout=3)
    with _cache_lock:
        payload = _cache["payload"]
        error = _cache["last_error"]
    if payload is not None:
        return _decorate_payload(payload, stale=False)
    return {"error": error or "数据正在首次同步，请稍后刷新",
            "degraded": True, "refreshing": True,
            "updated_at": datetime.now(BJ_TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "snapshot_meta": {"timezone": "Asia/Shanghai", "status": "degraded"}}


def _decorate_payload(payload, *, stale):
    out = dict(payload)
    out["degraded"] = bool(stale or payload.get("error_core"))
    out["refreshing"] = _cache.get("refreshing", False)
    out["cache_age_seconds"] = round(max(0, time.time() - _cache.get("ts", time.time())))
    out["data_quality"] = "stale" if stale else ("partial" if out["degraded"] else "fresh")
    return out


def _refresh_payload():
    try:
        result = collect()
        with _cache_lock:
            _cache["payload"] = result
            _cache["ts"] = time.time()
            _cache["last_error"] = result.get("error_core", "")
    except Exception as exc:  # noqa: BLE001
        with _cache_lock:
            _cache["last_error"] = str(exc)[:300]
    finally:
        with _cache_lock:
            _cache["refreshing"] = False
        _cache_ready.set()


# ============================================================
# 页面模板（构建号单点注入：前端不再硬编码版本，避免白屏式版本门禁）
# ============================================================
def render_page():
    """读取页面并把构建号注入占位符。每次请求都读盘，改 HTML 无需重启服务。"""
    try:
        raw = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    except OSError as exc:
        return f"<h1>dashboard.html 读取失败</h1><pre>{exc}</pre>"
    return raw.replace("__FUNDOS_BUILD__", BUILD_ID)


HTML = render_page()


# ============================================================
# HTTP 服务
# ============================================================
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # 静默访问日志，只留 notify 日志
        pass

    def _send(self, code, body, ctype):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-FundOS-Build", BUILD_ID)
        self.send_header("X-FundOS-Timezone", "Asia/Shanghai")
        self.end_headers()
        try:
            self.wfile.write(data)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            with _cache_lock:
                age = round(time.time() - _cache["ts"]) if _cache["ts"] else None
                ready = _cache["payload"] is not None
                refreshing = _cache["refreshing"]
                error = _cache["last_error"]
            body = {"ok": ready and not error, "service": "FundOS dashboard",
                    "build": BUILD_ID, "timezone": "Asia/Shanghai",
                    "cache_age_seconds": age, "refreshing": refreshing,
                    "data_quality": "unavailable" if not ready else ("partial" if error else ("stale" if age and age > DATA_TTL * 3 else "fresh")),
                    "last_error": error,
                    "sources": (_cache["payload"].get("data_sources", {}) if ready else {})}
            self._send(200, json.dumps(body, ensure_ascii=False),
                       "application/json; charset=utf-8")
        elif path == "/api/data":
            try:
                if "fresh=1" in (urlparse(self.path).query or ""):
                    with _cache_lock:      # 强制后台重算，但不阻塞这次请求
                        _cache["ts"] = 0.0
                payload = get_payload()
                self._send(200, json.dumps(payload, ensure_ascii=False),
                           "application/json; charset=utf-8")
            except Exception as exc:  # noqa: BLE001
                self._send(500, json.dumps({"error": str(exc)[:300]}, ensure_ascii=False),
                           "application/json; charset=utf-8")
        elif path == "/static/echarts.min.js":
            local = DATA_DIR / "static" / "echarts.min.js"
            if local.exists():
                self._send(200, local.read_bytes(),
                           "application/javascript; charset=utf-8")
            else:
                self._send(404, "echarts not bundled", "text/plain; charset=utf-8")
        elif path == "/api/llm/refresh":
            try:
                import fundos_llm
                payload = get_payload()
                context = {"guide": payload.get("guide"),
                           "news": payload.get("news", []),
                           "news_day": payload.get("news_day"),
                           "portfolio": payload.get("portfolio"),
                           "risk": payload.get("risk")}
                out = fundos_llm.regenerate(context)
                self._send(200, json.dumps(out, ensure_ascii=False),
                           "application/json; charset=utf-8")
            except Exception as exc:  # noqa: BLE001
                self._send(500, json.dumps({"error": str(exc)[:300]}, ensure_ascii=False),
                           "application/json; charset=utf-8")
        elif path == "/":
            try:
                page = (ROOT / "dashboard.html").read_text(encoding="utf-8")
                self._send(200, page, "text/html; charset=utf-8")
            except OSError as exc:
                self._send(500, str(exc), "text/plain; charset=utf-8")
        else:
            self._send(404, "not found", "text/plain; charset=utf-8")

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/api/directive/confirm", "/api/directive/cancel"):
            self._send(404, "not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            key = str(body.get("execution_key", "")).strip()
            title = str(body.get("title", "")).strip()
            rule = str(body.get("rule", "")).strip()
            if not key or not title or not rule or key != _directive_key({"title": title, "rule": rule}):
                raise ValueError("invalid directive")
            if path.endswith("/confirm"):
                with _cache_lock:
                    current = _cache.get("payload") or {}
                live = next((d for d in (current.get("guide", {}).get("directives", []) or [])
                             if d.get("execution_key") == key), None)
                if live and live.get("expired"):
                    raise ValueError("directive expired; refresh guide before confirming")
            with _directive_state_lock:
                state = _load_directive_state()
                previous = state.get(key, {})
                action = "cancelled" if path.endswith("/cancel") else "confirmed"
                now = datetime.now(BJ_TZ).isoformat(timespec="seconds")
                state[key] = {"status": action, "title": title, "rule": rule,
                              "updated_at": now,
                              **({"confirmed_at": previous["confirmed_at"]}
                                 if action == "confirmed" and previous.get("confirmed_at") else {}),
                              **({"cancelled_at": previous["cancelled_at"]}
                                 if action == "cancelled" and previous.get("cancelled_at") else {}),
                              ("cancelled_at" if action == "cancelled" else "confirmed_at"): now}
                _save_directive_state(state)
            with _cache_lock:
                _cache["payload"] = None
                _cache["ts"] = 0
            self._send(200, json.dumps({"ok": True, "execution": state[key]}, ensure_ascii=False),
                       "application/json; charset=utf-8")
        except Exception as exc:
            self._send(400, json.dumps({"ok": False, "error": str(exc)[:200]}, ensure_ascii=False),
                       "application/json; charset=utf-8")


def _lan_ips():
    """本机局域网 IPv4 列表（供手机同一 WiFi 访问）。"""
    import socket
    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))          # 不发数据，仅取本机出口网卡地址
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."):
                ips.add(ip)
    except OSError:
        pass
    return sorted(ips)


def main():
    # 无控制台模式守卫（pythonw 自启动时 stdout/stderr 为 None，print 会崩）
    if sys.stdout is None:
        sys.stdout = open(DATA_DIR / "logs" / "dashboard_stdout.log", "a",
                          encoding="utf-8", buffering=1)
    if sys.stderr is None:
        sys.stderr = sys.stdout
    parser = argparse.ArgumentParser(description="FundOS 可视化面板")
    parser.add_argument("--port", type=int, default=PORT_DEFAULT)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--lan", action="store_true",
                        help="允许手机同一WiFi访问（绑定0.0.0.0，打印局域网地址）")
    args = parser.parse_args()
    host = "0.0.0.0" if args.lan else "127.0.0.1"
    url = f"http://127.0.0.1:{args.port}"
    try:
        server = ThreadingHTTPServer((host, args.port), Handler)
    except OSError as exc:
        if "10048" in str(exc) or "in use" in str(exc).lower():
            # 已有实例在跑（如登录自启动的常驻服务），静默退出即可
            print(f"面板已在运行: {url}")
            return 0
        raise
    print(f"📊 FundOS 可视化面板已启动: {url}  (Ctrl+C 停止)")
    # 预热：服务一起来就在后台算一遍，避免第一个访问者盯着空白页等十几秒
    if _cache["payload"] is None:
        with _cache_lock:
            _cache["refreshing"] = True
        threading.Thread(target=_refresh_payload, daemon=True,
                         name="fundos-prewarm").start()
    if args.lan:
        print("📱 手机访问（需同一 WiFi，微信里打开亦可）:")
        for ip in _lan_ips():
            print(f"    http://{ip}:{args.port}")
        print("    ⚠️ 局域网内任何人可查看，请勿在公共网络使用")
    log = f"[{datetime.now(BJ_TZ):%Y-%m-%d %H:%M:%S %z}] [INFO] 面板启动 {url} (lan={args.lan})"
    try:
        (DATA_DIR / "logs").mkdir(parents=True, exist_ok=True)
        with (DATA_DIR / "logs" / f"auto_{datetime.now(BJ_TZ):%Y-%m-%d}.log").open("a", encoding="utf-8") as fh:
            fh.write(log + "\n")
    except OSError:
        pass
    if not args.no_browser:
        threading.Timer(0.8, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 面板已停止")


if __name__ == "__main__":
    main()
