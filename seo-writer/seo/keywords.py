"""키워드 발굴 엔진 (블로소득 방법).

시드 키워드 → 롱테일 후보 대량 생성 + 각 후보의 구글 `allintitle:` 링크 생성.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import quote_plus

from .strategy import MODIFIERS, classify_competition


@dataclass
class KeywordCandidate:
    keyword: str
    intent: str
    allintitle_url: str
    search_url: str
    # 경쟁도(수동/자동 조회 후 채워짐)
    allintitle_count: int | None = None
    competition_label: str | None = None
    competition_tone: str | None = None
    competition_hint: str | None = None

    def apply_count(self, count: int) -> None:
        self.allintitle_count = count
        label, tone, hint = classify_competition(count)
        self.competition_label = label
        self.competition_tone = tone
        self.competition_hint = hint


def allintitle_url(keyword: str) -> str:
    """제목에 키워드가 들어간 글만 세는 구글 검색 URL(진짜 경쟁자 수)."""
    return f"https://www.google.com/search?q={quote_plus('allintitle:' + keyword)}"


def search_url(keyword: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(keyword)}"


def _norm(s: str) -> str:
    return " ".join(s.split())


def generate_keywords(
    seed: str,
    years: list[int] | None = None,
    intents: list[str] | None = None,
    limit: int = 120,
) -> list[KeywordCandidate]:
    """시드 키워드로 롱테일 후보를 생성한다.

    - years: 연도 조합 (예: [2025, 2026]) — 시즌성 최신 수요
    - intents: 포함할 의도 (기본: 전체)
    """
    seed = _norm(seed)
    if not seed:
        return []

    years = years or []
    intent_keys = intents or list(MODIFIERS.keys())

    out: list[KeywordCandidate] = []
    seen: set[str] = set()

    def push(keyword: str, intent: str) -> None:
        k = _norm(keyword)
        if not k or k in seen:
            return
        seen.add(k)
        out.append(
            KeywordCandidate(
                keyword=k,
                intent=intent,
                allintitle_url=allintitle_url(k),
                search_url=search_url(k),
            )
        )

    # 1) 연도 조합 (시즌성)
    for y in years:
        push(f"{y} {seed}", "시즌형")
        push(f"{seed} {y}", "시즌형")

    # 2) 시드 + 수식어
    for ik in intent_keys:
        for m in MODIFIERS.get(ik, []):
            push(f"{seed} {m}", ik)

    # 3) 연도 + 시드 + 수식어 (가장 경쟁 낮은 롱테일)
    for y in years:
        for ik in intent_keys:
            for m in MODIFIERS.get(ik, []):
                push(f"{y} {seed} {m}", ik)

    return out[:limit]
