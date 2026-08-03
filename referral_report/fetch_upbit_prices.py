#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
업비트 KRW 마켓 일봉 종가 수집기.

Upbit Open API (인증 불필요 public endpoint) 를 호출해
대상 기간의 일별 종가를 upbit_prices.json 으로 저장한다.

  python3 fetch_upbit_prices.py [-o upbit_prices.json]

인터넷에서 api.upbit.com 에 접근 가능한 환경에서 실행해야 한다.
표준 라이브러리만 사용하므로 추가 설치는 필요 없다.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

BASE = "https://api.upbit.com/v1"
KST = timezone(timedelta(hours=9))

# 보고서 대상 기간 (KST). to 파라미터는 exclusive 이므로 마지막 날 +1일까지 요청한다.
START_KST = "2026-07-05"
END_KST = "2026-08-03"

NEEDED_COINS = ["USDT", "LUNC", "LUNA", "AB", "U"]


def http_get_json(url, retries=4):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/json", "User-Agent": "referral-krw-report/1.0"}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code} {e.reason}"
            if e.code == 429:  # rate limit
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"{url} -> {last}") from e
        except Exception as e:  # 네트워크 오류는 지수 백오프 재시도
            last = repr(e)
            time.sleep(2 ** attempt)
    raise RuntimeError(f"{url} -> 재시도 {retries}회 실패: {last}")


def list_krw_markets():
    data = http_get_json(f"{BASE}/market/all")
    return {m["market"] for m in data if m.get("market", "").startswith("KRW-")}


def fetch_daily_candles(market, to_kst_date, count=200):
    """to 는 UTC 기준 exclusive. KST 날짜 to_kst_date 00:00 == UTC 전날 15:00."""
    to_utc = datetime.strptime(to_kst_date, "%Y-%m-%d").replace(tzinfo=KST).astimezone(timezone.utc)
    to_param = to_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"{BASE}/candles/days?market={market}&count={count}&to={to_param}"
    return http_get_json(url)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="upbit_prices.json")
    args = ap.parse_args()

    fetched_at = datetime.now(KST).isoformat(timespec="seconds")
    print(f"조회 시각(KST): {fetched_at}")

    print("1) KRW 마켓 목록 조회 ...")
    krw_markets = list_krw_markets()
    print(f"   KRW 마켓 {len(krw_markets)}개 확인")

    markets_checked = {}
    prices = {}
    warnings = []

    # 종료일 다음날을 to 로 주면 END_KST 캔들까지 포함된다.
    to_kst = (datetime.strptime(END_KST, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    for coin in NEEDED_COINS:
        market = f"KRW-{coin}"
        listed = market in krw_markets
        markets_checked[market] = listed
        if not listed:
            print(f"2) {market}: 업비트 KRW 마켓 미상장 -> 환산 제외")
            warnings.append(f"{market} 업비트 KRW 마켓 미상장 (환산 제외)")
            continue

        print(f"2) {market}: 일봉 조회 ...")
        candles = fetch_daily_candles(market, to_kst)
        time.sleep(0.2)  # 초당 10회 제한 준수

        by_date = {}
        for c in candles:
            d = c["candle_date_time_kst"][:10]
            if START_KST <= d <= END_KST:
                # trade_price 를 문자열로 보존해 float 오차를 만들지 않는다.
                by_date[d] = repr(c["trade_price"])
        prices[coin] = dict(sorted(by_date.items()))
        print(f"   {len(by_date)}일치 종가 수집 ({min(by_date, default='-')} ~ {max(by_date, default='-')})")

    out = {
        "fetched_at_kst": fetched_at,
        "source": "Upbit Open API GET /v1/candles/days (candle_date_time_kst, trade_price)",
        "period": {"start_kst": START_KST, "end_kst": END_KST},
        "markets_checked": markets_checked,
        "prices": prices,
        "warnings": warnings,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"\n저장 완료: {args.out}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as e:
        print(f"\n[오류] {e}", file=sys.stderr)
        print("api.upbit.com 접근이 가능한 네트워크에서 실행해야 합니다.", file=sys.stderr)
        sys.exit(2)
