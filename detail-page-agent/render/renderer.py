"""HTML → PNG 렌더러 (Playwright + 사전설치 Chromium).

RenderPlan의 각 섹션을 개별 PNG로 저장한다. 결과물은 한국형 상세페이지
섹션 이미지 묶음(기본 13장)이 된다.
"""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from config import CHROMIUM_PATH, DEVICE_SCALE, OUTPUT_DIR, PAGE_HEIGHT, PAGE_WIDTH
from contracts import RenderPlan

from .templates import render_section_html


def render_plan(plan: RenderPlan, out_dir: Path | None = None) -> list[Path]:
    out = Path(out_dir or OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)

    launch_kwargs = {"args": ["--no-sandbox", "--force-color-profile=srgb"]}
    if CHROMIUM_PATH:
        launch_kwargs["executable_path"] = CHROMIUM_PATH

    paths: list[Path] = []
    feature_idx = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page(
            viewport={"width": PAGE_WIDTH, "height": PAGE_HEIGHT},
            device_scale_factor=DEVICE_SCALE,
        )
        for i, section in enumerate(plan.sections, start=1):
            flip = False
            if section.template == "feature":
                flip = feature_idx % 2 == 1
                feature_idx += 1
            html = render_section_html(section, flip=flip, brand=plan.brand)
            page.set_content(html, wait_until="networkidle")
            fname = f"{i:02d}_{section.id}.png"
            fpath = out / fname
            # .section 요소만 정확히 캡처(자연 높이 그대로)
            el = page.query_selector(".section")
            el.screenshot(path=str(fpath))
            paths.append(fpath)

        browser.close()

    # 렌더 플랜(이미지 프롬프트 포함)도 함께 저장 — '개발용' 산출물
    (out / "render_plan.json").write_text(
        plan.model_dump_json(indent=2), encoding="utf-8"
    )
    return paths


def stitch_full_page(image_paths: list[Path], out_dir: Path | None = None) -> Path | None:
    """13장 섹션 PNG를 세로로 이어붙인 미리보기 1장을 만든다(선택).

    Pillow가 있으면 생성하고, 없으면 조용히 건너뛴다.
    """
    try:
        from PIL import Image
    except ImportError:
        return None
    out = Path(out_dir or OUTPUT_DIR)
    imgs = [Image.open(p) for p in image_paths]
    width = max(im.width for im in imgs)
    total_h = sum(im.height for im in imgs)
    canvas = Image.new("RGB", (width, total_h), "#ffffff")
    y = 0
    for im in imgs:
        canvas.paste(im, (0, y))
        y += im.height
    full = out / "00_full_preview.png"
    canvas.save(full)
    return full
