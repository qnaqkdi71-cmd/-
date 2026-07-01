import type { ChartVideoProject } from "../chart/types";
import { valueAt, fmtWon, fmtReturn, frameIndexAt } from "../chart/format";
import type { RenderTheme } from "./theme";
import { roundRect } from "./canvasUtils";

// 하단 요약(floating summary): 현재 프레임 기준 1위 자산과 원금→현재가치 요약을
// 화면 하단에 떠 있는 카드로 그립니다.

export function drawFloatingSummary(
  ctx: CanvasRenderingContext2D,
  project: ChartVideoProject,
  progress: number,
  theme: RenderTheme,
) {
  const series = project.series;
  if (!series.length) return;

  const vals = series.map((s) => valueAt(s.values, progress));
  let leaderIdx = 0;
  for (let i = 1; i < vals.length; i++) if (vals[i] > vals[leaderIdx]) leaderIdx = i;
  const leader = series[leaderIdx];
  const leaderMult = vals[leaderIdx];
  const leaderWon = leaderMult * project.initialInvestment;

  const x = 72;
  const w = project.width - 144;
  const h = 132;
  const y = project.height - 250;

  // 카드 배경
  ctx.save();
  roundRect(ctx, x, y, w, h, 26);
  ctx.fillStyle = theme.summaryBg;
  ctx.fill();
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = theme.summaryBorder;
  ctx.stroke();

  // 왼쪽: 1위 색 표식 + 이름
  const padX = 34;
  const dotR = 16;
  ctx.beginPath();
  ctx.arc(x + padX + dotR, y + h / 2, dotR, 0, Math.PI * 2);
  ctx.fillStyle = leader.color;
  ctx.fill();

  const textX = x + padX + dotR * 2 + 22;
  ctx.textAlign = "left";
  ctx.textBaseline = "alphabetic";
  ctx.font = "700 30px Pretendard, system-ui, sans-serif";
  ctx.fillStyle = theme.summaryText;
  ctx.fillText(`현재 1위 · ${leader.name}`, textX, y + 52);

  ctx.font = "400 24px Pretendard, system-ui, sans-serif";
  ctx.fillStyle = theme.mult;
  const initTxt = fmtWon(project.initialInvestment);
  ctx.fillText(`원금 ${initTxt} → ${fmtWon(leaderWon)}`, textX, y + 96);

  // 오른쪽: 수익률 배수 크게
  const mode = project.returnDisplay === "multiple" ? "multiple" : "percent";
  const retTxt = fmtReturn(leaderMult, mode);
  const gain = leaderMult >= 1;
  ctx.textAlign = "right";
  ctx.font = "800 52px Pretendard, system-ui, sans-serif";
  ctx.fillStyle = gain ? theme.gainColor : theme.lossColor;
  ctx.fillText(retTxt, x + w - padX, y + h / 2 + 18);
  ctx.restore();

  // 진행 표시(현재 연도 라벨은 renderFrame 의 큰 연도로 표현되지만 여기도 작게)
  const fi = frameIndexAt(progress, project.frames.length);
  void fi;
}
