import type { ChartVideoProject, ChartSeries, ChartPoint } from "./types";
import { ASSET_PRESETS } from "../market/assets";

// 실제 데이터를 불러오기 전에 미리보기에 바로 보여줄 데모 프로젝트.
// (원본 디자인에 하드코딩돼 있던 근사 수익률 배수를 그대로 사용)

const YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026];

const DEMO: Record<string, number[]> = {
  BTC: [1.0, 2.23, 32.92, 8.7, 16.74, 67.4, 107.7, 38.4, 98.4, 217.2, 267.4],
  NVDA: [1.0, 3.24, 5.87, 4.05, 7.14, 15.85, 35.7, 17.74, 60.12, 163.0, 233.8],
  TSLA: [1.0, 0.89, 1.3, 1.39, 1.74, 14.7, 22.02, 7.7, 15.53, 25.24, 23.73],
  "005930.KS": [1.0, 1.43, 2.02, 1.54, 2.21, 3.21, 3.11, 2.19, 3.12, 2.11, 3.97],
};

const INITIAL = 1_000_000;

function demoSeries(symbol: string): ChartSeries {
  const preset = ASSET_PRESETS.find((p) => p.symbol === symbol)!;
  const mults = DEMO[symbol];
  const values: ChartPoint[] = YEARS.map((year, i) => {
    const m = mults[i];
    return {
      index: i,
      value: m,
      label: String(year),
      meta: {
        date: `${year}-01-01`,
        price: m,
        close: m,
        currentValue: INITIAL * m,
        returnPct: (m - 1) * 100,
      },
    };
  });
  return {
    id: preset.symbol,
    name: preset.name,
    symbol: preset.symbol,
    kind: preset.kind,
    color: preset.color,
    logoLetter: preset.logoLetter,
    values,
  };
}

export function createDefaultProject(): ChartVideoProject {
  return {
    mode: "barRace",
    kicker: "주식 vs 코인 · 10년 수익률",
    title: "10년 전 100만원을",
    titleHighlight: "투자했다면?",
    handle: "@your_handle",
    footnote:
      "2016년 초 각 자산에 100만원씩 투자했을 때의 현재 평가액 근사치. 연초 종가 기준, 배당·세금·수수료 미반영. 출처: Yahoo Finance / Binance.",
    initialInvestment: INITIAL,
    frames: YEARS.map(String),
    series: ["BTC", "NVDA", "TSLA", "005930.KS"].map(demoSeries),
    theme: "dark",
    accent: "#2997ff",
    returnDisplay: "percent",
    barGlow: true,
    durationSec: 12,
    fps: 60,
    width: 1080,
    height: 1920,
  };
}

export const DEFAULT_YEARS = YEARS;
