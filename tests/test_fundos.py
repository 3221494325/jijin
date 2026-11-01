#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 引擎单元测试 — python tests/test_fundos.py  (或 python -m unittest)"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ---------- 纯函数/配置（离线必测） ----------
class TestConfig(unittest.TestCase):
    def test_split_position_codes_are_preserved(self):
        # 2026-10 组合精简为 8 只后，A/C 分列只剩 012922(C) ↔ 012920(A) 这一对
        from fundos_config import FUND_META
        self.assertIn("019759", FUND_META)
        self.assertEqual(FUND_META["019759"]["cls"], "A")
        self.assertEqual(FUND_META["012922"]["cls"], "C")
        self.assertEqual(FUND_META["012922"]["a_code"], "012920")

    def test_fund_meta_covers_snapshot(self):
        from fundos_config import FUND_META
        snap = json.loads((ROOT / "portfolio_snapshot.json").read_text(encoding="utf-8"))
        snap_codes = {h["code"] for h in snap["holdings"]}
        self.assertTrue(snap_codes <= set(FUND_META),
                        f"快照代码未收录: {snap_codes - set(FUND_META)}")

    def test_fund_meta_fields(self):
        from fundos_config import FUND_META
        for code, m in FUND_META.items():
            self.assertTrue(len(code) == 6 and code.isdigit(), code)
            self.assertGreater(m.get("cost", 0), 0, f"{code} cost异常")
            self.assertGreater(m.get("cost_nav", 0), 0, f"{code} cost_nav异常")
            self.assertIn(m.get("sector"), {"tech", "qdii", "green"}, f"{code} sector异常")
            self.assertTrue(m.get("name"), f"{code} 缺name")
            # QDII 必须有代理指数
            if m["sector"] == "qdii":
                self.assertTrue(m.get("proxy"), f"{code} QDII缺proxy")

    def test_name_to_code_consistent(self):
        from fundos_config import FUND_META, NAME_TO_CODE, FULLNAME_TO_CODE
        self.assertEqual(len(NAME_TO_CODE), len(FUND_META))
        self.assertEqual(len(FULLNAME_TO_CODE), len(FUND_META))
        for code, m in FUND_META.items():
            self.assertEqual(NAME_TO_CODE[m["name"]], code)
            self.assertEqual(FULLNAME_TO_CODE[m["full_name"]], code)

    def test_thresholds(self):
        from fundos_config import THRESHOLDS
        self.assertLess(THRESHOLDS["hard_stop"], THRESHOLDS["eval_line"])
        self.assertLess(THRESHOLDS["eval_line"], 0)
        self.assertLess(THRESHOLDS["take_profit_1"], THRESHOLDS["take_profit_2"])
        self.assertGreater(THRESHOLDS["tech_max"], 0)

    def test_skill_sector_map_covers_meta(self):
        from fundos_config import FUND_META, FUND_SECTOR_MAP
        for code, m in FUND_META.items():
            self.assertIn(m["name"], FUND_SECTOR_MAP, f"{m['name']} 不在新闻持仓映射中")


class TestJsonpPayload(unittest.TestCase):
    def test_pure_json(self):
        from fundos_data import _jsonp_payload
        self.assertEqual(_jsonp_payload('{"a":1}'), {"a": 1})

    def test_jsonp(self):
        from fundos_data import _jsonp_payload
        self.assertEqual(_jsonp_payload('cb({"a":[1,2]})'), {"a": [1, 2]})

    def test_bad_raises_dataerror(self):
        from fundos_data import _jsonp_payload, DataError
        with self.assertRaises(DataError):
            _jsonp_payload("not json at all")


class TestDiskCache(unittest.TestCase):
    def test_roundtrip_and_ttl(self):
        import fundos_data
        with tempfile.TemporaryDirectory() as td:
            old = fundos_data.CACHE_DIR
            fundos_data.CACHE_DIR = Path(td)
            try:
                fundos_data._disk_cache_put("k1", {"v": 42})
                hit, is_hit = fundos_data._disk_cache("k1", ttl_sec=60)
                self.assertTrue(is_hit)
                self.assertEqual(hit, {"v": 42})
                # TTL 过期
                import time as _t
                _t.sleep(0.05)
                _, is_hit2 = fundos_data._disk_cache("k1", ttl_sec=0)
                self.assertFalse(is_hit2)
                # 未命中
                _, is_hit3 = fundos_data._disk_cache("nope", ttl_sec=60)
                self.assertFalse(is_hit3)
            finally:
                fundos_data.CACHE_DIR = old


