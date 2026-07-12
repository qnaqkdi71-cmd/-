"""mock 모드용 샘플 데이터.

ANTHROPIC_API_KEY 없이도 파이프라인 전체가 돌아가도록, 하나의 일관된
샘플 제품(무선 미니 가습기)에 대한 각 단계 출력을 담아둔다.
키를 넣으면 이 데이터 대신 Claude가 임의 제품에 대해 생성한다.
"""
from __future__ import annotations

from contracts import (
    Competitor,
    CopyDeck,
    CopySection,
    DesignSpec,
    MarketResearch,
    ProductBrief,
    SectionDesign,
    SpecItem,
    Theme,
)

SAMPLE_INPUT = {
    "name": "포레스트 무선 미니 가습기",
    "brand": "FOREST",
    "raw": "무선 USB-C 충전, 500ml, 12시간 연속분무, 25dB 저소음, 7색 무드등, "
           "무수 자동꺼짐, 2000mAh 배터리, 무게 240g. 가격 29,900원. "
           "타깃: 건조한 실내가 신경 쓰이는 1인 가구·직장인.",
}


def brief() -> ProductBrief:
    return ProductBrief(
        name="포레스트 무선 미니 가습기",
        brand="FOREST",
        category="생활가전 · 가습기",
        price="29,900원",
        target_customer="건조한 실내가 신경 쓰이지만 관리는 번거로운 1인 가구·직장인",
        key_features=[
            "무선 USB-C 충전으로 12시간 연속 분무",
            "25dB 초저소음 무화 방식",
            "7색 LED 무드등 내장",
            "물이 떨어지면 자동으로 꺼지는 무수 감지",
            "500ml 대용량 물탱크",
        ],
        usp=[
            "선 없이 어디든 놓는 완전 무선",
            "수면을 방해하지 않는 도서관급 저소음",
            "물 없으면 알아서 꺼지는 안심 설계",
        ],
        specs=[
            SpecItem(label="물탱크 용량", value="500ml"),
            SpecItem(label="분무량", value="약 30ml/h"),
            SpecItem(label="배터리", value="2000mAh 내장"),
            SpecItem(label="연속 사용", value="최대 12시간"),
            SpecItem(label="소음", value="25dB"),
            SpecItem(label="무게", value="240g"),
            SpecItem(label="충전", value="USB-C"),
            SpecItem(label="크기", value="72 × 72 × 140mm"),
        ],
        tone="깔끔하고 감성적이며 신뢰감 있는",
    )


def research() -> MarketResearch:
    return MarketResearch(
        keywords=[
            "무선 가습기", "미니 가습기", "저소음 가습기", "USB 가습기",
            "무드등 가습기", "사무실 가습기", "차량용 가습기", "1인 가구 가습기",
        ],
        competitors=[
            Competitor(name="일반 저가 미니 가습기",
                       positioning="1만원대 초저가 USB 가습기",
                       weakness="선 필수, 소음 큼, 무드등·안전 기능 없음"),
            Competitor(name="대형 초음파 가습기",
                       positioning="가정용 대용량 3~5L",
                       weakness="부피 크고 콘센트 필요, 이동 불가"),
        ],
        customer_pains=[
            "난방으로 실내 습도가 30% 아래로 떨어져 목·눈이 건조함",
            "콘센트 위치 때문에 가습기 놓을 자리가 마땅치 않음",
            "밤에 켜두면 소음이 신경 쓰여 잠을 설침",
            "물때 세척·관리가 번거로움",
        ],
        objections=[
            "배터리로 정말 밤새 가동되나?",
            "미니 사이즈라 가습량이 부족하지 않을까?",
            "저소음이라는데 실제로 조용할까?",
        ],
        selling_angles=[
            "완전 무선 → 배치의 자유",
            "초저소음 → 수면·집중 방해 없음",
            "무수 자동꺼짐 → 안전·안심",
            "무드등 → 감성 인테리어 소품 겸용",
        ],
    )


