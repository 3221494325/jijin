#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FundOS 大模型接入层 v1.1 — OpenAI 兼容协议（免费供应商一键接入）

定位: 在【规则引擎(fundos_advisor)】之上做叙事综合层。
硬约束: LLM 只解读规则引擎的输出，不得推翻其边界；未配置密钥时全链路优雅降级，
       看板与指南完全可用（纯规则模式）。

配置优先级: 环境变量 > 配置文件(data/llm/config.json，由 setup_llm.py 写入) > 默认值
  环境变量: FUNDOS_LLM_API_KEY / FUNDOS_LLM_BASE_URL / FUNDOS_LLM_MODEL
  免费供应商(2026-08 调研): 智谱GLM-4-Flash系列 永久免费不限量(推荐) /
      硅基流动(注册送14元+免费小模型) / 魔搭ModelScope(每日2000次)

缓存: data/llm/last_brief.json —— 相同输入(指南+新闻摘要)直接复用，30分钟过期。
"""
import hashlib
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta

from fundos_config import DATA_DIR

CACHE_FILE = DATA_DIR / "llm" / "last_brief.json"
CONFIG_FILE = DATA_DIR / "llm" / "config.json"
CACHE_TTL_MIN = 30
TIMEOUT = 90

DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
DEFAULT_MODEL = "glm-4-flash-250414"

SYSTEM_PROMPT = (
    "你是 FundOS 个人基金看板的首席投资官（总裁人格）：纪律>预测，先结论后依据。"
    "你必须基于【规则引擎输出】做解读与综合，硬约束："
    "1) 不得推翻或弱化规则引擎的禁止清单与触发线边界；"
    "2) 不得承诺收益、不得输出'必涨/必跌'；"
    "3) 每条执行指令必须含分批节奏（单次≤1/3）与触发条件；"
    "4) 新闻情绪只作观察层，须等价格确认；"
    "5) 用中文，简洁有力，总长不超过500字。"
    "输出格式：形势研判 / 持仓体检 / 执行指令 / 风控边界 四段，末行加上："
    "'—— AI生成，仅供参考，不构成投资建议。'"
)


def load_config():
    """读配置文件（setup_llm.py 写入）。"""
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(api_key, base_url, model):
    """持久化配置（密钥仅存本机 data/llm/config.json，不进 git——已 gitignore? 注意提醒用户）。"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(
        {"api_key": api_key, "base_url": base_url, "model": model},
        ensure_ascii=False, indent=1), encoding="utf-8")
    # 密钥文件不入版本库
    gitignore = DATA_DIR.parent / ".gitignore"
    try:
        text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
        if "data/llm/" not in text:
            gitignore.write_text(text.rstrip("\n") + "\ndata/llm/\n", encoding="utf-8")
    except OSError:
        pass


def _effective():
    """生效配置：环境变量优先，其次配置文件，最后默认值。"""
    cfg = load_config()
    api_key = os.environ.get("FUNDOS_LLM_API_KEY") or cfg.get("api_key", "")
    base_url = (os.environ.get("FUNDOS_LLM_BASE_URL") or cfg.get("base_url", "")
                or DEFAULT_BASE_URL)
    model = os.environ.get("FUNDOS_LLM_MODEL") or cfg.get("model", "") or DEFAULT_MODEL
    return api_key, base_url, model


def status():
    """面板显示用：是否配置、模型、密钥掩码。"""
    api_key, base_url, model = _effective()
    return {
        "configured": bool(api_key),
        "base_url": base_url,
        "model": model if api_key else "",
        "key_masked": (api_key[:6] + "…" + api_key[-4:]) if len(api_key) > 12 else ("已设置" if api_key else ""),
    }


def test_call(api_key, base_url, model):
    """最小连通性测试：返回 (ok, 描述)。setup_llm 向导用。"""
    body = {"model": model, "messages": [{"role": "user", "content": "回复：OK"}],
            "max_tokens": 8, "temperature": 0}
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"})
    try:
        resp = urllib.request.urlopen(req, timeout=45)
        data = json.loads(resp.read().decode("utf-8"))
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        return True, f"连通成功，模型回复: {content[:30]!r}"
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", "replace")[:160]
        except OSError:
            detail = ""
        return False, f"HTTP {exc.code}: {detail}"
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"{type(exc).__name__}: {exc}"


