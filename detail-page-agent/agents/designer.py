"""Phase 4 · 디자인 에이전트.

카피덱을 보고 전체 디자인 시스템(테마 컬러·무드)과 섹션별 레이아웃/배경/
텍스트 컬러/이미지 슬롯 여부를 정한 DesignSpec을 만든다.
"""
from __future__ import annotations

from config import MODELS
from contracts import CopyDeck, DesignSpec, ProductBrief

from . import mockdata
from .base import run_agent


def design(
    brief: ProductBrief, copy: CopyDeck, use_mock: bool = False
) -> DesignSpec:
    section_ids = [s.id for s in copy.sections]
    user = (
        "아래 제품과 카피덱에 맞는 상세페이지 디자인 시스템을 설계하세요.\n\n"
        f"[제품] {brief.name} / 카테고리: {brief.category} / 톤: {brief.tone}\n"
        f"[USP] {', '.join(brief.usp)}\n\n"
        f"[카피덱]\n{copy.model_dump_json(indent=2)}\n\n"
        "요구사항:\n"
        "- theme: 제품 톤에 맞는 primary/accent/bg/text HEX와 mood 키워드.\n"
        f"- sections: 다음 id 전부에 대해 순서대로 디자인을 지정하세요: {section_ids}\n"
        "- 각 섹션의 bg(HEX 또는 CSS linear-gradient), text 컬러, accent, "
        "image_slot(제품 사진/이미지가 들어갈 섹션이면 true)을 정하세요.\n"
        "- hero와 cta는 강한 배경(그라디언트 등), 특징 섹션은 이미지 슬롯 권장.\n"
        "- 명암 대비를 확보해 가독성을 지키세요."
    )
    return run_agent(
        name="designer",
        model=MODELS["designer"],
        user_content=user,
        schema=DesignSpec,
        mock_provider=mockdata.design,
        use_mock=use_mock,
        max_tokens=8000,
    )
