import { Muxer, ArrayBufferTarget } from "mp4-muxer";
import type { ChartVideoProject } from "../chart/types";
import { renderFrame } from "../render/renderFrame";
import { ensureFonts } from "./fonts";

// ============================================================================
// WebCodecs 기반 MP4 내보내기 (화면 녹화가 아님).
// ----------------------------------------------------------------------------
// 1) 보이지 않는 캔버스(1080×1920 풀 해상도)에 매 프레임을 renderFrame 으로 직접 그림
// 2) 그 프레임을 60fps 로 순서대로 뽑아 WebCodecs VideoEncoder 로 인코딩
// 3) 인코딩된 프레임을 mp4-muxer 로 MP4 컨테이너에 묶어 다운로드
// 미리보기와 "완전히 같은 렌더러"를 쓰기 때문에 화면 녹화보다 깨끗하고 정확합니다.
// ============================================================================

export interface ExportOptions {
  bitrate?: number; // bits/sec (기본 12Mbps)
  onProgress?: (done: number, total: number) => void;
  images?: Record<string, HTMLImageElement | ImageBitmap | null>;
  fileName?: string;
}

export function isExportSupported(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof (window as unknown as { VideoEncoder?: unknown }).VideoEncoder !== "undefined" &&
    typeof (window as unknown as { VideoFrame?: unknown }).VideoFrame !== "undefined"
  );
}

/** 지원되는 H.264 코덱 문자열을 고른다 */
async function pickCodec(width: number, height: number, fps: number): Promise<string> {
  const candidates = [
    "avc1.640034", // High 5.2
    "avc1.640033", // High 5.1
    "avc1.640032", // High 5.0
    "avc1.4d0034", // Main 5.2
    "avc1.42E034", // Baseline 5.2
    "avc1.42001f", // Baseline 3.1
  ];
  for (const codec of candidates) {
    try {
      const support = await (
        window as unknown as {
          VideoEncoder: {
            isConfigSupported: (c: unknown) => Promise<{ supported?: boolean }>;
          };
        }
      ).VideoEncoder.isConfigSupported({
        codec,
        width,
        height,
        framerate: fps,
        bitrate: 12_000_000,
      });
      if (support?.supported) return codec;
    } catch {
      // 다음 후보로
    }
  }
  return "avc1.42001f";
}

export async function exportMp4(
  project: ChartVideoProject,
  options: ExportOptions = {},
): Promise<Blob> {
  if (!isExportSupported()) {
    throw new Error(
      "이 브라우저는 WebCodecs 영상 내보내기를 지원하지 않습니다. 최신 크롬(데스크톱)에서 시도해 주세요.",
    );
  }

  await ensureFonts();

  const W = project.width;
  const H = project.height;
  const fps = project.fps;
  const totalFrames = Math.max(1, Math.round(project.durationSec * fps));
  const bitrate = options.bitrate ?? 12_000_000;

  // 숨겨진 풀 해상도 캔버스
  const canvas = document.createElement("canvas");
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext("2d", { alpha: false });
  if (!ctx) throw new Error("캔버스 2D 컨텍스트를 만들 수 없습니다.");

  const codec = await pickCodec(W, H, fps);

  const muxer = new Muxer({
    target: new ArrayBufferTarget(),
    video: { codec: "avc", width: W, height: H },
    fastStart: "in-memory",
  });

  const VideoEncoderCtor = (window as unknown as { VideoEncoder: any }).VideoEncoder;
  const VideoFrameCtor = (window as unknown as { VideoFrame: any }).VideoFrame;

  let encodeError: unknown = null;
  const encoder = new VideoEncoderCtor({
    output: (chunk: any, meta: any) => muxer.addVideoChunk(chunk, meta),
    error: (e: unknown) => {
      encodeError = e;
    },
  });

  encoder.configure({
    codec,
    width: W,
    height: H,
    bitrate,
    framerate: fps,
  });

  const frameDurUs = 1_000_000 / fps;
  const keyEvery = fps * 2; // 2초마다 키프레임

  for (let f = 0; f < totalFrames; f++) {
    if (encodeError) break;
    const progress = totalFrames > 1 ? f / (totalFrames - 1) : 0;

    renderFrame(ctx, project, progress, { images: options.images });

    const frame = new VideoFrameCtor(canvas, {
      timestamp: Math.round(f * frameDurUs),
      duration: Math.round(frameDurUs),
    });
    encoder.encode(frame, { keyFrame: f % keyEvery === 0 });
    frame.close();

    options.onProgress?.(f + 1, totalFrames);

    // 인코더 큐가 너무 밀리지 않도록 가끔 양보
    if (encoder.encodeQueueSize > 30) {
      await new Promise((r) => setTimeout(r, 0));
    }
  }

  await encoder.flush();
  encoder.close();
  if (encodeError) throw encodeError as Error;

  muxer.finalize();
  const { buffer } = muxer.target as ArrayBufferTarget;
  return new Blob([buffer], { type: "video/mp4" });
}

/** 내보낸 뒤 바로 파일로 다운로드 */
export async function exportAndDownload(
  project: ChartVideoProject,
  options: ExportOptions = {},
): Promise<void> {
  const blob = await exportMp4(project, options);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = options.fileName ?? "asset-race-1080x1920.mp4";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 8000);
}
