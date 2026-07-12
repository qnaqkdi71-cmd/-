"""빠른 데모 실행기.

Claude Code 없이도, 동봉된 예시 데이터로 상세페이지 PNG 13장을 바로
만들어 결과를 확인하는 용도입니다. (실제 사용은 Claude Code에서 에이전트
팀에게 요청 → output/에 copy_output.json·design_direction.json 생성)

    python3 main.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RENDER = ROOT / ".claude" / "skills" / "detail-page-render" / "scripts" / "render.py"
SAMPLE = ROOT / "examples" / "sample_output"


def main() -> None:
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    for f in ("structured_brief.json", "copy_output.json", "design_direction.json"):
        shutil.copy(SAMPLE / f, out / f)
    print("예시 데이터를 output/에 복사했습니다. 렌더를 시작합니다...\n")
    subprocess.run([sys.executable, str(RENDER)], check=True)


if __name__ == "__main__":
    main()
