#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
레퍼럴 수익 원화 환산 보고서 생성기
=====================================

비트겟 / OKX 레퍼럴(제휴) 수수료 수익을 **수익 발생 당일의 국내 거래소 KRW-USDT 종가**로
환산해 합산하고, 검증 결과와 함께 PDF / CSV 보고서를 생성한다.

대상 기간 : 2026-07-05 ~ 2026-08-05 (KST)

핵심 원칙
---------
* 모든 금액 계산은 ``decimal.Decimal``. float 곱셈/합산 금지.
* 반올림은 최종 표시 단계에서만. 총합은 반올림 전 값의 합을 마지막에 한 번 반올림.
* 종가를 못 구하면 **추정·보간하지 않고 중단**한다. 값을 지어내지 않는다.
* 업비트/빗썸을 날짜별로 섞어 쓰지 않는다. 한 소스로 전 구간을 채운다.

사용법
------
    python3 referral_krw_report.py [--closes-file CLOSES.csv] [--outdir DIR]

``--closes-file`` 은 API 접근이 막힌 환경에서 종가를 수동 공급하기 위한 탈출구다.
형식은 ``YYYY-MM-DD,종가`` 헤더 없는 CSV 이며, ``--closes-source`` 로 출처를
반드시 함께 명시해야 한다(출처 불명 데이터로 보고서를 만들지 않기 위함).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple

KST = timezone(timedelta(hours=9))

PERIOD_START = date(2026, 7, 5)
PERIOD_END = date(2026, 8, 5)

QTY_TOL = Decimal("1e-8")          # 13-1 수량 검증 허용 오차
QTY_DP = Decimal("1e-10")          # 코인 수량 표시 소수점 10자리
KRW_DP = Decimal("1")              # 원화 표시 원 단위

# ---------------------------------------------------------------------------
# 원본 데이터 (KST 일자 귀속 완료 — 추가 시차 보정 금지)
#   비트겟 원본은 UTC   기준 → +9시간
#   OKX    원본은 UTC+8 기준 → +1시간
# ---------------------------------------------------------------------------

BITGET_REBATE_REWARDS_USDT = """
2026-07-06|0.0551908637
2026-07-07|0.7231824524
2026-07-08|1.4488093051
2026-07-09|0.6539182230
2026-07-10|0.4076246315
2026-07-11|0.9766804713
2026-07-12|1.0809243640
2026-07-13|0.3491221966
2026-07-14|0.4339682141
2026-07-15|0.8871752295
2026-07-16|0.5802801875
2026-07-17|1.1281477486
2026-07-18|2.2227186663
2026-07-19|2.7455600522
2026-07-20|2.6313544986
2026-07-21|0.0483068900
2026-07-22|0.0010894417
2026-07-23|0.4684899557
2026-07-24|0.9420119752
2026-07-25|2.0524652866
2026-07-26|2.8884151820
2026-07-27|0.4393013590
2026-07-28|0.0973067602
2026-07-29|1.3495364738
2026-07-30|0.5710259657
2026-07-31|2.4763269527
2026-08-01|2.5633607792
2026-08-02|1.7249635971
2026-08-03|0.1584417840
2026-08-04|0.4163171676
2026-08-05|1.1493873561
"""

# 업비트/빗썸 KRW 마켓 미상장 → 수량만 표기, 원화 0원, 환산 제외
BITGET_UNLISTED = """
2026-07-24|U|0.0009804960
2026-07-26|LUNA|0.0160108650
2026-07-28|AB|0.4988895750
2026-07-29|LUNC|60.6742920000
"""

# 본인 거래 수수료 환급 — 본 합계 제외, 별도 섹션
BITGET_REBATE_USDT = """
2026-07-11|0.0061650000
2026-07-24|0.0141480000
2026-07-25|0.0200070000
2026-07-26|0.0037080000
2026-07-28|0.0121680000
2026-07-29|0.0089280000
2026-08-01|0.0060390000
2026-08-04|0.0044640000
"""

OKX_AFFILIATE_USDT = """
2026-07-05|6.3732790500
2026-07-06|0.3566732300
2026-07-07|1.7280407500
2026-07-08|0.3304426500
2026-07-09|0.1399312300
2026-07-10|0.3972743100
2026-07-11|0.3610608500
2026-07-12|0.3703768400
2026-07-13|0.3726558900
2026-07-14|0.3216085200
2026-07-15|0.5875989600
2026-07-16|0.2159403100
2026-07-17|0.1504223800
2026-07-18|0.0689806300
2026-07-19|0.4954701500
2026-07-20|4.4271922600
2026-07-21|0.8930611300
2026-07-22|17.7638694900
2026-07-23|2.6773749100
2026-07-24|0.1412246500
2026-07-25|0.0509548800
2026-07-26|0.0345597100
2026-07-27|0.2401610500
2026-07-28|0.1752103100
2026-07-29|0.1260904800
2026-07-30|0.1279225500
2026-07-31|0.9591428400
2026-08-01|0.6127384600
2026-08-02|0.4939289300
2026-08-03|0.2968817700
2026-08-04|0.7567961300
2026-08-05|0.1755008000
"""

# 본인 거래 수수료 환급 — 본 합계 제외, 별도 섹션
#
# [채택값 주의] 지시 문서 §12 는 이 값을 0.0972540000 으로 적었으나, OKX 원본 export 의
# 2026-07-06 두 행(0.04827443 + 0.0489801)을 합하면 0.09725453 이다. 차이 5.3e-7 은
# 허용 오차 1e-8 을 넘는다. 거래소 원본 export 가 증빙의 근거이므로 **원본값을 채택**한다.
# (사용자 확인 완료. 이 항목은 본 합계에서 제외되는 참고 항목이라 총 레퍼럴 수익액에는
#  영향이 없다.) 문서값과의 차이는 경고 섹션과 검증 부록에 그대로 남긴다.
OKX_FEE_REBATE_USDT = """
2026-07-06|0.0972545300
"""

# 지시 문서 §12/§13-1 에 적혀 있던 값 — 원본과 불일치하여 채택하지 않았음을 기록해 둔다.
DOC_SPEC_OKX_FEE_REBATE = Decimal("0.0972540000")

# 13-1 수량 검증 기대값 (OKX Fee rebate 는 위 사유로 원본 기준값 사용)
EXPECTED_TOTALS = {
    "비트겟 Rebate rewards USDT 합계": Decimal("33.6714040311"),
    "비트겟 Rebate USDT 합계": Decimal("0.0756270000"),
    "비트겟 LUNC": Decimal("60.6742920000"),
    "비트겟 LUNA": Decimal("0.0160108650"),
    "비트겟 AB": Decimal("0.4988895750"),
    "비트겟 U": Decimal("0.0009804960"),
    "OKX Affiliate commission USDT 합계": Decimal("42.2223661000"),
    "OKX Fee rebate USDT 합계": Decimal("0.0972545300"),
}

EXPECTED_ROWCOUNTS = {"bitget": 47, "okx": 470}

# 4. 종가 타당성 검증 — 같은 기간 원달러 환율 실측 참고치
FX_REFERENCE = {
    date(2026, 7, 5): Decimal("1550"),    # 07-초 1,550원대
    date(2026, 7, 21): Decimal("1473.4"),
    date(2026, 7, 29): Decimal("1446.7"),
}
FX_TOLERANCE = Decimal("0.03")            # ±3%
CLOSE_RANGE = (Decimal("1300"), Decimal("1650"))
AVG_PRICE_RANGE = (Decimal("1400"), Decimal("1560"))   # 13-3 역산 평균단가


