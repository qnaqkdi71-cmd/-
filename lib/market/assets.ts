import type { AssetKind } from "../chart/types";

// 자주 쓰는 자산 카탈로그 — 심볼/티커 → 표시이름, 브랜드색, 로고글자, 종류
// (원본 디자인의 색상값을 그대로 사용)

export interface AssetPreset {
  key: string;
  name: string;
  symbol: string; // 주식은 Yahoo 티커, 코인은 Binance 베이스 심볼
  kind: AssetKind;
  color: string;
  logoLetter: string;
}

export const ASSET_PRESETS: AssetPreset[] = [
  // 코인
  { key: "btc", name: "비트코인", symbol: "BTC", kind: "coin", color: "#F7931A", logoLetter: "B" },
  { key: "eth", name: "이더리움", symbol: "ETH", kind: "coin", color: "#627EEA", logoLetter: "Ξ" },
  { key: "sol", name: "솔라나", symbol: "SOL", kind: "coin", color: "#14F195", logoLetter: "S" },
  { key: "xrp", name: "리플", symbol: "XRP", kind: "coin", color: "#23292F", logoLetter: "X" },
  { key: "doge", name: "도지코인", symbol: "DOGE", kind: "coin", color: "#C2A633", logoLetter: "Ð" },

  // 미국 주식 / ETF
  { key: "nvda", name: "엔비디아", symbol: "NVDA", kind: "stock", color: "#76B900", logoLetter: "N" },
  { key: "tsla", name: "테슬라", symbol: "TSLA", kind: "stock", color: "#E82127", logoLetter: "T" },
  { key: "aapl", name: "애플", symbol: "AAPL", kind: "stock", color: "#A2AAAD", logoLetter: "" },
  { key: "msft", name: "마이크로소프트", symbol: "MSFT", kind: "stock", color: "#00A4EF", logoLetter: "M" },
  { key: "googl", name: "구글", symbol: "GOOGL", kind: "stock", color: "#4285F4", logoLetter: "G" },
  { key: "amzn", name: "아마존", symbol: "AMZN", kind: "stock", color: "#FF9900", logoLetter: "a" },
  { key: "qqq", name: "나스닥100 ETF", symbol: "QQQ", kind: "stock", color: "#5b9bd5", logoLetter: "Q" },
  { key: "spy", name: "S&P500 ETF", symbol: "SPY", kind: "stock", color: "#c08fe0", logoLetter: "S" },

  // 한국 주식
  { key: "samsung", name: "삼성전자", symbol: "005930.KS", kind: "stock", color: "#3B6CFF", logoLetter: "S" },
  { key: "hynix", name: "SK하이닉스", symbol: "000660.KS", kind: "stock", color: "#EE2737", logoLetter: "H" },
  { key: "kospi", name: "코스피 ETF", symbol: "069500.KS", kind: "stock", color: "#5dcaa5", logoLetter: "K" },
];

/** 심볼로 프리셋 찾기 (없으면 undefined) */
export function findPreset(symbolOrKey: string): AssetPreset | undefined {
  const s = symbolOrKey.trim().toLowerCase();
  return ASSET_PRESETS.find(
    (p) =>
      p.key.toLowerCase() === s ||
      p.symbol.toLowerCase() === s ||
      p.name.toLowerCase() === s,
  );
}

/** 자동으로 자산 종류 추정: .KS/.KQ 나 알파벳 티커면 주식, 아니면 코인 */
export function guessKind(symbol: string): AssetKind {
  const s = symbol.trim().toUpperCase();
  if (/\.(KS|KQ)$/.test(s)) return "stock";
  const preset = findPreset(symbol);
  if (preset) return preset.kind;
  // 3~4글자 순수 알파벳이고 흔한 코인 티커면 coin 으로 추정
  const COIN_HINTS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "BNB", "AVAX", "DOT", "MATIC", "LINK"];
  if (COIN_HINTS.includes(s)) return "coin";
  return "stock";
}

/** 팔레트 — 프리셋에 없는 자산에 색을 부여할 때 순환 사용 */
export const FALLBACK_COLORS = [
  "#2997ff",
  "#30D158",
  "#FFD60A",
  "#FF453A",
  "#BF5AF2",
  "#64D2FF",
  "#FF9F0A",
];
