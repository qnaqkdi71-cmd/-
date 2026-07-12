---
name: detail-page-copy-framework
description: 한국형 커머스 상세페이지 카피라이팅 프레임워크. 후킹→근거→신뢰→행동유도 흐름, AIDA/PAS 구조, 섹션별 카피 작성 지침과 톤 규칙을 담는다. copywriter 에이전트가 13섹션 카피를 쓸 때 사용한다.
---

# 상세페이지 카피 프레임워크

## 전체 흐름 (스크롤 설득 구조)

```
후킹    hero          → 3초 안에 시선·핵심 편익
공감    problem       → "이런 고민 있으셨죠?" 고객 언어로 통증 자극
전환    solution      → 그 통증을 우리 제품이 해결
신뢰    trust         → 판매량·인증·보증으로 안심
근거    feature×3     → USP를 하나씩 증명(숫자·원리)
정보    spec/howto    → 스펙·사용법으로 확신
비교    compare       → 경쟁 대비 우위를 표로
증거    review        → 실제 후기(사회적 증거)
해소    faq           → 구매 직전 반론 제거
행동    cta           → 가격·배송·보증 + 구매 유도
```

## 프레임워크

- **PAS**: Problem(문제) → Agitate(증폭) → Solve(해결). problem·solution 섹션에.
- **AIDA**: Attention → Interest → Desire → Action. 페이지 전체 골격.
- **FAB**: Feature(기능) → Advantage(장점) → Benefit(편익). feature 섹션은 항상
  "기능"이 아니라 "고객이 얻는 것"으로 끝맺는다. (예: "2000mAh" → "밤새 선 없이")

## 섹션별 지침

- **hero**: headline은 8~14자 내외, 두 줄 이내(줄바꿈은 `\n`). 핵심 편익 1개만.
- **problem**: body 3개, 고객이 실제로 내뱉을 법한 구어체.
- **feature_1~3**: 각 섹션 1개 USP. `highlight`에 숫자/키워드(예: `12h`, `25dB`).
- **compare**: `items`에 4행 내외. us는 강점, others는 일반 제품의 한계.
- **review**: 과장 금지. 별점 4~5, 사람 이름은 `김**` 형태. 구체적 상황 포함.
- **faq**: research의 objections(반론)를 Q로 만들어 A로 해소.
- **cta**: 가격·배송·교환/보증을 명확히. 클릭을 부르는 한 문장.

## 톤 규칙

- research의 `objections`를 카피 곳곳에서 선제적으로 해소한다.
- 과장·허위·근거 없는 수치("업계 1위" 등)는 쓰지 않는다.
- 짧고 스캔하기 좋게. 한 문장 = 한 메시지.
- 제품 `tone`(브리프)에 맞춰 어휘를 고른다.

## 작업 방법

1. `workspace/brief.json`과 `workspace/research.json`을 읽는다.
2. 위 흐름대로 13개 섹션 카피를 쓴다(청사진 id·순서 준수).
3. `detail-page-blueprint`의 CopyDeck 스키마에 맞춰
   `workspace/copydeck.json`으로 저장한다.
