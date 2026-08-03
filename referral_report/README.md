# 레퍼럴 수익 원화 환산 보고서

비트겟(Rebate rewards) · OKX(Affiliate commission) 레퍼럴 수익을
업비트 KRW 마켓 일별 종가로 환산해 PDF 보고서를 생성한다.

- 대상 기간: 2026-07-05 ~ 2026-08-03 (KST)
- 계산식: `일별 원화 수익액(t) = 코인 수량(t) × 업비트 KRW 마켓 당일 종가(t)`

## 현재 상태

원본 데이터 검증은 **전 항목 통과**했고 보고서 생성 파이프라인도 완성·검증되었다.
다만 이 실행 환경에서는 `api.upbit.com` 이 **네트워크 정책상 차단**되어 있어
실제 종가를 수집하지 못했다. 종가 파일만 확보되면 즉시 최종 산출물이 생성된다.

```
$ curl https://api.upbit.com/v1/market/all
curl: (56) CONNECT tunnel failed, response 403
# 프록시 진단: "gateway answered 403 to CONNECT (policy denial)" host=api.upbit.com:443
```

## 실행 순서

```bash
# 1) 원본 파일 대조 검증 (네트워크 불필요)
python3 reconcile_sources.py

# 2) 업비트 종가 수집 — api.upbit.com 접근 가능한 환경에서 실행
python3 fetch_upbit_prices.py -o upbit_prices.json

# 3) 보고서 생성
python3 build_report.py --prices upbit_prices.json
```

## 스크립트

| 파일 | 역할 |
|---|---|
| `reconcile_sources.py` | 비트겟 `.xls` / OKX `.csv` 원본에서 KST 일별 집계를 독립 재계산하고 기준값과 대조 |
| `fetch_upbit_prices.py` | Upbit Open API 일봉 종가 수집 → `upbit_prices.json` (표준 라이브러리만 사용) |
| `build_report.py` | 원화 환산 계산 + 검증 + `referral_krw_report.pdf` / `referral_krw_calc.csv` 생성 |

## 산출물

- `referral_krw_report.pdf` — 표지 / 요약 / 계산 기준 / 거래소별 일별 명세 / 참고 / 부록(검증·종가 원본)
- `referral_krw_calc.csv` — 날짜, 거래소, 코인, 수량, 종가, 원화액(반올림 전·후), 비고

## 계산 규칙

1. 모든 산술은 `decimal.Decimal`. `float` 곱셈·합산 없음.
2. 반올림은 최종 표시 단계에서만. 중간 계산은 원본 정밀도 유지.
   - 원화: `ROUND_HALF_UP` 원 단위 반올림
   - 코인 수량: 소수점 8자리
3. 총합은 **반올림 전 값의 합을 마지막에 한 번 반올림**한 값.
   반올림된 일별 금액의 단순 합과 다르면 그 차이를 보고서 각주에 표기한다.
4. 거래소별 소계와 전체 합계를 모두 산출한다.
5. 업비트 KRW 미상장 코인(`AB`, `U`)은 다른 시세를 임의로 끌어오지 않고
   원화 환산액 0원 + "업비트 KRW 미상장 → 환산 제외" 로 표기한다.
6. 종가가 없는 날짜는 추정값으로 채우지 않는다. 해당 행은 "종가 없음" 으로
   표시되고 검증이 FAIL 처리되어 보고서 생성이 중단된다.

## 시차 귀속

| 거래소 | 원본 기준 | 보정 | 결과 |
|---|---|---|---|
| 비트겟 | UTC | +9h | KST |
| OKX | UTC+8 | +1h | KST |

업비트 일봉은 KST 00:00 마감이므로 위 KST 일자와 업비트 일봉 날짜를 1:1 매칭한다.

## 집계 대상 / 제외

- **비트겟**: `Type == "Rebate rewards"` 만 채택 (37건).
- **OKX**: `Type == "Affiliate commission"` 만 채택 (426건).
  - `Fee rebate` 2건(합계 0.09725453 USDT)은 본인 거래 수수료 환급이므로
    **총합 제외**, 보고서에 참고 섹션으로만 표시.
  - 계정 간 이체 2건 · 출금 1건은 수익이 아니므로 제외.
