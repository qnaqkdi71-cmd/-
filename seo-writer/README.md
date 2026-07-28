# 랭크업 · 구글 상위노출 글 자동작성기

키워드(또는 초안)를 넣으면 → **이길 수 있는 키워드인지 판별**하고 → **검색 의도·E-E-A-T·5대 태그**를
반영한 **상위노출용 글**을 써 주는 프로그램입니다. 유튜브 SEO 전문가 5인의 노하우를 코드로 옮겼습니다.

> ⚠️ 솔직히: 어떤 도구도 1등을 100% 보장할 수는 없습니다(순위엔 사이트 권위·백링크·시간도 작용).
> 이 도구는 **내가 통제할 수 있는 74%(콘텐츠 57% + 온페이지·링크 설계)를 최대로** 끌어올려
> 상위노출 **확률을 극대화**합니다.

## 무료로 시작 (키 없이도 실행됨)

```bash
cd seo-writer
python -m venv .venv && source .venv/bin/activate    # (윈도우: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env         # 키는 나중에 채워도 됨
uvicorn app:app --reload
# → http://localhost:8000
```

### 윈도우는 더 쉽게 — 원클릭
윈도우 사용자는 명령어 없이, `seo-writer` 폴더의 **`run-windows.bat` 더블클릭** 한 번이면 됩니다.
(최초 실행 시 가상환경 생성 → 메모장으로 `.env`에 키 입력 → 패키지 설치 → 서버 실행 → 브라우저 자동 열림)
전제: [python.org](https://www.python.org/downloads/)에서 Python 설치 시 **"Add python.exe to PATH" 체크**.

**키가 하나도 없어도** 경쟁분석 링크·글 구조(골격)·온페이지 세팅·SEO 점수·배포 플랜까지 다 보여줍니다.

## 무료 AI 연결 (실제 글 자동작성)

1. [aistudio.google.com](https://aistudio.google.com) 에서 **무료 Gemini API 키** 발급
2. `.env` 파일에 입력:
   ```
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=여기에_키
   GEMINI_MODEL=gemini-2.5-flash     # 무료는 Flash 계열만 · Pro(유료/크레딧)는 gemini-2.5-pro
   ```
3. 서버 재시작 → 이제 실제 글이 작성됩니다.

## (선택) 경쟁분석 자동화 — Serper

`.env`에 `SERPER_API_KEY`를 넣으면 `allintitle` 실경쟁자 수 + 상위 10개 글을 **자동** 조회합니다.
없으면 `allintitle` 링크를 눌러 직접 확인하는 **수동 모드**(영구 무료)로 동작합니다.
→ [serper.dev](https://serper.dev) 가입 시 무료 크레딧 제공.

## 이미지 자동 생성 (Gemini)

글에 어울리는 **이미지를 Gemini로 자동 생성**해 본문에 붙입니다. **글쓰기와 같은 `GEMINI_API_KEY`·크레딧**을 재사용하므로 추가 발급이 없습니다. (결제/Paid tier 필요 — 이미지 생성은 유료·크레딧)

`.env`에서:
```
IMAGE_PROVIDER=gemini
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image   # 상세페이지에서 쓰던 모델로 맞추면 됨(예: imagen-4.0-generate-001)
IMAGE_ASPECT=16:9
IMAGE_COUNT=3          # 대표 1 + 본문 2
```
동작 원리: 글이 만들어낸 **이미지 alt(설명)** → 이미지 프롬프트로 변환 → 생성 → 결과 화면에 **갤러리 + 다운로드**로 표시. 끄려면 `IMAGE_PROVIDER=none` 또는 생성 화면의 체크박스 해제.

> ⚠️ AI 생성 이미지는 **실제 특정 장소·제품을 정확히 재현하지 못할 수** 있습니다(여행 명소 등). 그런 글은 실사진(스톡)이 더 정확합니다.

## 나중에 투자 (Claude로 전환)

품질·물량·프라이버시가 필요해지면 `.env`만 바꾸면 됩니다 (코드 수정 불필요):
```
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-5
```
`pip install anthropic` 후 서버 재시작.

## 동작 (5단계)

1. **경쟁 판별** — 롱테일 후보 생성 + `allintitle` 실경쟁자 확인 (블로소득)
2. **상위글 해부** — 현재 1페이지 글 분석 → 채울 틈 파악 (노아)
3. **글 작성 + 이미지** — 검색의도·E-E-A-T·실물(템플릿/사례) 반영 (오석종·전문가) + 어울리는 **이미지 자동 생성**(Gemini)
4. **온페이지 조립** — 타이틀·메타·헤딩·slug·alt·앵커 + JSON-LD (전문가)
5. **점수 + 배포 플랜** — SEO 자동 채점 + 소셜 SEO 유입 플랜 (오석종)

## 구조

```
seo-writer/
  app.py                 # FastAPI: 입력 폼 + /generate
  seo/
    strategy.py          # 전략 상수 + AI 글쓰기 프롬프트(두뇌)
    keywords.py          # 롱테일 생성 + allintitle URL + 경쟁도
    serp.py              # Serper 조회(+수동 폴백)
    llm.py               # gemini / claude / none 제공자 추상화
    images.py            # Gemini 이미지 생성(imagen / gemini-*-image)
    pipeline.py          # 글 생성·온페이지·점수·플랜·마크다운 렌더
  templates/  static/    # 화면(HTML/CSS)
  .env.example           # 키 설정 예시
```

> 🔒 `.env`(키)는 `.gitignore`로 깃에 올라가지 않습니다. 절대 공개 금지.
