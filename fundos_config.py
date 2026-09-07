#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 统一配置层 v1.0 — 单一事实来源 (Single Source of Truth)

此前持仓元数据在 fundos_core.METADATA / daily_check.HOLDINGS / daily_update.FUNDS /
trade_journal.FUNDS / news_fetch_v2.FUND_SECTOR_MAP 五处复制且互相矛盾。
本模块是唯一的持仓/路径/阈值定义处，其他脚本一律 `from fundos_config import ...`。
"""
from pathlib import Path

# ============================================================
# 路径（全部相对项目根，禁止在业务脚本里硬编码盘符）
# ============================================================
ROOT = Path(__file__).resolve().parent

SNAPSHOT = ROOT / "portfolio_snapshot.json"
DAILY_RESULT = ROOT / "daily_check_result.json"
MANUAL_DATA = ROOT / "manual_updates.json"
NEWS_JSON = ROOT / "news_result.json"
NEWS_MD = ROOT / "fund_news_report.md"

DATA_DIR = ROOT / "data"
NAV_HISTORY_DIR = DATA_DIR / "nav_history"
BOARD_HISTORY_DIR = DATA_DIR / "board_history"
CACHE_DIR = DATA_DIR / "cache"

REPORTS_DIR = ROOT / "reports"
SKILL_DIR = ROOT / ".codex" / "skills" / "fundos"

# ============================================================
# 持仓元数据（2026-08-26 用户确认快照，9 只持仓，A/C 分开计）
# ------------------------------------------------------------
# cost    : 持仓成本(元)，来自快照（权威）
# cost_nav: 成本净值，按 App 摊薄成本口径校准:
#           ret = value/cost - 1（快照自洽真值，勿用 ret_pct 字段，个别有偏差）
#           cost_nav = nav(锚定日) / (1 + ret)；锚定日 = 快照确认时点最近已公布净值日
#           （A股 2026-08-25 / QDII 2026-08-24）
#           校准重跑时机: 用户更新 portfolio_snapshot.json 后重新反推
# type    : A股估值映射类别（TYPE_WEIGHTS 的 key）
# proxy   : QDII 实时估值代理指数 [(新浪全球码, 权重)]，未含汇率损益
# switch_th/penalty/note: daily_check 换A/赎回费规则（原 daily_check.HOLDINGS）
# ============================================================
FUND_META = {
    "018735": {"name": "华夏绿电", "full_name": "华夏中证绿色电力ETF联接C",
               "cls": "C", "sector": "green", "type": "A股ETF",
               "cost": 480.00, "cost_nav": 1.1555,
               "a_code": "018734", "switch_th": -0.02, "penalty": None,
               "note": "光伏反内卷利好; 反弹到 -2% 换A"},
    "012922": {"name": "全球成长", "full_name": "易方达全球成长精选混合(QDII)C",
               "cls": "C", "sector": "qdii", "type": "QDII",
               "cost": 390.00, "cost_nav": 4.6448,
               "a_code": "012920", "switch_th": -0.10, "penalty": None,
               "proxy": [("gb_$inx", 0.5), ("gb_$ixic", 0.5)],
               "note": "已破-15%评估线; 硬止损-25%(3.4836); 禁摊平; 反弹-10%减1/3"},
    "017641": {"name": "标普500", "full_name": "摩根标普500指数(QDII)A",
               "cls": "A", "sector": "qdii", "type": "QDII美股",
               "cost": 720.00, "cost_nav": 1.6847,
               "a_code": None, "switch_th": None, "penalty": None,
               "proxy": [("gb_$inx", 1.0)],
               "note": "1年内赎回0.5%, 不急卖"},
    "019172": {"name": "纳斯达克100", "full_name": "摩根纳斯达克100指数(QDII)A",
               "cls": "A", "sector": "qdii", "type": "QDII美股",
               "cost": 419.98, "cost_nav": 1.7830,
               "a_code": None, "switch_th": None, "penalty": None,
               "proxy": [("gb_$ixic", 1.0)],
               "note": "净值滞后1-2天; 不接飞刀"},
    "011608": {"name": "科创50联接", "full_name": "易方达科创50联接A",
               "cls": "A", "sector": "tech", "type": "A股指数",
               "cost": 382.42, "cost_nav": 1.4103,
               "a_code": None, "switch_th": None, "penalty": None,
               "note": "180天内赎回0.1%; 减仓优先"},
    "001513": {"name": "信息产业A", "full_name": "易方达信息产业混合A",
               "cls": "A", "sector": "tech", "type": "A股混合",
               "cost": 198.70, "cost_nav": 8.1910,
               "a_code": None, "switch_th": None, "penalty": None,
               "note": "已转A(08-10到账); 部分赎回亏损摊入成本, App口径8.1910"},
    "022365": {"name": "科技智选", "full_name": "永赢科技智选混合C",
               "cls": "C", "sector": "tech", "type": "A股混合",
               "cost": 422.36, "cost_nav": 5.4455,
               "a_code": "022364", "switch_th": 0.0, "penalty": "2026-08-27",
               "note": "07-28转换批次满30天后换A更优"},
    "019759": {"name": "半导体A", "full_name": "中欧半导体产业股票A",
               "cls": "A", "sector": "tech", "type": "A股行业",
               "cost": 113.13, "cost_nav": 2.4314,
               "a_code": None, "switch_th": None, "penalty": None,
               "note": "A类批次; 08-26锚点校准成本净值"},
    "019764": {"name": "半导体", "full_name": "中欧半导体产业股票C",
               "cls": "C", "sector": "tech", "type": "A股行业",
               "cost": 99.10, "cost_nav": 2.3546,
               "a_code": "019759", "switch_th": 0.0, "penalty": "2026-08-15",
               "note": "C批次满30天后换A更优"},
}

# 兼容别名：短名 -> 代码（供 trade_journal / daily_update 等按名字找码）
NAME_TO_CODE = {meta["name"]: code for code, meta in FUND_META.items()}
FULLNAME_TO_CODE = {meta["full_name"]: code for code, meta in FUND_META.items()}

SECTOR_LABEL = {"tech": "科技/AI", "qdii": "QDII海外", "green": "绿色电力"}

# ============================================================
# 指数（新浪 hq.sinajs.cn）
# ============================================================
INDEX_MAP = {
    "sh000001": "上证指数", "sz399001": "深证成指", "sz399006": "创业板指",
    "sh000688": "科创50",   "sh000300": "沪深300", "sh000016": "上证50",
    "sz399673": "创业板50",
}

GLOBAL_INDEX_MAP = {
    "gb_$dji": "道琼斯", "gb_$ixic": "纳斯达克", "gb_$inx": "标普500",
    "gb_hsi": "恒生指数", "gb_$n225": "日经225",
}

# A股基金今日估算的指数映射权重（沿用 fundos_core 旧口径）
TYPE_WEIGHTS = {
    "A股指数": 0.95, "A股ETF": 0.30, "A股行业": 0.70,
    "A股混合": 0.65, "QDII": 0.0, "QDII美股": 0.0,
}

# ============================================================
# 策略阈值（与 daily_check.py / persona 铁律一致）
# ============================================================
THRESHOLDS = {
    "hard_stop": -0.25,        # 硬止损收益率
    "eval_line": -0.15,        # -15% 评估线
    "take_profit_1": 0.15,     # 止盈1：减1/3
    "take_profit_2": 0.20,     # 止盈2：再减1/3
    "tech_max": 40.0,          # 科技/AI 行业集中度上限 %
    "qdii_max": 40.0,          # QDII 占比上限 %
    "batch_max_pct": 20,       # 单次调仓 ≤ 相关仓位 20%
    "reserve_min_pct": 10,     # 现金弹药下限 %
}

# market_scan 持仓相关板块观察关键词（按包含匹配，适配新浪板块命名变动）
WATCH_BOARDS = ["半导体", "芯片", "软件开发", "国产软件", "通信设备", "电子信息",
                "消费电子", "计算机", "电力行业", "新能源", "光伏", "医疗器械",
                "生物制药", "科创50"]

# market_scan 强弱对比口径（与旧版一致：观察板块全集）
HOLDING_RELATED_BOARDS = set(WATCH_BOARDS)
TECH_SECTOR_BOARDS = HOLDING_RELATED_BOARDS  # 兼容命名

# 新闻引擎（news_fetch_v2）按板块匹配持仓
FUND_SECTOR_MAP = {
    "华夏绿电": ["绿色电力"],
    "全球成长": ["美股"],
    "标普500": ["美股"],
    "纳斯达克100": ["美股", "AI科技"],
    "科创50联接": ["科创50", "半导体"],
    "信息产业A": ["AI科技"],
    "科技智选": ["AI科技"],
    "半导体A": ["半导体"],
    "半导体": ["半导体"],
}


def get_meta(code):
    """按代码取元数据；未知代码给中性默认值，不让程序崩。"""
    return FUND_META.get(code, {
        "name": code, "full_name": code, "cls": "?", "sector": "other",
    })
