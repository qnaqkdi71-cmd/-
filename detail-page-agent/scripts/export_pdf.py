"""섹션 PNG들을 이어붙여 PDF로 내보낸다.

사용:
    python3 scripts/export_pdf.py <섹션PNG_폴더> <출력.pdf>
    python3 scripts/export_pdf.py output output/final_page.pdf
"""
from __future__ import annotations

import sys
from pathlib import Path

from stitch_images import find_section_images, stitch_sections


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    folder = Path(sys.argv[1])
    out = Path(sys.argv[2])
    if out.suffix.lower() != ".pdf":
        out = out.with_suffix(".pdf")
    paths = find_section_images(folder)
    if not paths:
        print(f"[오류] {folder}에서 섹션 PNG를 찾지 못했습니다.")
        sys.exit(1)
    stitch_sections(paths, out)
    print(f"완료: PDF 내보내기 → {out}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
