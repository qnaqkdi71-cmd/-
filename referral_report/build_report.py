#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
레퍼럴 수익 원화 환산 보고서 생성기.

  python3 build_report.py --prices upbit_prices.json

산출물:
  referral_krw_report.pdf   최종 보고서
  referral_krw_calc.csv     일별 계산 원본

계산 규칙 (엄수):
  * 모든 산술은 decimal.Decimal. float 곱셈/합산 없음.
  * 반올림은 최종 표시 단계에서만. 중간값은 원본 정밀도 유지.
  * 원화 표시: ROUND_HALF_UP 으로 원 단위 반올림.
  * 코인 수량 표시: 소수점 8자리.
  * 총합 = 반올림 전 값의 합을 마지막에 한 번 반올림.
    (반올림된 일별 금액의 단순 합과 다르면 각주로 차이 표기)
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP, getcontext

getcontext().prec = 60
KST = timezone(timedelta(hours=9))

PERIOD_START = "2026-07-05"
PERIOD_END = "2026-08-03"

FONT_DIR = "/usr/share/fonts/truetype/nanum"
FONT_REGULAR = os.path.join(FONT_DIR, "NanumGothic.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "NanumGothicBold.ttf")


# ============================================================ 원천 데이터
# 아래 표는 reconcile_sources.py 로 원본 파일(비트겟 .xls / OKX .csv)에서
# 독립 재계산하여 전 항목 일치를 확인한 값이다. 날짜는 이미 KST 로 귀속됨.
BITGET_RAW = """2026-07-06|USDT|0.05519086
2026-07-07|USDT|0.72318245
2026-07-08|USDT|1.44880931
2026-07-09|USDT|0.65391822
2026-07-10|USDT|0.40762463
2026-07-11|USDT|0.97668047
2026-07-12|USDT|1.08092436
2026-07-13|USDT|0.34912220
2026-07-14|USDT|0.43396821
2026-07-15|USDT|0.88717523
2026-07-16|USDT|0.58028019
2026-07-17|USDT|1.12814775
2026-07-18|USDT|2.22271867
2026-07-19|USDT|2.74556005
2026-07-20|USDT|2.63135450
2026-07-21|USDT|0.04830689
2026-07-22|USDT|0.00108944
2026-07-23|USDT|0.46848996
2026-07-24|USDT|0.94201198
2026-07-24|U|0.00098050
2026-07-25|USDT|2.05246529
2026-07-26|USDT|2.88841518
2026-07-26|LUNA|0.01601086
2026-07-27|USDT|0.43930136
2026-07-28|USDT|0.09730676
2026-07-28|AB|0.49888957
2026-07-29|USDT|1.34953647
2026-07-29|LUNC|60.67429200
2026-07-30|USDT|0.57102597
2026-07-31|USDT|2.47632695
2026-08-01|USDT|2.56336078
2026-08-02|USDT|1.72496360
2026-08-03|USDT|0.15844178"""

OKX_RAW = """2026-07-05|USDT|6.37327905
2026-07-06|USDT|0.35667323
2026-07-07|USDT|1.72804075
2026-07-08|USDT|0.33044265
2026-07-09|USDT|0.13993123
2026-07-10|USDT|0.39727431
2026-07-11|USDT|0.36106085
2026-07-12|USDT|0.37037684
2026-07-13|USDT|0.37265589
2026-07-14|USDT|0.32160852
2026-07-15|USDT|0.58759896
2026-07-16|USDT|0.21594031
2026-07-17|USDT|0.15042238
2026-07-18|USDT|0.06898063
2026-07-19|USDT|0.49547015
2026-07-20|USDT|4.42719226
2026-07-21|USDT|0.89306113
2026-07-22|USDT|17.76386949
2026-07-23|USDT|2.67737491
2026-07-24|USDT|0.14122465
2026-07-25|USDT|0.05095488
2026-07-26|USDT|0.03455971
2026-07-27|USDT|0.24016105
2026-07-28|USDT|0.17521031
2026-07-29|USDT|0.12609048
2026-07-30|USDT|0.12792255
2026-07-31|USDT|0.95914284
2026-08-01|USDT|0.61273846
2026-08-02|USDT|0.07151718"""

# 본인 거래 수수료 환급 — 레퍼럴 소득이 아니므로 총합에서 제외, 참고 표시만.
OKX_FEE_REBATE_RAW = """2026-07-06|USDT|0.09725453"""

# 프롬프트 3-5항 검증 기준값
EXPECTED_TOTALS = [
    ("비트겟", "USDT", Decimal("32.10569951")),
    ("비트겟", "LUNC", Decimal("60.67429200")),
    ("비트겟", "LUNA", Decimal("0.01601086")),
    ("비트겟", "AB", Decimal("0.49888957")),
    ("비트겟", "U", Decimal("0.00098050")),
    ("OKX", "USDT", Decimal("40.57077565")),
]
TOL = Decimal("1e-8")


def parse_rows(text, exchange):
    rows = []
    for line in text.strip().splitlines():
        d, coin, amt = line.split("|")
        rows.append({"date": d, "exchange": exchange, "coin": coin, "qty": Decimal(amt)})
    return rows


# ============================================================ 표시 포맷
def fmt_krw(value: Decimal) -> str:
    """원 단위 ROUND_HALF_UP 반올림 후 천 단위 콤마 + '원'."""
    return f"{value.quantize(Decimal('1'), rounding=ROUND_HALF_UP):,}원"


def round_krw(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def fmt_qty(value: Decimal) -> str:
    """소수점 8자리 고정 + 천 단위 콤마."""
    q = value.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
    intpart, _, frac = f"{q:f}".partition(".")
    return f"{int(intpart):,}.{frac}"


def fmt_price(value: Decimal) -> str:
    """업비트 종가. 정수면 정수로, 소수면 유효 자리 유지."""
    if value == value.to_integral_value():
        return f"{value.to_integral_value():,}원"
    return f"{value.normalize():,f}원".replace("원", "") + "원"


# ============================================================ 계산 엔진
def compute(rows, price_map, listed_map):
    """각 행에 종가·원화액을 부여한다. 반올림은 하지 않는다."""
    out = []
    for r in rows:
        coin = r["coin"]
        date = r["date"]
        rec = dict(r)
        if not listed_map.get(coin, False):
            rec["price"] = None
            rec["krw_raw"] = Decimal(0)
            rec["status"] = "업비트 KRW 미상장 → 환산 제외"
        else:
            p = price_map.get(coin, {}).get(date)
            if p is None:
                rec["price"] = None
                rec["krw_raw"] = Decimal(0)
                rec["status"] = "종가 없음"
            else:
                rec["price"] = Decimal(p)
                rec["krw_raw"] = r["qty"] * Decimal(p)   # Decimal × Decimal
                rec["status"] = "정상"
        out.append(rec)
    return out


def subtotal(rows):
    """반올림 전 합계, 그리고 '반올림된 일별액의 합' 을 함께 돌려준다."""
    raw = sum((r["krw_raw"] for r in rows), Decimal(0))
    of_rounded = sum((round_krw(r["krw_raw"]) for r in rows), Decimal(0))
    return raw, of_rounded


# ============================================================ 검증
def run_verifications(bitget_rows, okx_rows, computed_all, price_map, listed_map):
    """검증 항목 목록을 만든다.

    각 항목은 (이름, 산출값, 기준값, 통과여부, 비고, 종류).
    종류가 'gate' 인 항목이 하나라도 실패하면 즉시 중단한다.
    종류가 'info' 인 항목은 참고용이며 중단 사유가 아니다.
    """
    checks = []

    per = defaultdict(lambda: Decimal(0))
    for r in bitget_rows:
        per[("비트겟", r["coin"])] += r["qty"]
    for r in okx_rows:
        per[("OKX", r["coin"])] += r["qty"]

    for ex, coin, expected in EXPECTED_TOTALS:
        actual = per.get((ex, coin))
        if actual is None:
            checks.append((f"{ex} {coin} 수량 합계", "—", f"{expected:f}", False,
                           "데이터에 해당 코인 없음", "gate"))
            continue
        diff = abs(actual - expected)
        checks.append((
            f"{ex} {coin} 수량 합계",
            f"{actual:f}", f"{expected:f}", diff <= TOL,
            f"차이 {diff:f} (허용 1e-8)", "gate",
        ))

    # 미상장 코인이 총합에 0원으로만 기여했는지 확인
    unlisted = [c for c, ok in listed_map.items() if not ok]
    bad = [r for r in computed_all
           if r["coin"] in unlisted and r["krw_raw"] != 0]
    checks.append((
        "미상장 코인 원화 환산액 = 0원",
        f"위반 {len(bad)}건", "0건", not bad,
        f"대상: {', '.join(unlisted) if unlisted else '없음'}", "gate",
    ))

    # 종가 누락 행 점검 — 추정값으로 채우지 않고 실패로 처리한다.
    missing = [r for r in computed_all if r["status"] == "종가 없음"]
    checks.append((
        "상장 코인 종가 누락 없음",
        f"누락 {len(missing)}건", "0건", not missing,
        ", ".join(f"{r['date']} {r['coin']}" for r in missing) or "—", "gate",
    ))

    # 총합 산출 방식 대조 — 차이가 나는 것은 정상이며 각주로 표기한다(§3-3).
    raw, of_rounded = subtotal(computed_all)
    diff = round_krw(raw) - of_rounded
    checks.append((
        "총합 산출방식 대조 (반올림 전 합의 반올림 vs 반올림액 단순합)",
        fmt_krw(raw), f"{of_rounded:,}원", diff == 0,
        "일치" if diff == 0 else f"차이 {diff:+,}원 → 각주 표기 (전자 채택)", "info",
    ))

    return checks


# ============================================================ CSV
def write_csv(path, computed_all):
    import csv

    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["날짜(KST)", "거래소", "코인", "수량",
                    "업비트종가(KRW)", "원화액(반올림전)", "원화액(원단위반올림)", "비고"])
        for r in computed_all:
            w.writerow([
                r["date"], r["exchange"], r["coin"], f"{r['qty']:f}",
                f"{r['price']:f}" if r["price"] is not None else "",
                f"{r['krw_raw']:f}",
                f"{round_krw(r['krw_raw']):f}",
                r["status"],
            ])


# ============================================================ PDF
def build_pdf(path, computed_all, bitget_c, okx_c, fee_c, checks,
              price_meta, price_map, listed_map):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        LongTable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, TableStyle,
    )

    pdfmetrics.registerFont(TTFont("Nanum", FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("NanumBd", FONT_BOLD))
    pdfmetrics.registerFontFamily("Nanum", normal="Nanum", bold="NanumBd")

    ss = getSampleStyleSheet()

    def style(name, size, leading, font="Nanum", **kw):
        return ParagraphStyle(name, parent=ss["Normal"], fontName=font,
                              fontSize=size, leading=leading, **kw)

    S = {
        "title": style("t", 26, 36, "NanumBd", alignment=TA_CENTER),
        "subtitle": style("st", 13, 20, alignment=TA_CENTER,
                          textColor=colors.HexColor("#444444")),
        "h1": style("h1", 16, 24, "NanumBd", spaceBefore=6, spaceAfter=10,
                    textColor=colors.HexColor("#1a3a6b")),
        "h2": style("h2", 12, 18, "NanumBd", spaceBefore=8, spaceAfter=5),
        "body": style("b", 9.5, 15),
        "small": style("s", 8.2, 12.5, textColor=colors.HexColor("#555555")),
        "big": style("big", 22, 30, "NanumBd", alignment=TA_CENTER,
                     textColor=colors.HexColor("#0b5c2e")),
        "cell": style("c", 8.5, 11.5),
        "cellr": style("cr", 8.5, 11.5, alignment=2),
        "cellb": style("cb", 8.5, 11.5, "NanumBd"),
        "cellbr": style("cbr", 8.5, 11.5, "NanumBd", alignment=2),
        "hdr": style("hd", 8.8, 12, "NanumBd", alignment=TA_CENTER,
                     textColor=colors.white),
    }

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=17 * mm, rightMargin=17 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title="레퍼럴 수익 원화 환산 보고서", author="referral_krw_report",
    )

    NAVY = colors.HexColor("#1a3a6b")
    GREY = colors.HexColor("#f2f4f7")
    LINE = colors.HexColor("#c8cdd6")

    def table(data, widths, repeat=1, align_right_cols=()):
        t = LongTable(data, colWidths=widths, repeatRows=repeat)
        cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("GRID", (0, 0), (-1, -1), 0.4, LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GREY]),
        ]
        t.setStyle(TableStyle(cmds))
        return t

    def total_row_style(t, nrows):
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, nrows - 1), (-1, nrows - 1), colors.HexColor("#dde6f5")),
            ("LINEABOVE", (0, nrows - 1), (-1, nrows - 1), 1.0, NAVY),
        ]))
        return t

    def P(text, s="cell"):
        return Paragraph(text, S[s])

    story = []
    now = datetime.now(KST)

    # ---------------------------------------------------------- 1. 표지
    story += [
        Spacer(1, 55 * mm),
        Paragraph("레퍼럴 수익 원화 환산 보고서", S["title"]),
        Spacer(1, 6 * mm),
        Paragraph("업비트 일별 종가 기준", S["subtitle"]),
        Spacer(1, 14 * mm),
        Paragraph(f"대상 기간 : {PERIOD_START} ~ {PERIOD_END} (KST)", S["subtitle"]),
        Paragraph("대상 거래소 : 비트겟(Bitget) · OKX", S["subtitle"]),
        Spacer(1, 10 * mm),
        Paragraph(f"생성일시 : {now.strftime('%Y-%m-%d %H:%M:%S')} (KST)", S["subtitle"]),
        PageBreak(),
    ]

    # ---------------------------------------------------------- 2. 요약
    bg_raw, bg_rounded = subtotal(bitget_c)
    okx_raw, okx_rounded = subtotal(okx_c)
    all_raw, all_rounded = subtotal(computed_all)

    story.append(Paragraph("1. 요약", S["h1"]))

    def coin_totals(rows):
        per = defaultdict(lambda: Decimal(0))
        for r in rows:
            per[r["coin"]] += r["qty"]
        return per

    bg_per = coin_totals(bitget_c)
    okx_per = coin_totals(okx_c)

    data = [[P("거래소", "hdr"), P("코인", "hdr"), P("수량 합계", "hdr"),
             P("원화 환산액", "hdr")]]
    for coin in sorted(bg_per, key=lambda c: (c != "USDT", c)):
        krw = sum((r["krw_raw"] for r in bitget_c if r["coin"] == coin), Decimal(0))
        note = "" if listed_map.get(coin) else "  (미상장)"
        data.append([P("비트겟"), P(coin + note), P(fmt_qty(bg_per[coin]), "cellr"),
                     P(fmt_krw(krw), "cellr")])
    data.append([P("비트겟 소계", "cellb"), P("", "cellb"), P("", "cellbr"),
                 P(fmt_krw(bg_raw), "cellbr")])
    for coin in sorted(okx_per, key=lambda c: (c != "USDT", c)):
        krw = sum((r["krw_raw"] for r in okx_c if r["coin"] == coin), Decimal(0))
        data.append([P("OKX"), P(coin), P(fmt_qty(okx_per[coin]), "cellr"),
                     P(fmt_krw(krw), "cellr")])
    data.append([P("OKX 소계", "cellb"), P("", "cellb"), P("", "cellbr"),
                 P(fmt_krw(okx_raw), "cellbr")])

    t = table(data, [32 * mm, 34 * mm, 55 * mm, 55 * mm])
    story += [t, Spacer(1, 10 * mm)]

    story.append(Paragraph("총 원화 수익액", S["h2"]))
    story.append(Paragraph(fmt_krw(all_raw), S["big"]))
    story.append(Spacer(1, 5 * mm))

    if round_krw(all_raw) != all_rounded:
        story.append(Paragraph(
            f"※ 각주 — 반올림 전 값의 합을 최종 반올림한 값은 <b>{fmt_krw(all_raw)}</b>, "
            f"반올림된 일별 금액을 단순 합산한 값은 <b>{all_rounded:,}원</b>으로 "
            f"<b>{abs(round_krw(all_raw) - all_rounded):,}원</b>의 차이가 있습니다. "
            f"본 보고서의 총액은 규칙에 따라 전자를 사용했습니다.", S["small"]))
    else:
        story.append(Paragraph(
            "※ 반올림 전 값의 합을 최종 반올림한 값과, 반올림된 일별 금액의 단순 합이 "
            "일치합니다 (차이 0원).", S["small"]))
    story.append(PageBreak())

    # ---------------------------------------------------------- 3. 계산 기준
    story.append(Paragraph("2. 계산 기준", S["h1"]))
    story.append(Paragraph("2.1 계산식", S["h2"]))
    story.append(Paragraph(
        "일별 원화 수익액(t) = 코인 수량(t) × 업비트 KRW 마켓 당일 종가(t)<br/>"
        "총 원화 수익액 = Σ 일별 원화 수익액", S["body"]))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("2.2 종가 출처", S["h2"]))
    story.append(Paragraph(
        f"Upbit Open API (인증 불필요 public endpoint)<br/>"
        f"엔드포인트 : GET https://api.upbit.com/v1/candles/days<br/>"
        f"사용 필드 : candle_date_time_kst (KST 일자), trade_price (종가)<br/>"
        f"마켓 존재 확인 : GET https://api.upbit.com/v1/market/all<br/>"
        f"조회 시각 : {price_meta.get('fetched_at_kst', '—')}", S["body"]))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("2.3 KST 귀속 기준", S["h2"]))
    story.append(Paragraph(
        "비트겟 원본은 UTC 기준이므로 +9시간을 적용해 KST 일자로 귀속했습니다.<br/>"
        "OKX 원본은 UTC+8 기준이므로 +1시간을 적용해 KST 일자로 귀속했습니다.<br/>"
        "업비트 일봉은 KST 00:00에 마감되므로, 위 KST 일자와 업비트 일봉 날짜를 "
        "1:1로 매칭했습니다. 추가 시차 보정은 적용하지 않았습니다.", S["body"]))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("2.4 정밀도 및 반올림", S["h2"]))
    story.append(Paragraph(
        "모든 산술은 Python decimal.Decimal 로 수행했으며 float 곱셈·합산은 "
        "사용하지 않았습니다. 반올림은 최종 표시 단계에서만 적용하고 중간 계산은 "
        "원본 정밀도를 유지했습니다. 원화 금액은 ROUND_HALF_UP 으로 원 단위 "
        "반올림했고, 코인 수량은 소수점 8자리로 표시했습니다. 총합은 반올림된 "
        "일별 금액의 합이 아니라 반올림 전 값의 합을 마지막에 한 번 반올림한 "
        "값입니다.", S["body"]))
    story.append(PageBreak())

    # ---------------------------------------------------- 4·5. 일별 명세
    def detail_section(title, rows, num):
        story.append(Paragraph(f"{num}. {title}", S["h1"]))
        data = [[P("날짜(KST)", "hdr"), P("코인", "hdr"), P("수량", "hdr"),
                 P("업비트 종가", "hdr"), P("원화 환산액", "hdr"), P("비고", "hdr")]]
        for r in rows:
            price_txt = fmt_price(r["price"]) if r["price"] is not None else "—"
            note = "" if r["status"] == "정상" else r["status"]
            data.append([
                P(r["date"]), P(r["coin"]), P(fmt_qty(r["qty"]), "cellr"),
                P(price_txt, "cellr"), P(fmt_krw(r["krw_raw"]), "cellr"),
                P(note, "small"),
            ])
        raw, _ = subtotal(rows)
        data.append([P("합계", "cellb"), P("", "cellb"), P("", "cellbr"),
                     P("", "cellbr"), P(fmt_krw(raw), "cellbr"), P("", "cellb")])
        t = table(data, [24 * mm, 15 * mm, 31 * mm, 27 * mm, 33 * mm, 46 * mm])
        total_row_style(t, len(data))
        story.extend([t, Spacer(1, 4 * mm)])
        story.append(Paragraph(
            "※ 합계는 반올림 전 원화액을 모두 더한 뒤 마지막에 한 번 반올림한 "
            "값입니다.", S["small"]))
        story.append(PageBreak())

    detail_section("비트겟 일별 명세 (Rebate rewards)", bitget_c, 3)
    detail_section("OKX 일별 명세 (Affiliate commission)", okx_c, 4)

    # ---------------------------------------------------------- 6. 참고
    story.append(Paragraph("5. 참고 사항", S["h1"]))

    story.append(Paragraph("5.1 OKX 본인 거래 수수료 환급 (총합 제외)", S["h2"]))
    story.append(Paragraph(
        "아래 항목은 본인 거래 수수료 환급(Fee rebate)으로 레퍼럴 소득과 성격이 "
        "다르므로 위 총합에 포함하지 않았습니다. OKX 원본의 계정 간 이체·출금 "
        "건은 수익이 아니므로 집계 단계에서 이미 제외했습니다.", S["body"]))
    story.append(Spacer(1, 3 * mm))
    data = [[P("날짜(KST)", "hdr"), P("코인", "hdr"), P("수량", "hdr"),
             P("업비트 종가", "hdr"), P("원화 환산액", "hdr")]]
    for r in fee_c:
        price_txt = fmt_price(r["price"]) if r["price"] is not None else "—"
        data.append([P(r["date"]), P(r["coin"]), P(fmt_qty(r["qty"]), "cellr"),
                     P(price_txt, "cellr"), P(fmt_krw(r["krw_raw"]), "cellr")])
    fee_raw, _ = subtotal(fee_c)
    data.append([P("합계(참고)", "cellb"), P("", "cellb"), P("", "cellbr"),
                 P("", "cellbr"), P(fmt_krw(fee_raw), "cellbr")])
    t = table(data, [26 * mm, 20 * mm, 40 * mm, 35 * mm, 55 * mm])
    total_row_style(t, len(data))
    story += [t, Spacer(1, 8 * mm)]

    story.append(Paragraph("5.2 업비트 KRW 미상장 코인 처리", S["h2"]))
    unlisted = [c for c, ok in listed_map.items() if not ok]
    if unlisted:
        story.append(Paragraph(
            "아래 코인은 <b>GET /v1/market/all</b> 조회 결과 업비트 KRW 마켓에 "
            "상장되어 있지 않습니다. 규칙에 따라 다른 시세를 임의로 대입하지 "
            "않고 원화 환산액을 <b>0원</b>으로 처리했으며, 총 원화 수익액에 "
            "기여하지 않습니다. 해당 코인 수량 자체는 명세에 그대로 표시됩니다.",
            S["body"]))
        story.append(Spacer(1, 3 * mm))
        data = [[P("코인", "hdr"), P("확인한 마켓코드", "hdr"), P("수량 합계", "hdr"),
                 P("처리", "hdr")]]
        for c in unlisted:
            qty = sum((r["qty"] for r in computed_all if r["coin"] == c), Decimal(0))
            data.append([P(c), P(f"KRW-{c}"), P(fmt_qty(qty), "cellr"),
                         P("업비트 KRW 미상장 → 환산 제외")])
        story.append(table(data, [22 * mm, 34 * mm, 40 * mm, 80 * mm]))
    else:
        story.append(Paragraph("해당 없음 — 모든 코인이 업비트 KRW 마켓에 "
                               "상장되어 있습니다.", S["body"]))
    story.append(PageBreak())

    # ---------------------------------------------------------- 7. 부록
    story.append(Paragraph("6. 부록", S["h1"]))
    story.append(Paragraph("6.1 검증 결과", S["h2"]))
    data = [[P("검증 항목", "hdr"), P("산출값", "hdr"), P("기준값", "hdr"),
             P("결과", "hdr"), P("비고", "hdr")]]
    for name, actual, expected, ok, note, kind in checks:
        if kind == "gate":
            verdict = "<b>PASS</b>" if ok else "<b>FAIL</b>"
        else:
            verdict = "<b>참고</b>"
        data.append([P(name), P(actual, "cellr"), P(expected, "cellr"),
                     P(verdict), P(note, "small")])
    t = table(data, [44 * mm, 32 * mm, 30 * mm, 16 * mm, 54 * mm])
    for i, (_, _, _, ok, _, kind) in enumerate(checks, start=1):
        if kind == "gate":
            col = colors.HexColor("#0b7a3b") if ok else colors.HexColor("#b3261e")
        else:
            col = colors.HexColor("#555555")
        t.setStyle(TableStyle([("TEXTCOLOR", (3, i), (3, i), col)]))
    story += [t, Spacer(1, 3 * mm)]
    story.append(Paragraph(
        "※ '참고' 항목은 합격/불합격 판정 대상이 아니라 산출 방식 대조 결과입니다. "
        "'PASS/FAIL' 항목은 하나라도 실패하면 보고서 생성이 중단되도록 되어 "
        "있으므로, 본 보고서가 존재한다는 것은 전 항목 PASS 를 의미합니다.",
        S["small"]))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("6.2 사용한 업비트 종가 원본", S["h2"]))
    story.append(Paragraph(
        f"조회 시각 : {price_meta.get('fetched_at_kst', '—')} · "
        f"출처 : {price_meta.get('source', '—')}", S["small"]))
    story.append(Spacer(1, 3 * mm))

    coins_with_prices = [c for c in price_map if price_map[c]]
    all_dates = sorted({d for c in coins_with_prices for d in price_map[c]})
    hdr = [P("날짜(KST)", "hdr")] + [P(f"KRW-{c}", "hdr") for c in coins_with_prices]
    data = [hdr]
    for d in all_dates:
        row = [P(d)]
        for c in coins_with_prices:
            v = price_map[c].get(d)
            row.append(P(fmt_price(Decimal(v)) if v is not None else "—", "cellr"))
        data.append(row)
    widths = [30 * mm] + [(146 / max(len(coins_with_prices), 1)) * mm] * len(coins_with_prices)
    story.append(table(data, widths))

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("6.3 마켓 존재 확인 결과", S["h2"]))
    data = [[P("마켓코드", "hdr"), P("업비트 KRW 마켓 상장 여부", "hdr")]]
    for m, ok in price_meta.get("markets_checked", {}).items():
        data.append([P(m), P("상장" if ok else "미상장 → 환산 제외")])
    story.append(table(data, [40 * mm, 80 * mm]))

    def footer(canv, doc_):
        canv.saveState()
        canv.setFont("Nanum", 7.5)
        canv.setFillColor(colors.HexColor("#777777"))
        canv.drawString(17 * mm, 11 * mm,
                        f"레퍼럴 수익 원화 환산 보고서 · {PERIOD_START} ~ {PERIOD_END} (KST)")
        canv.drawRightString(A4[0] - 17 * mm, 11 * mm, f"{doc_.page}")
        canv.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


