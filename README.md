# 자산 막대 레이스 · 영상 생성기

실제 **주식/ETF(Yahoo Finance)** 와 **코인(Binance)** 데이터로 인스타그램·유튜브 쇼츠용
**1080×1920 세로 막대 레이스(bar race) 영상**을 만드는 Next.js 앱입니다.

> "10년 전 100만원을 투자했다면?" 같은 자산별 현재가치 비교 영상을 만들 수 있어요.

## 핵심 동작

### 1. 데이터 불러오기
- **주식 / ETF**: 프론트에서 티커를 보내면 `app/api/market/stocks/history` 라우트가
  Yahoo Finance 계열 소스에서 `open/high/low/close/adjustedClose` 를 받아옵니다.
  차트 계산에는 **수정주가(adjustedClose)** 를 우선 사용합니다. (예: `AAPL`, `QQQ`, `005930.KS`, `207940.KS`)
- **코인**: `app/api/market/coins/history` 라우트가 Binance klines(캔들)에서
  `open/high/low/close` 를 받아옵니다. 일반 차트는 **종가(close)** 기준으로 수익률을 계산합니다.
  (예: `BTC`, `ETH`, `SOL`)

### 2. 공통 차트 포맷으로 변환
가져온 시장 데이터는 앱 내부에서 `ChartVideoProject.series[].values` 형태로 변환됩니다.
각 포인트는 `index, value, label, meta` 를 가집니다.
- `value` : 그래프에 그릴 수익률 값 (초기 투자금 대비 **배수**)
- `meta`  : `date, price, close, open/high/low, currentValue, returnPct`
(`lib/chart/types.ts`, `lib/market/fetchSeries.ts`)

### 3. 영상 내보내기 (화면 녹화 아님)
1. **숨겨진 캔버스(1080×1920 풀 해상도)** 에 매 프레임을 `renderFrame()` 으로 직접 그립니다.
   (`lib/render/renderFrame.ts` → `modes/barRace.ts` + `drawFloatingSummary.ts`)
2. 그 프레임들을 **60fps** 로 뽑아 **WebCodecs** `VideoEncoder` 로 인코딩합니다.
3. 인코딩된 프레임을 **`mp4-muxer`** 로 MP4 컨테이너에 묶어 다운로드합니다.
   (`lib/export/exportMp4.ts`)

미리보기와 **완전히 같은 렌더러**를 쓰기 때문에 화면 녹화보다 화질이 깨끗하고 정확합니다.

## 폴더 구조

```
app/
  page.tsx                            # 편집기 UI (미리보기 + 설정 + 내보내기)
  api/market/stocks/history/route.ts  # Yahoo Finance 주식/ETF
  api/market/coins/history/route.ts   # Binance 코인 캔들
lib/
  chart/types.ts        # ChartVideoProject / ChartSeries / ChartPoint
  chart/format.ts       # fmtWon, fmtReturn, 보간/이징
  chart/defaultProject.ts
  market/assets.ts      # 자산 프리셋(이름/색/로고 글자)
  market/fetchSeries.ts # 원본 데이터 → series[].values 변환
  render/renderFrame.ts # 프레임 단일 렌더러 (미리보기·내보내기 공용)
  render/modes/barRace.ts
  render/drawFloatingSummary.ts
  render/theme.ts, canvasUtils.ts
  export/exportMp4.ts   # WebCodecs + mp4-muxer 내보내기
  export/fonts.ts       # Pretendard 폰트 프리로드
components/ChartPreview.tsx
```

## 실행

```bash
npm install
npm run dev      # http://localhost:3000
```

1. 자산(티커) 목록을 정하고 **"실제 시장 데이터 불러오기"** 를 누릅니다.
2. 텍스트·테마·재생 길이 등을 조정하며 미리보기로 확인합니다.
3. **"MP4로 내보내기"** 로 1080×1920·60fps MP4 파일을 저장합니다.

> 영상 내보내기(WebCodecs)는 **데스크톱 크롬/엣지 최신 버전**에서 동작합니다.

## 참고
- `index (1).html` : 초기 프로토타입(DOM + 화면녹화 방식). 실제 앱은 이 방식을 캔버스+WebCodecs로 고도화한 것입니다.
- 수익률은 연초 종가·수정주가 기준 근사치이며 배당·세금·수수료·환율은 반영되지 않습니다.
