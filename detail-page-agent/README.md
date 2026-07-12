# 상세페이지 에이전트 (Detail Page Agent)

제품 정보를 주면 **5명의 AI 에이전트가 팀으로 협업**해 한국형 커머스
상세페이지를 만들고, **섹션 이미지(PNG) 13장**으로 내보냅니다.
Claude Code의 공식 기능(**서브에이전트 · 스킬 · Agent Teams**)으로 구성되어 있습니다.

```
정보수집 → 리서치 → 카피라이팅 → 디자인 → 프롬프팅/렌더 → PNG 13장
```

---

## 🟢 처음이신가요? 두 가지 실행 방법

### 방법 A — 빠른 데모 (코딩 몰라도 됩니다)
Claude 없이, 동봉된 샘플 제품으로 결과가 어떻게 나오는지 바로 봅니다.
```bash
cd detail-page-agent
pip install playwright jinja2 pydantic pillow
python3 main.py --mock
```
→ `output/` 폴더에 PNG 13장이 생깁니다.

### 방법 B — 진짜 사용 (Claude Code 팀 에이전트)
1. 이 `detail-page-agent` 폴더를 **Claude Code로 엽니다.**
2. 팀 리드(메인 세션)에게 이렇게 말합니다:
   > "이 제품으로 상세페이지 만들어줘: [제품명 / 스펙 / 특징]"
3. 5명의 에이전트가 순서대로 협업해 `output/`에 PNG 13장을 만듭니다.

> `.claude/settings.json`에 팀 기능 플래그가 이미 켜져 있습니다. Claude Code가
> 이 폴더를 열면 서브에이전트·스킬을 자동으로 인식합니다.

---

## 🗂️ 무엇이 어디에 있나요?

```
detail-page-agent/
├── .claude/                         ← Claude Code가 읽는 폴더
│   ├── settings.json                  팀 기능 켜기 + 권한
│   ├── agents/                        ── 5명의 에이전트(팀원) ──
│   │   ├── info-collector.md          ① 정보수집
│   │   ├── market-researcher.md       ② 리서치
│   │   ├── copywriter.md              ③ 카피라이팅
│   │   ├── designer.md                ④ 디자인
│   │   └── dev-prompter.md            ⑤ 프롬프팅·렌더
│   └── skills/                        ── 에이전트가 쓰는 지식·도구 ──
│       ├── detail-page-blueprint/       13섹션 청사진 + 데이터 규격
│       ├── detail-page-copy-framework/  카피 작성법
│       ├── detail-page-design-system/   디자인 규칙
│       ├── image-prompt-authoring/      이미지 프롬프트 작법
│       └── detail-page-render/          HTML→PNG 렌더(+스크립트)
├── workspace/                       ← 단계별 산출물(JSON)이 여기 쌓임
├── output/                          ← 최종 PNG 13장이 여기 생김
├── render/, contracts/             ← 렌더 엔진·데이터 스키마(공용)
├── agents/, prompts/, main.py      ← 방법 A(빠른 데모)용 코드
└── examples/sample_input.json      ← 샘플 제품
```

## 🤝 팀은 이렇게 일합니다 (Agent Teams)

각 에이전트는 자기 결과를 `workspace/`에 JSON으로 저장하고, 다음 담당자가
그걸 읽어 이어받습니다(순차 릴레이).

| 순서 | 에이전트 | 읽기 | 쓰기 |
|------|---------|------|------|
| ① | info-collector (haiku) | 사용자 입력 | `brief.json` |
| ② | market-researcher (opus) | `brief.json` | `research.json` |
| ③ | copywriter (opus) | brief + research | `copydeck.json` |
| ④ | designer (opus) | copydeck | `designspec.json` |
| ⑤ | dev-prompter (opus) | copydeck + designspec | `image_prompts.json` → 렌더 실행 |

마지막에 dev-prompter가 렌더 스킬을 실행해 `output/`에 PNG 13장을 만듭니다.

## 🎨 결과물 (output/)

- `01_hero.png` … `13_cta.png` — 섹션별 이미지(폭 860px · 2x 고해상도)
- `00_full_preview.png` — 13장을 세로로 이어붙인 전체 미리보기

## 🔧 커스터마이즈

- 섹션 구성/데이터 규격: `.claude/skills/detail-page-blueprint/SKILL.md`
- 카피 톤·전략: `.claude/skills/detail-page-copy-framework/SKILL.md`
- 디자인 규칙: `.claude/skills/detail-page-design-system/SKILL.md`
- 레이아웃 템플릿(HTML/CSS): `render/templates.py`
- 에이전트 역할/모델: `.claude/agents/*.md`의 frontmatter
