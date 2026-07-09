# 카드뉴스 생성기 (cardnews)

주제 · 제목 · (선택)요구사항을 입력하면 LLM이 카피를 쓰고, **1080×1350 (4:5) 인스타그램
캐러셀 카드뉴스 6~10장**을 자동 완성하는 웹앱입니다.
"카드뉴스 자동 생성기 — 완전 핸드오프" 문서를 React + Vite + TypeScript로 재구현했습니다.

## 핵심 기능

- **디자인 스킨 4종** — `minimal`(애플풍) / `hand`(손글씨·모눈종이) / `bold`(볼드 매거진) / `pop`(비비드·테두리 글씨).
  카피는 `rawCards`로 원본 저장되고 렌더마다 `decorate()`가 스킨을 다시 입히므로 **생성 후에도 재생성 없이 즉시 교체**됩니다.
- **카드 타입 5종** — `cover` / `big`(핵심 수치) / `list`(3항목) / `point` / `cta`. LLM이 카드마다 타입을 지정합니다.
- **가게 검색** (선택) — 카카오/네이버 무료 검색 API를 **서버 프록시**로 호출해 상호·주소·카테고리·전화·좌표를
  가져옵니다. 선택한 가게는 카피에 사실로 반영됩니다. **별점·리뷰·리뷰사진은 수집하지 않습니다**(법적·API 제약).
- **카드별 배경 이미지** (`none` / `ai`(주제 사진) / `place`(가게 지도) / `manual`(직접 업로드))
  - `ai` — 카테고리·카드 내용에 맞는 **주제 사진 자동**. Unsplash 키가 있으면 실사진(클라이언트 직접),
    없으면 서버의 **키리스 Openverse(CC0·공개도메인)** 사용, 그마저 실패하면 picsum 예시(결정적 해시)로 폴백.
  - `place` — 선택한 가게의 **위치 정적 지도**(네이버 클라우드 Maps). 지도 키 미설정 시 가게명 주제 사진으로 폴백.
  - `manual` — 드래그앤드롭/클릭 업로드 (IndexedDB에 카드별 안정 id `g{genId}-c{i}`로 영속)
- **모든 상태 localStorage 영속** — 키 `cardnews_generator_v1`. 새로고침·재접속에도 유지.
  (해석된 Unsplash URL은 저장하지 않고 재조회)

## 보안 원칙

**LLM API 키는 서버에만 있습니다.** 프론트엔드는 `POST /api/generate`로 입력값만 보내고,
서버(`server/index.mjs`)가 프롬프트를 조립해 Anthropic Messages API를 호출합니다.

## 실행

```bash
npm install

# 1) 서버 (LLM 프록시 + 가게 검색/지도/사진 프록시) — 키는 환경변수로만
ANTHROPIC_API_KEY=sk-ant-... \
  KAKAO_REST_KEY=... NAVER_SEARCH_ID=... NAVER_SEARCH_SECRET=... \
  npm run server                               # http://localhost:8787

# 2) 프론트 개발 서버 (별도 터미널, /api → 8787 프록시)
npm run dev                                    # http://localhost:5173
```

가게 검색·지도 키는 **선택**입니다. 안 넣으면 해당 UI가 자동으로 숨겨지고, 카드 배경은 주제 사진(Openverse/Unsplash)만 씁니다.
전체 환경변수는 `.env.example` 참고.

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
  index.mjs          # /api/generate · /api/place · /api/photo · /api/staticmap · /api/config + dist 정적 서빙
  prompt.mjs         # 프롬프트 계약 (문서 원문 + 선택한 가게 사실 주입, 별점 날조 금지)
  place.mjs          # 카카오/네이버 검색 프록시 → 사실 정보 정규화 (별점·리뷰 없음)
  photo.mjs          # Openverse CC0 키리스 주제 사진 검색
  staticmap.mjs      # 네이버 클라우드 Maps 정적 지도 프록시 (선택)
src/
  App.tsx            # 좌 420px 입력 패널 + 우 결과 그리드 2단 레이아웃 + config 로드
  types.ts           # RawCard/DecoratedCard/Place/AppConfig/스킨·카테고리 상수
  state/useAppState.ts   # 상태 + localStorage(cardnews_generator_v1) 저장/복원 + generate()
  lib/decorate.ts    # 스킨 스타일링 엔진 (부록 A decorate() 포팅). 배경 URL은 외부 주입
  lib/parseCards.ts  # LLM 응답에서 첫 {...} JSON 추출
  lib/manualImages.ts    # 수동 업로드 이미지 IndexedDB 저장 (다운스케일 → WebP)
  hooks/useCardImages.ts # 카드별 배경 해석: 지도 / Unsplash / Openverse / picsum 폴백
  components/
    InputPanel.tsx   # 스킨/카테고리/(가게검색)/제목/요구사항/카드수/톤/핸들/Unsplash키/생성
    PlaceSearch.tsx  # 가게 검색 UI (제공자 선택·결과 리스트·선택 칩)
    CardPreview.tsx  # 346×432 프레임 (scale 0.3204) + 주제사진/🗺지도/직접넣기/끄기/🔄
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
- 가게 **별점·리뷰·리뷰사진은 의도적으로 수집하지 않습니다**(약관·저작권·데이터베이스권 리스크). 상호·주소·카테고리 같은
  사실 정보만 공식 검색 API로 가져옵니다.
- 가게의 "실제 외관 사진"을 자동으로 합법적으로 가져올 깨끗한 경로는 없어서, 가게 배경은 **위치 지도**로 대체합니다.
  실제 매장 사진이 필요하면 `직접 넣기`(본인 촬영 사진)가 가장 안전합니다.
- 주제 사진 자동 소스는 **CC0/공개도메인(Openverse)** 만 사용해 저작자 표기 없이 재사용 가능합니다.
