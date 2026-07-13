# 🎯 상세페이지 생성 스킬 (PNG 이어붙이기 방식)

## 핵심 구조: Gemini 이미지 생성 + 섹션별 PNG 조립

---

## 1️⃣ 전체 플로우

```
[입력] 제품/서비스 정보
         ↓
[오케스트레이터] SKILL.md
         ↓
    ┌────┴────┬────────┬────────┐
    ↓         ↓        ↓        ↓
[리서치]  [카피]    [디자인]   [프롬프트]
 에이전트  에이전트   에이전트   생성 에이전트
    └────┬────┴────────┴────────┘
         ↓
[13개 섹션별 Gemini 이미지 프롬프트]
         ↓
[Gemini 3 Pro] → 섹션별 PNG 13장
         ↓
[이미지 스티칭] → 최종 상세페이지 PNG/PDF
```

---

## 2️⃣ 스킬 폴더 구조 (클로드 공식 가이드 준수)

```
landing-page-generator/
├── SKILL.md                          # 메인 오케스트레이터 (<500줄)
│
├── agents/                           # 서브에이전트 (나노바나나 @호출용)
│   ├── 01-intake.md                  # 입력 수집 & 검증
│   ├── 02-research.md                # 타겟/페인포인트 리서치
│   ├── 03-copy.md                    # 13섹션 카피라이팅
│   ├── 04-design-direction.md        # 디자인 방향 설정
│   └── 05-prompt-generator.md        # Gemini 이미지 프롬프트 생성
│
├── references/
│   ├── 13-section-guide.md           # 13단 구조 상세 설명
│   ├── copy-patterns.md              # 고전환 카피 패턴
│   ├── gemini-prompt-patterns.md     # Gemini 이미지 프롬프트 베스트 프랙티스
│   └── design-specs.md               # 이미지 사이즈/스타일 스펙
│
├── scripts/
│   ├── stitch_images.py              # PNG 이어붙이기 스크립트
│   └── export_pdf.py                 # PDF 변환 스크립트
│
└── assets/
    └── style-presets/                # 스타일 프리셋 레퍼런스 이미지
        ├── minimal-example.png
        ├── sales-example.png
        └── premium-example.png
```

> 이 프로젝트에서의 실제 매핑: agents/ → `.claude/agents/*.md`(실 서브에이전트),
> references/ → 각 스킬의 `references/`, scripts/ → 프로젝트 루트 `scripts/`,
> 이미지 생성은 기본 HTML 렌더(render 스킬) + 선택 Gemini(`scripts/gemini_api.py`).

---

## 3️⃣ 서브에이전트 상세 설계

### 01-intake.md (입력 수집)
```
역할: 상세페이지 생성에 필요한 정보 수집

필수 입력:
- product_name, one_liner, target_audience, main_problem,
  key_benefit, price, urgency

선택 입력:
- testimonials, creator_bio, bonus_items, guarantee, faq, brand_color

출력: structured_brief.json
```

### 02-research.md (리서치)
```
역할: 타겟 심층 분석 & 메시지 프레임 설계
분석: 페인포인트 5개 / 실패 원인 3개 / After 이미지 / 반대 의견·우려
출력: research_output.json
```

### 03-copy.md (카피라이팅)
```
역할: 13개 섹션별 카피 생성
카피 원칙: 자연스러운 구어체 / 감정→논리 / 구체적 숫자 / 2인칭 활용
출력: copy_output.json
```

### 04-design-direction.md (디자인 방향)
```
역할: 전체 비주얼 톤 & 스타일 결정
결정: 프리셋(minimal/sales/premium/community) / 팔레트 / 타이포 / 레이아웃
출력: design_direction.json
```

### 05-prompt-generator.md (Gemini 프롬프트 생성) ⭐핵심
```
역할: 13개 섹션별 Gemini 이미지 생성 프롬프트 작성
입력: copy + design_direction + image_spec(너비 1200px 고정)
프롬프트 원칙: 정확한 텍스트 지시 / 레이아웃 명시 / 스타일 일관성 / 한글 주의
출력: gemini_prompts.json
```

---

## 4️⃣ 13개 섹션 이미지 스펙

| # | 섹션명 | 권장 높이 | 핵심 요소 |
|---|--------|-----------|-----------|
| 01 | Hero (긴급성 헤더) | 800px | 헤드라인, 서브헤드, CTA, 긴급성 배지 |
| 02 | Pain (공감) | 600px | 페인포인트 3-4개, 감정 훅 |
| 03 | Problem (문제 정의) | 500px | 진짜 원인, 구조적 문제 |
| 04 | Story (Before→After) | 700px | 변화 스토리, 희망 메시지 |
| 05 | Solution Intro | 400px | 제품 한 줄 정의, 타겟 명시 |
| 06 | How It Works | 600px | 단계별 프로세스, 결과물 |
| 07 | Social Proof | 800px | 후기, 수치, 캡처 |
| 08 | Authority | 500px | 제작자 소개, 이력, 실적 |
| 09 | Benefits + Bonus | 700px | 혜택 요약, 보너스 구성 |
| 10 | Risk Removal | 500px | 환불 정책, FAQ, 보장 |
| 11 | Before/After Final | 400px | 최종 대비, 선택 압박 |
| 12 | Target Filter | 400px | 추천/비추천 대상 |
| 13 | Final CTA | 600px | 긴급성, CTA 버튼, 마지막 문구 |

**총 높이: ~7,000px (가변)**

---

## 5️⃣ 스티칭 스크립트 (scripts/stitch_images.py)

```python
from PIL import Image

def stitch_sections(image_paths: list, output_path: str):
    images = [Image.open(p) for p in image_paths]
    total_height = sum(img.height for img in images)
    max_width = max(img.width for img in images)
    result = Image.new('RGB', (max_width, total_height), 'white')
    y_offset = 0
    for img in images:
        x_offset = (max_width - img.width) // 2
        result.paste(img, (x_offset, y_offset))
        y_offset += img.height
    if output_path.endswith('.pdf'):
        result.save(output_path, 'PDF', resolution=150)
    else:
        result.save(output_path, 'PNG', optimize=True)
    return output_path
```

---

## 6️⃣ 실행 흐름 (나노바나나 프로 기준)

```
사용자: "○○ 상세페이지 만들어줘"
Step 1: @01-intake         → 필수 정보 수집
Step 2: @02-research       → 페인포인트/After 분석
Step 3: @03-copy           → 13섹션 카피
Step 4: @04-design-direction → 스타일/컬러
Step 5: @05-prompt-generator → Gemini 프롬프트 13개
Step 6: Gemini 이미지 생성  → 섹션별 PNG 13장
Step 7: stitch_images.py    → 최종 상세페이지 PNG/PDF
```

---

## 7️⃣ 핵심 고려사항

### Gemini 이미지 생성 한계
- 한글 렌더링: 깨질 수 있음 → 핵심 텍스트만 or 후보정
- 일관성: 13장 통일 어려움 → 스타일 앵커 강하게
- 해상도: 1200px 기준, 출력 해상도 확인

### 대안 옵션
1. 텍스트 오버레이: Gemini로 배경만 → Python 텍스트 오버레이
2. 하이브리드: 핵심만 Gemini, 나머지 HTML→PNG (← 이 프로젝트 기본)
3. Figma 연동

---

## ❓ 확인 사항
1. Gemini 호출 방식(API 연동 / 수동 복붙)
2. 한글 텍스트 처리(직접 렌더 / 배경만 + 오버레이)
3. 섹션 수(13 풀버전 / 7-8 간소화)
4. 최종 포맷(PNG / PDF / 둘 다)
