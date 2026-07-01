// 캔버스 공통 그리기 유틸

export function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
) {
  const radius = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  if (typeof (ctx as unknown as { roundRect?: unknown }).roundRect === "function") {
    ctx.roundRect(x, y, w, h, radius);
  } else {
    ctx.moveTo(x + radius, y);
    ctx.arcTo(x + w, y, x + w, y + h, radius);
    ctx.arcTo(x + w, y + h, x, y + h, radius);
    ctx.arcTo(x, y + h, x, y, radius);
    ctx.arcTo(x, y, x + w, y, radius);
    ctx.closePath();
  }
}

/** 원형 로고: 브랜드색 배경 + 흰 테두리 + 가운데 글자(또는 이미지) */
export function drawLogo(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  size: number,
  color: string,
  letter: string,
  ringColor: string,
  img?: HTMLImageElement | ImageBitmap | null,
) {
  const r = size / 2;
  ctx.save();
  // 배경 원
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();

  if (img) {
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.98, 0, Math.PI * 2);
    ctx.clip();
    const d = size * 0.62;
    ctx.drawImage(img, cx - d / 2, cy - d / 2, d, d);
    ctx.restore();
  } else {
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = `800 ${Math.round(size * 0.5)}px Pretendard, system-ui, sans-serif`;
    ctx.fillText(letter, cx, cy + size * 0.02);
  }

  // 테두리
  ctx.beginPath();
  ctx.arc(cx, cy, r - 1.5, 0, Math.PI * 2);
  ctx.lineWidth = 3;
  ctx.strokeStyle = ringColor;
  ctx.stroke();
  ctx.restore();
}

/** 알약(pill) 배경 텍스트 — 수익률 표기용 */
export function drawPill(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  text: string,
  fontPx: number,
  textColor: string,
  bgColor: string,
) {
  ctx.font = `800 ${fontPx}px Pretendard, system-ui, sans-serif`;
  ctx.textBaseline = "middle";
  ctx.textAlign = "left";
  const padX = fontPx * 0.5;
  const w = ctx.measureText(text).width + padX * 2;
  const h = fontPx * 1.5;
  roundRect(ctx, x, y - h / 2, w, h, h / 2);
  ctx.fillStyle = bgColor;
  ctx.fill();
  ctx.fillStyle = textColor;
  ctx.fillText(text, x + padX, y);
  return w;
}
