import { useEffect, useRef, useState } from 'react';
import type { ImgMode, RawCard } from '../types';

export type ResolvedUrls = Record<number, { k: string; url: string }>;

/**
 * Unsplash 키가 있을 때, imgMode가 'ai'인 카드마다 키워드 검색으로 실사진 URL을 해석한다.
 * - 캐시 키 = "키워드|시드" — 같은 키면 재요청하지 않음
 * - in-flight 요청은 pending으로 디듑
 * - 결과는 영속화하지 않는다 (복원 시 재조회)
 */
export function useUnsplashUrls(
  rawCards: RawCard[],
  imgMode: Record<number, ImgMode>,
  genSeed: Record<number, number>,
  unsplashKey: string,
  category: string,
): ResolvedUrls {
  const [imgUrls, setImgUrls] = useState<ResolvedUrls>({});
  const urlsRef = useRef(imgUrls);
  urlsRef.current = imgUrls;
  const pending = useRef<Record<number, string>>({});

  useEffect(() => {
    const key = unsplashKey.trim();
    if (!key || !rawCards.length) return;
    rawCards.forEach((c, i) => {
      if (imgMode[i] !== 'ai') return;
      const kw = c.img ? String(c.img) : category + ' 관련 사진';
      const seed = genSeed[i] || 1;
      const ck = kw + '|' + seed;
      const cur = urlsRef.current[i];
      if (cur && cur.k === ck) return;
      if (pending.current[i] === ck) return;
      pending.current[i] = ck;
      fetch(
        'https://api.unsplash.com/search/photos?per_page=5&content_filter=high&query=' +
          encodeURIComponent(kw) +
          '&client_id=' +
          encodeURIComponent(key),
      )
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => {
          const res = d && d.results;
          if (res && res.length) {
            const pick = res[(seed - 1) % res.length] || res[0];
            const u = pick && pick.urls && (pick.urls.regular || pick.urls.small);
            if (u) setImgUrls((prev) => ({ ...prev, [i]: { k: ck, url: u } }));
          }
        })
        .catch(() => {});
    });
  }, [rawCards, imgMode, genSeed, unsplashKey, category]);

  return imgUrls;
}
