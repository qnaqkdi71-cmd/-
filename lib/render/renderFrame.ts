import type { ChartVideoProject } from "../chart/types";
import { frameIndexAt } from "../chart/format";
import { getTheme } from "./theme";
import { roundRect } from "./canvasUtils";
import { drawBarRace } from "./modes/barRace";
import { drawFloatingSummary } from "./drawFloatingSummary";

// ============================================================================
// renderFrame — 미리보기와 영상 내보내기가 공유하는 단일 렌더러.
// 하나의 캔버스에 "한 프레임"을 통째로 그립니다.
//   배경(그라데이션+그리드+글로우) → 제목 → 큰 연도 → 모드 렌더러(막대 레이스)
//   → 하단 요약(drawFloatingSummary) → 각주
// ============================================================================

export interface RenderOptions {
  /** 로고 이미지 프리로드 맵 (id → 이미지). 없으면 글자 로고로 대체 */
  images?: Record<string, HTMLImageElement | ImageBitmap | null>;
}

export function renderFrame(
  ctx: CanvasRenderingContext2D,
  project: ChartVideoProject,
  progress: number,
  opts: RenderOptions = {},
) {
  const W = project.width;
  const H = project.height;
  const theme = getTheme(project.theme);

  // ---- 배경 ----
  ctx.clearRect(0, 0, W, H);
  if (theme.bgSolid) {
    ctx.fillStyle = theme.bgSolid;
    ctx.fillRect(0, 0, W, H);
  } else {
    // radial-gradient(120% 85% at 50% -8%, inner → mid → outer)
    const g = ctx.createRadialGradient(W / 2, -0.08 * H, 0, W / 2, -0.08 * H, 0.85 * H * 1.4);
    g.addColorStop(0, theme.bgInner);
    g.addColorStop(0.55, theme.bgMid);
    g.addColorStop(1, theme.bgOuter);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  }

  drawGrid(ctx, W, H, theme.gridLine);
  if (theme.glowAlpha > 0) drawGlow(ctx, W, project.accent, theme.glowAlpha);

  // ---- 제목 ----
  drawTitle(ctx, project, theme);

  // ---- 큰 연도(배경 뒤 장식) ----
  const fi = frameIndexAt(progress, project.frames.length);
  const yearLabel = project.frames[fi] ?? "";
  ctx.save();
  ctx.textAlign = "right";
  ctx.textBaseline = "alphabetic";
  ctx.font = "800 248px Pretendard, system-ui, sans-serif";
  ctx.fillStyle = theme.year;
  ctx.fillText(yearLabel, W - 60, 1520);
  ctx.restore();

  // ---- 모드 렌더러 ----
  if (project.mode === "barRace") {
    drawBarRace(ctx, project, progress, theme, opts.images);
  }

  // ---- 하단 요약 ----
  drawFloatingSummary(ctx, project, progress, theme);

  // ---- 각주 + 핸들 ----
  drawFootnote(ctx, project, theme);
}

function drawGrid(ctx: CanvasRenderingContext2D, W: number, H: number, color: string) {
  ctx.save();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;
  const step = 90;
  // 위/아래를 페이드 처리하기 위해 중앙부만 진하게 (근사)
  for (let x = 0; x <= W; x += step) {
    ctx.beginPath();
    ctx.moveTo(x + 0.5, 0);
    ctx.lineTo(x + 0.5, H);
    ctx.stroke();
  }
  for (let y = 0; y <= H; y += step) {
    ctx.beginPath();
    ctx.moveTo(0, y + 0.5);
    ctx.lineTo(W, y + 0.5);
    ctx.stroke();
  }
  ctx.restore();
}

function drawGlow(ctx: CanvasRenderingContext2D, W: number, accent: string, alpha: number) {
  ctx.save();
  const cx = W / 2;
  const cy = 60;
  const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, 460);
  g.addColorStop(0, hexA(accent, alpha));
  g.addColorStop(1, hexA(accent, 0));
  ctx.fillStyle = g;
  ctx.fillRect(0, -200, W, 620);
  ctx.restore();
}

function drawTitle(
  ctx: CanvasRenderingContext2D,
  project: ChartVideoProject,
  theme: ReturnType<typeof getTheme>,
) {
  const W = project.width;
  const cx = W / 2;

  // kicker
  ctx.textAlign = "center";
  ctx.textBaseline = "alphabetic";
  ctx.font = "700 32px Pretendard, system-ui, sans-serif";
  ctx.fillStyle = theme.kicker;
  ctx.fillText(spaced(project.kicker), cx, 170);

  // headline (두 줄: title / highlight)
  ctx.font = "800 76px Pretendard, system-ui, sans-serif";
  ctx.fillStyle = theme.headline;
  ctx.fillText(project.title, cx, 300);

  // highlight pill
  if (project.titleHighlight) {
    ctx.font = "800 76px Pretendard, system-ui, sans-serif";
    const tw = ctx.measureText(project.titleHighlight).width;
    const padX = 34;
    const boxW = tw + padX * 2;
    const boxH = 100;
    const bx = cx - boxW / 2;
    const by = 340;
    roundRect(ctx, bx, by, boxW, boxH, 20);
    ctx.fillStyle = hexA(project.accent, project.theme === "light" ? 0.12 : 0.14);
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = hexA(project.accent, 0.4);
    ctx.stroke();
    ctx.fillStyle = project.accent;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(project.titleHighlight, cx, by + boxH / 2 + 4);
  }
}

function drawFootnote(
  ctx: CanvasRenderingContext2D,
  project: ChartVideoProject,
  theme: ReturnType<typeof getTheme>,
) {
  const W = project.width;
  // 핸들
  if (project.handle) {
    ctx.textAlign = "center";
    ctx.textBaseline = "alphabetic";
    ctx.font = "600 26px Pretendard, system-ui, sans-serif";
    ctx.fillStyle = theme.mult;
    ctx.fillText(project.handle, W / 2, project.height - 96);
  }

  // 각주 (여러 줄 래핑)
  ctx.textAlign = "left";
  ctx.font = "400 22px Pretendard, system-ui, sans-serif";
  ctx.fillStyle = theme.footnote;
  wrapText(ctx, project.footnote, 72, project.height - 62, W - 144, 32);
}

function wrapText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  maxW: number,
  lineH: number,
) {
  const words = text.split(" ");
  let line = "";
  let yy = y;
  for (const word of words) {
    const test = line ? line + " " + word : word;
    if (ctx.measureText(test).width > maxW && line) {
      ctx.fillText(line, x, yy);
      line = word;
      yy += lineH;
    } else {
      line = test;
    }
  }
  if (line) ctx.fillText(line, x, yy);
}

function spaced(s: string): string {
  return s; // kicker 는 letter-spacing 을 캔버스에서 재현하기 어려워 그대로 사용
}

function hexA(hex: string, alpha: number): string {
  const h = hex.replace("#", "");
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
