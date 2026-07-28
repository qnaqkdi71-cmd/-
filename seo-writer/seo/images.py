"""이미지 생성 (Gemini) — 상세페이지에서 쓰던 방식 그대로.

글이 만들어낸 'alt(이미지 설명)'을 이미지 프롬프트로 바꿔 Gemini 이미지 모델로 생성한다.
같은 GEMINI_API_KEY / 크레딧을 사용한다.

- IMAGE_PROVIDER=gemini | none
- GEMINI_IMAGE_MODEL=... (imagen-* 이면 generate_images, 그 외 gemini-*-image 는 generate_content)
- IMAGE_ASPECT=16:9 (블로그 가로형)
- IMAGE_COUNT=3 (대표 1 + 본문 2)
"""

from __future__ import annotations

import base64
import os
import uuid
from dataclasses import dataclass


class ImageError(RuntimeError):
    pass


@dataclass
class GeneratedImage:
    url: str
    alt: str


def image_status() -> dict:
    provider = (os.getenv("IMAGE_PROVIDER") or "none").strip().lower()
    if provider == "vertex":
        ready = bool(os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GEMINI_VERTEX_PROJECT"))
    else:
        ready = provider == "gemini" and bool(os.getenv("GEMINI_API_KEY"))
    model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    return {"provider": provider, "ready": ready, "model": model}


def _build_client():
    """IMAGE_PROVIDER에 맞는 google-genai 클라이언트 생성."""
    provider = (os.getenv("IMAGE_PROVIDER") or "none").strip().lower()
    try:
        from google import genai  # lazy import
    except ImportError as e:
        raise ImageError("google-genai 미설치: pip install google-genai") from e
    if provider == "vertex":
        project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GEMINI_VERTEX_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("GEMINI_VERTEX_LOCATION", "global")
        if not project:
            raise ImageError("GEMINI_VERTEX_PROJECT(프로젝트 ID) 없음")
        return genai.Client(vertexai=True, project=project, location=location)
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ImageError("GEMINI_API_KEY 없음")
    return genai.Client(api_key=key)


def _default_style() -> str:
    return os.getenv(
        "IMAGE_STYLE",
        "photorealistic, editorial blog photography, natural lighting, high detail",
    )


def _build_prompt(description: str, keyword: str) -> str:
    return (
        f"{description}. "
        f"블로그 글 주제: {keyword}. "
        f"Style: {_default_style()}. "
        "Do not include any text, letters, captions, watermarks, or logos in the image."
    )


def _to_bytes(data) -> bytes | None:
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    if isinstance(data, str):
        try:
            return base64.b64decode(data)
        except Exception:
            return None
    return None


def _extract_inline(resp) -> bytes | None:
    for cand in getattr(resp, "candidates", None) or []:
        content = getattr(cand, "content", None)
        for part in getattr(content, "parts", None) or []:
            inline = getattr(part, "inline_data", None)
            if inline is not None:
                b = _to_bytes(getattr(inline, "data", None))
                if b:
                    return b
    return None


def _generate_one(prompt: str, aspect: str) -> bytes | None:
    """한 장 생성 → PNG/JPEG 바이트. 실패 시 ImageError."""
    model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    client = _build_client()

    # (1) Imagen 계열
    if model.startswith("imagen"):
        try:
            from google.genai import types
            resp = client.models.generate_images(
                model=model,
                prompt=prompt,
                config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio=aspect),
            )
            imgs = getattr(resp, "generated_images", None) or []
            if imgs:
                img = imgs[0].image
                return _to_bytes(getattr(img, "image_bytes", None))
            return None
        except Exception as e:
            raise ImageError(f"Imagen 생성 실패: {e}") from e

    # (2) Gemini 이미지 계열 (gemini-*-image) — 버전차 대응해 config 유무 둘 다 시도
    last = None
    for use_cfg in (True, False):
        try:
            if use_cfg:
                from google.genai import types
                cfg = types.GenerateContentConfig(response_modalities=["IMAGE"])
                resp = client.models.generate_content(model=model, contents=prompt, config=cfg)
            else:
                resp = client.models.generate_content(model=model, contents=prompt)
            data = _extract_inline(resp)
            if data:
                return data
        except Exception as e:
            last = e
    if last:
        raise ImageError(f"Gemini 이미지 생성 실패: {last}")
    return None


def generate_article_images(
    keyword: str,
    article: dict,
    out_dir: str,
    url_prefix: str,
) -> tuple[list[GeneratedImage], str | None]:
    """대표 이미지 + 본문 이미지 몇 장을 생성해 저장하고 (목록, 에러) 반환."""
    st = image_status()
    if not st["ready"]:
        return [], None  # 이미지 비활성 — 조용히 건너뜀

    try:
        count = max(1, min(int(os.getenv("IMAGE_COUNT", "3")), 6))
    except ValueError:
        count = 3
    aspect = os.getenv("IMAGE_ASPECT", "16:9")

    # 프롬프트 목록: 대표(H1/키워드) + alt들
    descriptions: list[str] = [f"{keyword} 대표 이미지, {article.get('h1', keyword)}"]
    descriptions += [a for a in (article.get("image_alts") or []) if isinstance(a, str)]
    descriptions = descriptions[:count]

    os.makedirs(out_dir, exist_ok=True)
    images: list[GeneratedImage] = []
    err: str | None = None

    for i, desc in enumerate(descriptions):
        try:
            data = _generate_one(_build_prompt(desc, keyword), aspect)
        except ImageError as e:
            err = str(e)
            break  # 첫 실패에서 중단(대개 모델명/권한 문제 → 나머지도 동일)
        if not data:
            continue
        fname = f"{uuid.uuid4().hex}.png"
        with open(os.path.join(out_dir, fname), "wb") as f:
            f.write(data)
        images.append(GeneratedImage(url=url_prefix + fname, alt=desc))

    return images, err
