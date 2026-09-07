#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 统一数据层 v1.0 — Provider 模式 + 重试退避 + 多源回退 + 本地沉淀

设计参考 GitHub 开源方案:
  - akshare / efinance 的"多源数据接口"思想（同一数据多个 provider，主源失败自动回退）
  - OpenBB Platform 的 Provider 架构（统一 schema 输出 + 来源标注）
  - 项目内已有数据契约 fundos.news.v1 / fundos.portfolio.v1

所有函数返回统一 schema 的 dict/list，并带 `source` 字段标注来源；
失败抛出 DataError（不再裸 except 吞错），由上层决定降级策略。
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from fundos_config import (
    NAV_HISTORY_DIR, BOARD_HISTORY_DIR, CACHE_DIR,
    INDEX_MAP, GLOBAL_INDEX_MAP,
)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

EM_HEADERS = {"User-Agent": UA, "Referer": "https://fund.eastmoney.com/"}
SINA_HEADERS = {"User-Agent": UA, "Referer": "https://finance.sina.com.cn/"}


class DataError(RuntimeError):
    """数据源不可用/返回异常。"""


# ============================================================
# HTTP 基础（重试 + 指数退避 + 超时）
# ============================================================
def http_get(url, *, headers=None, timeout=10, retries=3, backoff=1.5, encoding="utf-8"):
    """带重试的 GET。全部重试失败后抛 DataError。"""
    errs = []
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
            body = urllib.request.urlopen(req, timeout=timeout).read()
            return body.decode(encoding, errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            errs.append(f"{type(exc).__name__}: {exc}")
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
    raise DataError(f"GET失败({retries}次) {url} | " + "; ".join(errs[-2:]))


def http_get_json(url, **kw):
    text = http_get(url, **kw)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise DataError(f"非JSON响应 {url} | {text[:120]}") from exc


def _jsonp_payload(text):
    """兼容纯 JSON 与 JSONP 包裹两种响应。"""
    text = text.strip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise DataError(f"JSON解析失败: {text[:120]}") from exc
    try:
        start, end = text.find("("), text.rindex(")")
    except ValueError as exc:
        raise DataError(f"JSONP格式异常: {text[:120]}") from exc
    if start < 0 or end <= start:
        raise DataError(f"JSONP格式异常: {text[:120]}")
    try:
        return json.loads(text[start + 1:end])
    except json.JSONDecodeError as exc:
        raise DataError(f"JSONP内容解析失败: {text[:120]}") from exc


def _disk_cache(key, ttl_sec):
    """极简磁盘缓存：命中返回(数据,True)，未命中返回(None,False)。"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
            if time.time() - blob.get("_ts", 0) < ttl_sec:
                return blob.get("data"), True
        except (json.JSONDecodeError, OSError):
            pass
    return None, False


def _disk_cache_put(key, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{key}.json"
    path.write_text(json.dumps({"_ts": time.time(), "data": data},
                               ensure_ascii=False), encoding="utf-8")


# ============================================================
# Provider 1: 基金净值 — 东方财富 lsjz（主） / pingzhongdata（备）
# ============================================================
def fetch_fund_nav(code, *, use_cache=True):
    """最新净值。统一 schema: {code,date,nav,acc_nav,day_chg,source}"""
    key = f"nav_{code}"
    if use_cache:
        cached, hit = _disk_cache(key, ttl_sec=600)
        if hit:
            return {**cached, "source": cached.get("source") + "(cache)"}
    url = (f"https://api.fund.eastmoney.com/f10/lsjz?fundCode={code}"
           f"&pageIndex=1&pageSize=1")
    try:
        data = _jsonp_payload(http_get(url, headers=EM_HEADERS))
        items = (data.get("Data") or {}).get("LSJZList") or []
        if not items:
            raise DataError(f"{code} lsjz 返回空")
        x = items[0]
        out = {"code": code, "date": x["FSRQ"], "nav": float(x["DWJZ"]),
               "acc_nav": float(x.get("LJJZ") or x["DWJZ"]),
               "day_chg": float(x.get("JZZZL") or 0), "source": "eastmoney.lsjz"}
        _disk_cache_put(key, out)
        return out
    except DataError:
        return _fallback_pingzhong(code, latest_only=True)


def _fallback_pingzhong(code, *, latest_only=True):
    """备源: fund.eastmoney.com/pingzhongdata/{code}.js 的全量净值趋势。"""
    url = f"https://fund.eastmoney.com/pingzhongdata/{code}.js"
    text = http_get(url, headers=EM_HEADERS)
    m = re.search(r"var Data_netWorthTrend = (\[.+?\]);", text, re.DOTALL)
    if not m:
        raise DataError(f"{code} pingzhongdata 无净值趋势")
    rows = json.loads(m.group(1))
    if not rows:
        raise DataError(f"{code} pingzhongdata 空")
    if latest_only:
        last, prev = rows[-1], rows[-2] if len(rows) > 1 else rows[-1]
        day = (last["y"] / prev["y"] - 1) * 100 if prev["y"] else 0
        return {"code": code,
                "date": datetime.fromtimestamp(last["x"] / 1000).strftime("%Y-%m-%d"),
                "nav": float(last["y"]), "acc_nav": float(last.get("equityReturn") or last["y"]),
                "day_chg": round(day, 2), "source": "eastmoney.pingzhongdata"}
    return [{"date": datetime.fromtimestamp(r["x"] / 1000).strftime("%Y-%m-%d"),
             "nav": float(r["y"])} for r in rows if r.get("y")]


def fetch_fund_nav_history(code, days=120, *, use_cache=True):
    """净值历史（升序）。本地沉淀【全量】历史，按请求的 days 在读取时过滤。
    （v1.1 修复: 旧版把 days 过滤后的结果写回缓存，小窗口调用会截短沉淀数据）"""
    NAV_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = NAV_HISTORY_DIR / f"{code}.json"
    local_all = []
    if path.exists():
        try:
            local_all = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            local_all = []
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    local = [r for r in local_all if r["date"] >= cutoff and r["nav"] > 0]
    if local and use_cache:
        newest = max(r["date"] for r in local)
        if newest >= datetime.now().strftime("%Y-%m-%d"):
            return local
    # 补拉：lsjz 分页(每页49)，最多6页 ≈ 1年，覆盖 120+ 交易日
    fetched = {}
    try:
        for page in range(1, 7):
            url = (f"https://api.fund.eastmoney.com/f10/lsjz?fundCode={code}"
                   f"&pageIndex={page}&pageSize=49")
            data = _jsonp_payload(http_get(url, headers=EM_HEADERS))
            items = (data.get("Data") or {}).get("LSJZList") or []
            if not items:
                break
            for it in items:
                fetched[it["FSRQ"]] = float(it["DWJZ"])
            if items[-1]["FSRQ"] < cutoff:
                break
            time.sleep(0.25)
    except DataError:
        # 备源链: pingzhongdata → akshare（第二外部源，安装后才可用）
        for backup in (lambda: _fallback_pingzhong(code, latest_only=False),
                       lambda: _akshare_nav_history(code, days)):
            try:
                for r in backup():
                    fetched[r["date"]] = r["nav"]
                if fetched:
                    break
            except DataError:
                continue
    if not fetched and not local:
        raise DataError(f"{code} 净值历史完全不可用")
    merged = {r["date"]: r["nav"] for r in local_all}
    merged.update(fetched)
    full = [{"date": d, "nav": v} for d, v in sorted(merged.items()) if v > 0]
    if fetched:
        path.write_text(json.dumps(full, ensure_ascii=False), encoding="utf-8")
    return [r for r in full if r["date"] >= cutoff]


# ============================================================
# Provider 2: 指数行情 — 新浪（A股 / 全球）
# ============================================================
def fetch_indices(codes=None, *, use_cache=True):
    """A股指数实时。返回 {code: {name,price,prev_close,chg_pct,open,high,low}}"""
    codes = list(codes or INDEX_MAP.keys())
    key = "idx_" + "_".join(codes)
    if use_cache:
        cached, hit = _disk_cache(key, ttl_sec=60)
        if hit:
            return cached
    url = f"https://hq.sinajs.cn/list={','.join(codes)}"
    text = http_get(url, headers=SINA_HEADERS, encoding="gbk")
    out = {}
    for line in text.strip().splitlines():
        if "hq_str_" not in line or '"' not in line:
            continue
        code = line.split("var hq_str_")[1].split("=")[0]
        fields = line.split('"')[1].split(",")
        if len(fields) < 6 or not fields[3]:
            continue
        try:
            price, prev = float(fields[3]), float(fields[2])
            out[code] = {"name": INDEX_MAP.get(code, code), "price": price,
                         "prev_close": prev,
                         "chg_pct": (price - prev) / prev * 100 if prev else 0,
                         "open": float(fields[1]), "high": float(fields[4]),
                         "low": float(fields[5])}
        except (ValueError, IndexError):
            continue
    if not out:
        raise DataError("新浪A股指数无有效数据")
    _disk_cache_put(key, out)
    return out


def fetch_global_indices(codes=None, *, use_cache=True):
    """全球指数（美股/港股/日经）。返回 {code: {name,price,chg_pct}}
    注意：美股盘中价格为实时，收盘后为最近一个交易日收盘。"""
    codes = list(codes or GLOBAL_INDEX_MAP.keys())
    key = "gidx_" + "_".join(codes).replace("$", "")
    if use_cache:
        cached, hit = _disk_cache(key, ttl_sec=60)
        if hit:
            return cached
    url = f"https://hq.sinajs.cn/list={','.join(codes)}"
    text = http_get(url, headers=SINA_HEADERS, encoding="gbk")
    out = {}
    for line in text.strip().splitlines():
        if "hq_str_" not in line or '"' not in line:
            continue
        code = line.split("var hq_str_")[1].split("=")[0]
        fields = line.split('"')[1].split(",")
        # 全球指数格式: 名称,最新价,涨跌幅%,...
        if len(fields) < 3 or not fields[1]:
            continue
        try:
            out[code] = {"name": GLOBAL_INDEX_MAP.get(code, code),
                         "price": float(fields[1]),
                         "chg_pct": float(fields[2]) if fields[2] else 0}
        except (ValueError, IndexError):
            continue
    if not out:
        raise DataError("新浪全球指数无有效数据")
    _disk_cache_put(key, out)
    return out


# ============================================================
# Provider 4: 外汇 — 新浪（QDII 估值汇率因子）
# ============================================================
FX_MAP = {"fx_susdcnh": "离岸人民币", "fx_susdcny": "在岸人民币"}


def fetch_fx(code="fx_susdcnh", *, use_cache=True):
    """汇率行情。返回 {code,name,price,chg_pct}。新浪格式: 时间,买,卖,昨收,量,开,高,低,最新,名称,..."""
    key = f"fx_{code}"
    if use_cache:
        cached, hit = _disk_cache(key, ttl_sec=60)
        if hit:
            return cached
    url = f"https://hq.sinajs.cn/list={code}"
    text = http_get(url, headers=SINA_HEADERS, encoding="gbk")
    out = {}
    for line in text.strip().splitlines():
        if "hq_str_" not in line or '"' not in line:
            continue
        c = line.split("var hq_str_")[1].split("=")[0]
        f = line.split('"')[1].split(",")
        if len(f) < 9 or not f[8] or not f[3]:
            continue
        try:
            price, prev = float(f[8]), float(f[3])
            out[c] = {"name": FX_MAP.get(c, c), "price": price,
                      "chg_pct": (price / prev - 1) * 100 if prev else 0}
        except (ValueError, IndexError):
            continue
    if not out:
        raise DataError(f"汇率 {code} 无有效数据")
    result = out[code] if code in out else next(iter(out.values()))
    _disk_cache_put(key, result)
    return result


# ============================================================
# 可选 Provider: akshare 适配器（未安装时自动跳过，不引入强依赖）
# 启用: pip install akshare  →  净值历史的第二外部源
# ============================================================
def _akshare_nav_history(code, days=120):
    """akshare 基金净值历史（安装 akshare 后可用；失败抛 DataError）。"""
    try:
        import akshare as ak
    except ImportError:
        raise DataError("akshare 未安装")
    try:
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=days + 10)).strftime("%Y-%m-%d")
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势",
                                       period="成立来")
        rows = []
        for _, r in df.iterrows():
            d = str(r.get("净值日期", ""))
            v = r.get("单位净值")
            if d and v and str(d) >= start:
                rows.append({"date": d[:10], "nav": float(v)})
        if not rows:
            raise DataError(f"akshare {code} 无数据")
        return sorted(rows, key=lambda r: r["date"])
    except DataError:
        raise
    except Exception as exc:  # akshare 接口变动较多，包一层
        raise DataError(f"akshare 失败: {type(exc).__name__}: {exc}") from exc


# ============================================================
# Provider 3: 板块扫描 — 新浪行业 + 概念
# ============================================================
def _fetch_boards(url):
    text = http_get(url, encoding="gbk", retries=2)
    start, end = text.find("{"), text.rindex("}") + 1
    data = json.loads(text[start:end])
    out = []
    for _, v in data.items():
        p = v.split(",")
        if len(p) < 13:
            continue
        try:
            out.append({"code": p[0], "name": p[1], "count": int(p[2]),
                        "avg_chg": float(p[4]), "chg_pct": float(p[5]),
                        "amount": float(p[6]) / 1e8,
                        "leader": p[12], "leader_chg": float(p[9])})
        except (ValueError, IndexError):
            continue
    return out


def fetch_sector_boards(*, use_cache=True):
    """全市场行业+概念板块。返回 (industries, concepts)。"""
    key = "boards"
    if use_cache:
        cached, hit = _disk_cache(key, ttl_sec=300)
        if hit:
            return cached["industries"], cached["concepts"]
    industries = _fetch_boards("https://vip.stock.finance.sina.com.cn/q/view/newSinaHy.php")
    concepts = _fetch_boards("https://vip.stock.finance.sina.com.cn/q/view/newFLJK.php?param=class")
    if not industries and not concepts:
        raise DataError("新浪板块接口无有效数据")
    _disk_cache_put(key, {"industries": industries, "concepts": concepts})
    return industries, concepts


def save_board_snapshot(industries, concepts):
    """当日板块快照落盘，供主线连续性(轮动)对比。"""
    BOARD_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = BOARD_HISTORY_DIR / f"{today}.json"
    blob = {
        "date": today, "saved_at": datetime.now().isoformat(timespec="seconds"),
        "industries": industries, "concepts": concepts,
    }
    path.write_text(json.dumps(blob, ensure_ascii=False), encoding="utf-8")
    return path


def load_board_history(limit=5):
    """最近N天板块快照（日期升序）。"""
    if not BOARD_HISTORY_DIR.exists():
        return []
    snaps = []
    for p in sorted(BOARD_HISTORY_DIR.glob("*.json"))[-limit:]:
        try:
            snaps.append(json.loads(p.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return snaps


def board_momentum(history, name, top_n=15):
    """板块N日排名序列: [{date, chg_pct, rank, in_top, amount}]，缺日返回已有部分。"""
    series = []
    for snap in history:
        boards = sorted(snap.get("industries", []) + snap.get("concepts", []),
                        key=lambda x: x.get("chg_pct", 0), reverse=True)
        rank = next((i + 1 for i, b in enumerate(boards) if b.get("name") == name), None)
        chg = next((b.get("chg_pct") for b in boards if b.get("name") == name), None)
        amount = next((b.get("amount") for b in boards if b.get("name") == name), None)
        if rank is not None:
            series.append({"date": snap["date"], "chg_pct": chg, "rank": rank,
                           "in_top": rank <= top_n, "amount": amount})
    return series


def rotation_score(history, name, top_n=15):
    """主线轮动得分 0-100: 连续在榜(50) + 排名改善(30) + 成交趋势(20)。
    历史不足2天时 score=None（数据积累期）。"""
    series = board_momentum(history, name, top_n)
    if not series:
        return {"score": None, "days": 0, "note": "未上榜"}
    if len(series) < 2:
        return {"score": None, "days": len(series),
                "note": f"板块历史积累中({len(series)}/2天)"}
    latest, prev = series[-1], series[-2]
    streak = 0
    for s in reversed(series):
        if s["in_top"]:
            streak += 1
        else:
            break
    streak_part = 50 * min(streak, 5) / 5
    rank_imp = (prev["rank"] - latest["rank"]) / 30.0        # 升30名内线性
    rank_part = 30 * max(-1.0, min(1.0, rank_imp))
    prior_amounts = [s["amount"] for s in series[:-1] if s.get("amount")]
    if prior_amounts and latest.get("amount"):
        ratio = latest["amount"] / (sum(prior_amounts) / len(prior_amounts))
        amount_part = 20 if ratio > 1.1 else (10 if ratio > 0.9 else 0)
    else:
        amount_part = 10
    return {"score": round(streak_part + rank_part + amount_part, 1),
            "days": len(series), "streak": streak,
            "rank_now": latest["rank"], "rank_prev": prev["rank"],
            "chg_pct": latest["chg_pct"]}
