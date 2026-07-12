"""Phase 5 · 프롬프팅(개발) 에이전트.

두 가지 일을 한다.
1) 카피덱 + 디자인스펙을 섹션 단위 RenderPlan으로 병합(렌더러가 소비).
2) 이미지 슬롯이 있는 섹션마다 이미지 생성용 프롬프트(개발용)를 만든다.
   - 실제 모드: Claude가 섹션 맥락에 맞는 프롬프트를 작성.
   - mock 모드: 결정적 규칙으로 프롬프트를 조립.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from config import MODELS
from contracts import CopyDeck, DesignSpec, ProductBrief, RenderPlan, SectionRender

from .base import run_agent


class _ImgPrompt(BaseModel):
    id: str = Field(description="섹션 id")
    prompt: str = Field(description="영문 이미지 생성 프롬프트")


class _ImgPrompts(BaseModel):
    prompts: list[_ImgPrompt]


def _fallback_prompt(brief: ProductBrief, sec, accent: str) -> str:
    head = sec.headline.replace("\n", " ").strip()
    return (
        f"Product photography of {brief.name} ({brief.category}), "
        f"concept: {head}, minimalist Korean e-commerce detail page style, "
        f"clean studio background, soft natural lighting, subtle {accent} accent, "
        f"high detail, sharp focus, 4k --ar 4:3"
    )


def build_render_plan(
    brief: ProductBrief,
    copy: CopyDeck,
    design: DesignSpec,
    use_mock: bool = False,
) -> RenderPlan:
    design_by_id = {d.id: d for d in design.sections}

    slot_sections = [
        s for s in copy.sections
        if design_by_id.get(s.id) and design_by_id[s.id].image_slot
    ]

    # 이미지 슬롯 프롬프트 생성 (Claude 또는 mock)
    def _mock_prompts() -> _ImgPrompts:
        return _ImgPrompts(prompts=[
            _ImgPrompt(id=s.id,
                       prompt=_fallback_prompt(brief, s, design_by_id[s.id].accent))
            for s in slot_sections
        ])

    prompt_map: dict[str, str] = {}
    if slot_sections:
        summary = "\n".join(
            f"- {s.id}: {s.headline.replace(chr(10), ' ')}" for s in slot_sections
        )
        user = (
            f"제품: {brief.name} ({brief.category})\n"
            f"USP: {', '.join(brief.usp)}\n\n"
            "아래 각 섹션에 넣을 이미지의 '영문' 생성 프롬프트를 작성하세요. "
            "Midjourney/이미지 모델용으로, 상업 상세페이지에 어울리는 깔끔한 "
            "제품/라이프스타일 컷을 묘사하세요.\n\n"
            f"{summary}"
        )
        result = run_agent(
            name="prompter",
            model=MODELS["prompter"],
            user_content=user,
            schema=_ImgPrompts,
            mock_provider=_mock_prompts,
            use_mock=use_mock,
            max_tokens=4000,
        )
        prompt_map = {p.id: p.prompt for p in result.prompts}

    # 카피 + 디자인 → RenderPlan 병합
    sections: list[SectionRender] = []
    for c in copy.sections:
        d = design_by_id.get(c.id)
        if d is None:
            continue
        sections.append(SectionRender(
            id=c.id,
            template=d.template,
            eyebrow=c.eyebrow,
            headline=c.headline,
            subheadline=c.subheadline,
            body=c.body,
            highlight=c.highlight,
            items=c.items,
            bg=d.bg,
            text=d.text,
            accent=d.accent or design.theme.accent,
            image_slot=d.image_slot,
            image_prompt=prompt_map.get(c.id, ""),
        ))
    return RenderPlan(product_name=brief.name, brand=brief.brand, sections=sections)
