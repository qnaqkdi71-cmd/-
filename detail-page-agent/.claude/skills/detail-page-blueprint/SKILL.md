---
name: detail-page-blueprint
description: 세일즈형 상세페이지 제작의 공통 규격. 13개 섹션 청사진과 단계별 데이터 계약(structured_brief/research_output/copy_output/design_direction/gemini_prompts), output 파일 규약을 정의한다. 모든 에이전트가 이 규격을 따른다.
---

# 세일즈 상세페이지 청사진 & 데이터 계약

모든 산출물은 프로젝트 루트의 `output/` 폴더에 JSON으로 저장하고, 다음
담당자가 읽어 이어받는다.

## 파이프라인과 파일 규약 (output/)

| 순서 | 담당 | 읽기 | 쓰기 |
|------|------|------|------|
| 1 | intake-agent | 사용자 입력 | `structured_brief.json` |
| 2 | research-agent | structured_brief | `research_output.json` |
| 3 | copy-agent | brief + research | `copy_output.json` |
| 4 | design-direction-agent | copy_output | `design_direction.json` |
| 5 | prompt-generator-agent | copy + design | `gemini_prompts.json` + 렌더 실행 |

## 13-섹션 청사진 (id·순서 고정)

1. `hero` — 히어로·후킹
2. `pain` — 공감(페인)
3. `problem` — 문제 정의
4. `story` — 변화 스토리(Before→After)
5. `solution` — 솔루션 소개
6. `how_it_works` — 작동 방식
7. `social_proof` — 사회적 증거
8. `authority` — 권위·신뢰
9. `benefits` — 혜택·보너스
10. `risk_removal` — 리스크 제거
11. `comparison` — 최종 대비(있으면/없으면)
12. `target_filter` — 타겟 필터(추천/비추천)
13. `final_cta` — 최종 CTA

## copy_output.json (렌더레디) — copy-agent 출력

렌더러가 바로 소비하는 정규화 형식. 13개 섹션을 이 형식으로 채운다:

```json
{ "sections": [
  { "id": "hero", "eyebrow": "", "headline": "", "subheadline": "",
    "body": [], "highlight": "", "items": [] }
] }
```

`items`는 섹션별로 채운다:
- story: `[{"text": "before"}, {"text": "after"}]`
- how_it_works: `[{"title","desc"}]`
- social_proof: `[{"name","stars","text"}]`
- authority: `[{"label"}]`
- benefits: `[{"label","value"}]` (보너스)
- risk_removal: `[{"q","a"}]`
- comparison / target_filter: `[{"good","bad"}]` (+ body에 [좋은 헤더, 나쁜 헤더])

(각 섹션의 eyebrow/headline/… 매핑은 copy-agent 정의의 매핑표 참고)

## design_direction.json — design-direction-agent 출력

```json
{
  "style_preset": "premium",
  "color_palette": {"primary": "#...", "accent": "#...", "background": "#ffffff",
                    "background_alt": "#...", "text_primary": "#..."},
  "section_backgrounds": {"hero": "primary gradient", "pain": "background_alt", ...}
}
```
- 렌더러가 `section_backgrounds` 키워드(background / background_alt / primary /
  primary with opacity / gradient / primary gradient)와 팔레트로 섹션별
  배경·글자·포인트 색을 자동 해석한다.

## structured_brief.json — intake-agent 출력
product_name, brand, one_liner, target_audience, main_problem, key_benefit,
price{original,discounted}, urgency{type,value,bonus}, testimonials, creator_bio,
bonus_items, guarantee, faq, brand_color.

## research_output.json — research-agent 출력
pain_points[5], failure_reasons[3], after_image, objections, differentiators,
message_framework.

## 공통 원칙
- 없는 정보·수치·후기를 지어내지 않는다.
- 섹션 id·순서는 청사진을 벗어나지 않는다.
- 배경/글자 명암 대비를 확보한다.
