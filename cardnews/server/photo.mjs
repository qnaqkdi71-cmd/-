// 키리스 주제 사진 검색 — Openverse (CC0 / 퍼블릭도메인만).
// 여행·경제 등 "주제에 맞는 사진 자동" 용도. 키 없이 동작하고, CC0/PDM만
// 필터링하므로 카드뉴스 배경으로 재사용해도 저작자 표기 의무가 없다.
// (사용자가 자기 Unsplash 키를 넣으면 클라이언트에서 Unsplash를 우선 사용.)

const UA = 'cardnews-generator/1.0 (+https://example.com)';

/**
 * 키워드로 CC0/퍼블릭도메인 이미지 한 장의 URL을 반환. seed로 결과 내 위치 선택.
 * 실패하면 null (호출측이 picsum 등으로 폴백).
 */
export async function searchPhoto(keyword, seed = 1) {
  const q = String(keyword || '').trim();
  if (!q) return null;
  try {
    const r = await fetch(
      'https://api.openverse.org/v1/images/?license=cc0,pdm&mature=false&page_size=10&q=' + encodeURIComponent(q),
      { headers: { 'User-Agent': UA, Accept: 'application/json' } },
    );
    if (!r.ok) return null;
    const d = await r.json();
    const results = Array.isArray(d.results) ? d.results : [];
    if (!results.length) return null;
    const pick = results[(Math.max(1, seed) - 1) % results.length] || results[0];
    return pick.url || pick.thumbnail || null;
  } catch {
    return null;
  }
}
