"""오케스트레이션: 경쟁분석 → 글 생성 → 온페이지 조립 → 점수화 → 배포 플랜.

키가 없어도 전 단계가 '골격'으로 동작하도록 설계했다.
"""

from __future__ import annotations

import html
import json
import re

from .llm import LLM, LLMError
from .strategy import MODIFIERS, build_article_prompt


# ─────────────────────────────────────────────────────────────
# 의도 추정
# ─────────────────────────────────────────────────────────────
def guess_intent(keyword: str) -> str:
    kw = keyword.strip()
    for intent, mods in MODIFIERS.items():
        for m in mods:
            if kw.endswith(m) or f" {m}" in kw:
                return intent
    return "정보형"


# ─────────────────────────────────────────────────────────────
# 글 생성
# ─────────────────────────────────────────────────────────────
def generate_article(
    keyword: str,
    intent: str,
    competitor_titles: list[str] | None = None,
    draft: str | None = None,
) -> tuple[dict, str]:
    """(article dict, status 메시지) 반환. LLM 없으면 골격 생성."""
    llm = LLM()
    if not llm.available:
        return _skeleton_article(keyword, intent), (
            f"AI 미연결({llm.label}) → 골격만 생성했습니다. "
            ".env에 키를 넣으면 실제 글이 자동 작성됩니다."
        )

    prompt = build_article_prompt(keyword, intent, competitor_titles, draft)
    try:
        raw = llm.complete(prompt)
    except LLMError as e:
        return _skeleton_article(keyword, intent), f"AI 호출 실패 → 골격 생성. ({e})"

    article = _parse_json(raw)
    if article is None:
        # JSON 파싱 실패 → 최소한 본문이라도 살림
        art = _skeleton_article(keyword, intent)
        art["body_markdown"] = raw
        return art, f"{llm.label}로 생성(형식 보정)."
    art = _normalize_article(article, keyword)
    return art, f"{llm.label}로 생성 완료."


def _parse_json(text: str) -> dict | None:
    if not text:
        return None
    t = text.strip()
    # 코드펜스 제거
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?", "", t).strip()
        t = re.sub(r"```$", "", t).strip()
    # 첫 { ~ 마지막 } 구간만 추출
    start, end = t.find("{"), t.rfind("}")
    if start != -1 and end != -1 and end > start:
        t = t[start : end + 1]
    try:
        obj = json.loads(t)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def _normalize_article(a: dict, keyword: str) -> dict:
    """LLM 결과에 빠진 필드를 안전하게 채운다."""
    def s(key, default=""):
        v = a.get(key, default)
        return v if isinstance(v, str) else default

    def lst(key):
        v = a.get(key, [])
        return v if isinstance(v, list) else []

    faq = []
    for item in lst("faq"):
        if isinstance(item, dict):
            faq.append({"question": item.get("question", ""), "answer": item.get("answer", "")})

    return {
        "title_tag": s("title_tag") or f"{keyword} 완벽 정리",
        "meta_description": s("meta_description"),
        "slug": slugify(s("slug") or keyword),
        "h1": s("h1") or s("title_tag") or keyword,
        "intro": s("intro"),
        "outline": [x for x in lst("outline") if isinstance(x, str)],
        "body_markdown": s("body_markdown"),
        "faq": faq,
        "image_alts": [x for x in lst("image_alts") if isinstance(x, str)],
        "internal_anchor_suggestions": [x for x in lst("internal_anchor_suggestions") if isinstance(x, str)],
        "external_source_suggestions": [x for x in lst("external_source_suggestions") if isinstance(x, str)],
        "word_count": a.get("word_count") if isinstance(a.get("word_count"), int) else None,
        "is_skeleton": False,
    }


