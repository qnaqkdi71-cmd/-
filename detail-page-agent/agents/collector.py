"""Phase 1 · 정보수집 에이전트.

원자료(제품명·브랜드·메모·스펙)를 정규화된 ProductBrief로 만든다.
"""
from __future__ import annotations

import json

from config import MODELS
from contracts import ProductBrief

from . import mockdata
from .base import run_agent


def collect(raw_input: dict, use_mock: bool = False) -> ProductBrief:
    user = (
        "다음 제품 원자료를 상세페이지 제작에 쓸 제품 브리프로 정규화하세요.\n\n"
        f"제품명: {raw_input.get('name', '')}\n"
        f"브랜드: {raw_input.get('brand', '')}\n"
        f"원자료:\n{raw_input.get('raw', '')}\n\n"
        "누락된 스펙은 임의로 지어내지 말고, 제공된 정보에서 추출·정리만 하세요."
    )
    return run_agent(
        name="collector",
        model=MODELS["collector"],
        user_content=user,
        schema=ProductBrief,
        mock_provider=mockdata.brief,
        use_mock=use_mock,
    )
