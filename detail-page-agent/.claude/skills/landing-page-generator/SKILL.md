---
name: landing-page-generator
description: |
  한국어 상세페이지(랜딩페이지) 자동 생성 메인 오케스트레이터. 제품/서비스
  정보를 입력받아 5개 에이전트를 순서대로 지휘해 13개 섹션의 고전환
  상세페이지를 만들고 PNG 13장(+스티칭 PNG/PDF)으로 출력한다.
  Use when: 상세페이지·랜딩페이지·제품 소개/판매 페이지 생성 요청 시.
model: sonnet
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

# 상세페이지 생성기 (Landing Page Generator) — 오케스트레이터

제품/서비스 정보를 기반으로 13개 섹션 상세페이지를 자동 생성하는 전체
파이프라인을 지휘한다. 이 스킬은 "무엇을 어떤 순서로" 할지 정하고, 실제
작업은 `.claude/agents/`의 서브에이전트와 렌더 스킬이 수행한다.

## 실행 흐름 (7단계)

```
[입력] 제품/서비스 정보
  → Step 1  intake-agent           → output/structured_brief.json
  → Step 2  research-agent          → output/research_output.json
  → Step 3  copy-agent              → output/copy_output.json
  → Step 4  design-direction-agent  → output/design_direction.json
  → Step 5  prompt-generator-agent  → output/gemini_prompts.json
  → Step 6  이미지 생성
             · 기본: HTML 렌더(render 스킬) → output/NN_*.png
             · 고급: scripts/gemini_api.py (GEMINI_API_KEY 필요)
  → Step 7  스티칭 → output/final_page.png (+ export_pdf → .pdf)
```

## 오케스트레이션 방법

1. **정보 수집**: 사용자 입력이 부족하면 `intake-agent`(또는 AskUserQuestion)로
   필수 항목(product_name/one_liner/target/main_problem/key_benefit/price/urgency)을
   확보한다. 제품 이미지가 있으면 우선 분석한다.
2. **순차 위임**: Task로 각 에이전트를 순서대로 호출한다(각 단계는 앞 단계의
   output/*.json을 읽어 이어받음). Agent Teams가 켜져 있으면 팀으로 협업한다.
3. **렌더**: 마지막에 렌더 스킬을 실행한다.
   ```bash
   python3 .claude/skills/detail-page-render/scripts/render.py
   ```
4. **스티칭/PDF**(선택):
   ```bash
   python3 scripts/stitch_images.py output output/final_page.png
   python3 scripts/export_pdf.py   output output/final_page.pdf
   ```
5. 결과(PNG 13장 + final_page)를 사용자에게 보고한다.

## 필수/선택 입력

- 필수: product_name, one_liner, target_audience, main_problem, key_benefit,
  price, urgency
- 선택: testimonials, creator_bio, bonus_items, guarantee, faq, brand_color

## 13 섹션 (id · 높이)

hero(800) · pain(600) · problem(500) · story(700) · solution(400) ·
how_it_works(600) · social_proof(800) · authority(500) · benefits(700) ·
risk_removal(500) · comparison(400) · target_filter(400) · final_cta(600)
→ 총 ~7,000px, 너비 1200px 고정.

## 기술 스펙 / 필수 준수

- 너비 **1200px 고정(FULL BLEED)**, 실사 사진 스타일(일러스트 금지),
  스타일 앵커로 13장 일관성 유지. 상세는 아래 참조.

## 참조 문서

- 전체 설계: [references/prompt.md](references/prompt.md)
- 13섹션 가이드: `detail-page-copy-framework/references/13-section-guide.md`
- 카피 패턴: `detail-page-copy-framework/references/copy-patterns.md`
- Gemini 프롬프트: `image-prompt-authoring/references/gemini-prompt-patterns.md`
- 디자인 스펙: `detail-page-design-system/references/design-specs.md`
- 데이터 규격: `detail-page-blueprint/SKILL.md`
