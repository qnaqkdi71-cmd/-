// 정적 지도 이미지 프록시 — 가게 위치를 배경으로 쓸 때 사용.
// 네이버 클라우드 플랫폼(NCP) Maps 정적(래스터) 지도를 서버에서 받아 그대로 전달한다.
// 이건 "실제 가게 사진"이 아니라 위치 지도이며, 합법적으로 자동 사용할 수 있는 소스다.
//
// 키(서버 환경변수): NCP_MAP_KEY_ID / NCP_MAP_KEY
// 미설정 시 이 기능은 꺼지고, 가게 카드도 주제 사진으로 폴백된다.

export function staticMapConfigured() {
  return !!(process.env.NCP_MAP_KEY_ID && process.env.NCP_MAP_KEY);
}

/**
 * lat/lng 중심의 지도 PNG 바이트를 반환. 실패 시 null.
 * 카드 배경(1080×1350, 4:5)에 맞춰 세로 비율로 요청한다.
 */
export async function fetchStaticMap({ lat, lng, w = 540, h = 675, level = 16 }) {
  if (!staticMapConfigured()) return null;
  const la = Number(lat);
  const ln = Number(lng);
  if (!Number.isFinite(la) || !Number.isFinite(ln)) return null;
  const url =
    'https://naveropenapi.apigw.ntruss.com/map-static/v2/raster' +
    `?w=${w}&h=${h}&center=${ln},${la}&level=${level}&scale=2` +
    `&markers=type:d|size:mid|pos:${ln}%20${la}`;
  try {
    const r = await fetch(url, {
      headers: {
        'X-NCP-APIGW-API-KEY-ID': process.env.NCP_MAP_KEY_ID,
        'X-NCP-APIGW-API-KEY': process.env.NCP_MAP_KEY,
      },
    });
    if (!r.ok) return null;
    const buf = Buffer.from(await r.arrayBuffer());
    return { buf, contentType: r.headers.get('content-type') || 'image/png' };
  } catch {
    return null;
  }
}
