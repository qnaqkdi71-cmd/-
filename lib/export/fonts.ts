// Pretendard 웹폰트를 캔버스 렌더 전에 확실히 로드하기 위한 헬퍼.
// 폰트가 로드되기 전에 캔버스에 그리면 글자가 기본 폰트로 나오므로,
// 미리보기 시작/영상 내보내기 전에 반드시 ensureFonts() 를 await 합니다.

let loaded: Promise<void> | null = null;

const WEIGHTS = ["400", "600", "700", "800"];

export function ensureFonts(): Promise<void> {
  if (loaded) return loaded;
  loaded = (async () => {
    if (typeof document === "undefined" || !("fonts" in document)) return;
    try {
      // @font-face 는 globals.css 에서 CDN(Pretendard) 으로 선언됨.
      await Promise.all(
        WEIGHTS.map((w) =>
          (document as Document).fonts.load(`${w} 64px Pretendard`, "가나다ABC0123"),
        ),
      );
      await (document as Document).fonts.ready;
    } catch {
      // 폰트 로드 실패해도 렌더는 시스템 폰트로 진행
    }
  })();
  return loaded;
}