def _copy_sections() -> list[CopySection]:
    return [
        CopySection(
            id="hero", eyebrow="무선 미니 가습기",
            headline="건조한 밤,\n선 없이 촉촉하게",
            subheadline="500ml 대용량 · 12시간 연속 분무",
        ),
        CopySection(
            id="trust", headline="이미 3만 가구가 선택했습니다",
            items=[{"label": "누적 판매 32,000+"}, {"label": "재구매율 41%"},
                   {"label": "KC 인증 완료"}, {"label": "1년 무상 A/S"}],
        ),
        CopySection(
            id="problem", eyebrow="이런 고민, 있으셨죠?",
            headline="아침마다 칼칼한 목,\n뻑뻑한 눈",
            body=[
                "난방을 켜면 실내 습도가 30% 아래로 뚝 떨어지고",
                "가습기는 선 때문에 놓을 자리가 마땅치 않고",
                "밤새 돌리자니 소음이 신경 쓰이죠",
            ],
        ),
        CopySection(
            id="solution", eyebrow="그래서 만들었습니다",
            headline="선 없이, 어디든,\n밤새 조용히",
            body=[
                "USB-C 완충 한 번으로 최대 12시간 연속 가동",
                "침대 옆·책상 위·차 안까지 자유롭게",
                "물이 떨어지면 알아서 꺼지는 안심 설계",
            ],
        ),
        CopySection(
            id="feature_1", eyebrow="FEATURE 01", highlight="12h",
            headline="선을 뽑아도\n12시간 계속됩니다",
            body=[
                "2000mAh 내장 배터리로 완전 무선 가동",
                "USB-C 고속 충전, 약 2시간이면 완충",
                "콘센트 위치에 얽매이지 않는 자유로운 배치",
            ],
        ),
        CopySection(
            id="feature_2", eyebrow="FEATURE 02", highlight="25dB",
            headline="귓가에서도\n들리지 않는 25dB",
            body=[
                "도서관보다 조용한 초저소음 무화 방식",
                "수면과 집중을 방해하지 않습니다",
                "취침 예약으로 알아서 종료",
            ],
        ),
        CopySection(
            id="feature_3", eyebrow="FEATURE 03", highlight="7색",
            headline="7가지 무드등으로\n감성 한 스푼",
            body=[
                "은은한 7색 LED 무드등 내장",
                "가습 없이 조명만으로도 사용 가능",
                "버튼 하나로 부드럽게 색 전환",
            ],
        ),
        CopySection(
            id="spec", eyebrow="SPECIFICATION", headline="상세 스펙",
            items=[
                {"label": "물탱크 용량", "value": "500ml"},
                {"label": "분무량", "value": "약 30ml/h"},
                {"label": "배터리", "value": "2000mAh"},
                {"label": "연속 사용", "value": "최대 12시간"},
                {"label": "소음", "value": "25dB"},
                {"label": "무게", "value": "240g"},
                {"label": "충전 방식", "value": "USB-C"},
                {"label": "크기", "value": "72 × 72 × 140mm"},
            ],
        ),
        CopySection(
            id="howto", eyebrow="HOW TO USE", headline="3단계면 충분합니다",
            items=[
                {"title": "물 채우기", "desc": "상단을 열고 500ml까지 물을 채웁니다"},
                {"title": "전원 켜기", "desc": "버튼을 길게 눌러 분무를 시작합니다"},
                {"title": "모드 선택", "desc": "연속·간헐 분무와 무드등을 선택하세요"},
            ],
        ),
        CopySection(
            id="compare", eyebrow="WHY FOREST",
            headline="일반 가습기와 무엇이 다를까요?",
            items=[
                {"feature": "전원", "us": "완전 무선(배터리)", "others": "콘센트 필수"},
                {"feature": "소음", "us": "25dB 초저소음", "others": "35dB 이상"},
                {"feature": "안전", "us": "무수 자동 꺼짐", "others": "수동 관리"},
                {"feature": "무드등", "us": "7색 내장", "others": "없음"},
            ],
        ),
        CopySection(
            id="review", eyebrow="REAL REVIEW", headline="고객님들의 진짜 후기",
            items=[
                {"name": "김**", "stars": 5,
                 "text": "선이 없으니 침대 협탁에 딱 맞아요. 밤새 틀어도 진짜 조용합니다."},
                {"name": "이**", "stars": 5,
                 "text": "물이 없으면 알아서 꺼져서 안심돼요. 무드등도 감성 뿜뿜."},
                {"name": "박**", "stars": 4,
                 "text": "사무실 책상에 두고 쓰는데 목이 훨씬 편해졌어요."},
            ],
        ),
        CopySection(
            id="faq", eyebrow="FAQ", headline="자주 묻는 질문",
            items=[
                {"q": "세척은 어떻게 하나요?",
                 "a": "상단을 분리해 물로 헹군 뒤 자연 건조하면 됩니다. 주 1회 권장드려요."},
                {"q": "한 번 충전하면 얼마나 쓰나요?",
                 "a": "간헐 분무 기준 최대 12시간, 연속 분무 기준 약 6시간 사용 가능합니다."},
                {"q": "어떤 물을 넣어야 하나요?",
                 "a": "깨끗한 물이면 됩니다. 미네랄이 적은 물일수록 백분 현상이 줄어듭니다."},
            ],
        ),
        CopySection(
            id="cta", eyebrow="지금 만나보세요",
            headline="건조한 밤과\n이제 안녕하세요",
            subheadline="29,900원 · 무료배송",
            body=[
                "오늘 주문 시 내일 도착 (평일 기준)",
                "1년 무상 A/S · 7일 무료 교환/반품",
                "KC 인증 완료 안심 제품",
            ],
        ),
    ]


def copy() -> CopyDeck:
    return CopyDeck(sections=_copy_sections())


def design() -> DesignSpec:
    theme = Theme(primary="#2E7D5B", accent="#7FC8A9",
                  bg="#ffffff", text="#1b2b24", mood="내추럴 · 청량 · 미니멀")
    dark = "#16241d"
    soft = "#f2f7f3"
    green = "#2E7D5B"
    plan = {
        "hero":      ("linear-gradient(160deg,#2E7D5B 0%,#16241d 100%)", "#ffffff", "#7FC8A9", True),
        "trust":     (soft, "#1b2b24", green, False),
        "problem":   (dark, "#eaf1ec", "#7FC8A9", False),
        "solution":  (green, "#ffffff", "#d7f0e2", False),
        "feature_1": ("#ffffff", "#1b2b24", green, True),
        "feature_2": (soft, "#1b2b24", green, True),
        "feature_3": ("#ffffff", "#1b2b24", green, True),
        "spec":      (dark, "#eaf1ec", "#7FC8A9", False),
        "howto":     (soft, "#1b2b24", green, False),
        "compare":   ("#ffffff", "#1b2b24", green, False),
        "review":    (soft, "#1b2b24", green, False),
        "faq":       ("#ffffff", "#1b2b24", green, False),
        "cta":       ("linear-gradient(160deg,#2E7D5B 0%,#16241d 100%)", "#ffffff", "#7FC8A9", False),
    }
    from config import TEMPLATE_BY_ID
    sections = [
        SectionDesign(id=sid, template=TEMPLATE_BY_ID[sid], bg=bg,
                      text=text, accent=accent, image_slot=slot)
        for sid, (bg, text, accent, slot) in plan.items()
    ]
    return DesignSpec(theme=theme, sections=sections)
