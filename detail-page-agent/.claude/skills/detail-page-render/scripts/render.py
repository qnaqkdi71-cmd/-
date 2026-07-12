"""참고 사양의 산출물을 합쳐 상세페이지 PNG 13장을 만든다.

읽기 (output/):
  copy_output.json       (필수, copy-agent 산출 · 렌더레디 13섹션)
  design_direction.json  (필수, design-direction-agent 산출 · 팔레트+섹션배경)
  structured_brief.json  (선택, 제품명·브랜드)
쓰기:
  output/renderplan.json (병합된 최종 렌더 명세)
  output/01_*.png ~ 13_*.png, 00_full_preview.png

design_direction.json의 color_palette + section_backgrounds로 각 섹션의
배경/글자/포인트 색을 해석하고, 섹션 template은 config의 청사진을 따른다.
프로젝트 루트의 render/ 엔진을 재사용한다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from config import TEMPLATE_BY_ID  # noqa: E402
from contracts import RenderPlan, SectionRender  # noqa: E402
from render import render_plan, stitch_full_page  # noqa: E402

OUT = ROOT / "output"


def _load(name: str, required: bool = False):
    path = OUT / name
    if not path.exists():
        if required:
            print(f"[오류] 필요한 파일이 없습니다: output/{name}")
            print("      앞 단계(카피/디자인) 에이전트를 먼저 완료해 주세요.")
            sys.exit(1)
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _hex(c: str, default: str) -> str:
    c = (c or "").strip()
    return c if c.startswith("#") and len(c) in (4, 7) else default


def _rgb(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _to_hex(rgb) -> str:
    return "#" + "".join(f"{max(0, min(255, int(v))):02x}" for v in rgb)


def _darken(h: str, f: float = 0.34) -> str:
    return _to_hex(v * f for v in _rgb(h))


def _lighten(h: str, f: float = 0.45) -> str:
    return _to_hex(v + (255 - v) * f for v in _rgb(h))


def _resolve_style(section_id: str, design: dict):
    """design_direction → (bg, text, accent) 해석."""
    pal = design.get("color_palette", {})
    primary = _hex(pal.get("primary"), "#2E7D5B")
    accent = _hex(pal.get("accent"), "#7FC8A9")
    bg = _hex(pal.get("background"), "#ffffff")
    bg_alt = _hex(pal.get("background_alt"), "#f2f7f3")
    text = _hex(pal.get("text_primary"), "#1a1a1a")

    val = str(design.get("section_backgrounds", {}).get(section_id, "background")).lower()
    if "gradient" in val:
        return (f"linear-gradient(160deg,{primary} 0%,{_darken(primary)} 100%)",
                "#ffffff", _lighten(accent))
    if "primary" in val:  # "primary" 또는 "primary with opacity"
        return (primary, "#ffffff", _lighten(accent))
    if "alt" in val:
        return (bg_alt, text, primary)
    return (bg, text, primary)


def main() -> None:
    copy = _load("copy_output.json", required=True)
    design = _load("design_direction.json", required=True)
    brief = _load("structured_brief.json") or {}

    sections_in = copy.get("sections", copy if isinstance(copy, list) else [])
    sections: list[SectionRender] = []
    for c in sections_in:
        sid = c.get("id", "")
        template = TEMPLATE_BY_ID.get(sid, "solution")
        bg, text, accent = _resolve_style(sid, design)
        sections.append(SectionRender(
            id=sid,
            template=template,
            eyebrow=c.get("eyebrow", ""),
            headline=c.get("headline", ""),
            subheadline=c.get("subheadline", ""),
            body=c.get("body", []),
            highlight=c.get("highlight", ""),
            items=c.get("items", []),
            bg=bg, text=text, accent=accent,
            image_slot=(sid == "hero"),
        ))

    if not sections:
        print("[오류] copy_output.json에 sections가 없습니다.")
        sys.exit(1)

    name = brief.get("product_name") or brief.get("name", "")
    brand = brief.get("brand", "")
    plan = RenderPlan(product_name=name, brand=brand, sections=sections)
    OUT.mkdir(exist_ok=True)
    (OUT / "renderplan.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    paths = render_plan(plan, out_dir=OUT)
    stitch_full_page(paths, out_dir=OUT)
    print(f"\n완료! 상세페이지 이미지 {len(paths)}장 → {OUT}")
    for p in paths:
        print("   -", p.name)
    print("   - 00_full_preview.png")


if __name__ == "__main__":
    main()
