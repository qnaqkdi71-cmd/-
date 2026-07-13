"""전역 설정: 모델 배치, 렌더 환경, 13-섹션 청사진.

이 파일 하나만 고치면 모델/폭/섹션 구성을 바꿀 수 있습니다.
"""
from __future__ import annotations

import glob
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
PROMPTS_DIR = ROOT / "prompts"

# ── 모델 배치 (Claude) ───────────────────────────────────────────────
# 정보수집은 저렴한 Haiku, 나머지 추론·생성 단계는 Opus 4.8.
OPUS = "claude-opus-4-8"
HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-5"

MODELS = {
    "collector": HAIKU,
    "researcher": OPUS,
    "copywriter": OPUS,
    "designer": OPUS,
    "prompter": OPUS,
}

# ── 렌더 환경 ────────────────────────────────────────────────────────
PAGE_WIDTH = 1200         # design-specs 규격: 너비 1200px 고정(FULL BLEED)
PAGE_HEIGHT = 1200        # 세로도 1200px 고정 → 모든 섹션 정사각 1200×1200
DEVICE_SCALE = 1          # 정확히 1200×1200 픽셀로 출력
FONT_STACK = (
    "'Pretendard', 'Pretendard Variable', 'Apple SD Gothic Neo', "
    "'Noto Sans KR', 'Noto Sans CJK KR', 'Malgun Gothic', sans-serif"
)


def find_chromium() -> str | None:
    """Playwright 사전설치 Chromium 실행 파일 경로를 찾는다.

    이 실행 환경은 브라우저를 /opt/pw-browsers 에 미리 깔아두므로
    playwright 패키지 버전과 빌드 번호가 어긋나도 직접 지정해 쓴다.
    반환값이 None이면 playwright 기본 탐색에 맡긴다.
    """
    env = os.getenv("CHROMIUM_PATH")
    if env and Path(env).exists():
        return env
    for pat in (
        "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
        "/opt/pw-browsers/chromium/chrome-linux/chrome",
    ):
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


CHROMIUM_PATH = find_chromium()

# ── 13-섹션 청사진 ───────────────────────────────────────────────────
# 한국형 커머스 상세페이지의 정석 흐름. id는 파이프라인 전 구간에서
# 섹션을 잇는 키로 쓰인다. template은 렌더러의 기본 레이아웃 힌트.
# 세일즈형 13섹션 (참고 사양의 섹션 id·순서와 정확히 일치)
SECTION_BLUEPRINT: list[dict] = [
    {"id": "hero",         "label": "히어로·후킹",   "template": "hero"},
    {"id": "pain",         "label": "공감(페인)",    "template": "pain"},
    {"id": "problem",      "label": "문제 정의",     "template": "problem"},
    {"id": "story",        "label": "변화 스토리",   "template": "story"},
    {"id": "solution",     "label": "솔루션 소개",   "template": "solution"},
    {"id": "how_it_works", "label": "작동 방식",     "template": "howto"},
    {"id": "social_proof", "label": "사회적 증거",   "template": "social_proof"},
    {"id": "authority",    "label": "권위·신뢰",     "template": "authority"},
    {"id": "benefits",     "label": "혜택·보너스",   "template": "benefits"},
    {"id": "risk_removal", "label": "리스크 제거",   "template": "risk"},
    {"id": "comparison",   "label": "최종 대비",     "template": "versus"},
    {"id": "target_filter","label": "타겟 필터",     "template": "versus"},
    {"id": "final_cta",    "label": "최종 CTA",      "template": "cta"},
]

SECTION_IDS = [s["id"] for s in SECTION_BLUEPRINT]
TEMPLATE_BY_ID = {s["id"]: s["template"] for s in SECTION_BLUEPRINT}
LABEL_BY_ID = {s["id"]: s["label"] for s in SECTION_BLUEPRINT}


def has_api_key() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))
