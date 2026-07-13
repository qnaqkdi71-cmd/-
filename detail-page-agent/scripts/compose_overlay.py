"""Gemini 사진(output/sections/*.png) 위에 한글 카피를 얹어 최종 섹션을 만든다.

사진을 풀블리드 배경으로 깔고, 하단 그라디언트 스크림 위에 섹션 카피(eyebrow·
headline·핵심 라인·하이라이트 배지)를 흰 글씨로 올린다. 결과는 output/NN_*.png
(1200×1200). 이후 stitch_images.py로 이어붙인다.
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

from jinja2 import Environment
from markupsafe import Markup, escape
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import CHROMIUM_PATH, FONT_STACK  # noqa: E402

OUT = ROOT / "output"
SEC = OUT / "sections"

env = Environment(autoescape=True)
env.filters["nl2br"] = lambda v: Markup("<br>".join(escape(x) for x in str(v).split("\n")))

TPL = env.from_string("""<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1200px;height:1200px}
.wrap{width:1200px;height:1200px;position:relative;font-family:%FONT%;overflow:hidden}
.photo{position:absolute;inset:0;background:url('data:image/png;base64,{{img}}') center/cover}
.scrim{position:absolute;left:0;right:0;bottom:0;height:66%;
 background:linear-gradient(180deg,rgba(12,20,15,0) 0%,rgba(12,20,15,.5) 42%,rgba(10,17,12,.93) 100%)}
.txt{position:absolute;left:0;right:0;bottom:0;padding:60px 72px;color:#fff}
.eyebrow{font-size:20px;font-weight:800;letter-spacing:.1em;color:{{tint}};margin-bottom:14px}
.headline{font-size:50px;font-weight:900;line-height:1.22;letter-spacing:-.02em;
 text-shadow:0 2px 16px rgba(0,0,0,.45)}
.sub{font-size:23px;font-weight:600;margin-top:16px;opacity:.96}
.badge{display:inline-block;margin-top:18px;background:{{primary}};color:#fff;font-weight:800;
 font-size:22px;padding:9px 22px;border-radius:999px}
.lines{margin-top:18px}
.lines li{list-style:none;font-size:20px;line-height:1.65;opacity:.96;padding-left:28px;
 position:relative;margin-top:4px}
.lines li::before{content:"✓";position:absolute;left:0;color:{{tint}};font-weight:900}
</style></head><body><div class="wrap">
 <div class="photo"></div><div class="scrim"></div>
 <div class="txt">
  {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
  <div class="headline">{{ s.headline|nl2br }}</div>
  {% if s.subheadline %}<div class="sub">{{ s.subheadline }}</div>{% endif %}
  {% if s.badge %}<div class="badge">{{ s.badge }}</div>{% endif %}
  {% if s.lines %}<ul class="lines">{% for l in s.lines %}<li>{{ l }}</li>{% endfor %}</ul>{% endif %}
 </div>
</div></body></html>""".replace("%FONT%", FONT_STACK))


def support_lines(sec: dict) -> list[str]:
    sid = sec["id"]
    body = sec.get("body", [])
    items = sec.get("items", [])
    if sid in ("comparison", "target_filter"):
        return [it.get("good", "") for it in items[:2]]
    if body:
        return body[:2]
    if items:
        it0 = items[0]
        if "text" in it0:
            return [it0["text"]]
        if "value" in it0:
            return [f"{it.get('label','')} {it.get('value','')}".strip() for it in items[:3]]
        if "title" in it0:
            return [" · ".join(it.get("title", "") for it in items[:3])]
        if "q" in it0:
            return [it0["q"]]
        if "label" in it0:
            return [" · ".join(it.get("label", "") for it in items[:3])]
    return []


def _lighten(hex_c: str, f: float = 0.55) -> str:
    h = hex_c.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return "#cfe9f4"
    return "#" + "".join(f"{int(v + (255 - v) * f):02x}" for v in (r, g, b))


def main() -> None:
    copy = json.loads((OUT / "copy_output.json").read_text(encoding="utf-8"))
    design = json.loads((OUT / "design_direction.json").read_text(encoding="utf-8"))
    pal = design.get("color_palette", {})
    primary = pal.get("primary", "#1E88B0")
    tint = _lighten(pal.get("accent", primary), 0.55)
    launch = {"args": ["--no-sandbox", "--force-color-profile=srgb"]}
    if CHROMIUM_PATH:
        launch["executable_path"] = CHROMIUM_PATH

    made = 0
    with sync_playwright() as p:
        b = p.chromium.launch(**launch)
        page = b.new_page(viewport={"width": 1200, "height": 1200}, device_scale_factor=1)
        for i, sec in enumerate(copy["sections"], 1):
            photo = SEC / f"{i:02d}_{sec['id']}.png"
            if not photo.exists():
                print(f"  ⚠️ 사진 없음: {photo.name}")
                continue
            ctx = {
                "img": base64.b64encode(photo.read_bytes()).decode(),
                "s": {
                    "eyebrow": sec.get("eyebrow", ""),
                    "headline": sec.get("headline", ""),
                    "subheadline": sec.get("subheadline", ""),
                    "badge": sec.get("highlight", ""),
                    "lines": support_lines(sec),
                },
            }
            page.set_content(TPL.render(**ctx, primary=primary, tint=tint), wait_until="networkidle")
            out = OUT / f"{i:02d}_{sec['id']}.png"
            page.query_selector(".wrap").screenshot(path=str(out))
            made += 1
            print(f"  ✅ {out.name}")
        b.close()
    print(f"\n합성 완료: {made}장 → {OUT}")


if __name__ == "__main__":
    main()
