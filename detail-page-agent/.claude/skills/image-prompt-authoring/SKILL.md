---
name: image-prompt-authoring
description: 13개 섹션별 Gemini 이미지 생성 프롬프트 작성법. 1200px 크기 고정, 실사 사진 스타일, 풀 블리드, 섹션별 프롬프트 템플릿을 담는다. prompt-generator-agent가 gemini_prompts.json을 만들 때 사용한다.
---

# Gemini 이미지 프롬프트 작법 (개발용)

카피(copy_output.json) + 디자인(design_direction.json)을 바탕으로 13개
섹션 이미지의 Gemini 생성 프롬프트를 만든다.

## ⚠️ 필수 준수 (CRITICAL)

### 1. 크기 고정 (DIMENSION LOCK)
- 너비는 **반드시 정확히 1200px**. 그 외 너비 금지.
- 높이는 섹션별 400~800px 가변.
- 이미지가 1200px 전체를 **마진 없이** 채운다.

### 2. 실사 사진 스타일 (MANDATORY)
- **일러스트/카툰/만화 금지.** 인물은 실제 모델(자연스러운 피부 질감).
- 설화수·이니스프리·라네즈 광고 수준의 리얼리스틱 품질.
- 전문 조명·구도.

### 3. 풀 블리드 (FULL BLEED)
- 좌우 마진·테두리 없이 가장자리까지 콘텐츠가 채움.

## 공통 프롬프트 구조 (모든 섹션 공통 앵커)

```
Create a professional landing page section image.

=== CRITICAL ===
1. EXACT DIMENSIONS: 1200x[HEIGHT] pixels - MUST be exactly 1200px wide
2. FULL BLEED: fills ENTIRE 1200px width, NO margins/borders

=== PHOTOGRAPHY STYLE (MANDATORY) ===
- REALISTIC PHOTOGRAPHY, NOT illustrations/cartoons
- Real human models with natural skin texture when people appear
- Photo-realistic like high-end Korean beauty ads (Sulwhasoo, Innisfree, Laneige)

=== DESIGN ===
- Style: [style_preset]; Palette: primary [color], accent [color], bg [color]

=== LAYOUT / TEXT (Korean) / VISUAL ELEMENTS ===
[섹션별 지시 + 정확한 한글 텍스트]

=== FINAL CHECKLIST ===
✓ EXACTLY 1200x[HEIGHT]px  ✓ full width no margins
✓ realistic photos not illustrations  ✓ Korean text clear  ✓ ad-quality
```

## 섹션별 높이 가이드
hero 800 · pain 600 · problem 500 · story 700 · solution 400 · how_it_works 600 ·
social_proof 800 · authority 500 · benefits 700 · risk_removal 500 ·
comparison 400 · target_filter 400 · final_cta 600

## 출력: `output/gemini_prompts.json`
```json
{ "section_01_hero": {"prompt": "...", "width": 1200, "height": 800, "filename": "01_hero.png"} }
```

## 작성 원칙
1. 구체적 레이아웃 지시(위치·크기·정렬)
2. 정확한 한글 텍스트 포함(모델은 글자에 약하니 명확히 요청)
3. 모든 섹션 동일 스타일 앵커
4. 시각적 계층(중요도별 크기/색)

## 참고 문헌 (필요 시 열어보기)
- `references/gemini-prompt-patterns.md` — Gemini 베스트 프랙티스(공통 구조,
  스타일·컬러·레이아웃 지시어, 한글 렌더링 3방법, 섹션별 프롬프트 예시,
  피해야 할 것, 스타일 앵커·시리즈 명시 팁)
