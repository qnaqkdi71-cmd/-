"""상세페이지 에이전트 · 중앙 제어(오케스트레이터).

제품 원자료를 입력받아 5단계 파이프라인을 순차 실행하고, 최종적으로
상세페이지 섹션 이미지(PNG) 묶음을 output/ 에 생성한다.

    Phase 1 정보수집 → Phase 2 리서치 → Phase 3 카피라이팅
              → Phase 4 디자인 → Phase 5 프롬프팅 → 렌더(PNG)

사용법:
    python main.py                     # 예시 제품 + (키 없으면) mock 자동
    python main.py --mock              # 강제 mock 모드
    python main.py --input examples/sample_input.json
    python main.py --name "제품명" --brand "브랜드" --raw "스펙/메모..."
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import agents
from config import OUTPUT_DIR, SECTION_BLUEPRINT, has_api_key
from render import render_plan, stitch_full_page

ROOT = Path(__file__).resolve().parent


def _log(step: str, msg: str) -> None:
    print(f"  \033[92m✓\033[0m [{step}] {msg}")


def _phase(n, title: str) -> None:
    print(f"\n\033[1m▸ Phase {n} · {title}\033[0m")


def load_input(args) -> dict:
    if args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        return data
    if args.name:
        return {"name": args.name, "brand": args.brand or "", "raw": args.raw or ""}
    # 기본: 동봉된 예시 제품
    from agents.mockdata import SAMPLE_INPUT
    return dict(SAMPLE_INPUT)


def run(args) -> int:
    use_mock = args.mock or not has_api_key()
    mode = "MOCK (샘플 데이터)" if use_mock else "LIVE (Claude Opus 4.8)"
    raw = load_input(args)

    print("\033[1m=" * 56)
    print(" 상세페이지 에이전트 파이프라인")
    print("=" * 56 + "\033[0m")
    print(f" 모드   : {mode}")
    print(f" 제품   : {raw.get('name', '(미지정)')}")
    print(f" 섹션   : {len(SECTION_BLUEPRINT)}개")
    if use_mock and not args.mock:
        print(" \033[93m※ ANTHROPIC_API_KEY 미설정 → mock 모드로 자동 전환\033[0m")

    _phase(1, "정보수집")
    brief = agents.collect(raw, use_mock=use_mock)
    _log("collector", f"제품 브리프 정규화 · 특징 {len(brief.key_features)}개 · 스펙 {len(brief.specs)}개")

    _phase(2, "리서치")
    market = agents.research(brief, use_mock=use_mock)
    _log("researcher", f"키워드 {len(market.keywords)} · 반론 {len(market.objections)} · 앵글 {len(market.selling_angles)}")

    _phase(3, "카피라이팅")
    copy = agents.write_copy(brief, market, use_mock=use_mock)
    _log("copywriter", f"섹션 카피 {len(copy.sections)}개 작성")

    _phase(4, "디자인")
    design = agents.design(brief, copy, use_mock=use_mock)
    slots = sum(1 for s in design.sections if s.image_slot)
    _log("designer", f"테마 {design.theme.primary} · 이미지 슬롯 {slots}개")

    _phase(5, "프롬프팅(개발)")
    plan = agents.build_render_plan(brief, copy, design, use_mock=use_mock)
    prompts = sum(1 for s in plan.sections if s.image_prompt)
    _log("prompter", f"렌더 플랜 병합 · 이미지 프롬프트 {prompts}개 생성")

    _phase("R", "렌더링 (HTML → PNG)")
    out_dir = Path(args.out) if args.out else OUTPUT_DIR
    paths = render_plan(plan, out_dir=out_dir)
    _log("renderer", f"섹션 PNG {len(paths)}장 저장")
    if not args.no_stitch:
        full = stitch_full_page(paths, out_dir=out_dir)
        if full:
            _log("renderer", f"전체 미리보기 1장 저장 → {full.name}")

    print("\n\033[1m완료.\033[0m 결과물:", out_dir)
    for p in paths:
        print("   -", p.name)
    print("   - render_plan.json  (섹션별 렌더 명세 + 이미지 프롬프트)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="상세페이지 생성 멀티 에이전트")
    ap.add_argument("--mock", action="store_true", help="Claude 호출 없이 샘플 데이터로 실행")
    ap.add_argument("--input", help="제품 입력 JSON 경로")
    ap.add_argument("--name", help="제품명")
    ap.add_argument("--brand", help="브랜드명")
    ap.add_argument("--raw", help="원자료(스펙/메모) 텍스트")
    ap.add_argument("--out", help="출력 디렉터리 (기본 output/)")
    ap.add_argument("--no-stitch", action="store_true", help="전체 미리보기 합성 생략")
    args = ap.parse_args()
    try:
        return run(args)
    except Exception as e:  # noqa: BLE001
        print(f"\n\033[91m✗ 파이프라인 실패:\033[0m {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    sys.exit(main())
