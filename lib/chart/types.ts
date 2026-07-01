// ============================================================================
// 차트 영상 프로젝트 데이터 모델
// ----------------------------------------------------------------------------
// 주식(Yahoo Finance)과 코인(Binance)에서 가져온 서로 다른 원본 데이터는
// 모두 앱 내부에서 아래의 동일한 "차트용 시계열 포맷"으로 변환되어
// 렌더러(renderFrame)에 들어갑니다.
// ============================================================================

/** 자산 종류 */
export type AssetKind = "stock" | "coin";

/**
 * 각 시계열 포인트.
 *  - index : 프레임(연도/구간) 순번 (0부터)
 *  - value : 그래프에 그릴 "수익률 값" = 초기 투자금 대비 배수 (1.0 = 원금, 2.0 = 2배)
 *  - label : 축에 표시할 라벨 (예: "2016")
 *  - meta  : 계산·표시에 쓰는 부가 데이터
 */
export interface ChartPoint {
  index: number;
  value: number;
  label: string;
  meta: ChartPointMeta;
}

export interface ChartPointMeta {
  /** ISO 날짜 (YYYY-MM-DD) */
  date: string;
  /** 기본 가격(주식은 수정주가 우선, 코인은 종가) */
  price: number;
  /** 종가 */
  close: number;
  /** 시가 */
  open?: number;
  /** 고가 */
  high?: number;
  /** 저가 */
  low?: number;
  /** 현재가치 = 초기 투자금 × value(배수) */
  currentValue: number;
  /** 수익률(%) = (value - 1) × 100 */
  returnPct: number;
}

/** 하나의 자산(막대 하나)을 나타내는 시계열 */
export interface ChartSeries {
  id: string;
  /** 화면에 표시되는 이름 (예: "비트코인") */
  name: string;
  /** 원본 심볼/티커 (예: "BTC", "AAPL", "005930.KS") */
  symbol: string;
  kind: AssetKind;
  /** 막대 색(브랜드 컬러) */
  color: string;
  /** 로고 이미지 URL(있으면 사용) */
  logoUrl?: string;
  /** 로고 이미지가 없을 때 원 안에 표시할 글자 */
  logoLetter: string;
  /** 시계열 값들 (프레임 순서대로) */
  values: ChartPoint[];
}

/** 렌더 모드 (지금은 막대 레이스 한 종류지만 확장 가능하도록 분리) */
export type ChartMode = "barRace";

export type ReturnDisplay = "percent" | "multiple" | "hidden";
export type ThemeName = "dark" | "light";

/** 렌더러에 최종적으로 들어가는 프로젝트 전체 */
export interface ChartVideoProject {
  mode: ChartMode;

  // 텍스트
  kicker: string; // 위 작은 글씨 (예: "주식 vs 코인 · 10년 수익률")
  title: string; // 큰 제목 (예: "10년 전 100만원을")
  titleHighlight: string; // 강조 문구 (예: "투자했다면?")
  handle: string; // 계정명
  footnote: string; // 하단 각주

  // 데이터
  initialInvestment: number; // 초기 투자금(원)
  frames: string[]; // 각 프레임 라벨 (연도 목록)
  series: ChartSeries[];

  // 표시 옵션
  theme: ThemeName;
  accent: string; // 강조색
  returnDisplay: ReturnDisplay;
  barGlow: boolean;

  // 영상 설정
  durationSec: number;
  fps: number;
  width: number; // 1080
  height: number; // 1920
}
