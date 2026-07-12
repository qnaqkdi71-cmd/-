---
name: detail-page-blueprint
description: 커머스 상세페이지 제작의 공통 규격. 13개 섹션 청사진과 단계별 데이터 계약(brief/research/copydeck/designspec/renderplan JSON 스키마), workspace 파일 규약을 정의한다. 정보수집·리서치·카피·디자인·프롬프팅 에이전트가 모두 이 규격을 따른다.
---

# 상세페이지 청사진 & 데이터 계약

팀의 모든 에이전트는 이 규격을 공유한다. 산출물은 프로젝트 루트의
`workspace/` 폴더에 JSON으로 저장하고, 다음 담당자가 읽어 이어받는다.

## 파이프라인과 workspace 파일 규약

| 순서 | 담당 | 읽는 파일 | 쓰는 파일 | 스키마 |
|------|------|-----------|-----------|--------|
| 1 | info-collector | (사용자 입력) | `workspace/brief.json` | ProductBrief |
| 2 | market-researcher | `brief.json` | `workspace/research.json` | MarketResearch |
| 3 | copywriter | `brief.json`, `research.json` | `workspace/copydeck.json` | CopyDeck |
| 4 | designer | `copydeck.json`, `brief.json` | `workspace/designspec.json` | DesignSpec |
| 5 | dev-prompter | `copydeck.json`, `designspec.json` | `workspace/image_prompts.json` → 렌더 실행 | (아래 render 스킬) |

각 파일은 아래 스키마를 **정확히** 지켜야 다음 단계가 깨지지 않는다.

## 13-섹션 청사진 (id·순서 고정)

1. `hero` — 키비주얼·후킹 헤드라인
2. `trust` — 브랜드·신뢰 배지
3. `problem` — 고객 고민 제기
4. `solution` — 해결 제시
5. `feature_1` — 핵심 특징 1
6. `feature_2` — 핵심 특징 2
7. `feature_3` — 핵심 특징 3
8. `spec` — 상세 스펙·구성
9. `howto` — 사용법
10. `compare` — 비교·차별점
11. `review` — 고객 후기
12. `faq` — 자주 묻는 질문
13. `cta` — 구매 유도·안내

## 데이터 계약 (JSON 스키마)

### ProductBrief (brief.json)
```json
{
  "name": "string", "brand": "string", "category": "string",
  "price": "string", "target_customer": "string",
  "key_features": ["string"], "usp": ["string"],
  "specs": [{"label": "string", "value": "string"}],
  "tone": "string"
}
```

### MarketResearch (research.json)
```json
{
  "keywords": ["string"],
  "competitors": [{"name": "string", "positioning": "string", "weakness": "string"}],
  "customer_pains": ["string"], "objections": ["string"], "selling_angles": ["string"]
}
```

### CopyDeck (copydeck.json) — 13개 섹션
```json
{
  "sections": [
    {
      "id": "hero",
      "eyebrow": "string", "headline": "string", "subheadline": "string",
      "body": ["string"], "highlight": "string",
      "items": []
    }
  ]
}
```
`items`는 섹션 종류별로 채운다:
- spec: `{"label","value"}`  · howto: `{"title","desc"}`
- compare: `{"feature","us","others"}`  · review: `{"name","stars","text"}`
- faq: `{"q","a"}`  · trust: `{"label"}`
- hero/problem/solution/feature/cta: items 비워도 됨(body 사용)

### DesignSpec (designspec.json)
```json
{
  "theme": {"primary": "#hex", "accent": "#hex", "bg": "#hex", "text": "#hex", "mood": "string"},
  "sections": [
    {"id": "hero", "template": "hero", "bg": "#hex 또는 CSS gradient",
     "text": "#hex", "accent": "#hex", "image_slot": true}
  ]
}
```
`template` 허용값: `hero, trust, problem, solution, feature, spec, howto, compare, review, faq, cta`
(각 섹션 id의 기본 template은 청사진 순서와 동일)

### image_prompts.json (dev-prompter 작성)
```json
{ "hero": "영문 이미지 프롬프트", "feature_1": "...", "feature_2": "...", "feature_3": "..." }
```
`image_slot: true`인 섹션에 대해서만 작성한다.

## 공통 원칙
- 없는 스펙·수치·후기를 지어내지 않는다(제공 정보 기반).
- 색은 배경/텍스트 명암 대비를 충분히 확보한다.
- 섹션 id와 순서는 청사진을 벗어나지 않는다.
