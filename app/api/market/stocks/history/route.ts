import { NextRequest, NextResponse } from "next/server";

// ============================================================================
// 주식 / ETF 가격 히스토리
// ----------------------------------------------------------------------------
// 프론트에서 티커를 보내면 이 라우트가 Yahoo Finance 계열 데이터 소스에서
// open/high/low/close/adjustedClose 를 받아옵니다.
// 차트 기본 계산에는 수정주가(adjustedClose) 계열을 우선 사용합니다.
//   예: AAPL, QQQ, 005930.KS, 207940.KS
// ----------------------------------------------------------------------------
// GET /api/market/stocks/history?ticker=AAPL&range=10y&interval=1mo
// ============================================================================

export const dynamic = "force-dynamic";
export const revalidate = 0;

export interface HistoryPoint {
  date: string; // YYYY-MM-DD
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  adjClose: number | null;
}

export interface StockHistoryResponse {
  symbol: string;
  currency: string;
  kind: "stock";
  points: HistoryPoint[];
}

const YAHOO_HOSTS = [
  "https://query1.finance.yahoo.com",
  "https://query2.finance.yahoo.com",
];

function toISODate(epochSec: number): string {
  return new Date(epochSec * 1000).toISOString().slice(0, 10);
}

async function fetchYahoo(
  ticker: string,
  range: string,
  interval: string,
): Promise<StockHistoryResponse> {
  const qs = new URLSearchParams({
    range,
    interval,
    includePrePost: "false",
    events: "div,splits",
    includeAdjustedClose: "true",
  });

  let lastErr: unknown = null;
  for (const host of YAHOO_HOSTS) {
    const url = `${host}/v8/finance/chart/${encodeURIComponent(ticker)}?${qs}`;
    try {
      const res = await fetch(url, {
        headers: {
          // Yahoo는 UA 없는 요청을 자주 막으므로 브라우저처럼 보이게 함
          "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
          Accept: "application/json",
        },
        cache: "no-store",
      });
      if (!res.ok) {
        lastErr = new Error(`Yahoo ${res.status} for ${ticker}`);
        continue;
      }
      const json = await res.json();
      const result = json?.chart?.result?.[0];
      if (!result) {
        lastErr = new Error(`Yahoo: no result for ${ticker}`);
        continue;
      }

      const timestamps: number[] = result.timestamp ?? [];
      const quote = result.indicators?.quote?.[0] ?? {};
      const adj = result.indicators?.adjclose?.[0]?.adjclose ?? [];
      const currency: string = result.meta?.currency ?? "USD";

      const points: HistoryPoint[] = timestamps.map((ts, i) => ({
        date: toISODate(ts),
        open: numOrNull(quote.open?.[i]),
        high: numOrNull(quote.high?.[i]),
        low: numOrNull(quote.low?.[i]),
        close: numOrNull(quote.close?.[i]),
        adjClose: numOrNull(adj?.[i] ?? quote.close?.[i]),
      })).filter((p) => p.close != null || p.adjClose != null);

      return { symbol: ticker, currency, kind: "stock", points };
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr ?? new Error(`Yahoo fetch failed for ${ticker}`);
}

function numOrNull(v: unknown): number | null {
  return typeof v === "number" && Number.isFinite(v) ? v : null;
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const ticker = searchParams.get("ticker")?.trim();
  const range = searchParams.get("range")?.trim() || "10y";
  const interval = searchParams.get("interval")?.trim() || "1mo";

  if (!ticker) {
    return NextResponse.json(
      { error: "ticker 파라미터가 필요합니다." },
      { status: 400 },
    );
  }

  try {
    const data = await fetchYahoo(ticker, range, interval);
    if (!data.points.length) {
      return NextResponse.json(
        { error: `데이터를 찾을 수 없습니다: ${ticker}` },
        { status: 404 },
      );
    }
    return NextResponse.json(data, {
      headers: { "Cache-Control": "s-maxage=3600, stale-while-revalidate=86400" },
    });
  } catch (e) {
    return NextResponse.json(
      { error: (e as Error).message || "주식 데이터 조회 실패" },
      { status: 502 },
    );
  }
}
