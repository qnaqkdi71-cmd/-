---
name: detail-page-render
description: 세일즈 상세페이지 데이터를 실제 PNG 이미지로 렌더링한다. output의 copy_output/design_direction을 합쳐 HTML/CSS로 그린 뒤 Chromium으로 캡처해 PNG 13장을 만든다. prompt-generator-agent가 마지막 단계에서 사용한다.
allowed-tools: Bash(python3:*), Read, Write
---

# 상세페이지 렌더 (HTML → PNG)

앞 단계 산출물을 합쳐 **상세페이지 이미지 13장**을 만든다. Gemini로 실제
이미지를 생성하기 전에도 즉시 미리보기를 얻는 HTML/CSS 렌더 경로다.

## 실행

프로젝트 루트에서:
```bash
python3 .claude/skills/detail-page-render/scripts/render.py
```

## 준비물 (output/)

| 파일 | 필수 | 내용 |
|------|------|------|
| `copy_output.json` | ✅ | 13섹션 카피 (copy-agent, 렌더레디) |
| `design_direction.json` | ✅ | 팔레트 + 섹션 배경 (design-direction-agent) |
| `structured_brief.json` | 선택 | 제품명·브랜드 |

스크립트가 `design_direction.json`의 color_palette + section_backgrounds로
섹션별 배경/글자/포인트 색을 해석하고, 섹션 template은 config의 청사진을 따른다.

## 결과물 (output/)
- `01_hero.png` … `13_final_cta.png` — 섹션별 이미지(폭 860px · 2x)
- `00_full_preview.png` — 전체 이어붙인 미리보기
- `renderplan.json` — 병합된 최종 렌더 명세

## 렌더 엔진
HTML/CSS 템플릿은 프로젝트 루트 `render/`, 데이터 스키마는 `contracts/`.
이 스크립트는 그 엔진을 재사용한다.

## 처음 실행 시
```bash
pip install playwright jinja2 pydantic pillow
```
Chromium은 이 환경에 사전설치. 필요 시 `CHROMIUM_PATH` 환경변수로 지정.
