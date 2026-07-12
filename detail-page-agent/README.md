# 상세페이지 에이전트 (Detail Page Agent)

제품 정보를 입력하면 **5단계 멀티 에이전트 파이프라인**이 한국형 커머스
상세페이지를 만들어 **섹션 이미지(PNG) 13장**으로 내보냅니다.
Claude Opus 4.8 기반이며, API 키가 없으면 **mock 모드**로 즉시 동작합니다.

```
            ┌─────────────────────────────┐
            │   Orchestrator (main.py)     │  중앙 제어
            └──────────────┬──────────────┘
   ┌───────────────────────┼───────────────────────┐
   ▼                       ▼                        ▼
Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──▶ Phase 4 ──▶ Phase 5 ──▶ 렌더(PNG×13)
정보수집     리서치      카피라이팅    디자인      프롬프팅
Collector  Research   Copywriter   Designer   Prompting
```

각 단계는 **Pydantic 데이터 계약**으로만 소통합니다. 단계별로 독립
재생성·검수·교체가 가능합니다.

| Phase | 에이전트 | 입력 → 출력 | 모델 |
|-------|---------|-------------|------|
| 1 | 정보수집 | 원자료 → `ProductBrief` | Haiku 4.5 |
| 2 | 리서치 | Brief → `MarketResearch` | Opus 4.8 |
| 3 | 카피라이팅 | Brief+Research → `CopyDeck` | Opus 4.8 |
| 4 | 디자인 | CopyDeck → `DesignSpec` | Opus 4.8 |
| 5 | 프롬프팅(개발) | Copy+Design → `RenderPlan` (+이미지 프롬프트) | Opus 4.8 |
| R | 렌더러 | RenderPlan → **PNG 13장** | Playwright + Chromium |

## 13-섹션 청사진

`hero · trust · problem · solution · feature×3 · spec · howto · compare ·
review · faq · cta` — 한국형 상세페이지의 정석 흐름. `config.py`의
`SECTION_BLUEPRINT`에서 순서·구성을 바꿀 수 있습니다.

## 설치

```bash
cd detail-page-agent
pip install -r requirements.txt
# Chromium은 이 환경에 사전설치돼 있습니다. 없다면: playwright install chromium
```

## 실행

```bash
# 1) mock 모드 — 키 없이 동봉된 샘플 제품으로 13장 생성
python main.py --mock

# 2) 실제 모드 — Claude가 임의 제품에 대해 생성
export ANTHROPIC_API_KEY=sk-ant-...
python main.py --input examples/sample_input.json
python main.py --name "제품명" --brand "브랜드" --raw "스펙/메모..."
```

키가 없으면 자동으로 mock 모드로 전환됩니다.

## 결과물 (`output/`)

- `01_hero.png` … `13_cta.png` — 섹션별 상세페이지 이미지 (폭 860px · 2x 고해상도)
- `00_full_preview.png` — 13장을 세로로 이어붙인 전체 미리보기
- `render_plan.json` — 섹션별 렌더 명세 + 이미지 슬롯 생성 프롬프트(개발용)

## 구조

```
detail-page-agent/
├── main.py               # 오케스트레이터 (중앙 제어)
├── config.py             # 모델 배치 · 렌더 설정 · 13-섹션 청사진
├── contracts/            # 데이터 계약 (Pydantic) — 시스템의 척추
├── agents/               # 5개 에이전트 + base 실행기 + mock 데이터
├── prompts/              # 에이전트별 시스템 프롬프트 (.md)
├── render/               # HTML/CSS 템플릿 + Playwright PNG 렌더러
├── examples/             # 샘플 제품 입력
└── output/               # 생성 결과 (PNG 13장 등)
```

## 커스터마이즈

- **섹션 구성**: `config.py`의 `SECTION_BLUEPRINT`
- **모델 배치**: `config.py`의 `MODELS`
- **카피 톤/전략**: `prompts/*.md`
- **디자인/레이아웃**: `render/templates.py` (섹션 템플릿 11종)
- **데이터 스키마**: `contracts/models.py`

## 이미지 슬롯

`feature`/`hero` 등 이미지 슬롯이 있는 섹션은 현재 깔끔한 플레이스홀더로
렌더링되며, 프롬프팅 에이전트가 각 슬롯의 **이미지 생성 프롬프트**를
`render_plan.json`에 함께 출력합니다. 이후 이미지 생성 API를 연동해 이
프롬프트로 실제 컷을 만들어 끼우도록 확장할 수 있습니다.
