"""섹션 PNG를 세로로 이어붙여 최종 상세페이지 한 장을 만든다.

디자인 스펙 준수: 모든 섹션을 너비 1200px로 맞춘 뒤(FULL BLEED) 스티칭.

사용:
    python3 scripts/stitch_images.py <섹션PNG_폴더> <출력경로(.png|.pdf)>
    python3 scripts/stitch_images.py output output/final_page.png
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image

TARGET_WIDTH = 1200
SECTION_RE = re.compile(r"^\d{2}_.+\.png$")  # 01_hero.png ~ 13_final_cta.png


def find_section_images(folder: Path) -> list[Path]:
    imgs = [p for p in folder.iterdir()
            if SECTION_RE.match(p.name) and not p.name.startswith("00_")]
    return sorted(imgs, key=lambda p: p.name)


def stitch_sections(image_paths: list[Path], output_path: Path,
                    target_width: int = TARGET_WIDTH) -> Path:
    images = []
    for p in image_paths:
        img = Image.open(p).convert("RGB")
        if img.width != target_width:  # 1200px로 정규화
            h = round(img.height * target_width / img.width)
            img = img.resize((target_width, h), Image.LANCZOS)
        images.append(img)

    total_height = sum(img.height for img in images)
    result = Image.new("RGB", (target_width, total_height), "white")
    y = 0
    for img in images:
        result.paste(img, (0, y))
        y += img.height

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() == ".pdf":
        result.save(output_path, "PDF", resolution=150.0)
    else:
        result.save(output_path, "PNG", optimize=True)
    return output_path


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    folder = Path(sys.argv[1])
    out = Path(sys.argv[2])
    paths = find_section_images(folder)
    if not paths:
        print(f"[오류] {folder}에서 섹션 PNG(01_*.png ~)를 찾지 못했습니다.")
        sys.exit(1)
    stitch_sections(paths, out)
    print(f"완료: {len(paths)}장 스티칭 → {out}")


if __name__ == "__main__":
    main()