# ---------------------------------------------------------------------------
# 유틸
# ---------------------------------------------------------------------------

def parse_block(block: str, with_coin: bool = False) -> List[tuple]:
    """``날짜|수량`` 또는 ``날짜|코인|수량`` 블록을 파싱한다."""
    out = []
    for line in block.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if with_coin:
            d, coin, qty = parts
            out.append((date.fromisoformat(d), coin, Decimal(qty)))
        else:
            d, qty = parts
            out.append((date.fromisoformat(d), Decimal(qty)))
    return out


def q_krw(v: Decimal) -> Decimal:
    return v.quantize(KRW_DP, rounding=ROUND_HALF_UP)


def q_qty(v: Decimal) -> Decimal:
    return v.quantize(QTY_DP, rounding=ROUND_HALF_UP)


def fmt_krw(v: Optional[Decimal]) -> str:
    if v is None:
        return "종가 없음"
    return f"{q_krw(v):,}"


def fmt_qty(v: Decimal) -> str:
    return f"{q_qty(v):,.10f}"


def daterange(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


class Console:
    """콘솔 출력을 그대로 모아두었다가 PDF 부록에 재사용한다."""

    def __init__(self):
        self.lines: List[str] = []

    def __call__(self, msg: str = ""):
        print(msg)
        self.lines.append(msg)

    def rule(self, title: str = ""):
        self("")
        self("=" * 78)
        if title:
            self(title)
            self("=" * 78)


LOG = Console()


class Checks:
    """항목별 PASS/FAIL 기록."""

    def __init__(self):
        self.items: List[Tuple[str, bool, str]] = []

    def add(self, name: str, ok: bool, detail: str = ""):
        self.items.append((name, ok, detail))
        LOG(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
        return ok

    @property
    def passed(self) -> int:
        return sum(1 for _, ok, _ in self.items if ok)

    @property
    def failed(self) -> int:
        return sum(1 for _, ok, _ in self.items if not ok)


CHECKS = Checks()

# 보고서 상단 경고 섹션에 실릴 문구들
WARNINGS: List[str] = []


# ---------------------------------------------------------------------------
# 3. 종가 조회 — 업비트(1순위) → 빗썸(2순위)
# ---------------------------------------------------------------------------

class PriceSourceError(RuntimeError):
    pass


def _requests():
    try:
        import requests  # noqa
        return requests
    except ImportError:  # pragma: no cover
        raise PriceSourceError("requests 모듈이 없습니다. pip install requests")


def fetch_upbit() -> Tuple[Dict[date, Decimal], str]:
    """업비트 Open API. candle_date_time_kst 의 날짜부 + trade_price(종가)."""
    rq = _requests()
    url = ("https://api.upbit.com/v1/candles/days"
           "?market=KRW-USDT&count=60&to=2026-08-06T00:00:00Z")
    r = rq.get(url, timeout=30, headers={"Accept": "application/json"})
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or not data:
        raise PriceSourceError(f"업비트 응답이 비정상입니다: {str(data)[:300]}")
    closes = {}
    for c in data:
        d = date.fromisoformat(c["candle_date_time_kst"][:10])
        closes[d] = Decimal(str(c["trade_price"]))
    return closes, json.dumps(data[:3], ensure_ascii=False)[:1500]


def fetch_bithumb_v1() -> Tuple[Dict[date, Decimal], str]:
    """빗썸 Public API v1 (업비트 호환 스키마)."""
    rq = _requests()
    url = "https://api.bithumb.com/v1/candles/days?market=KRW-USDT&count=60"
    r = rq.get(url, timeout=30, headers={"Accept": "application/json"})
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or not data:
        raise PriceSourceError(f"빗썸 v1 응답이 비정상입니다: {str(data)[:300]}")
    closes = {}
    for c in data:
        d = date.fromisoformat(c["candle_date_time_kst"][:10])
        closes[d] = Decimal(str(c["trade_price"]))
    return closes, json.dumps(data[:3], ensure_ascii=False)[:1500]


def fetch_bithumb_legacy() -> Tuple[Dict[date, Decimal], str]:
    """빗썸 구버전. [timestamp(ms), 시가, 종가, 고가, 저가, 거래량] — 종가는 index 2."""
    rq = _requests()
    url = "https://api.bithumb.com/public/candlestick/USDT_KRW/24h"
    r = rq.get(url, timeout=30, headers={"Accept": "application/json"})
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") != "0000":
        raise PriceSourceError(f"빗썸 구버전 status={payload.get('status')}")
    closes = {}
    for row in payload["data"]:
        ts_ms = int(row[0])
        close = Decimal(str(row[2]))          # index 2 = 종가
        d = datetime.fromtimestamp(ts_ms / 1000, tz=KST).date()
        closes[d] = close
    return closes, json.dumps(payload["data"][:3], ensure_ascii=False)[:1500]


PRICE_SOURCES = [
    ("업비트 Open API (api.upbit.com/v1/candles/days)", fetch_upbit),
    ("빗썸 Public API v1 (api.bithumb.com/v1/candles/days)", fetch_bithumb_v1),
    ("빗썸 Public API 구버전 (api.bithumb.com/public/candlestick)", fetch_bithumb_legacy),
]


def load_closes_from_file(path: str, source_label: str):
    closes = {}
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            row = [c.strip() for c in row if c.strip()]
            if not row or row[0].lower().startswith(("date", "날짜")):
                continue
            closes[date.fromisoformat(row[0])] = Decimal(row[1].replace(",", ""))
    if not closes:
        raise PriceSourceError(f"{path} 에서 종가를 하나도 읽지 못했습니다.")
    return closes, source_label, f"수동 공급 파일: {os.path.abspath(path)}"


def get_closes(args) -> Tuple[Dict[date, Decimal], str, str, str]:
    """(closes, 소스명, 조회시각(KST), raw 발췌) 를 돌려준다."""
    if args.closes_file:
        if not args.closes_source:
            raise PriceSourceError(
                "--closes-file 을 쓸 때는 --closes-source 로 출처를 반드시 명시해야 합니다.")
        closes, label, raw = load_closes_from_file(args.closes_file, args.closes_source)
        return closes, label, datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST"), raw

    errors = []
    for name, fn in PRICE_SOURCES:
        LOG(f"  종가 소스 시도: {name}")
        try:
            closes, raw = fn()
            LOG(f"  → 성공. {len(closes)}일치 수신.")
            return closes, name, datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST"), raw
        except Exception as e:                    # noqa: BLE001
            msg = f"{type(e).__name__}: {e}"
            LOG(f"  → 실패. {msg}")
            errors.append(f"    - {name}\n        {msg}")
        time.sleep(0.3)                            # 초당 10회 제한 대비

    raise PriceSourceError(
        "업비트·빗썸 어느 소스에서도 KRW-USDT 일봉 종가를 받지 못했습니다.\n"
        + "\n".join(errors)
        + "\n\n  종가를 추정하거나 보간하지 않고 여기서 중단합니다."
    )


# ---------------------------------------------------------------------------
# 원본 파일 교차 검증 (선택) — 업로드 원본이 있으면 문서 표와 대조한다
# ---------------------------------------------------------------------------

def crosscheck_raw(bitget_xls: Optional[str], okx_csv: Optional[str], spec: dict):
    LOG.rule("원본 파일 교차 검증 (문서 표 ↔ 거래소 원본 export)")
    if not bitget_xls and not okx_csv:
        LOG("  원본 파일 경로가 지정되지 않아 건너뜁니다.")
        return

    if bitget_xls and os.path.exists(bitget_xls):
        try:
            import xlrd
            sh = xlrd.open_workbook(bitget_xls).sheet_by_index(0)
            n = sh.nrows - 1
            CHECKS.add("비트겟 원본 행 수 47행",
                       n == EXPECTED_ROWCOUNTS["bitget"], f"실제 {n}행")
            agg = defaultdict(Decimal)
            for r in range(1, sh.nrows):
                _, dt, coin, typ, amt, _fee, _av = [str(x).strip() for x in sh.row_values(r)]
                kst = (datetime.strptime(dt, "%Y-%m-%d %H:%M:%S") + timedelta(hours=9)).date()
                agg[(typ, coin, kst)] += Decimal(amt)
            _compare_raw("비트겟", agg, spec)
        except Exception as e:                     # noqa: BLE001
            CHECKS.add("비트겟 원본 파싱", False, f"{type(e).__name__}: {e}")

    if okx_csv and os.path.exists(okx_csv):
        try:
            lines = open(okx_csv, encoding="utf-8-sig").read().splitlines()
            rows = list(csv.DictReader(lines[1:]))
            rows = [{k.strip("\ufeff").strip(): (v.strip("\ufeff").strip() if v else v)
                     for k, v in r.items()} for r in rows]
            CHECKS.add("OKX 원본 행 수 470행",
                       len(rows) == EXPECTED_ROWCOUNTS["okx"], f"실제 {len(rows)}행")
            cnt = defaultdict(int)
            agg = defaultdict(Decimal)
            for r in rows:
                cnt[r["Type"]] += 1
                kst = (datetime.strptime(r["Time"], "%Y-%m-%d %H:%M:%S")
                       + timedelta(hours=1)).date()
                agg[(r["Type"], r["Symbol"], kst)] += Decimal(r["Amount"])
            CHECKS.add("OKX 유형별 행 수 (Affiliate 465 / Fee rebate 2 / 이체 2 / 출금 1)",
                       cnt["Affiliate commission"] == 465 and cnt["Fee rebate"] == 2
                       and cnt["From unified trading account"] == 2
                       and cnt["Withdrawal"] == 1,
                       ", ".join(f"{k}={v}" for k, v in sorted(cnt.items())))
            _compare_raw("OKX", agg, spec)
        except Exception as e:                     # noqa: BLE001
            CHECKS.add("OKX 원본 파싱", False, f"{type(e).__name__}: {e}")


def _compare_raw(exch: str, agg: Dict[tuple, Decimal], spec: dict):
    """원본에서 집계한 (유형, 코인, KST일자) 합계를 문서 표와 대조한다."""
    mapping = {
        "비트겟": [("Rebate rewards", "USDT", spec["bitget_rewards"]),
                   ("Rebate", "USDT", spec["bitget_rebate"])],
        "OKX": [("Affiliate commission", "USDT", spec["okx_affiliate"]),
                ("Fee rebate", "USDT", spec["okx_fee_rebate"])],
    }[exch]

    for typ, coin, table in mapping:
        raw_total = sum((v for (t, c, _), v in agg.items() if t == typ and c == coin),
                        Decimal(0))
        doc_total = sum((q for _, q in table), Decimal(0))
        ok = abs(raw_total - doc_total) <= QTY_TOL
        CHECKS.add(
            f"{exch} {typ}/{coin} 원본 합계 == 문서 표 합계",
            ok,
            f"원본 {raw_total} / 문서 {doc_total} / 차이 {raw_total - doc_total}",
        )
        raw_daily = {d: v for (t, c, d), v in agg.items() if t == typ and c == coin}
        doc_daily = dict(table)
        bad = [d for d in sorted(set(raw_daily) | set(doc_daily))
               if abs(raw_daily.get(d, Decimal(0)) - doc_daily.get(d, Decimal(0))) > QTY_TOL]
        CHECKS.add(
            f"{exch} {typ}/{coin} 일자별 수량 == 문서 표",
            not bad,
            "전부 일치" if not bad else "불일치 일자: " + ", ".join(
                f"{d} (원본 {raw_daily.get(d, 0)} / 문서 {doc_daily.get(d, 0)})" for d in bad),
        )

    if exch == "비트겟":
        for coin in ("LUNC", "LUNA", "AB", "U"):
            raw_total = sum((v for (t, c, _), v in agg.items()
                             if t == "Rebate rewards" and c == coin), Decimal(0))
            doc_total = sum((q for _, cc, q in spec["bitget_unlisted"] if cc == coin),
                            Decimal(0))
            CHECKS.add(f"비트겟 미상장 {coin} 원본 == 문서 표",
                       abs(raw_total - doc_total) <= QTY_TOL,
                       f"원본 {raw_total} / 문서 {doc_total}")


# ---------------------------------------------------------------------------
# 4. 종가 타당성 검증
# ---------------------------------------------------------------------------

def validate_closes(closes: Dict[date, Decimal], source: str, raw_excerpt: str) -> List[str]:
    warnings = WARNINGS

    LOG.rule("4. 종가 타당성 검증")
    LOG(f"  소스: {source}")

    # 4-1. 전 구간 종가 테이블 (날짜순 전부 출력)
    LOG("")
    LOG("  [4-1] KRW-USDT 일봉 종가 전 구간")
    LOG(f"  {'날짜':<12} {'종가(원)':>12}")
    LOG("  " + "-" * 26)
    for d in daterange(PERIOD_START, PERIOD_END):
        c = closes.get(d)
        LOG(f"  {d.isoformat():<12} {(f'{c:,}' if c is not None else '종가 없음'):>12}")

    # 4-2. 원달러 실측 참고치 대조 (±3%)
    LOG("")
    LOG("  [4-2] 원달러 환율 실측 참고치 대조 (±3%)")
    for d, fx in FX_REFERENCE.items():
        c = closes.get(d)
        if c is None:
            CHECKS.add(f"종가 타당성 {d} (참고 {fx}원)", False, "해당 일자 종가 없음")
            warnings.append(f"{d} 종가 없음 — 원달러 참고치 대조 불가")
            continue
        dev = (c - fx) / fx
        ok = abs(dev) <= FX_TOLERANCE
        CHECKS.add(f"종가 타당성 {d} (참고 {fx}원, ±3%)", ok,
                   f"종가 {c:,}원 / 괴리 {dev * 100:.2f}%")
        if not ok:
            warnings.append(
                f"{d} 종가 {c:,}원이 원달러 참고치 {fx}원 대비 {dev * 100:.2f}% 괴리 (±3% 초과)")
            LOG("      ↳ API 원문 발췌:")
            LOG("      " + raw_excerpt[:800])

    # 4-3. 최소/최대/평균
    LOG("")
    LOG("  [4-3] 전 구간 종가 최소/최대/평균")
    vals = [closes[d] for d in daterange(PERIOD_START, PERIOD_END) if d in closes]
    if vals:
        lo, hi = min(vals), max(vals)
        avg = sum(vals, Decimal(0)) / Decimal(len(vals))
        LOG(f"      최소 {lo:,}원 / 최대 {hi:,}원 / 평균 {avg.quantize(Decimal('0.01')):,}원")
        ok = CLOSE_RANGE[0] <= lo and hi <= CLOSE_RANGE[1]
        CHECKS.add(f"전 구간 종가가 {CLOSE_RANGE[0]:,}~{CLOSE_RANGE[1]:,}원 범위 내", ok,
                   f"최소 {lo:,} / 최대 {hi:,} / 평균 {avg.quantize(Decimal('0.01')):,}")
        if not ok:
            warnings.append(
                f"종가 범위 이탈: 최소 {lo:,}원, 최대 {hi:,}원 "
                f"(기대 {CLOSE_RANGE[0]:,}~{CLOSE_RANGE[1]:,}원)")
    else:
        CHECKS.add("전 구간 종가 범위", False, "종가가 하나도 없음")

    # 4-4. 연속 날짜 누락 확인
    LOG("")
    LOG("  [4-4] 2026-07-05 ~ 2026-08-05 연속 날짜 확인")
    missing = [d for d in daterange(PERIOD_START, PERIOD_END) if d not in closes]
    CHECKS.add("대상 기간 전 일자 종가 존재", not missing,
               "누락 없음" if not missing else "누락: " + ", ".join(d.isoformat() for d in missing))
    if missing:
        warnings.append("종가 없음 일자: " + ", ".join(d.isoformat() for d in missing))

    return warnings


# ---------------------------------------------------------------------------
# 계산
# ---------------------------------------------------------------------------

class Row:
    __slots__ = ("d", "exchange", "kind", "coin", "qty", "close", "krw_raw", "converted")

    def __init__(self, d, exchange, kind, coin, qty, close, converted=True):
        self.d = d
        self.exchange = exchange
        self.kind = kind
        self.coin = coin
        self.qty = qty
        self.close = close
        self.converted = converted
        # 중간 계산은 반올림하지 않는다 (원본 정밀도 유지)
        self.krw_raw = (qty * close) if (converted and close is not None) else Decimal(0)

    @property
    def krw_display(self) -> Optional[Decimal]:
        if not self.converted:
            return Decimal(0)
        if self.close is None:
            return None
        return q_krw(self.krw_raw)


def build_rows(spec: dict, closes: Dict[date, Decimal]) -> Dict[str, List[Row]]:
    def mk(table, exchange, kind, coin="USDT", converted=True):
        return [Row(d, exchange, kind, coin, qty, closes.get(d), converted)
                for d, qty in table]

    return {
        "bitget_rewards": mk(spec["bitget_rewards"], "비트겟", "레퍼럴 수익 (Rebate rewards)"),
        "okx_affiliate": mk(spec["okx_affiliate"], "OKX", "레퍼럴 수익 (Affiliate commission)"),
        "bitget_rebate": mk(spec["bitget_rebate"], "비트겟", "본인 수수료 환급 (Rebate)"),
        "okx_fee_rebate": mk(spec["okx_fee_rebate"], "OKX", "본인 수수료 환급 (Fee rebate)"),
        "unlisted": [Row(d, "비트겟", "레퍼럴 수익 (미상장)", coin, qty, None, converted=False)
                     for d, coin, qty in spec["bitget_unlisted"]],
    }


def total_raw(rows: List[Row]) -> Decimal:
    """반올림 전 값의 총합 (마지막에 한 번만 반올림하기 위함)."""
    return sum((r.krw_raw for r in rows), Decimal(0))


def total_of_rounded(rows: List[Row]) -> Decimal:
    """비교용: 반올림된 일별 금액의 합."""
    return sum((q_krw(r.krw_raw) for r in rows), Decimal(0))


# ---------------------------------------------------------------------------
# 13. 검증
# ---------------------------------------------------------------------------

def validate_quantities(spec: dict):
    LOG.rule("13-1. 수량 검증 (허용 오차 1e-8)")
    actual = {
        "비트겟 Rebate rewards USDT 합계": sum((q for _, q in spec["bitget_rewards"]), Decimal(0)),
        "비트겟 Rebate USDT 합계": sum((q for _, q in spec["bitget_rebate"]), Decimal(0)),
        "비트겟 LUNC": sum((q for _, c, q in spec["bitget_unlisted"] if c == "LUNC"), Decimal(0)),
        "비트겟 LUNA": sum((q for _, c, q in spec["bitget_unlisted"] if c == "LUNA"), Decimal(0)),
        "비트겟 AB": sum((q for _, c, q in spec["bitget_unlisted"] if c == "AB"), Decimal(0)),
        "비트겟 U": sum((q for _, c, q in spec["bitget_unlisted"] if c == "U"), Decimal(0)),
        "OKX Affiliate commission USDT 합계": sum((q for _, q in spec["okx_affiliate"]), Decimal(0)),
        "OKX Fee rebate USDT 합계": sum((q for _, q in spec["okx_fee_rebate"]), Decimal(0)),
    }
    for name, exp in EXPECTED_TOTALS.items():
        got = actual[name]
        CHECKS.add(f"수량 {name}", abs(got - exp) <= QTY_TOL,
                   f"기대 {exp} / 실제 {got} / 차이 {got - exp}")

    # 지시 문서 §12 기대값과 원본값이 어긋난 항목을 명시적으로 남긴다 (조용히 넘기지 않음).
    fee = actual["OKX Fee rebate USDT 합계"]
    gap = fee - DOC_SPEC_OKX_FEE_REBATE
    if gap != 0:
        CHECKS.add(
            "OKX Fee rebate: 문서 기대값 대신 원본 export 값 채택 (사유 명시)",
            True,
            f"문서 §12 {DOC_SPEC_OKX_FEE_REBATE} / 원본 {fee} / 차이 {gap} — "
            f"원본 2026-07-06 두 행(0.04827443 + 0.0489801)이 근거. "
            f"참고 항목이므로 총 레퍼럴 수익액에는 영향 없음",
        )
        WARNINGS.append(
            f"OKX <b>Fee rebate</b> 수량은 지시 문서에 적힌 {DOC_SPEC_OKX_FEE_REBATE} 가 아니라 "
            f"거래소 원본 export 기준 <b>{fee}</b> 를 채택했습니다 "
            f"(원본 2026-07-06 두 행 0.04827443 + 0.0489801, 차이 {gap}). "
            f"본 항목은 참고 섹션 전용이므로 <b>총 레퍼럴 수익액에는 영향이 없습니다.</b>"
        )
    return actual


def validate_rows(all_rows: Dict[str, List[Row]]):
    """13-2 행 단위 재계산 / 13-4 종가 없음 검사."""
    LOG.rule("13-2. 행 단위 재계산 (수량 x 종가 == 원화액)")
    bad = []
    checked = 0
    for rows in all_rows.values():
        for r in rows:
            if not r.converted or r.close is None:
                continue
            checked += 1
            if Decimal(str(r.qty)) * Decimal(str(r.close)) != r.krw_raw:
                bad.append(f"{r.exchange} {r.d} {r.coin}")
    CHECKS.add("모든 환산 행 수량 x 종가 == 원화액 (독립 재계산)", not bad,
               f"{checked}행 검증, 불일치 {len(bad)}건" + (": " + ", ".join(bad) if bad else ""))

    LOG.rule("13-4. 종가 없음 검사 (종가 0/None 인데 원화액 != 0 이면 에러)")
    viol = []
    for rows in all_rows.values():
        for r in rows:
            if (r.close is None or r.close == 0) and r.krw_raw != 0:
                viol.append(f"{r.exchange} {r.d} {r.coin} 원화 {r.krw_raw}")
    CHECKS.add("종가 없음 행의 원화액이 모두 0", not viol,
               "위반 없음" if not viol else "; ".join(viol))
    if viol:
        raise SystemExit("[치명] 종가 없이 원화액이 계산된 행이 있습니다. 중단합니다.\n"
                         + "\n".join(viol))


def validate_avg_price(bitget_krw: Decimal, okx_krw: Decimal, actual_qty: dict):
    LOG.rule("13-3. 역산 평균단가 검사")
    res = {}
    for label, krw, qty in (
        ("비트겟", bitget_krw, actual_qty["비트겟 Rebate rewards USDT 합계"]),
        ("OKX", okx_krw, actual_qty["OKX Affiliate commission USDT 합계"]),
    ):
        avg = (krw / qty) if qty else Decimal(0)
        res[label] = avg
        ok = AVG_PRICE_RANGE[0] <= avg <= AVG_PRICE_RANGE[1]
        CHECKS.add(f"{label} 역산 평균단가 {AVG_PRICE_RANGE[0]:,}~{AVG_PRICE_RANGE[1]:,}원", ok,
                   f"{avg.quantize(Decimal('0.01')):,}원 (원화소계 {q_krw(krw):,} ÷ {qty})")
        if not ok:
            LOG("      ↳ 범위 이탈. 종가 매칭이 하루씩 밀렸을 가능성을 먼저 의심하십시오.")
    return res


# ---------------------------------------------------------------------------
# 산출물
# ---------------------------------------------------------------------------

def write_csv(path: str, all_rows: Dict[str, List[Row]]):
    order = ["bitget_rewards", "okx_affiliate", "bitget_rebate", "okx_fee_rebate", "unlisted"]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["날짜", "거래소", "구분", "코인", "수량", "종가", "원화액"])
        for key in order:
            for r in sorted(all_rows[key], key=lambda x: (x.d, x.coin)):
                w.writerow([
                    r.d.isoformat(), r.exchange, r.kind, r.coin,
                    fmt_qty(r.qty),
                    ("" if r.close is None else f"{r.close}"),
                    ("" if r.krw_display is None else f"{r.krw_display}"),
                ])
    LOG(f"  CSV 생성: {path}")


def register_korean_font() -> Tuple[str, str]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    home = os.path.expanduser("~")
    candidates = [
        # Linux (Debian/Ubuntu: apt-get install -y fonts-nanum)
        ("NanumGothic", "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
         "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
        ("NanumBarunGothic", "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
         "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf"),
        # Windows
        ("MalgunGothic", "C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/malgunbd.ttf"),
        ("NanumGothic", "C:/Windows/Fonts/NanumGothic.ttf",
         "C:/Windows/Fonts/NanumGothicBold.ttf"),
        # macOS
        ("AppleSDGothicNeo", "/System/Library/Fonts/AppleSDGothicNeo.ttc", None),
        ("AppleGothic", "/System/Library/Fonts/Supplemental/AppleGothic.ttf", None),
        ("NanumGothic", f"{home}/Library/Fonts/NanumGothic.ttf",
         f"{home}/Library/Fonts/NanumGothicBold.ttf"),
        # 스크립트와 같은 디렉터리에 폰트를 직접 놓은 경우
        ("NanumGothic", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "NanumGothic.ttf"), None),
    ]
    for name, reg, bold in candidates:
        if os.path.exists(reg):
            pdfmetrics.registerFont(TTFont(name, reg))
            bold_name = name
            if bold and os.path.exists(bold):
                bold_name = name + "-Bold"
                pdfmetrics.registerFont(TTFont(bold_name, bold))
            from reportlab.lib.fonts import addMapping
            addMapping(name, 0, 0, name)
            addMapping(name, 1, 0, bold_name)
            LOG(f"  한글 폰트 등록: {name} ({reg})")
            return name, bold_name
    raise SystemExit(
        "[치명] 한글 폰트를 찾지 못했습니다. 한글이 깨진 PDF 를 만들지 않기 위해 중단합니다.\n"
        "  Debian/Ubuntu : sudo apt-get install -y fonts-nanum\n"
        "  macOS         : brew install --cask font-nanum-gothic\n"
        "  Windows       : 맑은 고딕이 기본 설치되어 있습니다 (C:/Windows/Fonts/malgun.ttf)\n"
        "  또는 NanumGothic.ttf 를 이 스크립트와 같은 디렉터리에 두고 다시 실행하십시오.")


def build_pdf(path, all_rows, spec, closes, source, fetched_at, totals, avg, warnings):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                    Table, TableStyle)

    font, font_b = register_korean_font()
    ss = getSampleStyleSheet()

    def S(name, **kw):
        base = dict(fontName=font, leading=14, fontSize=9.5)
        base.update(kw)
        return ParagraphStyle(name, parent=ss["Normal"], **base)

    st_title = S("t", fontName=font_b, fontSize=24, leading=32, alignment=TA_CENTER)
    st_sub = S("s", fontSize=12, leading=20, alignment=TA_CENTER,
               textColor=colors.HexColor("#444444"))
    st_h1 = S("h1", fontName=font_b, fontSize=15, leading=22,
              spaceBefore=10, spaceAfter=8, textColor=colors.HexColor("#1a3a6b"))
    st_h2 = S("h2", fontName=font_b, fontSize=11.5, leading=18, spaceBefore=8, spaceAfter=4)
    st_body = S("b")
    st_small = S("sm", fontSize=8.2, leading=12, textColor=colors.HexColor("#555555"))
    st_mono = S("mono", fontName=font, fontSize=7.4, leading=10)
    st_big = S("big", fontName=font_b, fontSize=30, leading=40, alignment=TA_CENTER,
               textColor=colors.HexColor("#0b3d91"))
    st_warn = S("w", fontSize=9.5, leading=15, textColor=colors.HexColor("#a10000"))

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
        title="레퍼럴 수익 원화 환산 보고서", author="referral_krw_report.py")

    def tbl(data, widths, align_right=(), header=True, size=8.4):
        t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
        style = [
            ("FONTNAME", (0, 0), (-1, -1), font),
            ("FONTSIZE", (0, 0), (-1, -1), size),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
        if header:
            style += [
                ("FONTNAME", (0, 0), (-1, 0), font_b),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#f7f9fc")]),
            ]
        for c in align_right:
            style.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
        t.setStyle(TableStyle(style))
        return t

    E = []

    # ---- 1. 표지 -----------------------------------------------------------
    E += [Spacer(1, 46 * mm),
          Paragraph("레퍼럴 수익 원화 환산 보고서", st_title),
          Spacer(1, 6 * mm),
          Paragraph("비트겟 · OKX 제휴 수수료 수익 / 발생 시점 기준 KRW 환산", st_sub),
          Spacer(1, 16 * mm)]
    E.append(tbl([
        ["대상 기간", f"{PERIOD_START} ~ {PERIOD_END} (KST)"],
        ["생성 일시", datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")],
        ["종가 소스", source],
        ["종가 조회 시각", fetched_at],
        ["환산 기준", "수익 발생 당일 국내 거래소 KRW-USDT 일봉 종가"],
    ], [40 * mm, 118 * mm], header=False, size=9.5))
    E.append(PageBreak())

    # ---- 경고 --------------------------------------------------------------
    if warnings:
        E += [Paragraph("⚠ 경고", st_h1)]
        for w in warnings:
            E.append(Paragraph(f"• {w}", st_warn))
        E.append(Spacer(1, 6 * mm))

    # ---- 2. 한 눈에 보기 ----------------------------------------------------
    E += [Paragraph("한 눈에 보기", st_h1),
          Spacer(1, 4 * mm),
          Paragraph("총 레퍼럴 원화 수익액", S("c", alignment=TA_CENTER, fontSize=11)),
          Paragraph(f"{q_krw(totals['referral_raw']):,} 원", st_big),
          Spacer(1, 6 * mm)]
    E.append(tbl([
        ["구분", "수량 (USDT)", "원화 환산액 (원)"],
        ["비트겟 레퍼럴 소계 (Rebate rewards)",
         fmt_qty(totals["bitget_qty"]), f"{q_krw(totals['bitget_raw']):,}"],
        ["OKX 레퍼럴 소계 (Affiliate commission)",
         fmt_qty(totals["okx_qty"]), f"{q_krw(totals['okx_raw']):,}"],
        ["레퍼럴 수익 합계",
         fmt_qty(totals["bitget_qty"] + totals["okx_qty"]),
         f"{q_krw(totals['referral_raw']):,}"],
        ["참고: 본인 수수료 환급 포함 시 합계",
         fmt_qty(totals["bitget_qty"] + totals["okx_qty"] + totals["rebate_qty"]),
         f"{q_krw(totals['with_rebate_raw']):,}"],
    ], [82 * mm, 38 * mm, 38 * mm], align_right=(1, 2)))
    E += [Spacer(1, 3 * mm),
          Paragraph("※ ‘레퍼럴 수익 합계’ 가 소득 증빙 대상 금액이며, 본인 거래 수수료 환급분은 "
                    "여기에 포함되지 않습니다.", st_small),
          Paragraph(f"※ 미상장 코인(LUNC·LUNA·AB·U)은 KRW 마켓 미상장으로 환산에서 제외되어 "
                    f"위 합계에 0원으로 반영됩니다.", st_small)]

    # 정밀도 각주 (§5-3)
    diff = q_krw(totals["referral_raw"]) - totals["referral_rounded_sum"]
    if diff != 0:
        E.append(Paragraph(
            f"※ 총합은 반올림 전 값의 총합을 마지막에 한 번 반올림한 값입니다. "
            f"반올림된 일별 금액을 단순 합산하면 {totals['referral_rounded_sum']:,}원으로 "
            f"{abs(diff):,}원 차이가 발생합니다.", st_small))
    else:
        E.append(Paragraph(
            "※ 총합은 반올림 전 값의 총합을 마지막에 한 번 반올림한 값이며, "
            "반올림된 일별 금액의 단순 합산 결과와 일치합니다.", st_small))

    # 소계를 눈으로 더했을 때 합계와 1원 어긋나 보이는 경우를 미리 설명한다.
    sub_diff = (q_krw(totals["bitget_raw"]) + q_krw(totals["okx_raw"])
                - q_krw(totals["referral_raw"]))
    if sub_diff != 0:
        E.append(Paragraph(
            f"※ 표의 거래소별 소계를 그대로 더하면 "
            f"{q_krw(totals['bitget_raw']) + q_krw(totals['okx_raw']):,}원이 되어 "
            f"합계와 {abs(sub_diff):,}원 어긋나 보입니다. 이는 오류가 아니라 각 소계를 "
            f"원 단위로 표시하면서 생긴 반올림 차이이며, 합계는 반올림 전 원본 값을 모두 "
            f"더한 뒤 한 번만 반올림한 값입니다.", st_small))
    E.append(PageBreak())

    # ---- 3. 거래소별 일별 명세 ----------------------------------------------
    for title, key in (("비트겟 일별 명세 (Rebate rewards / USDT)", "bitget_rewards"),
                       ("OKX 일별 명세 (Affiliate commission / USDT)", "okx_affiliate")):
        E.append(Paragraph(title, st_h1))
        data = [["날짜 (KST)", "수량 (USDT)", "당일 종가 (원)", "원화액 (원)"]]
        for r in sorted(all_rows[key], key=lambda x: x.d):
            data.append([r.d.isoformat(), fmt_qty(r.qty),
                         (f"{r.close:,}" if r.close is not None else "종가 없음"),
                         fmt_krw(r.krw_raw if r.close is not None else None)])
        sub_raw = total_raw(all_rows[key])
        data.append(["소계", fmt_qty(sum((r.qty for r in all_rows[key]), Decimal(0))),
                     "", f"{q_krw(sub_raw):,}"])
        t = tbl(data, [34 * mm, 42 * mm, 38 * mm, 44 * mm], align_right=(1, 2, 3))
        t.setStyle(TableStyle([
            ("FONTNAME", (0, len(data) - 1), (-1, len(data) - 1), font_b),
            ("BACKGROUND", (0, len(data) - 1), (-1, len(data) - 1),
             colors.HexColor("#dce6f4")),
        ]))
        E += [t, PageBreak()]

    # ---- 4. 일자별 통합 요약 -------------------------------------------------
    E.append(Paragraph("일자별 통합 요약 (비트겟 + OKX 레퍼럴)", st_h1))
    bg = {r.d: r for r in all_rows["bitget_rewards"]}
    ox = {r.d: r for r in all_rows["okx_affiliate"]}
    data = [["날짜 (KST)", "비트겟 수량", "OKX 수량", "합계 수량", "종가 (원)", "원화액 (원)"]]
    for d in daterange(PERIOD_START, PERIOD_END):
        b = bg.get(d)
        o = ox.get(d)
        if not b and not o:
            continue
        bq = b.qty if b else Decimal(0)
        oq = o.qty if o else Decimal(0)
        close = closes.get(d)
        krw = (b.krw_raw if b else Decimal(0)) + (o.krw_raw if o else Decimal(0))
        data.append([d.isoformat(), fmt_qty(bq), fmt_qty(oq), fmt_qty(bq + oq),
                     (f"{close:,}" if close is not None else "종가 없음"),
                     fmt_krw(krw if close is not None else None)])
    data.append(["합계", fmt_qty(totals["bitget_qty"]), fmt_qty(totals["okx_qty"]),
                 fmt_qty(totals["bitget_qty"] + totals["okx_qty"]), "",
                 f"{q_krw(totals['referral_raw']):,}"])
    t = tbl(data, [24 * mm, 30 * mm, 30 * mm, 30 * mm, 24 * mm, 32 * mm],
            align_right=(1, 2, 3, 4, 5), size=7.6)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, len(data) - 1), (-1, len(data) - 1), font_b),
        ("BACKGROUND", (0, len(data) - 1), (-1, len(data) - 1), colors.HexColor("#dce6f4")),
    ]))
    E += [t, PageBreak()]

    # ---- 5. 참고 섹션: 본인 수수료 환급 --------------------------------------
    E += [Paragraph("참고: 본인 거래 수수료 환급 (본 합계 제외)", st_h1),
          Paragraph("본인이 낸 거래 수수료를 되돌려받은 금액으로, 레퍼럴 수익과 성격이 다릅니다. "
                    "위 ‘레퍼럴 수익 합계’ 에는 포함되지 않습니다.", st_body),
          Spacer(1, 4 * mm)]
    for title, key in (("비트겟 Rebate", "bitget_rebate"), ("OKX Fee rebate", "okx_fee_rebate")):
        E.append(Paragraph(title, st_h2))
        data = [["날짜 (KST)", "수량 (USDT)", "당일 종가 (원)", "원화액 (원)"]]
        for r in sorted(all_rows[key], key=lambda x: x.d):
            data.append([r.d.isoformat(), fmt_qty(r.qty),
                         (f"{r.close:,}" if r.close is not None else "종가 없음"),
                         fmt_krw(r.krw_raw if r.close is not None else None)])
        data.append(["소계", fmt_qty(sum((r.qty for r in all_rows[key]), Decimal(0))),
                     "", f"{q_krw(total_raw(all_rows[key])):,}"])
        t = tbl(data, [34 * mm, 42 * mm, 38 * mm, 44 * mm], align_right=(1, 2, 3))
        t.setStyle(TableStyle([
            ("FONTNAME", (0, len(data) - 1), (-1, len(data) - 1), font_b),
            ("BACKGROUND", (0, len(data) - 1), (-1, len(data) - 1),
             colors.HexColor("#dce6f4")),
        ]))
        E += [t, Spacer(1, 5 * mm)]
    E.append(Paragraph(
        f"본인 수수료 환급 합계: {fmt_qty(totals['rebate_qty'])} USDT / "
        f"{q_krw(totals['rebate_raw']):,} 원", st_h2))
    E.append(Paragraph(
        "※ OKX Fee rebate 수량은 거래소 원본 export 의 2026-07-06 두 행"
        "(0.04827443 + 0.0489801 = 0.09725453)을 기준으로 산정했습니다. "
        "본 항목은 총 레퍼럴 수익액에 포함되지 않습니다.", st_small))
    E.append(PageBreak())

    # ---- 6. 미상장 코인 -----------------------------------------------------
    E += [Paragraph("미상장 코인 (환산 제외)", st_h1),
          Paragraph("아래 코인은 2026-08-06 기준 업비트·빗썸 KRW 마켓에 상장되어 있지 않습니다. "
                    "대체 시세를 적용하지 않고 수량만 표기하며, 원화 환산액은 0원으로 처리해 "
                    "총 레퍼럴 수익액에 반영하지 않았습니다.", st_body),
          Spacer(1, 4 * mm)]
    data = [["날짜 (KST)", "거래소", "코인", "수량", "원화액 (원)", "비고"]]
    for r in sorted(all_rows["unlisted"], key=lambda x: x.d):
        data.append([r.d.isoformat(), r.exchange, r.coin, fmt_qty(r.qty), "0",
                     "KRW 마켓 미상장, 환산 제외"])
    E.append(tbl(data, [24 * mm, 20 * mm, 16 * mm, 34 * mm, 22 * mm, 50 * mm],
                 align_right=(3, 4), size=8))
    E.append(PageBreak())

    # ---- 7. 고지 사항 -------------------------------------------------------
    E.append(Paragraph("고지 사항", st_h1))
    notices = [
        ("발췌 구간임 (전체 누적 아님)",
         f"본 보고서는 {PERIOD_START} 부터의 <b>발췌 구간</b>이며 각 거래소 계정의 전체 누적 "
         "수익이 아닙니다. OKX 첫 행의 Before Balance 가 142.774351 USDT, 비트겟 첫 행의 "
         "Available 이 57.7696067323 USDT 로, 해당 시점 이전에 이미 수령 내역이 존재함이 "
         "확인됩니다."),
        ("종가 소스 및 조회 시각",
         f"KRW-USDT 일봉 종가는 <b>{source}</b> 에서 {fetched_at} 에 조회했습니다. "
         "전 구간을 단일 소스로 채웠으며, 날짜별로 서로 다른 거래소 시세를 섞어 쓰지 "
         "않았습니다. 국내 거래소 일봉은 KST 00:00 마감이므로 KST 귀속 일자와 1:1 "
         "매칭됩니다."),
        ("비트겟 2026-07-05 무수령 사유",
         "비트겟 지급은 매일 UTC 16:00 경 발생하므로 KST 로는 익일 01:00 경이 됩니다. "
         "따라서 비트겟의 KST 첫 수령일은 <b>2026-07-06</b> 이며, 07-05 에 비트겟 수령분이 "
         "없는 것은 <b>데이터 누락이 아니라 시차 귀속의 결과</b>입니다. "
         "(비트겟 원본은 UTC 기준 +9시간, OKX 원본은 UTC+8 기준 +1시간을 적용해 KST 일자로 "
         "귀속했습니다.)"),
        ("미상장 코인 처리 방침",
         "LUNC · LUNA · AB · U 는 업비트·빗썸 KRW 마켓 미상장 종목입니다. 해외 시세나 "
         "대체 시세를 끌어와 환산하지 않고, 수량만 표기한 뒤 원화 0원 처리하여 총 레퍼럴 "
         "수익액에서 제외했습니다."),
        ("레퍼럴 수익과 본인 수수료 환급의 구분",
         "비트겟 <b>Rebate rewards</b> 와 OKX <b>Affiliate commission</b> 만 레퍼럴(제휴) "
         "수익으로 보아 본 합계에 포함했습니다. 비트겟 <b>Rebate</b> 와 OKX <b>Fee rebate</b> "
         "는 본인이 부담한 거래 수수료의 환급분이므로 별도 섹션으로 분리했고 총 레퍼럴 "
         "수익액에는 더하지 않았습니다. OKX 의 <b>Withdrawal</b> 및 "
         "<b>From unified trading account</b> 는 수익이 아닌 이체·출금이므로 완전히 "
         "제외했습니다."),
        ("환산 기준 시점",
         "매도 시점이 아니라 <b>수익 발생 시점</b>의 당일 종가로 환산했습니다. 소득 귀속 "
         "시기를 발생주의로 잡아 증빙에 사용하기 위함입니다."),
        ("계산 정밀도",
         "모든 계산은 <b>Decimal</b> 로 수행했으며 float 연산을 사용하지 않았습니다. "
         "반올림은 최종 표시 단계에서만 적용했고(원화 ROUND_HALF_UP 원 단위, 코인 수량 "
         "소수점 10자리), 총합은 반올림 전 값의 총합을 마지막에 한 번 반올림한 값입니다."),
    ]
    for i, (h, b) in enumerate(notices, 1):
        E += [Paragraph(f"{i}. {h}", st_h2), Paragraph(b, st_body), Spacer(1, 2 * mm)]
    E.append(PageBreak())

    # ---- 8. 부록: 검증 결과 --------------------------------------------------
    E.append(Paragraph("부록: 검증 결과", st_h1))
    E.append(Paragraph(
        f"총 {len(CHECKS.items)}개 항목 중 <b>PASS {CHECKS.passed}</b> / "
        f"<b>FAIL {CHECKS.failed}</b>", st_h2))
    data = [["항목", "결과", "상세"]]
    for name, ok, detail in CHECKS.items:
        data.append([Paragraph(name, st_mono),
                     Paragraph("PASS" if ok else "<b>FAIL</b>", st_mono),
                     Paragraph(detail, st_mono)])
    t = tbl(data, [58 * mm, 14 * mm, 102 * mm], size=7.4)
    t.setStyle(TableStyle([("BACKGROUND", (1, i + 1), (1, i + 1),
                           colors.HexColor("#ffe0e0"))
                          for i, (_, ok, _) in enumerate(CHECKS.items) if not ok]))
    E += [t, Spacer(1, 6 * mm)]

    E.append(Paragraph("역산 평균단가", st_h2))
    E.append(tbl([
        ["거래소", "원화 소계 (원)", "수량 (USDT)", "역산 평균단가 (원)", "허용 범위"],
        ["비트겟", f"{q_krw(totals['bitget_raw']):,}", fmt_qty(totals["bitget_qty"]),
         f"{avg['비트겟'].quantize(Decimal('0.01')):,}",
         f"{AVG_PRICE_RANGE[0]:,} ~ {AVG_PRICE_RANGE[1]:,}"],
        ["OKX", f"{q_krw(totals['okx_raw']):,}", fmt_qty(totals["okx_qty"]),
         f"{avg['OKX'].quantize(Decimal('0.01')):,}",
         f"{AVG_PRICE_RANGE[0]:,} ~ {AVG_PRICE_RANGE[1]:,}"],
    ], [24 * mm, 34 * mm, 38 * mm, 36 * mm, 36 * mm], align_right=(1, 2, 3)))
    E += [Spacer(1, 6 * mm), Paragraph("KRW-USDT 종가 전 구간", st_h2)]

    rows = [["날짜", "종가 (원)", "날짜", "종가 (원)"]]
    ds = list(daterange(PERIOD_START, PERIOD_END))
    half = (len(ds) + 1) // 2
    for i in range(half):
        left = ds[i]
        right = ds[i + half] if i + half < len(ds) else None
        lc = closes.get(left)
        rc = closes.get(right) if right else None
        rows.append([
            left.isoformat(), (f"{lc:,}" if lc is not None else "종가 없음"),
            (right.isoformat() if right else ""),
            ("" if right is None else (f"{rc:,}" if rc is not None else "종가 없음")),
        ])
    E.append(tbl(rows, [38 * mm, 40 * mm, 38 * mm, 40 * mm], align_right=(1, 3), size=8))

    doc.build(E)
    LOG(f"  PDF 생성: {path}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="레퍼럴 수익 원화 환산 보고서 생성")
    ap.add_argument("--outdir", default=".", help="산출물 디렉터리")
    ap.add_argument("--bitget-xls", default=None, help="비트겟 원본 xls (교차 검증용)")
    ap.add_argument("--okx-csv", default=None, help="OKX 원본 csv (교차 검증용)")
    ap.add_argument("--closes-file", default=None,
                    help="종가 수동 공급 CSV (YYYY-MM-DD,종가). API 차단 환경용")
    ap.add_argument("--closes-source", default=None,
                    help="--closes-file 사용 시 종가 출처 명시 (필수)")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    spec = {
        "bitget_rewards": parse_block(BITGET_REBATE_REWARDS_USDT),
        "bitget_rebate": parse_block(BITGET_REBATE_USDT),
        "bitget_unlisted": parse_block(BITGET_UNLISTED, with_coin=True),
        "okx_affiliate": parse_block(OKX_AFFILIATE_USDT),
        "okx_fee_rebate": parse_block(OKX_FEE_REBATE_USDT),
    }

    LOG.rule("레퍼럴 수익 원화 환산 보고서")
    LOG(f"  대상 기간 : {PERIOD_START} ~ {PERIOD_END} (KST)")
    LOG(f"  실행 시각 : {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')}")

    # 13-1 수량 검증
    actual_qty = validate_quantities(spec)

    # 원본 파일 교차 검증
    crosscheck_raw(args.bitget_xls, args.okx_csv, spec)

    # 3. 종가 조회
    LOG.rule("3. 종가 조회 (업비트 1순위 → 빗썸 2순위)")
    try:
        closes, source, fetched_at, raw_excerpt = get_closes(args)
    except PriceSourceError as e:
        LOG("")
        LOG("!" * 78)
        LOG("[중단] 종가 조회 실패 — 값을 추정하거나 보간하지 않고 여기서 멈춥니다.")
        LOG("!" * 78)
        LOG(str(e))
        LOG("")
        LOG("  지금까지의 수량 검증 결과:")
        LOG(f"    PASS {CHECKS.passed} / FAIL {CHECKS.failed}")
        return 2

    warnings = validate_closes(closes, source, raw_excerpt)

    # 계산
    all_rows = build_rows(spec, closes)
    validate_rows(all_rows)

    bitget_raw = total_raw(all_rows["bitget_rewards"])
    okx_raw = total_raw(all_rows["okx_affiliate"])
    referral_rows = all_rows["bitget_rewards"] + all_rows["okx_affiliate"] + all_rows["unlisted"]
    rebate_rows = all_rows["bitget_rebate"] + all_rows["okx_fee_rebate"]

    totals = {
        "bitget_qty": sum((r.qty for r in all_rows["bitget_rewards"]), Decimal(0)),
        "okx_qty": sum((r.qty for r in all_rows["okx_affiliate"]), Decimal(0)),
        "rebate_qty": sum((r.qty for r in rebate_rows), Decimal(0)),
        "bitget_raw": bitget_raw,
        "okx_raw": okx_raw,
        "referral_raw": total_raw(referral_rows),
        "referral_rounded_sum": total_of_rounded(referral_rows),
        "rebate_raw": total_raw(rebate_rows),
    }
    totals["with_rebate_raw"] = totals["referral_raw"] + totals["rebate_raw"]

    avg = validate_avg_price(bitget_raw, okx_raw, actual_qty)

    # 산출물
    LOG.rule("산출물 생성")
    csv_path = os.path.join(args.outdir, "레퍼럴수익_계산내역.csv")
    pdf_path = os.path.join(args.outdir, "레퍼럴수익_원화환산_보고서.pdf")
    write_csv(csv_path, all_rows)
    build_pdf(pdf_path, all_rows, spec, closes, source, fetched_at, totals, avg, warnings)

    # 최종 요약
    LOG.rule("최종 요약")
    LOG(f"  확정 구간        : {PERIOD_START} ~ {PERIOD_END} (KST)")
    LOG(f"  종가 소스        : {source} (조회 {fetched_at})")
    LOG(f"  비트겟 소계      : {q_krw(bitget_raw):,} 원 "
        f"({fmt_qty(totals['bitget_qty'])} USDT)")
    LOG(f"  OKX 소계         : {q_krw(okx_raw):,} 원 "
        f"({fmt_qty(totals['okx_qty'])} USDT)")
    LOG(f"  총 레퍼럴 수익액 : {q_krw(totals['referral_raw']):,} 원")
    LOG(f"  참고 합계        : {q_krw(totals['with_rebate_raw']):,} 원 "
        f"(본인 수수료 환급 {q_krw(totals['rebate_raw']):,} 원 포함)")
    LOG(f"  검증 PASS        : {CHECKS.passed} / {len(CHECKS.items)} (FAIL {CHECKS.failed})")
    LOG(f"  역산 평균단가    : 비트겟 {avg['비트겟'].quantize(Decimal('0.01')):,} 원 / "
        f"OKX {avg['OKX'].quantize(Decimal('0.01')):,} 원")

    return 1 if CHECKS.failed else 0


if __name__ == "__main__":
    sys.exit(main())
