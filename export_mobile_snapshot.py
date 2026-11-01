#!/usr/bin/env python3
"""Generate a static, mobile-safe FundOS snapshot for scheduled hosting.

除了 data.json / index.html，还生成 PWA 三件套（manifest.json、sw.js、图标），
这样手机上可以"添加到主屏幕"，断网也能看最近一次快照。
"""
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import dashboard

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "mobile_site"

MANIFEST = {
    "name": "FundOS 投资驾驶舱",
    "short_name": "FundOS",
    "description": "个人基金持仓看板：体检、绩效、要闻与操作纪律",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#07111f",
    "theme_color": "#07111f",
    "lang": "zh-CN",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ],
}

# 外壳缓存优先、data.json 网络优先（离线回退缓存）、/api/ 一律不缓存
SW_TEMPLATE = """/* FundOS service worker · build {build} */
const CACHE = 'fundos-{build}';
const SHELL = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', (e) => {{
  e.waitUntil(caches.open(CACHE)
    .then((c) => c.addAll(SHELL).catch(() => null))
    .then(() => self.skipWaiting()));
}});

self.addEventListener('activate', (e) => {{
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
}});

self.addEventListener('fetch', (e) => {{
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // 外部 CDN 交给浏览器缓存
  if (url.pathname.includes('/api/')) return;        // 实时接口不缓存

  if (url.pathname.endsWith('data.json')) {{          // 数据：先网络，失败用缓存
    e.respondWith(fetch(req).then((res) => {{
      const copy = res.clone();
      caches.open(CACHE).then((c) => c.put(req, copy));
      return res;
    }}).catch(() => caches.match(req)));
    return;
  }}

  e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => {{
    const copy = res.clone();
    caches.open(CACHE).then((c) => c.put(req, copy));
    return res;
  }}).catch(() => caches.match('./index.html'))));
}});
"""


def public_payload(payload):
    private = os.environ.get("FUNDOS_STATIC_PRIVATE") == "1"
    if private:
        return payload
    result = dict(payload)
    # GitHub Pages is intentionally public in this deployment; retain the full
    # dashboard fields so the mobile view can show portfolio value and P/L.
    result["privacy"] = "public-financial-data"
    return result


def write_pwa_assets():
    """写 manifest 与 service worker（图标是二进制，随仓库提交）。"""
    (OUT / "manifest.json").write_text(
        json.dumps(MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "sw.js").write_text(SW_TEMPLATE.format(build=dashboard.BUILD_ID), encoding="utf-8")
    missing = [n for n in ("icon-192.png", "icon-512.png") if not (OUT / n).exists()]
    if missing:
        print(f"⚠️ 缺少 PWA 图标: {', '.join(missing)}（安装到主屏幕会退回默认图标）")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = public_payload(dashboard.collect())
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    payload["snapshot_meta"] = {
        "source": "github_actions",
        "generated_at": now.isoformat(timespec="seconds"),
        "timezone": "Asia/Shanghai",
        "status": "success",
    }
    if os.environ.get("FUNDOS_LLM_API_KEY"):
        try:
            import fundos_llm
            context = {"guide": payload.get("guide"), "news": payload.get("news", []), "news_day": payload.get("news_day"), "portfolio": payload.get("portfolio"), "risk": payload.get("risk")}
            fundos_llm.regenerate(context)
            payload = public_payload(dashboard.collect())
        except Exception as exc:
            payload["static_ai_error"] = str(exc)[:200]
    (OUT / "data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    html = dashboard.HTML.replace("/static/echarts.min.js", "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js")
    (OUT / "index.html").write_text(html, encoding="utf-8")
    write_pwa_assets()
    print(f"wrote {OUT / 'data.json'} ({payload.get('privacy', 'private')})")


if __name__ == "__main__":
    main()
