# 상세페이지 에이전트 (Detail Page Agent)

제품 정보를 주면 **5명의 AI 에이전트가 팀으로 협업**해 **세일즈형 상세페이지**를
만들고, **섹션 이미지(PNG) 13장**으로 내보냅니다. Claude Code의 공식 기능
(**서브에이전트 · 스킬 · Agent Teams**)으로 구성되어 있습니다.

```
정보수집(intake) → 리서치(research) → 카피(copy)
        → 디자인(design-direction) → 프롬프팅/렌더(prompt-generator) → PNG 13장
```

---

## 🟢 두 가지 실행 방법

### 방법 A — 빠른 데모 (코딩 몰라도 됨)
동봉된 예시(어린녹차 크림)로 결과를 바로 확인합니다.
```bash
cd detail-page-agent
pip install playwright jinja2 pydantic pillow
python3 main.py
```
→ `output/` 폴더에 PNG 13장 + 전체 미리보기가 생깁니다.

### 방법 B — 진짜 사용 (Claude Code 팀 에이전트)
1. 이 `detail-page-agent` 폴더를 **Claude Code로 엽니다.**
2. 팀 리드에게: *"이 제품으로 상세페이지 만들어줘: [제품명/특징/스펙]"*
3. 5명의 에이전트가 순서대로 협업해 `output/`에 PNG 13장을 만듭니다.

---

## 🗂️ 무엇이 어디에 있나요?

```
detail-page-agent/
├── .claude/
│   ├── settings.json                     팀 기능 ON + 권한
│   ├── agents/   ── 5명의 에이전트(참고 사양 반영) ──
│   │   ├── intake-agent.md               ① 정보수집  (haiku)
│   │   ├── research-agent.md             ② 리서치    (sonnet)
│   │   ├── copy-agent.md                 ③ 카피      (sonnet)
│   │   ├── design-direction-agent.md     ④ 디자인    (haiku)
│   │   └── prompt-generator-agent.md     ⑤ 프롬프팅  (sonnet)
│   └── skills/   ── 에이전트가 쓰는 지식·도구 ──
│       ├── detail-page-blueprint/         13섹션 청사진 + 데이터 규격
│       ├── detail-page-copy-framework/    세일즈 카피 프레임워크
│       ├── detail-page-design-system/     프리셋·팔레트·섹션 배경
│       ├── image-prompt-authoring/        Gemini 이미지 프롬프트(1200px 실사)
│       └── detail-page-render/scripts/render.py   HTML→PNG 렌더
├── examples/sample_output/               예시 데이터(어린녹차)
├── output/                               최종 PNG 13장이 생기는 곳
├── render/ · contracts/ · config.py      렌더 엔진·스키마·설정(공용)
└── main.py                               빠른 데모 실행기
```

## 🤝 팀은 이렇게 일합니다 (output/ 릴레이)

| 순서 | 에이전트 | 읽기 | 쓰기 |
|------|---------|------|------|
| ① | intake-agent | 사용자 입력 | `structured_brief.json` |
| ② | research-agent | structured_brief | `research_output.json` |
| ③ | copy-agent | brief + research | `copy_output.json` |
| ④ | design-direction-agent | copy_output | `design_direction.json` |
| ⑤ | prompt-generator-agent | copy + design | `gemini_prompts.json` + 렌더 실행 |

## 📄 세일즈형 13섹션

`hero · pain · problem · story · solution · how_it_works · social_proof ·
authority · benefits · risk_removal · comparison · target_filter · final_cta`

## 🎨 이미지 두 가지 경로

- **HTML 렌더(즉시)**: 렌더 스킬이 카피+디자인을 HTML/CSS로 그려 PNG 13장을
  바로 만듭니다. 한글 텍스트가 정확합니다.
- **Gemini 프롬프트(고급)**: prompt-generator가 `gemini_prompts.json`(1200px·
  실사 스타일)을 만듭니다. Gemini로 실제 광고 컷을 생성해 교체할 수 있습니다.

## 🔧 커스터마이즈
- 섹션 구성·데이터 규격: `.claude/skills/detail-page-blueprint/SKILL.md`
- 카피 톤: `.claude/skills/detail-page-copy-framework/SKILL.md`
- 디자인 프리셋: `.claude/skills/detail-page-design-system/SKILL.md`
- 레이아웃 템플릿(HTML/CSS): `render/templates.py`
- 에이전트 역할/모델: `.claude/agents/*.md`