def _skeleton_article(keyword: str, intent: str) -> dict:
    """키 없이도 보여줄 구조 골격."""
    outline = [
        f"{keyword}(이)란? 핵심 요약",
        f"{keyword} 조건·대상 한눈에",
        f"{keyword} 신청 방법 (단계별)",
        "자주 하는 실수와 체크리스트",
        "실제 사례 / 예시",
    ]
    body = (
        f"## {keyword}, 결론부터\n\n"
        f"(여기에 검색자가 원하는 답을 2~3문장으로 먼저 제시)\n\n"
        + "\n\n".join(f"## {h}\n\n(내용)" for h in outline)
        + "\n\n> ⬆️ AI 키를 연결하면 이 골격이 실제 완성 원고로 자동 작성됩니다."
    )
    return {
        "title_tag": f"{keyword} 총정리 (조건·신청방법·서류)",
        "meta_description": f"{keyword} 핵심만 빠르게. 조건, 신청 방법, 서류, 자주 하는 실수까지 한 번에 정리했습니다.",
        "slug": slugify(keyword),
        "h1": f"{keyword} 완벽 가이드",
        "intro": f"{keyword}에 대해 검색자가 가장 궁금해하는 핵심을 먼저 정리합니다.",
        "outline": outline,
        "body_markdown": body,
        "faq": [
            {"question": f"{keyword} 신청 자격은?", "answer": "(AI 연결 시 자동 작성)"},
            {"question": f"{keyword} 지급일은 언제인가요?", "answer": "(AI 연결 시 자동 작성)"},
        ],
        "image_alts": [f"{keyword} 신청 화면 예시", f"{keyword} 자격 요건 표"],
        "internal_anchor_suggestions": [f"{keyword} 신청 방법 자세히 보기"],
        "external_source_suggestions": ["관련 정부기관 공식 페이지", "공신력 있는 통계/보도자료"],
        "word_count": None,
        "is_skeleton": True,
    }


# ─────────────────────────────────────────────────────────────
# 온페이지 조립 (5대 태그 + 구조화 데이터)
# ─────────────────────────────────────────────────────────────
def slugify(text: str) -> str:
    t = (text or "").strip().lower()
    t = re.sub(r"[^a-z0-9\s-]", "", t)          # 영문/숫자만
    t = re.sub(r"[\s-]+", "-", t).strip("-")
    return t or "seo-post"


def build_onpage(keyword: str, article: dict) -> dict:
    title = article.get("title_tag", "")
    meta = article.get("meta_description", "")
    return {
        "title_tag": title,
        "title_len": len(title),
        "meta_description": meta,
        "meta_len": len(meta),
        "slug": article.get("slug", ""),
        "url_example": f"https://내사이트.com/{article.get('slug', '')}",
        "h1": article.get("h1", ""),
        "headings": article.get("outline", []),
        "image_alts": article.get("image_alts", []),
        "anchor_good": f"{keyword} 자세히 보기",
        "anchor_bad": "여기 클릭",
        "json_ld": _json_ld(keyword, article),
    }


