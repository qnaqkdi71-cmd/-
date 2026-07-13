# CLAUDE.md

이 파일은 이 저장소(`detail-page-agent/`)에서 Claude Code가 작업할 때의
가이드입니다.

## 프로젝트 개요

**상세페이지 자동 생성기** — 제품/서비스 정보를 입력받아 13개 섹션의
고전환 한국어 상세페이지를 생성합니다. 두 가지 이미지 경로를 지원합니다:

1. **HTML 렌더(즉시·기본)**: 카피+디자인을 HTML/CSS로 그려 Chromium으로
   PNG 13장 생성. 한글 텍스트가 정확하고 키 없이 바로 동작.
2. **Gemini 이미지(고급)**: `05-prompt-generator`가 만든 Gemini 프롬프트로
   Gemini 3 Pro(Nano Banana Pro) 이미지를 생성 후 스티칭. (`GEMINI_API_KEY` 필요)

## 개발 커맨드

```bash
pip install -r requirements.txt

# 빠른 데모: 예시 데이터로 HTML 렌더 → output/에 PNG 13장 + 전체 미리보기
python3 main.py

# 렌더만 (output/의 copy_output.json + design_direction.json 사용)
python3 .claude/skills/detail-page-render/scripts/render.py

# 섹션 PNG 스티칭만
python3 scripts/stitch_images.py output output/final_page.png

# PDF로 내보내기
python3 scripts/export_pdf.py output output/final_page.pdf

# (선택) Gemini로 섹션 이미지 생성 — GEMINI_API_KEY 필요
python3 scripts/gemini_api.py
```

## 아키텍처

### 파이프라인
```
제품 정보
  → ① intake-agent      → output/structured_brief.json
  → ② research-agent     → output/research_output.json
  → ③ copy-agent         → output/copy_output.json
  → ④ design-direction-agent → output/design_direction.json
  → ⑤ prompt-generator-agent → output/gemini_prompts.json + 렌더
  → PNG 13장 (+ 스티칭 → final_page.png / .pdf)
```

### 핵심 파일
```
detail-page-agent/
├── CLAUDE.md                        # (이 파일)
├── main.py                          # 빠른 데모 실행기
├── .claude/
│   ├── settings.json                # Agent Teams ON + 권한
│   ├── agents/                      # 5개 서브에이전트
│   │   ├── intake-agent.md          # ① 입력 수집
│   │   ├── research-agent.md        # ② 리서치
│   │   ├── copy-agent.md            # ③ 13섹션 카피
│   │   ├── design-direction-agent.md# ④ 디자인 방향
│   │   └── prompt-generator-agent.md# ⑤ Gemini 프롬프트 + 렌더
│   └── skills/
│       ├── landing-page-generator/  # 메인 오케스트레이터 스킬(+ prompt.md)
│       ├── detail-page-blueprint/   # 데이터 규격
│       ├── detail-page-copy-framework/   (+ references)
│       ├── detail-page-design-system/    (+ references)
│       ├── image-prompt-authoring/       (+ references)
│       ├── detail-page-render/scripts/render.py  # HTML→PNG
│       └── architecture-diagram/    # 구조도 그리기
├── scripts/                         # stitch_images · export_pdf · gemini_api
├── render/ · contracts/ · config.py # 렌더 엔진·스키마·설정
├── examples/sample_output/          # 예시 데이터
└── output/                          # 생성 결과(gitignore)
```

## 기술 스펙

| 항목 | 값 |
|------|-----|
| 이미지 너비 | **1200px (고정)** |
| 총 높이 | ~7,000px (13개 섹션, 가변) |
| Gemini API | Gemini 3 Pro Image (Nano Banana Pro) |
| 출력 | PNG, PDF |

## 13 섹션 구조

1. **Hero** (800px) — 헤드라인·CTA·긴급성 배지
2. **Pain** (600px) — 페인포인트 3-4개
3. **Problem** (500px) — 진짜 원인·구조적 문제
4. **Story** (700px) — Before→After
5. **Solution** (400px) — 제품 한 줄 정의
6. **How It Works** (600px) — 단계별 프로세스
7. **Social Proof** (800px) — 후기·수치
8. **Authority** (500px) — 제작자/브랜드 소개
9. **Benefits** (700px) — 혜택·보너스
10. **Risk Removal** (500px) — 환불 정책·FAQ
11. **Comparison** (400px) — 있으면/없으면 대비
12. **Target Filter** (400px) — 추천/비추천
13. **Final CTA** (600px) — 최종 CTA

(섹션 id: hero, pain, problem, story, solution, how_it_works, social_proof,
authority, benefits, risk_removal, comparison, target_filter, final_cta)

## 환경 변수

`.env`:
```
ANTHROPIC_API_KEY=...   # Claude 에이전트(실사용 모드)
GEMINI_API_KEY=...      # (선택) Gemini 이미지 생성
```

## ⚠️ 필수 준수 사항 (Critical Requirements)

### 1. 이미지 크기 고정 (Dimension Lock)
- **너비: 정확히 1200px (변경 금지)**. 모든 섹션 동일 너비 → 좌우 마진 일관.
- Gemini 출력은 크기 보장이 안 되므로 스티칭 단계에서 1200px로 리사이즈.

### 2. 실사 사진 스타일 (Photography Style)
- 일러스트/카툰 금지. 인물은 실제 모델(리얼리스틱).
- 참조: 설화수·이니스프리·라네즈 광고. 모든 프롬프트에
  `PHOTOGRAPHY STYLE (MANDATORY)` 포함.

### 3. 풀 블리드 (Full Bleed)
- 좌우 마진 없이 전체 너비 사용.

## 커스터마이즈
1. 제품 정보: 대화로 입력하거나 `output/structured_brief.json` 수정
2. 카피/디자인 방향: `.claude/agents/*.md` 및 각 스킬의 `references/`
3. 스타일 프리셋·팔레트: `detail-page-design-system` 스킬
