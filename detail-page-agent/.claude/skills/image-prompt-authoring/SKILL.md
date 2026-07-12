---
name: image-prompt-authoring
description: 상세페이지 이미지 슬롯에 넣을 이미지 생성 프롬프트(영문) 작성법. 피사체·구도·조명·분위기·품질 키워드 구성과 예시를 담는다. dev-prompter 에이전트가 image_prompts.json을 만들 때 사용한다.
---

# 이미지 생성 프롬프트 작법 (개발용)

`image_slot: true`인 섹션마다, 이미지 생성 모델(Midjourney/이미지 API 등)에
넣을 **영문 프롬프트**를 만든다. 이후 실제 컷을 이 프롬프트로 생성해 자리에
끼운다.

## 프롬프트 구성 공식

```
[피사체] + [컨셉/상황] + [배경] + [조명] + [분위기·스타일] + [품질] + [파라미터]
```

- **피사체**: 제품명·형태를 구체적으로.
- **컨셉**: 해당 섹션 헤드라인과 연결(예: "12시간 지속" → 밤 침실 장면).
- **배경**: 상세페이지에 어울리는 깔끔한 스튜디오/라이프스타일.
- **조명**: soft natural light, studio lighting 등.
- **스타일**: minimalist Korean e-commerce detail page style.
- **품질**: high detail, sharp focus, 4k.
- **파라미터**: `--ar 4:3`(feature), `--ar 16:9`(hero) 등.

## 중요 규칙

- **화면에 글자를 넣지 않는다.** 이미지 모델은 텍스트에 약하므로, 문구는
  이후 오버레이한다고 전제한다. ("no text, no letters"를 넣어도 좋다.)
- 모든 컷의 제품 정체성(색·형태)을 일관되게 유지한다.
- 과장된 성능 묘사(연기/과한 안개 등)는 피하고 사실적으로.

## 예시

- hero: `Product photography of a wireless mini humidifier on a bedside table, soft mist, cozy dim bedroom at night, warm ambient light, minimalist Korean e-commerce style, high detail, no text --ar 16:9`
- feature(저소음): `Close-up of a wireless mini humidifier beside a sleeping person's nightstand, calm quiet mood, soft blue night light, shallow depth of field, clean minimalist style, no text --ar 4:3`

## 작업 방법

1. `workspace/copydeck.json`과 `workspace/designspec.json`을 읽는다.
2. `image_slot: true`인 섹션 id마다 위 공식으로 프롬프트를 만든다.
3. `{ "섹션id": "영문 프롬프트" }` 형태로 `workspace/image_prompts.json` 저장.
