"""구글 SERP 조회 (노아·블로소득 방법).

SERPER_API_KEY 가 있으면 Serper.dev로 실제 상위 결과/개수를 가져오고,
없으면 '수동 모드'(allintitle 링크를 직접 눌러 확인)로 안전하게 폴백한다.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import httpx

from .keywords import allintitle_url


@dataclass
class SerpResult:
    title: str
    link: str
    snippet: str


@dataclass
class CompetitionReport:
    keyword: str
    allintitle_count: int | None       # 자동 조회 성공 시 실경쟁자 수
    top_results: list[SerpResult]      # 상위 오가닉 글 (글쓰기 참고용)
    manual: bool                       # True면 수동 확인 필요
    allintitle_url: str
    note: str


class SerpClient:
    """Serper.dev 래퍼. 키가 없으면 manual=True 로 폴백."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("SERPER_API_KEY") or ""

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _post(self, query: str, num: int = 10) -> dict:
        resp = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
            json={"q": query, "gl": "kr", "hl": "ko", "num": num},
            timeout=20.0,
        )
        resp.raise_for_status()
        return resp.json()

    def competition(self, keyword: str) -> CompetitionReport:
        """키워드의 경쟁도 + 상위 글을 조사한다."""
        url = allintitle_url(keyword)

        if not self.enabled:
            return CompetitionReport(
                keyword=keyword,
                allintitle_count=None,
                top_results=[],
                manual=True,
                allintitle_url=url,
                note="SERPER_API_KEY 미설정 → 위 allintitle 링크를 눌러 결과 수를 직접 확인하세요(무료).",
            )

        try:
            # 1) allintitle 실경쟁자 수 (자동)
            at = self._post(f"allintitle:{keyword}", num=10)
            count = _extract_total(at)

            # 2) 상위 오가닉 글 (일반 검색 — 글쓰기 참고용)
            normal = self._post(keyword, num=10)
            top = [
                SerpResult(
                    title=o.get("title", ""),
                    link=o.get("link", ""),
                    snippet=o.get("snippet", ""),
                )
                for o in normal.get("organic", [])[:10]
            ]
            return CompetitionReport(
                keyword=keyword,
                allintitle_count=count,
                top_results=top,
                manual=False,
                allintitle_url=url,
                note="Serper로 자동 조회 완료.",
            )
        except Exception as e:  # 네트워크/쿼터 문제 → 수동 폴백
            return CompetitionReport(
                keyword=keyword,
                allintitle_count=None,
                top_results=[],
                manual=True,
                allintitle_url=url,
                note=f"자동 조회 실패({type(e).__name__}) → allintitle 링크로 직접 확인하세요.",
            )


def _extract_total(payload: dict) -> int | None:
    """Serper 응답에서 총 결과 수를 추정. 없으면 반환된 organic 개수로 대체."""
    info = payload.get("searchInformation") or {}
    for key in ("totalResults", "total_results"):
        v = info.get(key)
        if v is not None:
            try:
                return int(str(v).replace(",", ""))
            except (TypeError, ValueError):
                pass
    organic = payload.get("organic")
    if isinstance(organic, list):
        return len(organic)
    return None