def digest(context: dict) -> str:
    """输入指纹（结构指纹）：只有【指令类型/建议动作/禁止事项/环境档位】变化时
    才需重新生成。括号内的实时数字（权重47.6%、收益率-19.6%）、时间戳、
    逐条新闻等高频噪声一律剥离——它们不该使已生成的研判失效。"""
    import re as _re2

    def _norm(s):
        return _re2.sub(r"（[^）]*）|\([^)]*\)", "", str(s))[:40]

    g = context.get("guide") or {}
    nd = context.get("news_day") or {}
    slim = {
        "env": (g.get("environment") or {}).get("label", ""),
        "directives": sorted({(x.get("level"), _norm(x.get("title")))
                              for x in g.get("directives", [])}),
        "fund_guides": sorted({(x.get("code"), _norm(x.get("advice")))
                               for x in g.get("fund_guides", [])}),
        "forbidden": sorted({_norm(x) for x in g.get("forbidden", [])}),
        "weights": [round(g.get("tech_weight", 0)), round(g.get("qdii_weight", 0))],
        # 全天多空累计与当日利空/利好榜：新的重要消息进入榜单 → 提示重新生成
        "news_day": {"up": nd.get("up"), "down": nd.get("down"),
                     "bad": sorted({_norm(x.get("title", ""))[:24]
                                    for x in nd.get("top_bad", [])}),
                     "good": sorted({_norm(x.get("title", ""))[:24]
                                     for x in nd.get("top_good", [])})},
    }
    return hashlib.md5(json.dumps(slim, sort_keys=True,
                                  ensure_ascii=False).encode("utf-8")).hexdigest()


def load_cached(d: str):
    """返回 {"brief_md","model","generated_at","stale"}。
    指纹匹配 → stale=False；指纹不匹配（市场结构已变）→ 返回上一份并标 stale=True，
    面板据此提示"建议重新生成"——AI 版块永远有内容，而不是空白。"""
    try:
        blob = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not blob.get("brief_md"):
        return None
    stale = blob.get("digest") != d
    return {"brief_md": blob.get("brief_md", ""), "model": blob.get("model", ""),
            "generated_at": blob.get("generated_at", ""), "stale": stale}


def _build_user_prompt(context: dict) -> str:
    news_lines = [f"- [{n.get('label','中性')}] {n.get('title','')[:50]}"
                  for n in context.get("news", [])[:20]]
    return (
        "【规则引擎输出·今日操作指南】\n"
        + json.dumps(context.get("guide", {}), ensure_ascii=False, indent=1)
        + "\n\n【组合概况】\n"
        + json.dumps(context.get("portfolio", {}), ensure_ascii=False)
        + "\n\n【风险指标】\n"
        + json.dumps(context.get("risk", {}), ensure_ascii=False)
        + "\n\n【最新快讯(已按利好/利空/中性标注)】\n"
        + ("\n".join(news_lines) or "- (无)")
        + "\n\n【今日全天累计快讯统计】(含已被最新快讯挤出视线的早间消息，"
          "是全天完整图景，权重应高于'最新快讯'一节)\n"
        + json.dumps(context.get("news_day", {}), ensure_ascii=False, indent=1)
        + "\n\n请按系统约束输出总裁批示。"
    )


def regenerate(context: dict) -> dict:
    """同步调用 LLM 生成研判并写缓存。未配置/失败抛 RuntimeError。"""
    api_key, base_url, model = _effective()
    if not api_key:
        raise RuntimeError("未配置大模型：运行 python setup_llm.py 一键接入（免费）")
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(context)},
        ],
        "temperature": 0.4,
        "max_tokens": 1500,
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        data = json.loads(resp.read().decode("utf-8"))
        brief = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
    except (OSError, json.JSONDecodeError, urllib.error.HTTPError) as exc:
        detail = ""
        if isinstance(exc, urllib.error.HTTPError):
            try:
                detail = exc.read().decode("utf-8", "replace")[:200]
            except OSError:
                pass
        raise RuntimeError(f"LLM调用失败: {type(exc).__name__} {detail}") from exc
    if not brief:
        raise RuntimeError("LLM返回空内容")
    out = {"digest": digest(context), "model": model,
           "generated_at": datetime.now().isoformat(timespec="seconds"),
           "brief_md": brief}
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                          encoding="utf-8")
    return out