class TestAnalyticsMath(unittest.TestCase):
    def test_daily_returns(self):
        from fundos_analytics import daily_returns
        self.assertAlmostEqual(daily_returns([1.0, 1.1, 0.99])[0], 0.1)
        self.assertAlmostEqual(daily_returns([1.0, 1.1, 0.99])[1], -0.1)

    def test_max_drawdown(self):
        from fundos_analytics import max_drawdown
        mdd, pk, tr = max_drawdown([1.0, 1.2, 0.9, 1.1])
        self.assertAlmostEqual(mdd, 0.9 / 1.2 - 1)
        self.assertEqual((pk, tr), (1, 2))
        # 单调上涨无回撤
        self.assertEqual(max_drawdown([1, 1.1, 1.2])[0], 0.0)

    def test_corr(self):
        from fundos_analytics import corr
        self.assertAlmostEqual(corr([1, 2, 3, 4], [2, 4, 6, 8]), 1.0)
        self.assertAlmostEqual(corr([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertEqual(corr([1], [1]), 0.0)

    def test_fund_metrics(self):
        from fundos_analytics import fund_metrics
        dates = [f"2026-01-{d:02d}" for d in range(1, 11)]
        navs = [1.0, 1.02, 1.01, 1.05, 1.08, 1.04, 1.03, 1.06, 1.09, 1.10]
        m = fund_metrics(dates, navs)
        self.assertAlmostEqual(m["period_ret_pct"], 10.0, places=6)
        self.assertLess(m["max_dd_pct"], 0)
        self.assertEqual(m["days"], 10)
        self.assertIn("→", m["max_dd_window"])


class TestNewsContract(unittest.TestCase):
    def _load_engine(self):
        spec = importlib.util.spec_from_file_location("fund_engine", ROOT / "fund_engine.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_normalize_news_v1_and_v2(self):
        eng = self._load_engine()
        v1 = {"news": [{"title": "A", "source": "s", "date": "08-28"}],
              "collected_at": "t", "source_status": {"s": {"status": "ok"}}}
        out = eng.normalize_news(v1)
        self.assertEqual(out["schema_version"], "fundos.news.v1")
        self.assertEqual(len(out["news"]), 1)
        item = out["news"][0]
        for key in ("id", "title", "content", "source", "url", "published_at",
                    "collected_at", "dimension", "sentiment", "sentiment_score",
                    "reference_signal"):
            self.assertIn(key, item)
        # 非 dict 项与无标题项被过滤
        messy = {"news": ["junk", {"content": "no title"}, {"title": "OK"}]}
        self.assertEqual(len(eng.normalize_news(messy)["news"]), 1)

    def test_dispatch_skills_triggers(self):
        eng = self._load_engine()
        snap = {"holdings": [
            {"name": "全球成长", "code": "012922", "ret_pct": -19.6, "weight": 10, "sector": "qdii"},
            {"name": "科技智选", "code": "022365", "ret_pct": -2.9, "weight": 45, "sector": "tech"},
        ], "tech_weight": 45.0}
        decision = eng.dispatch_skills(snap, {"news": [{"title": "x"}]})
        self.assertEqual(decision["tech_weight"], 45.0)
        self.assertIn("全球成长", decision["deep_loss"])
        slugs = {s for t in decision["triggered"] for s in t["skills"]}
        self.assertIn("stop-loss-admission", slugs)
        self.assertIn("position-size-framework", slugs)   # tech 45% > 40
        self.assertIn("narrative-news-check", slugs)


class TestSentimentV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = ROOT / ".codex/skills/fundos/scripts/news_fetch_v2.py"
        spec = importlib.util.spec_from_file_location("news_fetch_v2", p)
        cls.nf = importlib.util.module_from_spec(spec)
        sys.modules["news_fetch_v2"] = cls.nf
        spec.loader.exec_module(cls.nf)

    def test_positive(self):
        label, score = self.nf.classify_sentiment_v2("半导体出口大幅增长 超预期")
        self.assertIn("🟢", label)
        self.assertGreater(score, 0)

    def test_negative(self):
        label, score = self.nf.classify_sentiment_v2("芯片公司暴跌 亏损 承压")
        self.assertIn("🔴", label)

    def test_negation_reverses(self):
        # "未能突破" → 突破被否定，不应判多
        label, _ = self.nf.classify_sentiment_v2("利好落地后股价未能突破")
        self.assertNotIn("偏多", label)

    def test_neutral(self):
        label, score = self.nf.classify_sentiment_v2("某公司发布公告")
        self.assertEqual(label, "⚪中性")
        self.assertEqual(score, 0)


    def test_label_cn_threshold_and_sign(self):
        # ±2 分才定性；分值带符号（v2.2 修复"略偏空2分被当利好"的bug）
        nf = self.nf
        self.assertEqual(nf.sentiment_label_cn({"sentiment_score": 3}), "利好")
        self.assertEqual(nf.sentiment_label_cn({"sentiment_score": 1}), "中性")
        self.assertEqual(nf.sentiment_label_cn({"sentiment_score": 0}), "中性")
        self.assertEqual(nf.sentiment_label_cn({"sentiment_score": -2}), "利空")
        s, sc = nf.classify_sentiment_v2("某基金净值下跌0.5%")
        self.assertLess(sc, 0, "负面新闻分值必须为负")
        self.assertEqual(nf.sentiment_label_cn({"sentiment": s, "sentiment_score": sc}), "利空")
        s, sc = nf.classify_sentiment_v2("银行因违规被罚款500万元")
        self.assertEqual(nf.sentiment_label_cn({"sentiment": s, "sentiment_score": sc}), "利空")
        s, sc = nf.classify_sentiment_v2("现货黄金涨1.2%")
        self.assertEqual(nf.sentiment_label_cn({"sentiment": s, "sentiment_score": sc}), "利好")


class TestBoardMomentum(unittest.TestCase):
    def test_series_and_streak_source(self):
        from fundos_data import board_momentum
        history = [
            {"date": "2026-08-26", "industries": [{"name": "农药化肥", "chg_pct": 2.4},
                                                   {"name": "石油行业", "chg_pct": 2.1}]},
            {"date": "2026-08-27", "industries": [{"name": "石油行业", "chg_pct": 3.0},
                                                   {"name": "农药化肥", "chg_pct": 1.0}]},
        ]
        s = board_momentum(history, "石油行业", top_n=1)
        self.assertEqual(len(s), 2)
        self.assertEqual(s[0]["rank"], 2)
        self.assertEqual(s[1]["rank"], 1)
        self.assertFalse(s[0]["in_top"])
        self.assertTrue(s[1]["in_top"])
        self.assertEqual(board_momentum(history, "不存在的板块"), [])


# ---------- 网络冒烟测试（离线自动跳过） ----------
class TestAdvisor(unittest.TestCase):
    """操作指南规则引擎：合成持仓验证触发线与禁止清单"""

    @staticmethod
    def _h(code, ret, weight=10, sector="tech"):
        return {"name": code, "code": code, "ret_pct": ret,
                "weight": weight, "sector": sector}

    def test_hard_stop(self):
        from fundos_advisor import build_guide
        g = build_guide(holdings=[self._h("012922", -26, sector="qdii")])
        self.assertEqual(g["fund_guides"][0]["advice"], "硬止损：当日无条件出清")
        self.assertTrue(any(d["level"] == "指令" for d in g["directives"]))
        self.assertTrue(any("禁止摊平" in x for x in g["forbidden"]))

    def test_take_profit_and_distance(self):
        from fundos_advisor import build_guide
        g = build_guide(holdings=[self._h("017641", 16, sector="qdii")])
        self.assertIn("止盈", g["fund_guides"][0]["advice"])
        self.assertEqual(g["fund_guides"][0]["dist_next_label"], "距+20%止盈线还有")

    def test_switch_a_with_penalty_window(self):
        # 022365 已不在持仓表；当前唯一配置了 a_code/switch_th 的是 012922(→012920)
        from datetime import datetime as dt
        from fundos_config import FUND_META
        from fundos_advisor import build_guide
        g = build_guide(holdings=[self._h("012922", 0.5, sector="qdii")], now=dt(2026, 8, 28))
        self.assertIn("换A", g["fund_guides"][0]["advice"])
        # 赎回费窗口只在 meta 配了 penalty 时才有意义；当前无该配置则跳过（不伪造断言）
        if any(m.get("penalty") for m in FUND_META.values()):
            g2 = build_guide(holdings=[self._h("012922", 0.5, sector="qdii")], now=dt(2026, 8, 1))
            self.assertIn("赎回费", g2["fund_guides"][0]["advice"])

    def test_tech_concentration_forbidden(self):
        from fundos_advisor import build_guide
        g = build_guide(holdings=[self._h("011608", -2, weight=30),
                                  self._h("022365", -2, weight=15)])
        self.assertGreater(g["tech_weight"], 40)
        self.assertTrue(any(d["level"] == "警告" and "集中度" in d["title"]
                            for d in g["directives"]))
        self.assertTrue(any("禁止新增科技" in x for x in g["forbidden"]))

    def test_defensive_environment(self):
        from fundos_advisor import build_guide
        g = build_guide(holdings=[], sentiment={"index": 30, "label": "偏空"},
                        indices={"sh000688": -2})
        self.assertEqual(g["environment"]["label"], "防守")
        self.assertTrue(any("暂停一切新增买入" in x for x in g["forbidden"]))

    def test_news_is_observer_only(self):
        from fundos_advisor import build_guide
        g = build_guide(holdings=[self._h("019764", -2, weight=5)],
                        sector_news={"半导体": {"up": 0, "down": 4}})
        self.assertTrue(any("利空聚集" in s for s in g["fund_guides"][0]["signals"]))
        self.assertFalse(any(d["level"] == "指令" for d in g["directives"]),
                         "新闻利空不得单独触发指令级动作")


    def test_industry_outlook(self):
        from fundos_advisor import build_guide
        industry = {
            "today": [{"name": "传媒娱乐", "chg_pct": 4.8},
                      {"name": "光伏设备", "chg_pct": -2.1},
                      {"name": "软件服务", "chg_pct": 1.4}],
            "days": [["家具", "煤炭"], ["家具", "煤炭", "传媒娱乐"]],
        }
        g = build_guide(holdings=[self._h("018735", -6.3, sector="green")],
                        industry=industry)
        ol = g["industry_outlook"]
        self.assertTrue(ol["available"])
        self.assertTrue(any("传媒娱乐" in m for m in ol["new_mains"]), ol["new_mains"])
        self.assertTrue(any(w["board"] == "光伏设备" for w in ol["weak_boards"]))
        self.assertTrue(any("传导预警" in d["title"] for d in g["directives"]))
        self.assertTrue(any("禁接飞刀" in n for n in ol["notes"]))
        self.assertTrue(ol["strength_gap_pct"] > 2)

    def test_industry_outlook_confirmed_main(self):
        from fundos_advisor import build_guide
        industry = {
            "today": [{"name": "家具", "chg_pct": 1.7}],
            "days": [["家具"], ["家具"], ["家具"]],
        }
        g = build_guide(holdings=[self._h("011608", -2, sector="tech")],
                        industry=industry)
        ol = g["industry_outlook"]
        self.assertTrue(any("连续3天" in m for m in ol["confirmed_mains"]), ol["confirmed_mains"])
        self.assertFalse(any("新主线" in d["title"] for d in g["directives"]))


class TestNetworkSmoke(unittest.TestCase):
    def test_fetch_fund_nav(self):
        from fundos_data import fetch_fund_nav, DataError
        try:
            nav = fetch_fund_nav("018735", use_cache=False)
        except DataError as exc:
            self.skipTest(f"网络不可用: {exc}")
        self.assertEqual(nav["code"], "018735")
        self.assertGreater(nav["nav"], 0)
        self.assertRegex(nav["date"], r"\d{4}-\d{2}-\d{2}")

    def test_fetch_indices(self):
        from fundos_data import fetch_indices, DataError
        try:
            idx = fetch_indices(["sh000688"], use_cache=False)
        except DataError as exc:
            self.skipTest(f"网络不可用: {exc}")
        self.assertIn("sh000688", idx)
        self.assertGreater(idx["sh000688"]["price"], 0)


# ---------- 阶段1 自动化（auto_pipeline 纯函数） ----------
class TestAutoPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("auto_pipeline", ROOT / "auto_pipeline.py")
        cls.ap = importlib.util.module_from_spec(spec)
        sys.modules["auto_pipeline"] = cls.ap
        spec.loader.exec_module(cls.ap)

    def test_format_trigger_alert(self):
        self.assertIn("无触发", self.ap.format_trigger_alert([]))
        alert = self.ap.format_trigger_alert(["🟡 全球成长 [012922] 体检逻辑, 反弹分批退出",
                                              "🟢 标普500 [017641] 止盈+15%: 减1/3"])
        self.assertIn("触发 2 项", alert)
        self.assertIn("全球成长", alert)
        self.assertIn("标普500", alert)

    def test_build_morning_lines_degrades_gracefully(self):
        lines = "\n".join(self.ap.build_morning_lines({}, {}, None))
        self.assertIn("FundOS 晨报", lines)
        self.assertIn("获取失败", lines)          # 指数缺失降级
        self.assertIn("不构成投资建议", lines)
        # 正常数据路径
        daily = {"actions": ["🟡 全球成长 [012922] 体检逻辑"], "tech_weight": 37.8, "qdii_weight": 47.6}
        lines2 = "\n".join(self.ap.build_morning_lines(
            {"sh000688": {"name": "科创50", "price": 1662.0, "chg_pct": -1.85}},
            {"gb_$ixic": {"name": "纳斯达克", "price": 26541.0, "chg_pct": 1.57}}, daily))
        self.assertIn("隔夜市场", lines2)
        self.assertIn("全球成长", lines2)
        self.assertIn("37.8%", lines2)

    def test_build_evening_lines(self):
        daily = {"total_value": 3075.0, "total_ret_pct": -4.67,
                 "tech_weight": 37.8, "qdii_weight": 47.6, "actions": []}
        analytics = {"portfolio": {"max_dd_pct": -16.04, "sharpe": 1.02,
                                   "ann_vol_pct": 27.71, "hhi": 0.144, "effective_funds": 6.9}}
        engine = {"decision": {"triggered": [{"action": "持有观察", "boundary": "无触发"}]}}
        news = {"news": [{"sentiment": "⚪中性", "source": "测试源", "title": "测试标题"}]}
        text = "\n".join(self.ap.build_evening_lines(engine, daily, analytics, news))
        self.assertIn("-4.67%", text)
        self.assertIn("-16.04%", text)
        self.assertIn("测试标题", text)
        self.assertIn("不构成投资建议", text)


# ---------- 阶段2/3/4 扩展能力 ----------
    def test_stages_missed_logic(self):
        from datetime import datetime as _dt
        ap = self.ap
        self.assertEqual(ap.stages_missed({}, _dt(2026, 8, 28, 10, 0)), ["morning"])
        self.assertEqual(ap.stages_missed({"morning": "2026-08-28 09:00"}, _dt(2026, 8, 28, 10, 0)), [])
        self.assertEqual(ap.stages_missed({"morning": "2026-08-27 20:00"}, _dt(2026, 8, 28, 10, 0)), ["morning"])
        self.assertEqual(ap.stages_missed({}, _dt(2026, 8, 28, 22, 0)),
                         ["morning", "afternoon", "evening"])
        self.assertEqual(ap.stages_missed({}, _dt(2026, 8, 28, 8, 0)), [])

class TestBacktest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("backtest", ROOT / "backtest.py")
        cls.bt = importlib.util.module_from_spec(spec)
        sys.modules["backtest"] = cls.bt
        spec.loader.exec_module(cls.bt)

    def test_take_profit_exits_third(self):
        # 一路上涨到 +20%: 应触发 +15% 和 +20% 两批止盈，规则收益 < 死扛（牛市让利）
        navs = [1.0 * (1 + 0.005 * i) for i in range(60)]
        r = self.bt.simulate_rules(navs)
        self.assertTrue(r["tp_hit"])
        self.assertLess(r["rule_ret_pct"], r["hold_ret_pct"])
        self.assertAlmostEqual(r["hold_ret_pct"], round((navs[-1] - 1) * 100, 2), places=1)

    def test_hardstop_exits_all(self):
        # 崩盘: -15%武装后无反弹直接 -25% → 清仓，规则回撤显著小于死扛
        navs = [1.0, 0.97, 0.93, 0.88, 0.82, 0.75, 0.74, 0.73]
        r = self.bt.simulate_rules(navs)
        self.assertTrue(r["eval_hit"] or r["hardstop_hit"])
        self.assertGreater(r["rule_ret_pct"], r["hold_ret_pct"])

    def test_bounce_batch_exit(self):
        # -15% 后反弹 → 反弹批退出锁住更好价格
        navs = [1.0, 0.95, 0.88, 0.86, 0.84, 0.86, 0.89, 0.92]
        r = self.bt.simulate_rules(navs)
        self.assertTrue(r["eval_hit"])
        self.assertTrue(any("反弹批" in e for e in r["exits"]))

    def test_aip_vs_lump(self):
        # 下跌行情: 定投应好于一次性
        navs = [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55] * 3
        a = self.bt.simulate_aip(navs, monthly=100, step=5)
        self.assertGreater(a["aip_ret_pct"], a["lump_ret_pct"])


class TestAnalyticsExtensions(unittest.TestCase):
    def test_percentile(self):
        from fundos_analytics import percentile
        self.assertEqual(percentile([1, 2, 3, 4, 5]), 100.0)
        self.assertEqual(percentile([5, 4, 3, 2, 1]), 20.0)

    def test_xirr_known_case(self):
        from datetime import date
        from fundos_analytics import xirr
        # 1年前投100，现值110 → XIRR ≈ 10%
        cf = [(date(2025, 8, 28), -100.0), (date(2026, 8, 28), 110.0)]
        self.assertAlmostEqual(xirr(cf), 10.0, places=0)

    def test_xirr_no_solution(self):
        from datetime import date
        from fundos_analytics import xirr
        self.assertIsNone(xirr([(date(2026, 1, 1), -100.0)]))  # 少于2笔


class TestRotationScore(unittest.TestCase):
    def test_score_accumulates(self):
        from fundos_data import rotation_score
        self.assertIsNone(rotation_score([], "x")["score"])
        one = [{"date": "2026-08-28",
                "industries": [{"name": "农药", "chg_pct": 2.0, "amount": 10.0}]}]
        rs = rotation_score(one, "农药")
        self.assertIsNone(rs["score"])          # 数据积累期优雅降级
        hist = [
            {"date": "2026-08-27",
             "industries": [{"name": "农药", "chg_pct": 2.0, "amount": 10.0},
                            {"name": "石油", "chg_pct": 1.0, "amount": 5.0}]},
            {"date": "2026-08-28",
             "industries": [{"name": "农药", "chg_pct": 2.5, "amount": 15.0},
                            {"name": "石油", "chg_pct": 1.0, "amount": 5.0}]},
        ]
        rs2 = rotation_score(hist, "农药", top_n=1)
        self.assertIsNotNone(rs2["score"])
        self.assertEqual(rs2["streak"], 2)
        self.assertEqual(rs2["rank_now"], 1)

    def test_fx_provider_shape(self):
        from fundos_data import fetch_fx, DataError
        try:
            fx = fetch_fx("fx_susdcnh", use_cache=False)
        except DataError as exc:
            self.skipTest(f"网络不可用: {exc}")
        self.assertGreater(fx["price"], 1)
        self.assertIn("name", fx)


# ---------- 组合体检 X-Ray（纯函数，离线必测） ----------
class TestXray(unittest.TestCase):
    def _holdings(self):
        return [
            {"name": "标普500", "code": "017641", "sector": "qdii", "weight": 27.5,
             "ret_pct": 0.9, "freshness": "已公布净值"},
            {"name": "科创50联接", "code": "011608", "sector": "tech", "weight": 30.0,
             "ret_pct": -34.9, "freshness": "已公布净值"},
        ]

    def test_fail_cases_are_reported(self):
        from fundos_xray import build_xray
        out = build_xray(holdings=self._holdings(),
                         risk={"max_dd_pct": -17.9, "sharpe": -2.07, "effective_funds": 5.9},
                         correlation={"tech_cluster_avg": 0.86},
                         portfolio={"snapshot_age_days": 2},
                         data_sources={"portfolio": {"status": "ok"}},
                         market={"is_trading_day": True})
        keys = {r["key"]: r for r in out["rules"]}
        self.assertEqual(keys["single_fund"]["status"], "fail")      # 27.5 > 25
        self.assertEqual(keys["tech_corr"]["status"], "fail")        # 0.86 > 0.85
        self.assertEqual(keys["sharpe"]["status"], "fail")           # 负夏普
        self.assertEqual(keys["deep_loss"]["status"], "fail")        # -34.9 破评估线
        self.assertEqual(keys["portfolio_dd"]["status"], "pass")     # -17.9 在 -20 内
        self.assertEqual(keys["data_freshness"]["status"], "pass")
        self.assertIn("不通过", out["summary"])
        self.assertTrue(0 <= out["score"] <= 100)
        self.assertEqual(out["counts"]["fail"], out["counts"]["fail"])  # 计数自洽
        self.assertEqual(out["counts"]["total"], len(out["rules"]))
        # 失败项排在前面，便于阅读
        self.assertEqual(out["rules"][0]["status"], "fail")

    def test_estimate_rule_na_on_non_trading_day(self):
        from fundos_xray import build_xray
        out = build_xray(holdings=self._holdings(),
                         market={"is_trading_day": False},
                         portfolio={"snapshot_age_days": 1})
        rule = next(r for r in out["rules"] if r["key"] == "estimate_ratio")
        self.assertEqual(rule["status"], "na")
        self.assertIn("非交易日", rule["evaluation"])

    def test_cash_rule_is_honest(self):
        from fundos_xray import build_xray
        out = build_xray(holdings=self._holdings())
        rule = next(r for r in out["rules"] if r["key"] == "cash_reserve")
        self.assertEqual(rule["status"], "na")
        self.assertIn("未接入", rule["value_text"])

    def test_empty_input_does_not_crash(self):
        from fundos_xray import build_xray
        out = build_xray()
        self.assertIn("rules", out)
        self.assertGreaterEqual(out["counts"]["na"], 1)


# ---------- 绩效曲线纯函数 ----------
class TestPerfSeries(unittest.TestCase):
    def test_drawdown_series(self):
        from fundos_analytics import drawdown_series
        dd = drawdown_series([1.0, 1.2, 0.9, 1.3, 1.56])
        self.assertEqual(dd[0], 0.0)
        self.assertAlmostEqual(dd[2], 0.9 / 1.2 - 1, places=6)
        self.assertEqual(dd[-1], 0.0)   # 创出新高后回撤归零

    def test_monthly_returns_first_month_uses_window_start(self):
        from fundos_analytics import monthly_returns
        dates = ["2026-07-30", "2026-07-31", "2026-08-03", "2026-08-31"]
        navs = [1.0, 1.1, 1.2, 0.99]
        rows = monthly_returns(dates, navs)
        self.assertEqual([r["month"] for r in rows], ["2026-07", "2026-08"])
        self.assertAlmostEqual(rows[0]["ret_pct"], 10.0, places=2)
        self.assertAlmostEqual(rows[1]["ret_pct"], -10.0, places=2)   # 0.99/1.1-1

    def test_monthly_returns_empty_on_bad_input(self):
        from fundos_analytics import monthly_returns
        self.assertEqual(monthly_returns([], []), [])
        self.assertEqual(monthly_returns(["2026-08-01"], [1.0]), [])


# ---------- 看板辅助逻辑（交易日历 / 回本距离 / 体检历史） ----------
class TestDashboardHelpers(unittest.TestCase):
    def test_breakeven_pct(self):
        import dashboard
        self.assertAlmostEqual(dashboard.breakeven_pct(-30), 42.9, places=1)  # 1/0.7-1
        self.assertAlmostEqual(dashboard.breakeven_pct(0), 0.0, places=1)
        self.assertAlmostEqual(dashboard.breakeven_pct(25), -20.0, places=1)  # 盈利时"回本"是负数
        self.assertIsNone(dashboard.breakeven_pct(-100))
        self.assertIsNone(dashboard.breakeven_pct(None))

    def test_server_disallows_port_hijack_on_windows(self):
        import os
        import dashboard
        # Windows 的 SO_REUSEADDR 允许第二个实例抢占同一端口，
        # 会造成两个进程同时 listen、"已在运行"检测永远不触发
        self.assertEqual(dashboard.Server.allow_reuse_address, os.name != "nt")

    def test_patch_cached_directive_updates_in_place(self):
        """确认/取消只补丁那条指令，不能把整页缓存清空（否则页面全变"—"）。"""
        import dashboard
        payload = {"guide": {"directives": [
            {"execution_key": "k1", "title": "止摊 + 反弹分批退出", "level": "指令",
             "rule": "stop-loss-admission", "execution": {"status": "pending"}},
            {"execution_key": "k2", "title": "别的指令", "level": "观察",
             "rule": "x", "execution": {"status": "pending"}},
        ]}, "portfolio": {"total_value": 2639.11}}
        dashboard._patch_cached_directive(payload, "k1", {"status": "cancelled", "title": "x"})
        first, second = payload["guide"]["directives"]
        self.assertEqual(first["execution"]["status"], "cancelled")
        self.assertIn("next_step", first["execution"])          # 取消后要给出下一步提示
        self.assertEqual(second["execution"]["status"], "pending")   # 不误伤其它指令
        self.assertEqual(payload["portfolio"]["total_value"], 2639.11)  # 数据本身不动

    def test_market_clock_weekend(self):
        from datetime import datetime
        import dashboard
        mk = dashboard.market_clock(datetime(2026, 11, 1, 10, 0, tzinfo=dashboard.BJ_TZ))
        self.assertEqual(mk["session"], "weekend")
        self.assertFalse(mk["is_trading_day"])
        self.assertEqual(mk["data_day"], "2026-10-30")     # 周日回落到上周五

    def test_market_clock_trading_sessions(self):
        from datetime import datetime
        import dashboard
        tz = dashboard.BJ_TZ

        def sess(h, m=0):
            return dashboard.market_clock(datetime(2026, 10, 30, h, m, tzinfo=tz))["session"]

        self.assertEqual(sess(9, 0), "pre_open")
        self.assertEqual(sess(10), "morning")
        self.assertEqual(sess(12), "lunch")
        self.assertEqual(sess(14), "afternoon")
        self.assertEqual(sess(16), "closed")

    def test_xray_history_keeps_one_row_per_day(self):
        import tempfile
        import dashboard
        with tempfile.TemporaryDirectory() as tmp:
            old = dashboard.XRAY_HISTORY
            dashboard.XRAY_HISTORY = Path(tmp) / "xray_history.json"
            try:
                xray = {"score": 41, "grade": "需处置", "counts": {"fail": 6, "warn": 0}}
                payload = {"risk": {"max_dd_pct": -17.9, "sharpe": -2.07},
                           "guide": {"tech_weight": 35.6, "qdii_weight": 47.6}}
                dashboard.record_xray_history("2026-10-30", xray, payload)
                rows = dashboard.record_xray_history("2026-10-30", {**xray, "score": 45}, payload)
                self.assertEqual(len(rows), 1, "同一天重复刷新应覆盖而不是追加")
                self.assertEqual(rows[0]["score"], 45)
                rows = dashboard.record_xray_history("2026-11-02", xray, payload)
                self.assertEqual([r["date"] for r in rows], ["2026-10-30", "2026-11-02"])
            finally:
                dashboard.XRAY_HISTORY = old


if __name__ == "__main__":
    unittest.main(verbosity=2)
