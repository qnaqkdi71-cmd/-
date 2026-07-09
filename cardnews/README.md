# 카드뉴스 생성기 (cardnews)

주제 · 제목 · (선택)요구사항을 입력하면 LLM이 카피를 쓰고, **1080×1350 (4:5) 인스타그램
캐러셀 카드뉴스 6~10장**을 자동 완성하는 웹앱입니다.
"카드뉴스 자동 생성기 — 완전 핸드오프" 문서를 React + Vite + TypeScript로 재구현했습니다.

## 핵심 기능

- **디자인 스킨 4종** — `minimal`(애플풍) / `hand`(손글씨·모눈종이) / `bold`(볼드 매거진) / `pop`(비비드·테두리 글씨).
  카피는 `rawCards`로 원본 저장되고 렌더마다 `decorate()`가 스킨을 다시 입히므로 **생성 후에도 재생성 없이 즉시 교체**됩니다.
- **카드 타입 5종** — `cover` / `big`(핵심 수치) / `list`(3항목) / `point` / `cta`. LLM이 카드마다 타입을 지정합니다.
- **카드별 배경 이미지** (`none` / `ai` / `manual`)
  - `ai` + Unsplash 키 없음 → picsum 예시 사진 (키워드+시드의 결정적 해시라 카드마다 안정적, 🔄로 교체)
  - `ai` + Unsplash 키 있음 → 카드 키워드로 실사진 검색 (클라이언트에서 직접 호출, 사용자 본인 키)
  - `manual` → 드래그앤드롭/클릭 업로드 (IndexedDB에 카드별 안정 id `g{genId}-c{i}`로 영속)
- **모든 상태 localStorage 영속** — 키 `cardnews_generator_v1`. 새로고침·재접속에도 유지.
  (해석된 Unsplash URL은 저장하지 않고 재조회)

## 보안 원칙

**LLM API 키는 서버에만 있습니다.** 프론트엔드는 `POST /api/generate`로 입력값만 보내고,
서버(`server/index.mjs`)가 프롬프트를 조립해 Anthropic Messages API를 호출합니다.

## 실행

```bash
npm install

# 1) 서버 (LLM 프록시) — 키는 환경변수로만
ANTHROPIC_API_KEY=sk-ant-... npm run server   # http://localhost:8787

# 2) 프론트 개발 서버 (별도 터미널, /api → 8787 프록시)
npm run dev                                    # http://localhost:5173
```

프로덕션:

```bash
npm run build
ANTHROPIC_API_KEY=sk-ant-... npm start        # dist 정적 서빙 + /api, http://localhost:8787
```

환경변수는 `.env.example` 참고. 모델은 기본 `claude-sonnet-4-5`(핸드오프 문서 지정)이며
`CARDNEWS_MODEL`로 교체할 수 있습니다.

## 구조

```
server/
  index.mjs          # POST /api/generate (Anthropic SDK, 키는 여기만) + dist 정적 서빙
  prompt.mjs         # 프롬프트 계약 (문서 원문 그대로)
src/
  App.tsx            # 좌 420px 입력 패널 + 우 결과 그리드 2단 레이아웃
  types.ts           # RawCard/DecoratedCard/스킨·카테고리 상수
  state/useAppState.ts   # 상태 + localStorage(cardnews_generator_v1) 저장/복원 + generate()
  lib/decorate.ts    # 스킨 스타일링 엔진 (부록 A decorate() 포팅 — 색/타입 스케일 원본값)
  lib/parseCards.ts  # LLM 응답에서 첫 {...} JSON 추출
  lib/manualImages.ts    # 수동 업로드 이미지 IndexedDB 저장 (다운스케일 → WebP)
  hooks/useUnsplash.ts   # Unsplash 검색 해석 (캐시키·in-flight 디듑)
  components/
    InputPanel.tsx   # 스킨/카테고리/제목/요구사항/카드수/톤/핸들/Unsplash키/생성 버튼
    CardPreview.tsx  # 346×432 프레임 (scale 0.3204) + 이미지 모드 버튼/🔄/키워드 힌트
    CardView.tsx     # 실물 1080×1350 카드 (배경 레이어 + 콘텐츠 레이어)
    ImageDropSlot.tsx    # 수동 이미지 드래그앤드롭 슬롯
    EmptyState.tsx   # 빈/로딩 상태
```

## 원본 프로토타입과 다른 점 (의도적)

- `window.claude.complete` → 서버 엔드포인트 `/api/generate` (키 보안)
- `.dc.html` 커스텀 템플릿 런타임(`<sc-for>`, `{{ }}`)은 이식하지 않고 React로 재구현
- 수동 이미지 저장: `.image-slots.state.json` 사이드카 → IndexedDB (per-card id 계약은 동일)

## 주의

- 통계·수치는 프롬프트 규칙상 **실제 출처가 있는 것만** 사용하도록 강제합니다. 그래도 게시 전 출처 확인을 권장합니다.
- 가게 주소·별점 자동 수집은 구현하지 않았습니다(법적·API 제약). 실제 장소 사진은 `직접 넣기`가 안전합니다.
