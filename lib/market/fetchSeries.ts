import type {
  ChartSeries,
  ChartPoint,
  AssetKind,
} from "../chart/types";
import {
  findPreset,
  guessKind,
  FALLBACK_COLORS,
  type AssetPreset,
} from "./assets";

// ============================================================================
// 원본 시장 데이터(주식=Yahoo, 코인=Binance)를 가져와서
// 앱 내부의 ChartSeries(= series[].values) 포맷으로 변환합니다.
// ============================================================================

interface RawHistory {
  points: {
    date: string;
    open: number | null;
    high: number | null;
    low: number | null;
    close: number | null;
    adjClose: number | null;
  }[];
}

export interface FetchSeriesInput {
  symbol: string;
  /** 표시 이름 (없으면 프리셋/심볼에서 유추) */
  name?: string;
  color?: string;
  kind?: AssetKind;
  /** 색 순환용 인덱스 */
  colorIndex?: number;
}

export interface BuildOptions {
  /** 프레임 라벨(연도). 각 라벨 시점의 값으로 리샘플링 */
  years: number[];
  /** 초기 투자금(원) */
  initialInvestment: number;
}

/** 선택한 연도 범위를 모두 덮도록 Yahoo range 값을 고른다 */
function rangeForYears(years: number[]): string {
  const span = years.length ? years[years.length - 1] - years[0] : 10;
  if (span >= 9) return "max"; // 10년 이상은 넉넉히 전체
  return `${span + 1}y`;
}

/** 주식/코인 히스토리를 서버 라우트에서 받아온다 */
async function fetchRaw(
  symbol: string,
  kind: AssetKind,
  years: number[],
): Promise<RawHistory> {
  const url =
    kind === "coin"
      ? `/api/market/coins/history?symbol=${encodeURIComponent(symbol)}&interval=1M&limit=1000`
      : `/api/market/stocks/history?ticker=${encodeURIComponent(symbol)}&range=${rangeForYears(years)}&interval=1mo`;

  const res = await fetch(url);
  if (!res.ok) {
    const j = await res.json().catch(() => ({}));
    throw new Error(j.error || `${symbol} 데이터 조회 실패 (${res.status})`);
  }
  return (await res.json()) as RawHistory;
}

/** 특정 연도(정확히는 그 해의 첫 거래 시점)의 가격을 고른다 */
function priceAtYear(
  points: RawHistory["points"],
  year: number,
  useAdjusted: boolean,
): { price: number; row: RawHistory["points"][number] } | null {
  const start = `${year}-01-01`;
  // 그 해 이후 첫 포인트
  let candidate = points.find((p) => p.date >= start);
  // 없으면(미래 연도) 마지막 포인트 사용
  if (!candidate) candidate = points[points.length - 1];
  if (!candidate) return null;
  const price = useAdjusted
    ? candidate.adjClose ?? candidate.close
    : candidate.close ?? candidate.adjClose;
  if (price == null || !Number.isFinite(price)) return null;
  return { price, row: candidate };
}

/** 하나의 자산에 대해 ChartSeries 를 만든다 */
export async function buildSeries(
  input: FetchSeriesInput,
  opts: BuildOptions,
): Promise<ChartSeries> {
  const preset: AssetPreset | undefined = findPreset(input.symbol);
  const kind = input.kind ?? preset?.kind ?? guessKind(input.symbol);
  const raw = await fetchRaw(input.symbol, kind, opts.years);

  const useAdjusted = kind === "stock"; // 주식은 수정주가 우선
  const points = raw.points;

  // 각 연도 시점의 가격을 뽑는다
  const anchors = opts.years.map((y) => priceAtYear(points, y, useAdjusted));
  const base = anchors[0];
  if (!base) {
    throw new Error(`${input.symbol}: 기준 연도(${opts.years[0]}) 데이터가 없습니다.`);
  }

  const values: ChartPoint[] = opts.years.map((year, i) => {
    const a = anchors[i] ?? base;
    const multiple = a.price / base.price; // 초기 대비 배수 = 수익률 값
    return {
      index: i,
      value: multiple,
      label: String(year),
      meta: {
        date: a.row.date,
        price: a.price,
        close: a.row.close ?? a.price,
        open: a.row.open ?? undefined,
        high: a.row.high ?? undefined,
        low: a.row.low ?? undefined,
        currentValue: opts.initialInvestment * multiple,
        returnPct: (multiple - 1) * 100,
      },
    };
  });

  const color =
    input.color ??
    preset?.color ??
    FALLBACK_COLORS[(input.colorIndex ?? 0) % FALLBACK_COLORS.length];
  const name = input.name ?? preset?.name ?? input.symbol;
  const logoLetter = preset?.logoLetter ?? name.charAt(0).toUpperCase();

  return {
    id: input.symbol,
    name,
    symbol: input.symbol,
    kind,
    color,
    logoLetter,
    values,
  };
}

/** 여러 자산을 병렬로 만든다 (일부 실패해도 나머지는 진행) */
export async function buildAllSeries(
  inputs: FetchSeriesInput[],
  opts: BuildOptions,
): Promise<{ series: ChartSeries[]; errors: string[] }> {
  const results = await Promise.allSettled(
    inputs.map((inp, i) => buildSeries({ ...inp, colorIndex: i }, opts)),
  );
  const series: ChartSeries[] = [];
  const errors: string[] = [];
  results.forEach((r, i) => {
    if (r.status === "fulfilled") series.push(r.value);
    else errors.push(`${inputs[i].symbol}: ${r.reason?.message ?? r.reason}`);
  });
  return { series, errors };
}
