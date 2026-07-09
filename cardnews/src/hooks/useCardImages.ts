import { useEffect, useRef, useState } from 'react';
import type { AppConfig, ImgMode, Place, RawCard } from '../types';

export type BgUrls = Record<number, string>;

/**
 * 카드별 배경 URL을 해석한다. 소스는 카테고리/모드에 따라 자동으로 갈린다:
 *  - mode 'place' → 가게 위치 정적 지도(/api/staticmap). 지도 미설정 시 가게명 주제 사진으로 폴백.
 *  - mode 'ai'    → 주제 사진. Unsplash 키가 있으면 실사진(클라이언트 직접 호출),
 *                   없으면 서버의 키리스 Openverse(CC0)를 사용.
 * 해석 실패 시 해당 카드는 비워 두고 decorate가 picsum 예시로 폴백한다.
 * 결과는 영속화하지 않는다(복원 시 재조회).
 */
export function useCardImages(
  rawCards: RawCard[],
  imgMode: Record<number, ImgMode>,
  genSeed: Record<number, number>,
  unsplashKey: string,
  category: string,
  place: Place | null,
  config: AppConfig | null,
): BgUrls {
  const [urls, setUrls] = useState<BgUrls>({});
  const cacheKeys = useRef<Record<number, string>>({});
  const pending = useRef<Record<number, string>>({});

  useEffect(() => {
    const uKey = unsplashKey.trim();
    const mapOn = !!config?.staticMap && !!place && place.lat != null && place.lng != null;

    async function resolvePhoto(keyword: string, seed: number): Promise<string | null> {
      if (uKey) {
        // 사용자 본인 Unsplash 키 — 클라이언트에서 직접 (CORS 허용)
        try {
          const r = await fetch(
            'https://api.unsplash.com/search/photos?per_page=5&content_filter=high&query=' +
              encodeURIComponent(keyword) +
              '&client_id=' +
              encodeURIComponent(uKey),
          );
          if (r.ok) {
            const d = await r.json();
            const res = d && d.results;
            if (res && res.length) {
              const pick = res[(seed - 1) % res.length] || res[0];
              const u = pick && pick.urls && (pick.urls.regular || pick.urls.small);
              if (u) return u;
            }
          }
        } catch {
          /* 폴백으로 진행 */
        }
      }
      // 키리스 주제 사진 (서버 → Openverse CC0)
      try {
        const r = await fetch('/api/photo?seed=' + seed + '&q=' + encodeURIComponent(keyword));
        if (r.ok) {
          const d = await r.json();
          if (d && d.url) return d.url;
        }
      } catch {
        /* picsum 폴백 */
      }
      return null;
    }

    rawCards.forEach((c, i) => {
      const mode = imgMode[i] || 'none';
      if (mode !== 'ai' && mode !== 'place') return;
      const seed = genSeed[i] || 1;

      // 가게 지도 모드 — 정적 지도가 켜져 있으면 좌표로 즉시 URL 구성
      if (mode === 'place' && mapOn && place) {
        const ck = 'map|' + place.lat + '|' + place.lng;
        if (cacheKeys.current[i] === ck) return;
        cacheKeys.current[i] = ck;
        setUrls((prev) => ({ ...prev, [i]: '/api/staticmap?lat=' + place.lat + '&lng=' + place.lng }));
        return;
      }

      // 주제 사진 (place 모드지만 지도 미설정이면 가게명으로, 아니면 카드 키워드로)
      const keyword =
        mode === 'place' && place
          ? [place.name, place.category].filter(Boolean).join(' ')
          : c.img
            ? String(c.img)
            : category + ' 관련 사진';
      const ck = mode + '|' + keyword + '|' + seed + '|' + (uKey ? 'k' : '0');
      if (cacheKeys.current[i] === ck) return;
      if (pending.current[i] === ck) return;
      pending.current[i] = ck;
      void resolvePhoto(keyword, seed).then((url) => {
        if (pending.current[i] !== ck) return;
        cacheKeys.current[i] = ck;
        if (url) setUrls((prev) => ({ ...prev, [i]: url }));
      });
    });
  }, [rawCards, imgMode, genSeed, unsplashKey, category, place, config]);

  return urls;
}
