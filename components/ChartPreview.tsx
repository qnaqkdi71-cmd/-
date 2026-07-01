"use client";

import { useEffect, useRef } from "react";
import type { ChartVideoProject } from "../lib/chart/types";
import { renderFrame } from "../lib/render/renderFrame";
import { ensureFonts } from "../lib/export/fonts";

// 미리보기 캔버스 — 영상 내보내기와 "완전히 같은 renderFrame" 을 사용.
// 풀 해상도(1080×1920)로 그리고 CSS 로 축소해 보여줍니다.

export default function ChartPreview({
  project,
  progress,
  displayWidth = 360,
}: {
  project: ChartVideoProject;
  progress: number;
  displayWidth?: number;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fontsReady = useRef(false);

  useEffect(() => {
    ensureFonts().then(() => {
      fontsReady.current = true;
      draw();
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function draw() {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    renderFrame(ctx, project, progress);
  }

  useEffect(() => {
    draw();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [project, progress]);

  const ratio = project.height / project.width;
  return (
    <canvas
      ref={canvasRef}
      width={project.width}
      height={project.height}
      style={{
        width: displayWidth,
        height: displayWidth * ratio,
        borderRadius: 24,
        display: "block",
        background: "#04050a",
        boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
      }}
    />
  );
}
