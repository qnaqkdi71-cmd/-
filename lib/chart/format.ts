// 숫자 포맷 / 보간 유틸 — 원본 디자인의 fmtWon/fmtReturn/lerp/ease 규칙을 그대로 옮김

export function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

/** smoothstep 이징 (원본 디자인과 동일) */
export function smoothstep(t: number): number {
  return t * t * (3 - 2 * t);
}

/** 원화 금액 포맷: 1억 이상은 "N.NN억원", 그 미만은 "N,NNN만원" */
export function fmtWon(v: number): string {
  if (v >= 1e8) {
    const s = (v / 1e8).toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
    return s + "억원";
  }
  const man = Math.round(v / 1e4);
  return man.toLocaleString("en-US") + "만원";
}

/**
 * 수익률 표기.
 *  - m: 배수 (1.0 = 원금)
 *  - mode: "percent" | "multiple"
 */
export function fmtReturn(m: number, mode: "percent" | "multiple"): string {
  const up = m >= 1;
  const arrow = up ? "▲" : "▼";
  if (mode === "percent") {
    const pct = Math.round((m - 1) * 100);
    return arrow + " " + Math.abs(pct).toLocaleString("en-US") + "%";
  }
  const v = m >= 10 ? Math.round(m).toLocaleString("en-US") : m.toFixed(1);
  return arrow + " " + v + "배";
}

/** #rrggbb + alpha → rgba() 문자열 */
export function hexA(hex: string, alpha: number): string {
  const h = hex.replace("#", "");
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * 프레임 진행도(progress 0~1)에서 시계열의 보간된 배수를 구함.
 * value(배수)를 이징 보간해서 부드러운 애니메이션 값을 만든다.
 */
export function valueAt(values: { value: number }[], progress: number): number {
  const n = values.length;
  if (n === 0) return 1;
  if (n === 1) return values[0].value;
  const fp = progress * (n - 1);
  let i = Math.floor(fp);
  if (i >= n - 1) i = n - 2;
  if (i < 0) i = 0;
  const f = fp - i;
  const ef = smoothstep(f);
  return lerp(values[i].value, values[i + 1].value, ef);
}

/** 진행도 → 현재 프레임 라벨 인덱스 */
export function frameIndexAt(progress: number, frameCount: number): number {
  const fp = progress * (frameCount - 1);
  return Math.max(0, Math.min(frameCount - 1, Math.round(fp)));
}