def _json_ld(keyword: str, article: dict) -> str:
    faq = article.get("faq") or []
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article.get("title_tag", keyword),
        "description": article.get("meta_description", ""),
        "about": keyword,
    }
    if faq:
        data = [
            data,
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f.get("question", ""),
                        "acceptedAnswer": {"@type": "Answer", "text": f.get("answer", "")},
                    }
                    for f in faq
                ],
            },
        ]
    return json.dumps(data, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────
# 온페이지 자동 점수화
# ─────────────────────────────────────────────────────────────
def score_article(keyword: str, article: dict) -> dict:
    body = article.get("body_markdown", "") or ""
    title = article.get("title_tag", "") or ""
    meta = article.get("meta_description", "") or ""
    intro = (article.get("intro", "") or "") + body[:200]
    checks = []

    def add(ok, label, weight, tip=""):
        checks.append({"ok": bool(ok), "label": label, "weight": weight, "tip": tip})

    add(keyword.split()[0] in title, "제목(타이틀)에 핵심 키워드 포함", 5, "검색결과 제목에 키워드가 있어야 합니다.")
    add(0 < len(title) <= 60, "타이틀 길이 60자 이내", 2)
    add(keyword.split()[0] in intro, "도입부에 키워드(두괄식)", 4, "첫 문단에서 키워드로 답을 시작하세요.")
    add(len(article.get("outline") or []) >= 3, "H2 소제목 3개 이상(구조화)", 3)
    add(bool(re.search(r"(^|\n)\s*([-*]|\d+\.|\|)", body)), "목록/표 등 실물 요소 포함", 4,
        "템플릿·체크리스트·표·단계 목록 같은 '실물'을 넣으세요.")
    add(len(article.get("faq") or []) >= 3, "FAQ 3개 이상(AEO)", 3)
    add(0 < len(meta) <= 160 and keyword.split()[0] in meta, "메타설명(160자 이내+키워드)", 2)
    add(len(article.get("image_alts") or []) >= 1, "이미지 alt 텍스트 제안", 1)
    add(len(re.sub(r"\s", "", body)) >= 800, "본문 분량 충분(800자+)", 3)
    add(bool(article.get("slug")), "URL 슬러그 설정", 1)

    got = sum(c["weight"] for c in checks if c["ok"])
    total = sum(c["weight"] for c in checks)
    score = round(got / total * 100) if total else 0
    if score >= 90:
        grade = ("A", "상위노출 준비 완료. 발행하고 외부 트래픽을 유입하세요.")
    elif score >= 75:
        grade = ("B", "거의 완성. 빠진 항목만 보완하세요.")
    elif score >= 55:
        grade = ("C", "기반은 있으나 콘텐츠/구조에 구멍이 있습니다.")
    else:
        grade = ("D", "핵심(제목·키워드·구조·실물)부터 채우세요.")
    return {"checks": checks, "score": score, "grade": grade[0], "note": grade[1]}


# ─────────────────────────────────────────────────────────────
# 배포 플랜 (소셜 SEO — 오석종)
# ─────────────────────────────────────────────────────────────
def distribution_plan(keyword: str, intent: str) -> list[str]:
    return [
        f"‘{keyword}’에 관심 있는 사람이 모인 커뮤니티/카페/오픈채팅에 글을 '유용한 자료'로 소개하고 링크 연결",
        "요약본을 SNS(스레드·인스타·X)에 올리고 '자세한 건 블로그' 형태로 유입",
        "관련 질문이 올라오는 Q&A(지식iN 등)에 답변하며 자연스럽게 링크",
        "발행 후 구글 서치 콘솔에 색인 요청 + 노출 키워드 추적",
        "내 사이트의 관련 글에서 이 글로 내부 링크 연결(권위 분배)",
    ]


# ─────────────────────────────────────────────────────────────
# 마크다운 → 안전한 HTML (미리보기용)
# ─────────────────────────────────────────────────────────────
def md_to_html(md: str) -> str:
    if not md:
        return ""
    lines = md.split("\n")
    out: list[str] = []
    in_ul = in_ol = False
    table_buf: list[str] = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>"); in_ul = False
        if in_ol:
            out.append("</ol>"); in_ol = False

    def flush_table():
        nonlocal table_buf
        if not table_buf:
            return
        rows = [r for r in table_buf if not re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", r)]
        out.append('<div class="tbl"><table>')
        for i, row in enumerate(rows):
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            tag = "th" if i == 0 else "td"
            out.append("<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>")
        out.append("</table></div>")
        table_buf = []

    for line in lines:
        stripped = line.strip()
        if "|" in stripped and stripped.startswith("|"):
            close_lists()
            table_buf.append(stripped)
            continue
        else:
            flush_table()

        if not stripped:
            close_lists()
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            continue
        if re.match(r"^[-*]\s+", stripped):
            if not in_ul:
                close_lists(); out.append("<ul>"); in_ul = True
            item = re.sub(r"^[-*]\s+", "", stripped)
            out.append(f"<li>{_inline(item)}</li>")
            continue
        if re.match(r"^\d+\.\s+", stripped):
            if not in_ol:
                close_lists(); out.append("<ol>"); in_ol = True
            item = re.sub(r"^\d+\.\s+", "", stripped)
            out.append(f"<li>{_inline(item)}</li>")
            continue
        if stripped.startswith(">"):
            close_lists()
            quote = stripped.lstrip("> ")
            out.append(f"<blockquote>{_inline(quote)}</blockquote>")
            continue
        close_lists()
        out.append(f"<p>{_inline(stripped)}</p>")

    flush_table()
    close_lists()
    return "\n".join(out)


def _inline(text: str) -> str:
    # HTML 이스케이프 후 **굵게** / `코드` 만 허용 (XSS 방지)
    t = html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t
