"""Phase 3 · 카피라이팅 에이전트.

브리프 + 리서치를 바탕으로 13개 섹션의 상세페이지 카피를 쓴다.
섹션 id·순서는 청사진(SECTION_BLUEPRINT)을 그대로 따른다.
"""
from __future__ import annotations

import json

from config import SECTION_BLUEPRINT, MODELS
from contracts import CopyDeck, MarketResearch, ProductBrief

from . import mockdata
from .base import run_agent

_BLUEPRINT_TEXT = "\n".join(
    f"- {s['id']} ({s['label']}): 템플릿 {s['template']}" for s in SECTION_BLUEPRINT
)


def write_copy(
    brief: ProductBrief, market: MarketResearch, use_mock: bool = False
) -> CopyDeck:
    user = (
        "아래 제품 브리프와 시장 리서치를 바탕으로 한국형 커머스 상세페이지의 "
        "섹션별 카피를 작성하세요.\n\n"
        f"[제품 브리프]\n{brief.model_dump_json(indent=2)}\n\n"
        f"[시장 리서치]\n{market.model_dump_json(indent=2)}\n\n"
        "다음 13개 섹션을 정확히 이 id와 순서로 모두 작성하세요:\n"
        f"{_BLUEPRINT_TEXT}\n\n"
        "규칙:\n"
        "- headline은 짧고 강하게. 줄바꿈이 필요하면 \\n 사용.\n"
        "- spec/howto/compare/review/faq/trust 섹션은 items 배열을 채우세요.\n"
        "  (spec:{label,value} / howto:{title,desc} / compare:{feature,us,others} / "
        "review:{name,stars,text} / faq:{q,a} / trust:{label})\n"
        "- 과장·허위 표현은 피하고 리서치의 반론을 해소하는 방향으로 쓰세요."
    )
    return run_agent(
        name="copywriter",
        model=MODELS["copywriter"],
        user_content=user,
        schema=CopyDeck,
        mock_provider=mockdata.copy,
        use_mock=use_mock,
        max_tokens=12000,
    )
