"""Vertex AI(무료 크레딧)로 output/gemini_prompts.json 섹션 통째 생성.
429(분당 속도제한)는 대기 후 재시도. 사용 토큰은 output/_usage.json 저장.
    python3 scripts/gen_vertex.py [only_key1,only_key2]
"""
from __future__ import annotations
import io, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass
c = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if c and not os.path.isabs(c):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str((ROOT / c).resolve())

from google import genai
from google.genai import types
from PIL import Image

OUT = ROOT / "output"
MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")


def square1200(data: bytes) -> Image.Image:
    im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size; s = min(w, h)
    return im.crop(((w - s)//2, (h - s)//2, (w - s)//2 + s, (h - s)//2 + s)).resize(
        (1200, 1200), Image.LANCZOS)


def main() -> None:
    client = genai.Client(vertexai=True, project=os.environ["GOOGLE_CLOUD_PROJECT"],
                          location=os.getenv("GOOGLE_CLOUD_LOCATION", "global"))
    prompts = json.loads((OUT / "gemini_prompts.json").read_text(encoding="utf-8"))
    keys = sorted(prompts)
    if len(sys.argv) > 1:
        only = set(sys.argv[1].split(","))
        keys = [k for k in keys if k in only]
    print(f"모델 {MODEL} · {len(keys)}개 섹션 (Vertex/무료크레딧)", flush=True)

    made = tin = tout = 0
    for key in keys:
        fn = prompts[key]["filename"]
        for attempt in range(8):
            try:
                r = client.models.generate_content(
                    model=MODEL, contents=[prompts[key]["prompt"]],
                    config=types.GenerateContentConfig(response_modalities=["IMAGE"]))
                img = None
                for cand in (r.candidates or []):
                    for p in (cand.content.parts or []):
                        d = getattr(getattr(p, "inline_data", None), "data", None)
                        if d: img = d; break
                    if img: break
                um = getattr(r, "usage_metadata", None)
                if img:
                    square1200(img).save(OUT / fn)
                    made += 1
                    tin += getattr(um, "prompt_token_count", 0) or 0
                    tout += getattr(um, "candidates_token_count", 0) or 0
                    print(f"  OK {fn}", flush=True)
                    break
                time.sleep(6)
            except Exception as e:  # noqa: BLE001
                m = str(e)[:90]
                print(f"  retry{attempt+1} {fn}: {m}", flush=True)
                time.sleep(20 if ("429" in m or "RESOURCE" in m) else 5)
        time.sleep(2)

    (OUT / "_usage.json").write_text(json.dumps(
        {"images": made, "in_tokens": tin, "out_tokens": tout, "model": MODEL},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDONE {made}/{len(keys)} · in {tin} / out {tout} tok", flush=True)


if __name__ == "__main__":
    main()
