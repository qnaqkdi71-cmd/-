---
name: detail-page-render
description: 상세페이지 섹션 데이터를 실제 PNG 이미지로 렌더링한다. workspace의 copydeck/designspec/image_prompts를 합쳐 HTML/CSS로 그린 뒤 Chromium으로 캡처해 output/에 PNG 13장을 만든다. dev-prompter 에이전트가 마지막 단계에서 사용한다.
allowed-tools: Bash(python3:*), Read, Write
---

# 상세페이지 렌더 (HTML → PNG)

이 스킬은 앞 단계 산출물을 합쳐 **상세페이지 이미지 13장**을 만든다.
Playwright + 사전설치 Chromium으로 HTML/CSS를 스크린샷한다.

## 실행 방법

프로젝트 루트에서 아래 한 줄을 실행한다:

```bash
python3 .claude/skills/detail-page-render/scripts/render.py
```

## 준비물 (workspace/)

| 파일 | 필수 | 내용 |
|------|------|------|
| `copydeck.json` | ✅ | 13섹션 카피 (copywriter 산출) |
| `designspec.json` | ✅ | 디자인 시스템 (designer 산출) |
| `brief.json` | 선택 | 제품명 등 |
| `image_prompts.json` | 선택 | 이미지 슬롯 프롬프트 (dev-prompter 산출) |

스크립트가 이들을 병합해 `workspace/renderplan.json`을 만들고 렌더한다.

## 결과물 (output/)

- `01_hero.png` … `13_cta.png` — 섹션별 이미지(폭 860px·2x 고해상도)
- `00_full_preview.png` — 13장을 세로로 이어붙인 전체 미리보기

## 렌더 엔진 위치

실제 HTML/CSS 템플릿과 Playwright 코드는 프로젝트 루트의 `render/`,
데이터 스키마는 `contracts/`에 있다. 이 스크립트는 그 엔진을 재사용한다.

## 처음 실행 시 (의존성)

필요 패키지가 없다면 한 번만:
```bash
pip install playwright jinja2 pydantic pillow
```
Chromium은 이 환경에 사전설치되어 있다. 없다면 `playwright install chromium`.

## 문제 해결

- `workspace/copydeck.json 없음` → 카피/디자인 단계를 먼저 끝낸다.
- Chromium 실행 오류 → `config.py`의 `CHROMIUM_PATH`가 자동 탐색한다.
  필요하면 환경변수 `CHROMIUM_PATH`로 직접 지정한다.
