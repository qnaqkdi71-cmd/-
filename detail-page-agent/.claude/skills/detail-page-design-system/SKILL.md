---
name: detail-page-design-system
description: 커머스 상세페이지 디자인 시스템. 컬러·명암 대비 규칙, 11종 섹션 레이아웃 템플릿 카탈로그, 배경/텍스트 페어링과 이미지 슬롯 배치 원칙을 담는다. designer 에이전트가 designspec.json을 만들 때 사용한다.
---

# 상세페이지 디자인 시스템

## 컬러 원칙

- 제품 카테고리·톤에 맞는 `primary`(메인)와 `accent`(포인트) 2색을 중심으로.
- 색 수를 절제해 하나의 시스템으로 보이게 한다.
- **명암 대비 필수**: 밝은 배경 → 어두운 텍스트, 어두운 배경 → 밝은 텍스트.
  - 밝은 섹션 예: bg `#ffffff`/`#f2f7f3`, text `#1b2b24`
  - 어두운 섹션 예: bg `#16241d`, text `#eaf1ec`
- hero·cta는 그라디언트로 강조: `linear-gradient(160deg,#PRIMARY 0%,#DARK 100%)`.

## 리듬(배경 교차)

밝음→밝음이 계속되면 지루하다. 어두운 섹션(problem, spec)과 톤 배경(trust,
howto, review)을 섞어 스크롤에 리듬을 준다. 예시 배치:

| 섹션 | 배경 | 텍스트 | image_slot |
|------|------|--------|-----------|
| hero | 그라디언트(강) | 밝게 | ✅ |
| trust | 톤(연) | 어둡게 | — |
| problem | 어둡게 | 밝게 | — |
| solution | primary | 밝게 | — |
| feature_1 | 흰색 | 어둡게 | ✅ |
| feature_2 | 톤(연) | 어둡게 | ✅ |
| feature_3 | 흰색 | 어둡게 | ✅ |
| spec | 어둡게 | 밝게 | — |
| howto | 톤(연) | 어둡게 | — |
| compare | 흰색 | 어둡게 | — |
| review | 톤(연) | 어둡게 | — |
| faq | 흰색 | 어둡게 | — |
| cta | 그라디언트(강) | 밝게 | — |

## 11종 레이아웃 템플릿 (renderer가 지원)

`hero`(대형 헤드라인+이미지), `trust`(중앙 배지 행), `problem`(체크리스트),
`solution`(체크리스트), `feature`(좌우 2단: 텍스트+이미지, 자동 좌우 교차),
`spec`(2열 표), `howto`(3단계 카드), `compare`(비교 표), `review`(후기 카드),
`faq`(Q&A), `cta`(중앙 정렬+버튼).

각 섹션 id의 기본 template은 청사진과 동일하게 둔다(hero→hero, spec→spec …).

## 이미지 슬롯

`feature_*`와 `hero`처럼 제품 사진이 필요한 섹션은 `image_slot: true`로 둔다.
렌더러가 자리(placeholder)를 잡고, dev-prompter가 그 자리에 넣을 이미지
생성 프롬프트를 따로 만든다.

## 작업 방법

1. `workspace/copydeck.json`(과 `brief.json`)을 읽는다.
2. theme 2색과 mood를 정하고, 13개 섹션 각각의 bg/text/accent/image_slot을
   위 리듬·대비 규칙에 맞춰 정한다.
3. `detail-page-blueprint`의 DesignSpec 스키마에 맞춰
   `workspace/designspec.json`으로 저장한다.
