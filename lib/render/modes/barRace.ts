import type { ChartVideoProject } from "../../chart/types";
import { valueAt, fmtWon, fmtReturn } from "../../chart/format";
import type { RenderTheme } from "../theme";
import { roundRect, drawLogo, drawPill } from "../canvasUtils";

export interface BarLayout {
  rowLeft: number;
  nameRightX: number; // 자산명 오른쪽 정렬 기준 x
  barLeft: number;
  minBarW: number;
  maxBarW: number;
  logoW: number;
  logoGap: number;
  valGap: number;
  bandTop: number;
  barH: number;
  pitch: number;
  nameFont: number;
  valFont: number;
  multFont: number;
}

/** N개 자산에 맞춰 막대 레이아웃을 계산 (세로 공간에 자동 맞춤) */
export function computeBarLayout(
  project: ChartVideoProject,
  count: number,
): BarLayout {
  const N = Math.max(1, count);
  const regionTop = 610;
  const regionH = 880;
  const pitch = Math.min(196, regionH / N);
  const barH = Math.min(128, pitch * 0.68);
  const scale = barH / 128; // 128 기준 대비 축소 비율
  const logoW = Math.round(Math.min(80, barH * 0.62));

  return {
    rowLeft: 72,
    nameRightX: 300,
    barLeft: 320,
    minBarW: 84 * Math.max(0.8, scale),
    maxBarW: N <= 2 ? 372 : 460,
    logoW,
    logoGap: 12,
    valGap: 18,
    bandTop: regionTop + (regionH - pitch * N) / 2,
    barH,
    pitch,
    nameFont: Math.round(38 * Math.max(0.72, scale)),
    valFont: Math.round(42 * Math.max(0.72, scale)),
    multFont: Math.round(25 * Math.max(0.72, scale)),
  };
}

/** 막대 레이스 본체 — 한 프레임을 그림 */
export function drawBarRace(
  ctx: CanvasRenderingContext2D,
  project: ChartVideoProject,
  progress: number,
  theme: RenderTheme,
  images?: Record<string, HTMLImageElement | ImageBitmap | null>,
) {
  const series = project.series;
  const L = computeBarLayout(project, series.length);

  // 현재 프레임의 보간 배수
  const vals = series.map((s) => valueAt(s.values, progress));
  const maxV = Math.max(1e-6, ...vals);

  // 순위(값 내림차순)
  const order = series
    .map((_, i) => i)
    .sort((a, b) => vals[b] - vals[a]);
  const rankOf: number[] = [];
  order.forEach((si, rank) => (rankOf[si] = rank));

  series.forEach((s, i) => {
    const v = vals[i];
    const t = v / maxV;
    const barW = L.minBarW + t * (L.maxBarW - L.minBarW);
    const y = L.bandTop + rankOf[i] * L.pitch;
    const cy = y + L.barH / 2;

    // 자산명 (오른쪽 정렬)
    ctx.font = `700 ${L.nameFont}px Pretendard, system-ui, sans-serif`;
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ctx.fillStyle = theme.name;
    ctx.fillText(s.name, L.nameRightX, cy);

    // 막대 (글로우 옵션)
    ctx.save();
    if (project.barGlow && theme.glowAlpha > 0) {
      ctx.shadowColor = s.color;
      ctx.shadowBlur = 34;
    }
    roundRect(ctx, L.barLeft, y, barW, L.barH, Math.min(14, L.barH * 0.14));
    ctx.fillStyle = s.color;
    ctx.fill();
    ctx.restore();

    // 로고
    const logoCx = L.barLeft + barW + L.logoGap + L.logoW / 2;
    drawLogo(
      ctx,
      logoCx,
      cy,
      L.logoW,
      s.color,
      s.logoLetter,
      theme.logoRing,
      images?.[s.id],
    );

    // 금액 + 수익률
    const valX = logoCx + L.logoW / 2 + L.valGap;
    const won = v * project.initialInvestment;
    const showReturn = project.returnDisplay !== "hidden";

    if (showReturn) {
      // 금액을 위로, 수익률 알약을 아래로 (2줄)
      ctx.font = `800 ${L.valFont}px Pretendard, system-ui, sans-serif`;
      ctx.textAlign = "left";
      ctx.textBaseline = "alphabetic";
      ctx.fillStyle = theme.value;
      ctx.fillText(fmtWon(won), valX, cy - 4);

      const gain = v >= 1;
      const mode = project.returnDisplay === "multiple" ? "multiple" : "percent";
      drawPill(
        ctx,
        valX,
        cy + L.multFont + 4,
        fmtReturn(v, mode),
        L.multFont,
        gain ? theme.gainColor : theme.lossColor,
        gain ? "rgba(48,209,88,0.16)" : "rgba(255,69,58,0.16)",
      );
    } else {
      ctx.font = `800 ${L.valFont}px Pretendard, system-ui, sans-serif`;
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillStyle = theme.value;
      ctx.fillText(fmtWon(won), valX, cy);
    }
  });
}
