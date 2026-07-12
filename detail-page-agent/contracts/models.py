"""데이터 계약 (Pydantic).

5개 에이전트는 오직 이 모델들로만 소통한다. 각 단계의 출력이 다음
단계의 입력이며, 이 스키마가 그대로 Claude의 구조화 출력(tool schema)으로
쓰인다. 스키마를 바꾸면 프롬프트가 아니라 여기만 고치면 된다.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TemplateKind = Literal[
    "hero", "trust", "problem", "solution", "feature",
    "spec", "howto", "compare", "review", "faq", "cta",
]


# ── Phase 1 · 정보수집 → ProductBrief ────────────────────────────────
class SpecItem(BaseModel):
    label: str = Field(description="스펙 항목명 (예: 용량)")
    value: str = Field(description="스펙 값 (예: 500ml)")


class ProductBrief(BaseModel):
    """원자료를 정규화한 제품 브리프."""
    name: str = Field(description="제품명")
    brand: str = Field(default="", description="브랜드명")
    category: str = Field(description="카테고리 (예: 생활가전)")
    price: str = Field(default="", description="판매가 (예: 29,900원)")
    target_customer: str = Field(description="핵심 타깃 고객 한 문장")
    key_features: list[str] = Field(description="핵심 기능 3~6개")
    usp: list[str] = Field(description="차별화 포인트(USP) 2~4개")
    specs: list[SpecItem] = Field(default_factory=list, description="상세 스펙")
    tone: str = Field(default="신뢰감 있고 친근한", description="브랜드 톤")


# ── Phase 2 · 리서치 → MarketResearch ───────────────────────────────
class Competitor(BaseModel):
    name: str
    positioning: str = Field(description="경쟁사 포지셔닝 한 문장")
    weakness: str = Field(default="", description="공략 가능한 약점")


class MarketResearch(BaseModel):
    keywords: list[str] = Field(description="검색·SEO 키워드 5~10개")
    competitors: list[Competitor] = Field(default_factory=list)
    customer_pains: list[str] = Field(description="고객 불편·니즈 3~6개")
    objections: list[str] = Field(description="구매를 망설이게 하는 반론 3~5개")
    selling_angles: list[str] = Field(description="설득 앵글 3~5개")


# ── Phase 3 · 카피라이팅 → CopyDeck ─────────────────────────────────
class CopySection(BaseModel):
    id: str = Field(description="섹션 id (청사진과 일치)")
    eyebrow: str = Field(default="", description="헤드라인 위 작은 라벨")
    headline: str = Field(description="섹션 대표 헤드라인")
    subheadline: str = Field(default="", description="보조 헤드라인")
    body: list[str] = Field(default_factory=list, description="본문 문장/불릿")
    highlight: str = Field(default="", description="강조 숫자/키워드")
    items: list[dict] = Field(
        default_factory=list,
        description="템플릿별 반복 요소. spec:{label,value} / howto:{title,desc} / "
                    "compare:{feature,us,others} / review:{name,stars,text} / "
                    "faq:{q,a} / trust:{label}",
    )


class CopyDeck(BaseModel):
    sections: list[CopySection] = Field(description="13개 섹션 카피")


# ── Phase 4 · 디자인 → DesignSpec ───────────────────────────────────
class Theme(BaseModel):
    primary: str = Field(description="메인 컬러 HEX")
    accent: str = Field(description="강조 컬러 HEX")
    bg: str = Field(default="#ffffff", description="기본 배경 HEX")
    text: str = Field(default="#1a1a1a", description="기본 텍스트 HEX")
    mood: str = Field(default="", description="무드 키워드")


class SectionDesign(BaseModel):
    id: str
    template: TemplateKind
    bg: str = Field(description="섹션 배경 (HEX 또는 CSS gradient)")
    text: str = Field(default="#1a1a1a", description="섹션 텍스트 컬러")
    accent: str = Field(default="", description="섹션 강조 컬러")
    image_slot: bool = Field(default=False, description="이미지 영역 포함 여부")


class DesignSpec(BaseModel):
    theme: Theme
    sections: list[SectionDesign]


# ── Phase 5 · 프롬프팅(개발) → RenderPlan ───────────────────────────
class SectionRender(BaseModel):
    """렌더러가 그대로 소비하는 섹션 단위 렌더 명세 + 이미지 프롬프트."""
    id: str
    template: TemplateKind
    eyebrow: str = ""
    headline: str = ""
    subheadline: str = ""
    body: list[str] = Field(default_factory=list)
    highlight: str = ""
    items: list[dict] = Field(default_factory=list)
    bg: str = "#ffffff"
    text: str = "#1a1a1a"
    accent: str = "#111111"
    image_slot: bool = False
    image_prompt: str = Field(
        default="",
        description="이미지 슬롯용 생성 프롬프트(개발용). 슬롯이 없으면 빈 값.",
    )


class RenderPlan(BaseModel):
    product_name: str = ""
    sections: list[SectionRender]
