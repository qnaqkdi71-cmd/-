import type { ThemeName } from "../chart/types";

// 원본 디자인의 themes() 값을 캔버스 렌더용으로 옮김

export interface RenderTheme {
  // 배경 그라데이션 stop 색
  bgInner: string;
  bgMid: string;
  bgOuter: string;
  bgSolid?: string; // 라이트 테마용 단색
  gridLine: string;
  glowAlpha: number;
  kicker: string;
  headline: string;
  name: string;
  value: string;
  mult: string;
  year: string;
  footnote: string;
  logoRing: string;
  gainColor: string;
  lossColor: string;
  summaryBg: string;
  summaryBorder: string;
  summaryText: string;
}

const DARK: RenderTheme = {
  bgInner: "#161b26",
  bgMid: "#0a0d14",
  bgOuter: "#04050a",
  gridLine: "rgba(41,151,255,0.06)",
  glowAlpha: 0.2,
  kicker: "#5d6b86",
  headline: "#ffffff",
  name: "#f5f5f7",
  value: "#ffffff",
  mult: "#8a93a6",
  year: "rgba(255,255,255,0.055)",
  footnote: "#5a6275",
  logoRing: "#ffffff",
  gainColor: "#30D158",
  lossColor: "#FF453A",
  summaryBg: "rgba(20,24,32,0.72)",
  summaryBorder: "rgba(255,255,255,0.14)",
  summaryText: "#f5f5f7",
};

const LIGHT: RenderTheme = {
  bgInner: "#ffffff",
  bgMid: "#ffffff",
  bgOuter: "#ffffff",
  bgSolid: "#ffffff",
  gridLine: "rgba(0,0,0,0.04)",
  glowAlpha: 0,
  kicker: "#a1a1a6",
  headline: "#1d1d1f",
  name: "#1d1d1f",
  value: "#1d1d1f",
  mult: "#a1a1a6",
  year: "#e4e4e9",
  footnote: "#aeaeb2",
  logoRing: "#ffffff",
  gainColor: "#28A745",
  lossColor: "#FF3B30",
  summaryBg: "#f5f5f7",
  summaryBorder: "#e0e0e0",
  summaryText: "#1d1d1f",
};

export function getTheme(name: ThemeName): RenderTheme {
  return name === "light" ? LIGHT : DARK;
}
