"""(선택) Gemini로 섹션 이미지를 생성한다 — 고급 경로.

output/gemini_prompts.json(프롬프트 생성 에이전트 산출)을 읽어 각 섹션을
Gemini 이미지 모델로 생성하고 output/sections/에 저장한다. 이후
scripts/stitch_images.py로 이어붙인다.

전제:
  pip install google-genai pillow
  export GEMINI_API_KEY=...            # 필수(무료 발급: aistudio.google.com)
  export GEMINI_IMAGE_MODEL=...        # 선택(기본: gemini-2.5-flash-image = 무료 티어)

기본 모델은 무료 티어가 있는 Nano Banana(gemini-2.5-flash-image)입니다.
더 높은 품질은 GEMINI_IMAGE_MODEL=gemini-3-pro-image-preview(유료)로 바꾸세요.
주의: 모델 id/응답 형식은 제공자 업데이트로 달라질 수 있습니다.
키가 없으면 안내만 출력하고 종료합니다.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
SECTIONS = OUT / "sections"
MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")  # 무료 티어 모델


def _load_prompts() -> dict:
    p = OUT / "gemini_prompts.json"
    if not p.exists():
        print("[오류] output/gemini_prompts.json 이 없습니다. 먼저 프롬프트 생성 단계를 완료하세요.")
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))


def _save_image_bytes(data: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main() -> None:
    if not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY 가 설정되지 않았습니다.")
        print("  export GEMINI_API_KEY=... 후 다시 실행하세요.")
        print("  (키 없이 결과를 보려면: python3 main.py — HTML 렌더 경로)")
        sys.exit(0)
    try:
        from google import genai  # type: ignore
    except ImportError:
        print("google-genai 가 없습니다:  pip install google-genai")
        sys.exit(1)

    prompts = _load_prompts()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    SECTIONS.mkdir(parents=True, exist_ok=True)

    made = 0
    for key in sorted(prompts):
        spec = prompts[key]
        prompt = spec.get("prompt", "")
        filename = spec.get("filename", f"{key}.png")
        if not prompt:
            continue
        print(f"· 생성 중: {filename}")
        try:
            try:  # 이미지 출력 모달리티 요청(지원 시)
                from google.genai import types  # type: ignore
                cfg = types.GenerateContentConfig(response_modalities=["IMAGE"])
                resp = client.models.generate_content(
                    model=MODEL, contents=[prompt], config=cfg)
            except (ImportError, TypeError, ValueError):
                resp = client.models.generate_content(model=MODEL, contents=[prompt])
            saved = False
            for cand in getattr(resp, "candidates", []) or []:
                for part in getattr(cand.content, "parts", []) or []:
                    inline = getattr(part, "inline_data", None)
                    if inline and getattr(inline, "data", None):
                        _save_image_bytes(inline.data, SECTIONS / filename)
                        saved = True
                        made += 1
                        break
                if saved:
                    break
            if not saved:
                print(f"  [경고] 이미지 데이터를 찾지 못했습니다: {filename}")
        except Exception as e:  # noqa: BLE001
            print(f"  [오류] {filename}: {repr(e)[:200]}")
        time.sleep(3)  # 레이트 리밋 대비

    print(f"\n완료: {made}장 → {SECTIONS}")
    print("다음: python3 scripts/stitch_images.py output/sections output/final_page.png")


if __name__ == "__main__":
    main()
