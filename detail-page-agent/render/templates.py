"""섹션 HTML/CSS 템플릿 (Jinja).

RenderPlan의 각 SectionRender를 template 종류에 따라 HTML 문자열로 만든다.
렌더러는 이 HTML을 Chromium으로 스크린샷해 PNG로 저장한다.
"""
from __future__ import annotations

from jinja2 import Environment
from markupsafe import Markup, escape

from config import FONT_STACK, PAGE_WIDTH


def _nl2br(value) -> Markup:
    return Markup("<br>".join(escape(line) for line in str(value).split("\n")))


def _stars(n) -> Markup:
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = 5
    n = max(0, min(5, n))
    return Markup("★" * n + "☆" * (5 - n))


env = Environment(autoescape=True)
env.filters["nl2br"] = _nl2br
env.filters["stars"] = _stars

_BASE = env.from_string("""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:{{width}}px; }
  body { font-family:{{font}}; -webkit-font-smoothing:antialiased;
         text-rendering:optimizeLegibility; }
  .section { width:{{width}}px; background:{{bg}}; color:{{text}};
             padding:78px 56px; position:relative; overflow:hidden; }
  .eyebrow { font-size:14px; font-weight:800; letter-spacing:.16em;
             text-transform:uppercase; color:{{accent}}; margin-bottom:16px; }
  .headline { font-size:42px; line-height:1.26; font-weight:800;
              letter-spacing:-.025em; }
  .subheadline { font-size:20px; font-weight:600; opacity:.82; margin-top:18px; }
  .lead { margin-top:26px; font-size:18px; line-height:1.8; }
  .lead p { margin-top:10px; opacity:.9; }
  .highlight-num { font-size:88px; font-weight:900; line-height:1;
                   color:{{accent}}; letter-spacing:-.03em; }
  .imgbox { margin-top:34px; width:100%; height:360px; border-radius:20px;
            background:linear-gradient(135deg,{{accent}}22,{{accent}}0d);
            border:1.5px solid {{accent}}44; display:flex; flex-direction:column;
            align-items:center; justify-content:center; gap:10px; }
  .imgbox .glyph { font-size:44px; opacity:.5; }
  .imgbox .cap { font-size:14px; font-weight:600; opacity:.55;
                 letter-spacing:.04em; }
  .grid2 { display:grid; grid-template-columns:1.05fr .95fr; gap:40px;
           align-items:center; }
  .grid2.flip { grid-template-columns:.95fr 1.05fr; }
  .grid2.flip .col-text { order:2; }
  .checklist { list-style:none; margin-top:26px; }
  .checklist li { position:relative; padding-left:34px; margin-top:16px;
                  font-size:18px; line-height:1.6; }
  .checklist li::before { content:"✓"; position:absolute; left:0; top:0;
    width:24px; height:24px; border-radius:50%; background:{{accent}};
    color:#fff; font-size:14px; font-weight:900; display:flex;
    align-items:center; justify-content:center; }
  .badges { display:flex; flex-wrap:wrap; gap:14px; margin-top:8px; }
  .badge { padding:14px 22px; border-radius:999px; font-size:16px;
           font-weight:700; background:{{accent}}1a; color:{{accent}};
           border:1.5px solid {{accent}}33; }
  .spec-grid { display:grid; grid-template-columns:1fr 1fr; gap:2px;
               margin-top:34px; background:{{accent}}22; border-radius:16px;
               overflow:hidden; }
  .spec-row { display:flex; justify-content:space-between; gap:16px;
              padding:20px 24px; background:{{bg}}; font-size:17px; }
  .spec-row .k { opacity:.65; font-weight:600; }
  .spec-row .v { font-weight:800; }
  .steps { display:grid; grid-template-columns:repeat(3,1fr); gap:20px;
           margin-top:38px; }
  .step { padding:28px 22px; border-radius:18px; background:{{accent}}12;
          border:1.5px solid {{accent}}2e; }
  .step .n { width:40px; height:40px; border-radius:12px; background:{{accent}};
             color:#fff; font-weight:900; font-size:18px; display:flex;
             align-items:center; justify-content:center; margin-bottom:16px; }
  .step .t { font-size:19px; font-weight:800; }
  .step .d { margin-top:8px; font-size:15px; line-height:1.6; opacity:.82; }
  table.cmp { width:100%; border-collapse:separate; border-spacing:0;
              margin-top:36px; font-size:17px; }
  table.cmp th, table.cmp td { padding:18px 20px; text-align:center; }
  table.cmp thead th { font-size:15px; letter-spacing:.03em; opacity:.7; }
  table.cmp thead th.us { color:{{accent}}; opacity:1; font-weight:900; }
  table.cmp td.feat { text-align:left; font-weight:700; opacity:.8; }
  table.cmp td.us { background:{{accent}}14; font-weight:800;
                    color:{{accent}}; }
  table.cmp tbody tr td { border-top:1px solid {{accent}}22; }
  table.cmp td.other { opacity:.55; }
  .reviews { display:grid; gap:18px; margin-top:34px; }
  .review { padding:26px 28px; border-radius:18px; background:{{bg}};
            border:1.5px solid {{accent}}26;
            box-shadow:0 8px 24px rgba(0,0,0,.05); }
  .review .stars { color:#f5a623; font-size:18px; letter-spacing:2px; }
  .review .txt { margin-top:12px; font-size:17px; line-height:1.65; }
  .review .who { margin-top:14px; font-size:14px; font-weight:700; opacity:.6; }
  .faqs { margin-top:32px; }
  .faq { padding:24px 26px; border-radius:16px; background:{{accent}}0f;
         margin-top:14px; }
  .faq .q { font-size:18px; font-weight:800; }
  .faq .q::before { content:"Q  "; color:{{accent}}; font-weight:900; }
  .faq .a { margin-top:10px; font-size:16px; line-height:1.7; opacity:.85; }
  .cta-btn { display:inline-block; margin-top:34px; padding:22px 52px;
             border-radius:999px; background:{{accent}}; color:#10231a;
             font-size:20px; font-weight:900; letter-spacing:.02em; }
  .center { text-align:center; }
  .center .checklist { display:inline-block; text-align:left; }
</style></head>
<body>{{ body }}</body></html>""")

