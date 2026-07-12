"""Phase 2 · 리서치 에이전트.

ProductBrief를 바탕으로 키워드·경쟁사·고객 불편·구매 반론·설득 앵글을
정리한 MarketResearch를 만든다.
"""
from __future__ import annotations

from config import MODELS
from contracts import MarketResearch, ProductBrief

from . import mockdata
from .base import run_agent


def research(brief: ProductBrief, use_mock: bool = False) -> MarketResearch:
    user = (
        "다음 제품 브리프를 보고 상세페이지 설득 전략을 위한 시장 리서치를 하세요.\n\n"
        f"{brief.model_dump_json(indent=2)}\n\n"
        "검색 키워드, 경쟁 제품과 약점, 고객이 겪는 불편, 구매를 망설이게 하는 "
        "반론, 그리고 이를 뒤집을 설득 앵글을 도출하세요."
    )
    return run_agent(
        name="researcher",
        model=MODELS["researcher"],
        user_content=user,
        schema=MarketResearch,
        mock_provider=mockdata.research,
        use_mock=use_mock,
    )
