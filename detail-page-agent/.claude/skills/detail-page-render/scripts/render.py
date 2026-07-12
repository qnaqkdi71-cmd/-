"""workspace의 산출물을 합쳐 상세페이지 PNG 13장을 만든다.

읽기:
  workspace/copydeck.json     (필수, 카피)
  workspace/designspec.json   (필수, 디자인)
  workspace/brief.json        (선택, 제품명)
  workspace/image_prompts.json(선택, 이미지 슬롯 프롬프트)
쓰기:
  workspace/renderplan.json   (병합된 최종 렌더 명세)
  output/01_*.png ~ 13_*.png  (섹션 이미지)

이 스크립트는 프로젝트 루트의 render/ 렌더 엔진을 재사용한다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# .claude/skills/detail-page-render/scripts/render.py → parents[4] = 프로젝트 루트
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from contracts import RenderPlan, SectionRender  # noqa: E402
from render import render_plan, stitch_full_page  # noqa: E402

WS = ROOT / "workspace"


def _load(name: str, required: bool = False):
    path = WS / name
    if not path.exists():
        if required:
            print(f"[오류] 필요한 파일이 없습니다: workspace/{name}")
            print("      앞 단계(카피/디자인)를 먼저 완료해 주세요.")
            sys.exit(1)
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    copydeck = _load("copydeck.json", required=True)
    design = _load("designspec.json", required=True)
    brief = _load("brief.json") or {}
    img_prompts = _load("image_prompts.json") or {}

    design_by_id = {d["id"]: d for d in design.get("sections", [])}
    theme_accent = design.get("theme", {}).get("accent", "#111111")

    sections: list[SectionRender] = []
    for c in copydeck.get("sections", []):
        d = design_by_id.get(c["id"])
        if not d:
            print(f"[경고] designspec에 '{c['id']}' 섹션이 없어 건너뜁니다.")
            continue
        sections.append(SectionRender(
            id=c["id"],
            template=d.get("template", c["id"]),
            eyebrow=c.get("eyebrow", ""),
            headline=c.get("headline", ""),
            subheadline=c.get("subheadline", ""),
            body=c.get("body", []),
            highlight=c.get("highlight", ""),
            items=c.get("items", []),
            bg=d.get("bg", "#ffffff"),
            text=d.get("text", "#1a1a1a"),
            accent=d.get("accent") or theme_accent,
            image_slot=bool(d.get("image_slot", False)),
            image_prompt=img_prompts.get(c["id"], ""),
        ))

    if not sections:
        print("[오류] 렌더할 섹션이 없습니다. copydeck/designspec을 확인하세요.")
        sys.exit(1)

    plan = RenderPlan(
        product_name=brief.get("name", ""),
        brand=brief.get("brand", ""),
        sections=sections,
    )
    WS.mkdir(exist_ok=True)
    (WS / "renderplan.json").write_text(
        plan.model_dump_json(indent=2), encoding="utf-8"
    )

    paths = render_plan(plan)
    stitch_full_page(paths)

    print(f"\n완료! 상세페이지 이미지 {len(paths)}장을 만들었습니다 → {ROOT/'output'}")
    for p in paths:
        print("   -", p.name)
    print("   - 00_full_preview.png  (전체 이어붙인 미리보기)")


if __name__ == "__main__":
    main()
