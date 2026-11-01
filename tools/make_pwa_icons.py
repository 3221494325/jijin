#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 PWA 图标（mobile_site/icon-192.png、icon-512.png）。

一次性工具：只在需要改图标时手动运行（需要 Pillow）。
    python tools/make_pwa_icons.py
图标设计：深蓝底 + 青色网格 + 青色上行折线 + 红点（红涨口径）。
"""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "mobile_site"
BG = (7, 17, 31, 255)
GRID = (32, 54, 82, 255)
CYAN = (94, 231, 255, 255)
RED = (255, 107, 122, 255)
S = 4  # 超采样倍数


def draw_icon(size):
    n = size * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # 圆角底（maskable 安全区留 10% padding，内容居中）
    pad = int(n * 0.06)
    d.rounded_rectangle([pad, pad, n - pad, n - pad], radius=int(n * 0.22), fill=BG)
    # 网格
    step = n // 8
    for i in range(1, 8):
        x = i * step
        d.line([(x, pad * 2), (x, n - pad * 2)], fill=GRID, width=max(1, S))
        d.line([(pad * 2, x), (n - pad * 2, x)], fill=GRID, width=max(1, S))
    # 上行折线（左低右高，含一次回撤）
    pts = [(0.20, 0.70), (0.34, 0.56), (0.46, 0.63), (0.62, 0.40), (0.78, 0.32)]
    line = [(p[0] * n, p[1] * n) for p in pts]
    d.line(line, fill=CYAN, width=int(n * 0.045), joint="curve")
    # 折线下方色块（预先与底色混合，避免 RGBA 直接写入造成透明挖空）
    for i in range(len(pts) - 1):
        x0, y0 = line[i]
        x1, y1 = line[i + 1]
        d.polygon([(x0, y0), (x1, y1), (x1, n * 0.80), (x0, n * 0.80)],
                  fill=(21, 52, 70, 255))
    # 终点红点
    cx, cy = line[-1]
    r = n * 0.045
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    return img.resize((size, size), Image.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for size in (192, 512):
        path = OUT / f"icon-{size}.png"
        draw_icon(size).save(path)
        print("wrote", path)


if __name__ == "__main__":
    main()
