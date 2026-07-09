// 무료 검색 API 프록시 — 가게 "사실 정보"만 가져온다.
// 반환: 상호 · 주소 · 도로명 · 카테고리 · 전화 · 좌표(WGS84) · place URL.
// 별점 · 리뷰 · 리뷰사진은 절대 가져오지 않는다 (공식 API가 주지도 않음).
//
// 키(서버 환경변수):
//   KAKAO_REST_KEY                     — 카카오 로컬 REST 키
//   NAVER_SEARCH_ID / NAVER_SEARCH_SECRET — 네이버 검색(지역) 키
//
// 좌표 주의: 카카오는 x=경도/y=위도(WGS84)를 그대로 준다. 네이버 지역검색의
// mapx/mapy는 WGS84를 1e7배한 정수로 오는 경우가 많아 아래에서 보정한다.
// (형식이 계정/버전에 따라 다를 수 있어 지도 정밀도는 카카오가 안전.)

const strip = (s) => String(s == null ? '' : s).replace(/<[^>]*>/g, '').trim();

export function kakaoConfigured() {
  return !!process.env.KAKAO_REST_KEY;
}
export function naverConfigured() {
  return !!(process.env.NAVER_SEARCH_ID && process.env.NAVER_SEARCH_SECRET);
}

function normNaverCoord(v) {
  const n = Number(v);
  if (!Number.isFinite(n) || n === 0) return null;
  // 1e7배 정수(예: 1270276620 → 127.027662)면 스케일 다운, 이미 소수면 그대로.
  return Math.abs(n) > 1000 ? n / 1e7 : n;
}

async function searchKakao(query) {
  const r = await fetch(
    'https://dapi.kakao.com/v2/local/search/keyword.json?size=8&query=' + encodeURIComponent(query),
    { headers: { Authorization: 'KakaoAK ' + process.env.KAKAO_REST_KEY } },
  );
  if (!r.ok) throw new Error('kakao ' + r.status);
  const d = await r.json();
  return (d.documents || []).map((it) => ({
    provider: 'kakao',
    name: strip(it.place_name),
    category: strip(it.category_name),
    address: strip(it.address_name),
    roadAddress: strip(it.road_address_name),
    phone: strip(it.phone),
    lat: Number(it.y) || null,
    lng: Number(it.x) || null,
    placeUrl: strip(it.place_url),
  }));
}

async function searchNaver(query) {
  const r = await fetch('https://openapi.naver.com/v1/search/local.json?display=5&query=' + encodeURIComponent(query), {
    headers: {
      'X-Naver-Client-Id': process.env.NAVER_SEARCH_ID,
      'X-Naver-Client-Secret': process.env.NAVER_SEARCH_SECRET,
    },
  });
  if (!r.ok) throw new Error('naver ' + r.status);
  const d = await r.json();
  return (d.items || []).map((it) => ({
    provider: 'naver',
    name: strip(it.title),
    category: strip(it.category),
    address: strip(it.address),
    roadAddress: strip(it.roadAddress),
    phone: strip(it.telephone),
    lat: normNaverCoord(it.mapy),
    lng: normNaverCoord(it.mapx),
    placeUrl: strip(it.link),
  }));
}

/** provider: 'kakao' | 'naver' (미지정 시 설정된 것 중 카카오 우선) */
export async function searchPlaces(query, provider) {
  const q = String(query || '').trim();
  if (!q) return [];
  const use = provider === 'naver' || (!provider && !kakaoConfigured() && naverConfigured()) ? 'naver' : 'kakao';
  if (use === 'naver') {
    if (!naverConfigured()) throw new Error('네이버 검색 키가 설정되지 않았습니다.');
    return searchNaver(q);
  }
  if (!kakaoConfigured()) throw new Error('카카오 검색 키가 설정되지 않았습니다.');
  return searchKakao(q);
}
