"""Gemini(기본 3 Pro)로 '섹션 통째' 이미지를 생성한다 — 스킬 방식.

output/gemini_prompts.json 의 각 프롬프트(=섹션 전체 레이아웃 + 한글 텍스트)를
이미지 모델에 넣어, 텍스트·카드·다이어그램까지 이미지 안에 렌더된 완성 섹션을
output/NN_id.png 로 저장한다. (compose_overlay 불필요)

이후 scripts/stitch_images.py 로 이어붙인다.

    GEMINI_IMAGE_MODEL=gemini-3-pro-image-preview  # 기본(최상 품질, 유료)
    python3 scripts/gen_sections_pro.py
"""
from __future__ import annotations

import io
import json
import os
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

OUT = ROOT / "output"
MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")


def _square_1200(data: bytes) -> Image.Image:
    im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size
    s = min(w, h)
    return im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize(
        (1200, 1200), Image.LANCZOS)


def _make_client():
    """Vertex(무료 크레딧) 우선, 없으면 AI Studio API 키."""
    from google import genai

    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("true", "1", "yes")
    if use_vertex:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
        if not project:
            print("GOOGLE_CLOUD_PROJECT 가 없습니다 (.env).")
            sys.exit(1)
        # GOOGLE_APPLICATION_CREDENTIALS 는 상대경로면 ROOT 기준으로 보정
        cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if cred and not os.path.isabs(cred):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str((ROOT / cred).resolve())
        print(f"인증: Vertex AI · project={project} · location={location} (무료 크레딧)")
        return genai.Client(vertexai=True, project=project, location=location)

    if not os.getenv("GEMINI_API_KEY"):
        print("인증 정보가 없습니다: Vertex(GOOGLE_GENAI_USE_VERTEXAI) 또는 GEMINI_API_KEY 필요.")
        sys.exit(1)
    print("인증: AI Studio API 키")
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def main() -> None:
    from google.genai import types

    client = _make_client()
    prompts = json.loads((OUT / "gemini_prompts.json").read_text(encoding="utf-8"))
    print(f"모델: {MODEL} · {len(prompts)}개 섹션 생성")

    made = 0
    for key in sorted(prompts):
        fn = prompts[key]["filename"]
        for attempt in range(3):
            try:
                r = client.models.generate_content(
                    model=MODEL, contents=[prompts[key]["prompt"]],
                    config=types.GenerateContentConfig(response_modalities=["IMAGE"]))
                got = False
                for c in (r.candidates or []):
                    for p in (c.content.parts or []):
                        d = getattr(getattr(p, "inline_data", None), "data", None)
                        if d:
                            _square_1200(d).save(OUT / fn)
                            made += 1
                            got = True
                            print("  ✅", fn)
                            break
                    if got:
                        break
                if got:
                    break
                print("  ⚠️", fn, "이미지 없음(재시도)")
                time.sleep(5)
            except Exception as e:  # noqa: BLE001
                msg = str(e)[:100]
                print(f"  시도{attempt + 1} {fn}: {msg}")
                time.sleep(12 if ("429" in msg or "RESOURCE" in msg) else 4)
        time.sleep(1)

    print(f"\n생성 완료: {made}/{len(prompts)} → {OUT}")
    print("다음: python3 scripts/stitch_images.py output output/final_page.png")


if __name__ == "__main__":
    main()
