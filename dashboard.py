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
import json
import sys
import threading
import webbrowser
from datetime import datetime
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
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
    DAILY_RESULT, NEWS_JSON, DATA_DIR, FUND_META,
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
_cache = {"ts": 0.0, "payload": None}
_cache_lock = threading.Lock()
_live = {"ts": 0.0, "news": [], "news_ok": False}   # 新闻直连缓存
_live_lock = threading.Lock()

BOARD_DIR = DATA_DIR / "board_history"
SENTIMENT_DIR = DATA_DIR / "sentiment_history"


# ============================================================
# 数据聚合（全部复用现有引擎与缓存）
# ============================================================
def collect():
    """聚合面板数据。任何子模块失败都不拖垮整体（优雅降级为缺省块）。"""
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    payload = {"updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
               "snapshot_meta": {"source": "local_computer",
                                  "generated_at": now.isoformat(timespec="seconds"),
                                  "timezone": "Asia/Shanghai",
                                  "status": "success"}}

    # ---- 持仓 + 指数 + 今日估算（fundos_core，净值带10分钟缓存）----
    try:
        snap_date, funds = fundos_core.load_snapshot()
        indices = fundos_core.fetch_indices()
        proxies, fx_chg = fundos_core.fetch_qdii_proxies()
        manual = {}
        manual_path = ROOT / "manual_updates.json"
        if manual_path.exists():
            manual = json.loads(manual_path.read_text(encoding="utf-8")) \
                .get("updates", {}).get(datetime.now().strftime("%Y-%m-%d"), {})
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
        payload["holdings"] = [{
            "name": f["name"], "code": f["code"], "sector": f.get("sector", ""),
            "value": round(f.get("value", 0), 2), "weight": round(f.get("weight", 0), 1),
            "ret_pct": round(f.get("ret_pct", 0), 2),
            "return": round(f.get("return", 0), 2),
            "nav_date": f.get("nav_date", "-"),
            "nav_day_chg": f.get("nav_day_chg", 0),
            "today_est": round(f.get("today_est", 0), 2),
            "today_source": f.get("today_source", ""),
            "freshness": "估算" if f.get("today_source") not in ("", "QDII滞后") else "已公布净值",
        } for f in funds]
        payload["indices"] = [{"name": v["name"], "price": v["price"],
                               "chg_pct": round(v["chg_pct"], 2)}
                              for v in indices.values()]
        payload["global_indices"] = [{"name": v["name"], "price": v["price"],
                                      "chg_pct": round(v["chg_pct"], 2)}
                                     for v in proxies.values()]
    except Exception as exc:  # noqa: BLE001 — 面板不能崩
        payload["error_core"] = str(exc)[:200]
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
    except Exception as exc:  # noqa: BLE001
        payload["error_analytics"] = str(exc)[:200]

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

    # ---- 板块榜（实时抓取，fundos_data 自带5分钟缓存防爬） ----
    try:
        ind, con = fundos_data.fetch_sector_boards()
        ind = sorted(ind, key=lambda x: x.get("chg_pct", 0), reverse=True)
        con = sorted(con, key=lambda x: x.get("chg_pct", 0), reverse=True)
        payload["boards"] = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "industries": [{"name": b["name"], "chg_pct": round(b["chg_pct"], 2),
                            "amount": round(b.get("amount", 0), 1)} for b in ind[:10]],
            "concepts": [{"name": b["name"], "chg_pct": round(b["chg_pct"], 2)} for b in con[:10]],
        }
    except Exception as exc:  # noqa: BLE001
        payload["error_boards"] = str(exc)[:200]

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
            news_time = datetime.now().strftime("%m-%d %H:%M")
        else:
            news_items = news.get("news", [])
            news_time = (news.get("collected_at") or "")[5:16].replace("T", " ")
    payload["news_live"] = live_ok
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
    except Exception as exc:  # noqa: BLE001
        payload["error_guide"] = str(exc)[:200]

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


def _load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def get_payload():
    """带 TTL 的聚合缓存：面板高频刷新时几乎零开销。"""
    import time
    with _cache_lock:
        if _cache["payload"] is None or time.time() - _cache["ts"] > DATA_TTL:
            try:
                _cache["payload"] = collect()
            except Exception as exc:  # noqa: BLE001
                _cache["payload"] = {"error": str(exc)[:300],
                                     "updated_at": datetime.now().isoformat()}
            _cache["ts"] = time.time()
        return _cache["payload"]


# ============================================================
# 页面模板（ECharts CDN：npmmirror 主源 + jsdelivr 备源）
# ============================================================
HTML = (ROOT / "dashboard.html").read_text(encoding="utf-8")


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
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/data":
            try:
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
            self._send(200, HTML, "text/html; charset=utf-8")
        else:
            self._send(404, "not found", "text/plain; charset=utf-8")


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
    if args.lan:
        print("📱 手机访问（需同一 WiFi，微信里打开亦可）:")
        for ip in _lan_ips():
            print(f"    http://{ip}:{args.port}")
        print("    ⚠️ 局域网内任何人可查看，请勿在公共网络使用")
    log = f"[{datetime.now():%H:%M:%S}] [INFO] 面板启动 {url} (lan={args.lan})"
    try:
        (DATA_DIR / "logs").mkdir(parents=True, exist_ok=True)
        with (DATA_DIR / "logs" / f"auto_{datetime.now():%Y-%m-%d}.log").open("a", encoding="utf-8") as fh:
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