# ============================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prices", default="upbit_prices.json")
    ap.add_argument("--pdf", default="referral_krw_report.pdf")
    ap.add_argument("--csv", default="referral_krw_calc.csv")
    args = ap.parse_args()

    if not os.path.exists(args.prices):
        print(f"[오류] 종가 파일이 없습니다: {args.prices}\n"
              f"       먼저 fetch_upbit_prices.py 를 실행해 종가를 수집하세요.",
              file=sys.stderr)
        return 2

    with open(args.prices, encoding="utf-8") as fh:
        meta = json.load(fh)
    price_map = meta.get("prices", {})
    listed_map = {m.replace("KRW-", ""): ok
                  for m, ok in meta.get("markets_checked", {}).items()}

    bitget_rows = parse_rows(BITGET_RAW, "비트겟")
    okx_rows = parse_rows(OKX_RAW, "OKX")
    fee_rows = parse_rows(OKX_FEE_REBATE_RAW, "OKX(수수료환급)")

    bitget_c = compute(bitget_rows, price_map, listed_map)
    okx_c = compute(okx_rows, price_map, listed_map)
    fee_c = compute(fee_rows, price_map, listed_map)
    computed_all = bitget_c + okx_c   # 수수료 환급은 총합 제외

    checks = run_verifications(bitget_rows, okx_rows, computed_all,
                               price_map, listed_map)

    print("=" * 68)
    print("검증 결과")
    print("=" * 68)
    failed = 0
    for name, actual, expected, ok, note, kind in checks:
        tag = ("PASS" if ok else "FAIL") if kind == "gate" else "참고"
        print(f"  [{tag}] {name}")
        print(f"         산출={actual}  기준={expected}  {note}")
        if kind == "gate" and not ok:
            failed += 1
    if failed:
        print(f"\n[중단] 검증 {failed}건 실패. 보고서를 생성하지 않습니다.", file=sys.stderr)
        return 1

    write_csv(args.csv, computed_all + fee_c)
    build_pdf(args.pdf, computed_all, bitget_c, okx_c, fee_c, checks,
              meta, price_map, listed_map)

    bg_raw, _ = subtotal(bitget_c)
    okx_raw, _ = subtotal(okx_c)
    all_raw, all_rounded = subtotal(computed_all)

    print("\n" + "=" * 68)
    print("원화 환산 요약")
    print("=" * 68)
    print(f"  비트겟 소계 : {fmt_krw(bg_raw)}")
    print(f"  OKX    소계 : {fmt_krw(okx_raw)}")
    print(f"  총 원화 수익액 : {fmt_krw(all_raw)}")
    if round_krw(all_raw) != all_rounded:
        print(f"  ※ 반올림액 단순합 {all_rounded:,}원 과 "
              f"{abs(round_krw(all_raw) - all_rounded):,}원 차이 (각주 표기)")
    print(f"\n  생성: {args.pdf} / {args.csv}")
    print(f"  검증: {len(checks)}건 전부 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