_T = {
    "hero": env.from_string("""
<div class="section">
  {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
  <h1 class="headline" style="font-size:52px">{{ s.headline|nl2br }}</h1>
  {% if s.subheadline %}<div class="subheadline">{{ s.subheadline }}</div>{% endif %}
  {% if s.image_slot %}<div class="imgbox"><div class="glyph">◫</div>
    <div class="cap">제품 키비주얼</div></div>{% endif %}
</div>"""),

    "trust": env.from_string("""
<div class="section center">
  {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
  <h2 class="headline" style="font-size:32px">{{ s.headline|nl2br }}</h2>
  <div class="badges" style="justify-content:center;margin-top:28px">
    {% for it in s.items %}<div class="badge">{{ it.label }}</div>{% endfor %}
  </div>
</div>"""),

    "problem": env.from_string("""
<div class="section">
  {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
  <h2 class="headline">{{ s.headline|nl2br }}</h2>
  <ul class="checklist">
    {% for line in s.body %}<li>{{ line }}</li>{% endfor %}
  </ul>
</div>"""),

    "solution": env.from_string("""
<div class="section">
  {% if s.eyebrow %}<div class="eyebrow" style="color:{{ s.text }};opacity:.7">{{ s.eyebrow }}</div>{% endif %}
  <h2 class="headline">{{ s.headline|nl2br }}</h2>
  <ul class="checklist">
    {% for line in s.body %}<li>{{ line }}</li>{% endfor %}
  </ul>
</div>"""),

    "feature": env.from_string("""
<div class="section">
  <div class="grid2 {% if flip %}flip{% endif %}">
    <div class="col-text">
      {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
      {% if s.highlight %}<div class="highlight-num">{{ s.highlight }}</div>{% endif %}
      <h2 class="headline" style="font-size:34px;margin-top:14px">{{ s.headline|nl2br }}</h2>
      <ul class="checklist">
        {% for line in s.body %}<li>{{ line }}</li>{% endfor %}
      </ul>
    </div>
    <div class="col-img">
      <div class="imgbox" style="height:320px"><div class="glyph">◫</div>
        <div class="cap">{{ s.eyebrow or '제품 이미지' }}</div></div>
    </div>
  </div>
</div>"""),

    "spec": env.from_string("""
<div class="section">
  {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
  <h2 class="headline" style="font-size:32px">{{ s.headline|nl2br }}</h2>
  <div class="spec-grid">
    {% for it in s.items %}
    <div class="spec-row"><span class="k">{{ it.label }}</span><span class="v">{{ it.value }}</span></div>
    {% endfor %}
  </div>
</div>"""),

    "howto": env.from_string("""
<div class="section">
  {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
  <h2 class="headline" style="font-size:32px">{{ s.headline|nl2br }}</h2>
  <div class="steps">
    {% for it in s.items %}
    <div class="step"><div class="n">{{ loop.index }}</div>
      <div class="t">{{ it.title }}</div><div class="d">{{ it.desc }}</div></div>
    {% endfor %}
  </div>
</div>"""),

    "compare": env.from_string("""
<div class="section">
  {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
  <h2 class="headline" style="font-size:32px">{{ s.headline|nl2br }}</h2>
  <table class="cmp">
    <thead><tr><th></th><th class="us">FOREST</th><th>일반 제품</th></tr></thead>
    <tbody>
    {% for it in s.items %}
      <tr><td class="feat">{{ it.feature }}</td>
          <td class="us">{{ it.us }}</td>
          <td class="other">{{ it.others }}</td></tr>
    {% endfor %}
    </tbody>
  </table>
</div>"""),

    "review": env.from_string("""
<div class="section">
  {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
  <h2 class="headline" style="font-size:32px">{{ s.headline|nl2br }}</h2>
  <div class="reviews">
    {% for it in s.items %}
    <div class="review"><div class="stars">{{ it.stars|stars }}</div>
      <div class="txt">{{ it.text }}</div>
      <div class="who">{{ it.name }} 고객님</div></div>
    {% endfor %}
  </div>
</div>"""),

    "faq": env.from_string("""
<div class="section">
  {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
  <h2 class="headline" style="font-size:32px">{{ s.headline|nl2br }}</h2>
  <div class="faqs">
    {% for it in s.items %}
    <div class="faq"><div class="q">{{ it.q }}</div><div class="a">{{ it.a }}</div></div>
    {% endfor %}
  </div>
</div>"""),

    "cta": env.from_string("""
<div class="section center">
  {% if s.eyebrow %}<div class="eyebrow">{{ s.eyebrow }}</div>{% endif %}
  <h2 class="headline" style="font-size:44px">{{ s.headline|nl2br }}</h2>
  {% if s.subheadline %}<div class="subheadline">{{ s.subheadline }}</div>{% endif %}
  {% if s.body %}<ul class="checklist">
    {% for line in s.body %}<li>{{ line }}</li>{% endfor %}
  </ul>{% endif %}
  <div><span class="cta-btn">지금 구매하기</span></div>
</div>"""),
}


def render_section_html(section, flip: bool = False) -> str:
    """SectionRender → 완결 HTML 문서 문자열.

    pydantic 객체를 그대로 s로 넘긴다(s.headline 등 속성 접근). items의
    각 원소는 평범한 dict이며, Jinja가 it.label 을 dict['label']로 폴백 해석한다.
    """
    body_tpl = _T.get(section.template, _T["solution"])
    body = body_tpl.render(s=section, flip=flip)
    return _BASE.render(
        width=PAGE_WIDTH, font=FONT_STACK,
        bg=section.bg, text=section.text, accent=section.accent,
        body=Markup(body),
    )
