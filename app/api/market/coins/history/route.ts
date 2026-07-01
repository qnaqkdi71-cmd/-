import { NextRequest, NextResponse } from "next/server";
import type { HistoryPoint } from "../../stocks/history/route";

// ============================================================================
// 코인 가격 히스토리
// ----------------------------------------------------------------------------
// 코인은 Binance klines(캔들) 데이터를 사용합니다.
// 심볼을 Binance 형식(예: BTC → BTCUSDT)으로 맞춰서 일봉/월봉 캔들을 가져오고
// open/high/low/close 를 받아옵니다. 일반 차트는 종가(close) 기준으로 계산합니다.
//   예: BTC, ETH, SOL
// ----------------------------------------------------------------------------
// GET /api/market/coins/history?symbol=BTC&interval=1M&limit=180
// ============================================================================

export const dynamic = "force-dynamic";
export const revalidate = 0;

export interface CoinHistoryResponse {
  symbol: string; // 요청한 심볼 (BTC)
  binanceSymbol: string; // 실제 Binance 심볼 (BTCUSDT)
  currency: "USDT";
  kind: "coin";
  points: HistoryPoint[];
}

const BINANCE_HOSTS = [
  "https://api.binance.com",
  "https://data-api.binance.vision", // 공개 데이터 전용 미러 (지역 차단 우회에 유용)
];

/** 사용자가 넣은 심볼을 Binance 형식으로 정규화 */
function toBinanceSymbol(raw: string): string {
  let s = raw.trim().toUpperCase();
  // 이미 페어가 붙어있으면 그대로 사용
  if (/(USDT|BUSD|USD|BTC|ETH)$/.test(s) && s.length > 4) return s;
  // 흔한 별칭 정리
  s = s.replace(/[-/].*$/, ""); // BTC-USD, BTC/USDT → BTC
  return s + "USDT";
}

async function fetchKlines(
  binanceSymbol: string,
  interval: string,
  limit: number,
): Promise<HistoryPoint[]> {
  const qs = new URLSearchParams({
    symbol: binanceSymbol,
    interval,
    limit: String(Math.min(Math.max(limit, 1), 1000)),
  });

  let lastErr: unknown = null;
  for (const host of BINANCE_HOSTS) {
    const url = `${host}/api/v3/klines?${qs}`;
    try {
      const res = await fetch(url, {
        headers: { Accept: "application/json" },
        cache: "no-store",
      });
      if (!res.ok) {
        lastErr = new Error(`Binance ${res.status} for ${binanceSymbol}`);
        continue;
      }
      const rows: unknown[][] = await res.json();
      // klines 각 행: [openTime, open, high, low, close, volume, closeTime, ...]
      return rows.map((r) => ({
        date: new Date(Number(r[0])).toISOString().slice(0, 10),
        open: safeNum(r[1]),
        high: safeNum(r[2]),
        low: safeNum(r[3]),
        close: safeNum(r[4]),
        adjClose: safeNum(r[4]), // 코인은 수정주가 개념이 없어 종가와 동일
      }));
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr ?? new Error(`Binance fetch failed for ${binanceSymbol}`);
}

function safeNum(v: unknown): number | null {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const symbol = searchParams.get("symbol")?.trim();
  const interval = searchParams.get("interval")?.trim() || "1M"; // 월봉
  const limit = Number(searchParams.get("limit") ?? "180");

  if (!symbol) {
    return NextResponse.json(
      { error: "symbol 파라미터가 필요합니다." },
      { status: 400 },
    );
  }

  const binanceSymbol = toBinanceSymbol(symbol);

  try {
    const points = await fetchKlines(binanceSymbol, interval, limit);
    if (!points.length) {
      return NextResponse.json(
        { error: `데이터를 찾을 수 없습니다: ${symbol}` },
        { status: 404 },
      );
    }
    const data: CoinHistoryResponse = {
      symbol,
      binanceSymbol,
      currency: "USDT",
      kind: "coin",
      points,
    };
    return NextResponse.json(data, {
      headers: { "Cache-Control": "s-maxage=3600, stale-while-revalidate=86400" },
    });
  } catch (e) {
    return NextResponse.json(
      { error: (e as Error).message || "코인 데이터 조회 실패" },
      { status: 502 },
    );
  }
}
