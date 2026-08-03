#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
원본 파일(비트겟 .xls / OKX .csv)로부터 KST 일별 집계를 독립적으로 재계산하고,
프롬프트에 기재된 표 및 검증 기준값과 대조한다.

- 비트겟 원본: UTC 기준  -> +9h -> KST
- OKX  원본: UTC+8 기준 -> +1h -> KST
- 모든 산술은 decimal.Decimal 로만 수행한다 (float 금지).
"""

from decimal import Decimal, getcontext
from datetime import datetime, timedelta
from collections import defaultdict
import csv
import sys

getcontext().prec = 50

BITGET_XLS = "/root/.claude/uploads/5a120501-c174-56a4-af4f-1b727425cf28/8f0c90c5-Export_spot_transactions20260803_14_19_01.227.xls"
OKX_CSV = "/root/.claude/uploads/5a120501-c174-56a4-af4f-1b727425cf28/505db281-OKX_Funding_History_2026070520260801UTC89e022f45db1842518edd8c458cbb27da.csv"


# ---------------------------------------------------------------- 원본 파싱
def load_bitget():
    """비트겟 spot transactions. Type == 'Rebate rewards' 만 레퍼럴 수익."""
    import xlrd

    sheet = xlrd.open_workbook(BITGET_XLS).sheets()[0]
    header = [sheet.cell_value(0, c) for c in range(sheet.ncols)]
    idx = {name: i for i, name in enumerate(header)}

    rows = []
    skipped = []
    for r in range(1, sheet.nrows):
        rec = {k: sheet.cell_value(r, i) for k, i in idx.items()}
        if rec["Type"] != "Rebate rewards":
            skipped.append(rec)
            continue
        utc = datetime.strptime(rec["Date"], "%Y-%m-%d %H:%M:%S")
        kst = utc + timedelta(hours=9)
        rows.append(
            {
                "kst_date": kst.date().isoformat(),
                "coin": rec["Coin"],
                "amount": Decimal(rec["Amount"]),
                "raw_time_utc": rec["Date"],
            }
        )
    return rows, skipped


def load_okx():
    """OKX funding history. Type 별로 분류. 시간은 UTC+8."""
    affiliate = []
    fee_rebate = []
    other = []

    with open(OKX_CSV, encoding="utf-8-sig") as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]

    # 1행은 계정 메타(UID/Account Type/Time Zone), 2행이 실제 헤더
    reader = csv.DictReader(lines[1:])
    for rec in reader:
        rec = {(k or "").lstrip("﻿").strip(): (v or "").lstrip("﻿").strip()
               for k, v in rec.items()}
        local = datetime.strptime(rec["Time"], "%Y-%m-%d %H:%M:%S")  # UTC+8
        kst = local + timedelta(hours=1)
        item = {
            "kst_date": kst.date().isoformat(),
            "coin": rec["Symbol"],
            "amount": Decimal(rec["Amount"]),
            "raw_time_utc8": rec["Time"],
            "type": rec["Type"],
        }
        if rec["Type"] == "Affiliate commission":
            affiliate.append(item)
        elif rec["Type"] == "Fee rebate":
            fee_rebate.append(item)
        else:
            other.append(item)
    return affiliate, fee_rebate, other


def aggregate(rows):
    """(kst_date, coin) -> Decimal 합계"""
    agg = defaultdict(lambda: Decimal(0))
    for r in rows:
        agg[(r["kst_date"], r["coin"])] += r["amount"]
    return agg


# ------------------------------------------------- 프롬프트 기재 표 (대조용)
PROMPT_BITGET = """2026-07-06|USDT|0.05519086
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

