"""구글 상위노출 글 자동작성기 — FastAPI 앱.

실행:
    cp .env.example .env    # 키 채우기(없어도 실행됨)
    pip install -r requirements.txt
    uvicorn app:app --reload
    → http://localhost:8000
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Vertex 서비스 계정 파일: 상대경로면 seo-writer 폴더 기준 절대경로로
_cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if _cred and not os.path.isabs(_cred):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(BASE_DIR / _cred)

from seo.keywords import generate_keywords          # noqa: E402
from seo.llm import LLM                              # noqa: E402
from seo.serp import SerpClient                      # noqa: E402
from seo.images import generate_article_images, image_status  # noqa: E402
from seo.strategy import ALGO_WEIGHTS, classify_competition  # noqa: E402
from seo.pipeline import (                           # noqa: E402
    build_onpage,
    distribution_plan,
    generate_article,
    guess_intent,
    md_to_html,
    score_article,
)

GENERATED_DIR = BASE_DIR / "static" / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="구글 상위노출 글 자동작성기")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

INTENTS = ["자동 감지", "정보형", "거래형", "탐색형"]


def _status():
    llm = LLM()
    serp = SerpClient()
    img = image_status()
    return {
        "llm_label": llm.label,
        "llm_ready": llm.available,
        "serp_ready": serp.enabled,
        "img_ready": img["ready"],
        "img_model": img["model"],
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "intents": INTENTS,
            "weights": ALGO_WEIGHTS,
            "status": _status(),
        },
    )


@app.get("/health")
def health():
    return {"ok": True, **_status()}


@app.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    keyword: str = Form(""),
    draft: str = Form(""),
    intent_choice: str = Form("자동 감지"),
    write_article: str = Form(""),  # 체크박스: 있으면 "on"
    make_images: str = Form(""),    # 체크박스: 있으면 "on"
):
    keyword = (keyword or "").strip()
    draft = (draft or "").strip()

    # 초안만 주고 키워드가 비면, 초안 첫 줄을 키워드로 사용
    if not keyword and draft:
        keyword = draft.splitlines()[0][:40]

    if not keyword:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "intents": INTENTS,
                "weights": ALGO_WEIGHTS,
                "status": _status(),
                "error": "목표 키워드(또는 초안)를 입력해 주세요.",
            },
        )

    intent = guess_intent(keyword) if intent_choice == "자동 감지" else intent_choice

    # 1) 이길 수 있는 롱테일 후보 (allintitle 링크)
    year = datetime.now().year
    candidates = generate_keywords(keyword, years=[year, year + 1], limit=24)

    # 2) 메인 키워드 경쟁 분석 (Serper 있으면 자동, 없으면 수동 링크)
    serp = SerpClient()
    report = serp.competition(keyword)
    verdict = None
    if report.allintitle_count is not None:
        label, tone, hint = classify_competition(report.allintitle_count)
        verdict = {"count": report.allintitle_count, "label": label, "tone": tone, "hint": hint}
    competitor_titles = [r.title for r in report.top_results]

    # 3) 글 생성 (키 없으면 골격)
    if write_article == "on":
        article, gen_status = generate_article(keyword, intent, competitor_titles, draft or None)
    else:
        from seo.pipeline import _skeleton_article
        article, gen_status = _skeleton_article(keyword, intent), "글 생성 건너뜀(분석만)."

    # 4) 이미지 생성 (Gemini) — 켜져 있고 키가 있을 때만
    images, image_error = [], None
    if make_images == "on":
        gimgs, image_error = generate_article_images(
            keyword, article, str(GENERATED_DIR), "/static/generated/"
        )
        images = [{"url": g.url, "alt": g.alt} for g in gimgs]

    # 5) 온페이지 · 점수 · 배포 플랜
    onpage = build_onpage(keyword, article)
    score = score_article(keyword, article)
    plan = distribution_plan(keyword, intent)
    body_html = md_to_html(article.get("body_markdown", ""))

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "keyword": keyword,
            "intent": intent,
            "status": _status(),
            "gen_status": gen_status,
            "report": report,
            "verdict": verdict,
            "candidates": candidates,
            "article": article,
            "body_html": body_html,
            "onpage": onpage,
            "score": score,
            "plan": plan,
            "images": images,
            "image_error": image_error,
        },
    )
