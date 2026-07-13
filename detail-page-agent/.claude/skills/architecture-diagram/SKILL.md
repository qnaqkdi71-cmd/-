---
name: architecture-diagram
description: 상세페이지 생성기의 시스템 구조도(파이프라인 다이어그램)를 일관된 스타일로 그린다. 역할별 색상 팔레트와 Mermaid 템플릿을 따른다. "구조도/아키텍처/다이어그램 그려줘" 요청 시 사용한다.
---

# 아키텍처 다이어그램 스킬

상세페이지 에이전트 시스템의 구조도를 **일관된 색상·이모지 규칙**으로 그린다.

## 색상 규칙 (역할별)

| 역할 | 배경/테두리 |
|------|-------------|
| 🟡 메인/오케스트레이터 | `#fff59d` / `#f9a825` |
| 🔵 기획팀(정보수집·리서치) | `#bbdefb` / `#1976d2` |
| 🟢 카피팀 | `#c8e6c9` / `#388e3c` |
| 🟠 디자인팀 | `#ffe0b2` / `#f57c00` |
| 🟣 개발팀(프롬프팅) | `#e1bee7` / `#8e24aa` |
| 🟣 스크립트/자동화 | `#d1c4e9` / `#512da8` |
| 🔴 결과물/출력 | `#ffcdd2` / `#c62828` |

## 작성 방법

1. `references/diagram-style-preset.md`의 Mermaid 템플릿을 복사한다.
2. 이 프로젝트의 실제 구조(intake→research→copy→design→prompt→render→PNG 13장)에
   맞춰 노드 내용을 채운다.
3. 노드는 `["이모지 제목<br/>부제목<br/>───<br/>상세1<br/>상세2"]` 형식.
4. 병렬은 `A-->B` `A-->C` 후 `B-->D` `C-->D`로 합류 표현.
5. Whimsical MCP(`mcp__whimsical__create_whimsical_diagram`)가 있으면 그것으로
   렌더하고, 없으면 Mermaid 코드 블록으로 제시한다.

## 상세 규칙·전체 예시
→ `references/diagram-style-preset.md` 참고 (색상표·Mermaid 전체 템플릿·
   상세페이지 생성기 구조 예시·이모지 가이드 포함).