PROMPT_OKX = """2026-07-05|USDT|6.37327905
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


def parse_prompt_table(text):
    out = {}
    for line in text.strip().splitlines():
        d, coin, amt = line.split("|")
        out[(d, coin)] = Decimal(amt)
    return out


def compare(label, computed, stated, tol=Decimal("0.00000001")):
    """원본 재계산값 vs 프롬프트 기재값. 8자리 표기 차이는 tol 이내면 통과."""
    print(f"\n=== {label}: 원본 재계산 vs 프롬프트 기재 표 ===")
    keys = sorted(set(computed) | set(stated))
    mismatches = []
    for k in keys:
        c = computed.get(k)
        s = stated.get(k)
        if c is None:
            mismatches.append((k, "원본에 없음", s))
        elif s is None:
            mismatches.append((k, c, "프롬프트에 없음"))
        elif abs(c - s) > tol:
            mismatches.append((k, c, s))
    if not mismatches:
        print(f"  PASS - {len(keys)}개 (날짜,코인) 전부 일치 (허용오차 {tol})")
    else:
        print(f"  FAIL - 불일치 {len(mismatches)}건")
        for k, c, s in mismatches:
            print(f"    {k[0]} {k[1]:>5}: 재계산={c}  기재={s}")
    return mismatches


def check_totals(label, computed):
    print(f"\n=== {label}: 코인별 총량 (원본 재계산, 무반올림) ===")
    per_coin = defaultdict(lambda: Decimal(0))
    for (d, coin), v in computed.items():
        per_coin[coin] += v
    for coin in sorted(per_coin):
        print(f"  {coin:>5}: {per_coin[coin]}")
    return per_coin


EXPECTED = {
    ("bitget", "USDT"): Decimal("32.10569951"),
    ("bitget", "LUNC"): Decimal("60.67429200"),
    ("bitget", "LUNA"): Decimal("0.01601086"),
    ("bitget", "AB"): Decimal("0.49888957"),
    ("bitget", "U"): Decimal("0.00098050"),
    ("okx", "USDT"): Decimal("40.57077565"),
}


def main():
    print("=" * 72)
    print("원본 파일 -> KST 일별 집계 독립 재계산 및 대조")
    print("=" * 72)

    bg_rows, bg_skipped = load_bitget()
    print(f"\n[비트겟] Rebate rewards {len(bg_rows)}건 채택 / 기타 {len(bg_skipped)}건 제외")

    okx_aff, okx_fee, okx_other = load_okx()
    print(f"[OKX] Affiliate commission {len(okx_aff)}건 채택 / "
          f"Fee rebate {len(okx_fee)}건 / 기타(이체·출금 등) {len(okx_other)}건 제외")
    for o in okx_other:
        print(f"    제외: {o['raw_time_utc8']} {o['type']} {o['amount']} {o['coin']}")
    for f in okx_fee:
        print(f"    참고(Fee rebate): {f['raw_time_utc8']} KST {f['kst_date']} "
              f"{f['amount']} {f['coin']}")

    bg_agg = aggregate(bg_rows)
    okx_agg = aggregate(okx_aff)
    fee_agg = aggregate(okx_fee)

    m1 = compare("비트겟", bg_agg, parse_prompt_table(PROMPT_BITGET))
    m2 = compare("OKX", okx_agg, parse_prompt_table(PROMPT_OKX))

    bg_tot = check_totals("비트겟", bg_agg)
    okx_tot = check_totals("OKX", okx_agg)
    fee_tot = check_totals("OKX 본인 수수료 환급(Fee rebate, 합계 제외)", fee_agg)

    print("\n=== 프롬프트 3-5항 검증 기준값 대조 (허용오차 1e-8) ===")
    tol = Decimal("1e-8")
    all_pass = True
    for (ex, coin), expected in EXPECTED.items():
        actual = (bg_tot if ex == "bitget" else okx_tot).get(coin)
        if actual is None:
            print(f"  FAIL {ex} {coin}: 원본에서 산출 안 됨")
            all_pass = False
            continue
        diff = abs(actual - expected)
        ok = diff <= tol
        all_pass &= ok
        print(f"  {'PASS' if ok else 'FAIL'} {ex:>6} {coin:>5}: "
              f"재계산={actual}  기준={expected}  차이={diff}")

    print("\n" + "=" * 72)
    if m1 or m2 or not all_pass:
        print("결과: 불일치 존재 -> 위 내역 확인 필요")
        return 1
    print("결과: 원본 대조 및 기준값 검증 전부 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
