import type { PageContent } from "./types";

/** HTML 특수문자 이스케이프 (사용자 입력이 마크업을 깨지 않도록) */
function esc(s: string): string {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** 여러 줄 텍스트를 <br> 로 */
function nl2br(s: string): string {
  return esc(s).replace(/\n/g, "<br>");
}

function telHref(phone: string): string {
  const digits = phone.replace(/[^0-9+]/g, "");
  return digits ? `tel:${digits}` : "#contact";
}

function kakaoHref(kakao: string): string {
  if (!kakao) return "#contact";
  return /^https?:\/\//i.test(kakao) ? kakao : "#contact";
}

/** 별점 표시 */
function stars(n: number): string {
  const full = Math.max(0, Math.min(5, Math.round(n)));
  return "★★★★★☆☆☆☆☆".slice(5 - full, 10 - full);
}

/**
 * 상세페이지를 완결된 HTML 문서 문자열로 렌더링합니다.
 * 미리보기(iframe)와 다운로드가 이 함수 하나를 공유하므로,
 * 화면에서 본 것과 저장되는 파일이 100% 동일합니다.
 */
export function renderPageHtml(c: PageContent): string {
  const accent = c.accent;
  const hasPhone = !!c.contact.phone;
  const hasKakao = !!c.contact.kakao;
  const hasContact = hasPhone || hasKakao;

  const badges = c.hero.badges
    .map((b) => `<span class="badge">${esc(b)}</span>`)
    .join("");

  const statsHtml = c.stats
    .map(
      (s) =>
        `<div class="stat"><div class="stat-v">${esc(s.value)}</div><div class="stat-l">${esc(
          s.label,
        )}</div></div>`,
    )
    .join("");

  const problemsHtml = c.problems.items
    .map((p) => `<li class="prob"><span class="prob-ic">✓</span><span>${esc(p)}</span></li>`)
    .join("");

  const servicesHtml = c.services.items
    .map(
      (it, i) =>
        `<div class="card"><div class="card-n">${String(i + 1).padStart(
          2,
          "0",
        )}</div><h3>${esc(it.title)}</h3><p>${esc(it.desc)}</p></div>`,
    )
    .join("");

  const whyHtml = c.why.items
    .map(
      (it) =>
        `<div class="why-item"><div class="why-dot"></div><div><h3>${esc(
          it.title,
        )}</h3><p>${esc(it.desc)}</p></div></div>`,
    )
    .join("");

  const processHtml = c.process.steps
    .map(
      (s, i) =>
        `<div class="step"><div class="step-n">${i + 1}</div><div class="step-b"><h3>${esc(
          s.title,
        )}</h3><p>${esc(s.desc)}</p></div></div>`,
    )
    .join("");

  const testiHtml = c.testimonials.items
    .map(
      (t) =>
        `<div class="testi"><div class="testi-stars">${stars(
          t.rating,
        )}</div><p>“${esc(t.text)}”</p><div class="testi-name">${esc(
          t.name,
        )}</div></div>`,
    )
    .join("");

  const faqHtml = c.faq.items
    .map(
      (f) =>
        `<details class="faq"><summary>${esc(
          f.q,
        )}<span class="faq-plus">+</span></summary><div class="faq-a">${esc(
          f.a,
        )}</div></details>`,
    )
    .join("");

  const ctaButtons = (big: boolean) => {
    const cls = big ? "cta-btn cta-big" : "cta-btn";
    const parts: string[] = [];
    if (hasPhone) {
      parts.push(
        `<a class="${cls} cta-call" href="${telHref(c.contact.phone)}">📞 전화 상담</a>`,
      );
    }
    if (hasKakao) {
      const href = kakaoHref(c.contact.kakao);
      parts.push(
        `<a class="${cls} cta-kakao" href="${esc(href)}"${
          /^https?:/i.test(href) ? ' target="_blank" rel="noopener"' : ""
        }>💬 카카오톡 상담</a>`,
      );
    }
    if (!hasContact) {
      parts.push(`<a class="${cls} cta-call" href="#contact">문의하기</a>`);
    }
    return parts.join("");
  };

  const stickyBar = hasContact
    ? `<div class="sticky">${ctaButtons(false)}</div>`
    : "";

  const contactLines: string[] = [];
  if (hasPhone) contactLines.push(`전화: ${esc(c.contact.phone)}`);
  if (hasKakao) contactLines.push(`카카오톡: ${esc(c.contact.kakao)}`);

  return `<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(c.hero.title)} · ${esc(c.professionLabel)}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.css">
<style>
  :root{ --accent:${accent}; --ink:#111826; --muted:#5b6577; --line:#e8ebf0; --soft:#f5f7fa; }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:Pretendard,system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;color:var(--ink);background:#fff;line-height:1.65;-webkit-font-smoothing:antialiased}
  .wrap{max-width:720px;margin:0 auto;background:#fff;overflow:hidden}
  section{padding:56px 24px}
  h2{font-size:26px;font-weight:800;letter-spacing:-.02em;line-height:1.3}
  .sub{color:var(--muted);margin-top:10px;font-size:15px}
  .eyebrow{display:inline-block;color:var(--accent);font-weight:700;font-size:13px;letter-spacing:.02em;margin-bottom:8px}

  /* HERO */
  .hero{position:relative;color:#fff;padding:64px 24px 72px;background:
    radial-gradient(120% 90% at 85% 0%, color-mix(in srgb, var(--accent) 55%, #000) 0%, transparent 60%),
    linear-gradient(160deg, var(--accent) 0%, color-mix(in srgb, var(--accent) 65%, #0b1020) 100%);}
  .hero .kicker{font-size:13px;font-weight:700;opacity:.9;letter-spacing:.03em}
  .hero h1{font-size:34px;font-weight:900;letter-spacing:-.03em;line-height:1.22;margin:14px 0 4px}
  .hero .hl{color:#fff;background:rgba(255,255,255,.18);border-radius:8px;padding:2px 10px;display:inline-block;margin-top:6px;font-size:18px;font-weight:700}
  .hero p.lead{margin-top:18px;font-size:16px;line-height:1.7;color:rgba(255,255,255,.94);max-width:560px}
  .badges{margin-top:22px;display:flex;flex-wrap:wrap;gap:8px}
  .badge{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);padding:7px 13px;border-radius:999px;font-size:13px;font-weight:600}
  .hero-cta{margin-top:26px}
  .hero-cta a{display:inline-block;background:#fff;color:var(--accent);font-weight:800;font-size:16px;padding:15px 28px;border-radius:12px;text-decoration:none;box-shadow:0 10px 30px rgba(0,0,0,.18)}

  /* STATS */
  .stats{display:flex;background:var(--ink);color:#fff;padding:0}
  .stat{flex:1;text-align:center;padding:26px 8px;border-right:1px solid rgba(255,255,255,.1)}
  .stat:last-child{border-right:none}
  .stat-v{font-size:26px;font-weight:900;color:#fff}
  .stat-l{font-size:12px;color:rgba(255,255,255,.65);margin-top:4px}

  /* PROBLEMS */
  .problems{background:var(--soft)}
  .prob-list{list-style:none;margin-top:26px;display:flex;flex-direction:column;gap:12px}
  .prob{display:flex;gap:12px;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px;font-size:16px;font-weight:600}
  .prob-ic{flex:none;width:26px;height:26px;border-radius:50%;background:color-mix(in srgb,var(--accent) 14%,#fff);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800}

  /* SERVICES */
  .grid{margin-top:28px;display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .card{border:1px solid var(--line);border-radius:16px;padding:22px 18px;background:#fff}
  .card-n{color:var(--accent);font-weight:900;font-size:14px;letter-spacing:.05em}
  .card h3{font-size:17px;margin:8px 0 6px;font-weight:800}
  .card p{color:var(--muted);font-size:14px}

  /* WHY */
  .why{background:var(--soft)}
  .why-list{margin-top:26px;display:flex;flex-direction:column;gap:18px}
  .why-item{display:flex;gap:14px;align-items:flex-start}
  .why-dot{flex:none;width:14px;height:14px;border-radius:50%;background:var(--accent);margin-top:6px;box-shadow:0 0 0 5px color-mix(in srgb,var(--accent) 18%,#fff)}
  .why-item h3{font-size:17px;font-weight:800}
  .why-item p{color:var(--muted);font-size:14.5px;margin-top:3px}

  /* PROCESS */
  .steps{margin-top:28px;display:flex;flex-direction:column;gap:0}
  .step{display:flex;gap:16px;position:relative;padding-bottom:26px}
  .step:not(:last-child)::before{content:"";position:absolute;left:19px;top:40px;bottom:0;width:2px;background:var(--line)}
  .step-n{flex:none;width:40px;height:40px;border-radius:50%;background:var(--accent);color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:16px;z-index:1}
  .step-b h3{font-size:16.5px;font-weight:800}
  .step-b p{color:var(--muted);font-size:14px;margin-top:2px}

  /* TESTIMONIALS */
  .testis{background:var(--soft)}
  .testi-list{margin-top:26px;display:flex;flex-direction:column;gap:14px}
  .testi{background:#fff;border:1px solid var(--line);border-radius:16px;padding:20px}
  .testi-stars{color:#ffb400;font-size:16px;letter-spacing:2px}
  .testi p{margin:10px 0;font-size:15px;line-height:1.7}
  .testi-name{color:var(--muted);font-size:13px;font-weight:700}

  /* FAQ */
  .faq{border:1px solid var(--line);border-radius:14px;margin-top:12px;overflow:hidden;background:#fff}
  .faq summary{list-style:none;cursor:pointer;padding:18px 20px;font-weight:700;font-size:16px;display:flex;justify-content:space-between;align-items:center;gap:12px}
  .faq summary::-webkit-details-marker{display:none}
  .faq-plus{color:var(--accent);font-size:22px;font-weight:400;transition:transform .2s;flex:none}
  .faq[open] .faq-plus{transform:rotate(45deg)}
  .faq-a{padding:0 20px 18px;color:var(--muted);font-size:15px;line-height:1.7}

  /* FINAL CTA */
  .final{color:#fff;text-align:center;background:linear-gradient(160deg, var(--accent) 0%, color-mix(in srgb,var(--accent) 62%,#0b1020) 100%)}
  .final h2{color:#fff}
  .final .sub{color:rgba(255,255,255,.9)}
  .final-btns{margin-top:26px;display:flex;flex-direction:column;gap:12px;max-width:360px;margin-left:auto;margin-right:auto}
  .cta-big{padding:17px;font-size:17px;border-radius:14px}
  .cta-btn{text-decoration:none;font-weight:800;display:block;text-align:center}
  .cta-call{background:#fff;color:var(--accent)}
  .cta-kakao{background:#fee500;color:#3c1e1e}
  .final-note{margin-top:18px;font-size:13px;color:rgba(255,255,255,.8)}

  /* FOOTER */
  footer{padding:28px 24px 110px;text-align:center;color:var(--muted);font-size:13px;background:#fff}
  footer .biz{font-weight:800;color:var(--ink);font-size:15px}

  /* STICKY BAR */
  .sticky{position:fixed;left:0;right:0;bottom:0;z-index:50;display:flex;gap:8px;padding:10px 14px calc(10px + env(safe-area-inset-bottom));background:rgba(255,255,255,.92);backdrop-filter:blur(8px);border-top:1px solid var(--line);max-width:720px;margin:0 auto}
  .sticky .cta-btn{flex:1;padding:14px;border-radius:12px;font-size:15px}

  @media(max-width:520px){
    .hero h1{font-size:29px}
    h2{font-size:23px}
    .grid{grid-template-columns:1fr}
  }
</style>
</head>
<body>
<div class="wrap">

  <section class="hero">
    <div class="kicker">${esc(c.hero.kicker)}</div>
    <h1>${nl2br(c.hero.title)}</h1>
    <div class="hl">${esc(c.hero.highlight)}</div>
    <p class="lead">${nl2br(c.hero.subtitle)}</p>
    <div class="badges">${badges}</div>
    <div class="hero-cta"><a href="${hasContact ? (hasPhone ? telHref(c.contact.phone) : kakaoHref(c.contact.kakao)) : "#contact"}">${esc(c.hero.ctaPrimary)}</a></div>
  </section>

  <div class="stats">${statsHtml}</div>

  <section class="problems">
    <span class="eyebrow">CHECK</span>
    <h2>${esc(c.problems.title)}</h2>
    <p class="sub">${esc(c.problems.subtitle)}</p>
    <ul class="prob-list">${problemsHtml}</ul>
  </section>

  <section class="services">
    <span class="eyebrow">SERVICE</span>
    <h2>${esc(c.services.title)}</h2>
    <p class="sub">${esc(c.services.subtitle)}</p>
    <div class="grid">${servicesHtml}</div>
  </section>

  <section class="why">
    <span class="eyebrow">WHY US</span>
    <h2>${esc(c.why.title)}</h2>
    <p class="sub">${esc(c.why.subtitle)}</p>
    <div class="why-list">${whyHtml}</div>
  </section>

  <section class="process">
    <span class="eyebrow">PROCESS</span>
    <h2>${esc(c.process.title)}</h2>
    <p class="sub">${esc(c.process.subtitle)}</p>
    <div class="steps">${processHtml}</div>
  </section>

  <section class="testis">
    <span class="eyebrow">REVIEW</span>
    <h2>${esc(c.testimonials.title)}</h2>
    <div class="testi-list">${testiHtml}</div>
  </section>

  <section class="faqs">
    <span class="eyebrow">FAQ</span>
    <h2>${esc(c.faq.title)}</h2>
    ${faqHtml}
  </section>

  <section class="final" id="contact">
    <h2>${esc(c.finalCta.title)}</h2>
    <p class="sub">${esc(c.finalCta.subtitle)}</p>
    <div class="final-btns">${ctaButtons(true)}</div>
    <div class="final-note">${esc(c.finalCta.note)}</div>
  </section>

  <footer>
    <div class="biz">${esc(c.businessName)}</div>
    ${contactLines.length ? `<div style="margin-top:6px">${contactLines.join(" · ")}</div>` : ""}
  </footer>

</div>
${stickyBar}
</body>
</html>`;
}
