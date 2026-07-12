---
name: detail-page-design-system
description: 세일즈 상세페이지 디자인 시스템. 스타일 프리셋 4종·컬러 팔레트·타이포·섹션 배경 규칙을 담는다. design-direction-agent가 design_direction.json을 만들 때 사용한다.
---

# 세일즈 상세페이지 디자인 시스템

## 1. 스타일 프리셋

| 프리셋 | 특징 | 적합 |
|--------|------|------|
| minimal | 깔끔·여백·신뢰 | SaaS, 프리미엄 서비스 |
| sales | 긴급·강조·에너지 | 한정 판매, 이벤트 |
| premium | 고급·절제·품격 | 고가·럭셔리 |
| community | 친근·따뜻·소속감 | 커뮤니티, 교육 |

## 2. 프리셋별 기본 팔레트

```
minimal:   primary #2563EB  accent #3B82F6  bg #FFFFFF  text #1F2937
sales:     primary #DC2626  accent #F59E0B  bg #FEF3C7  text #1F2937
premium:   primary #1F2937  accent #D4AF37  bg #F9FAFB  text #111827
community: primary #7C3AED  accent #EC4899  bg #FAF5FF  text #374151
```
브랜드 컬러가 있으면 primary/accent에 우선 반영한다. (뷰티·자연 계열은
그린/세이지 톤 권장)

## 3. 타이포그래피
- 헤드라인: Bold/Black, 48~72px, 행간 1.2
- 서브헤드: SemiBold, 24~32px, 행간 1.4
- 본문: Regular, 16~18px, 행간 1.6
- CTA: Bold, 18~24px

## 4. 섹션 배경 (section_backgrounds) — 렌더러 해석 키워드

각 섹션에 아래 키워드 중 하나를 지정하면 렌더러가 팔레트로 실제 색을 만든다:

| 키워드 | 결과 |
|--------|------|
| `background` | 기본 배경 + 진한 글자 |
| `background_alt` | 보조(연한) 배경 + 진한 글자 |
| `primary` / `primary with opacity` | primary 배경 + 흰 글자 |
| `gradient` / `primary gradient` | primary→어두운색 그라디언트 + 흰 글자 |

**리듬 권장 배치**: hero=primary gradient, pain=background_alt, problem=background,
story=background_alt, solution=primary, how_it_works=background_alt,
social_proof=background, authority=background_alt, benefits=primary with opacity,
risk_removal=background, comparison=background_alt, target_filter=background,
final_cta=primary gradient.

## 5. 원칙
- 배경/글자 명암 대비를 반드시 확보(어두운 배경엔 흰 글자).
- 색 수를 절제해 하나의 시스템으로 보이게.
- hero·final_cta는 강한 배경으로 시선을 잡는다.

출력 형식은 detail-page-blueprint의 design_direction.json 규격을 따른다.
