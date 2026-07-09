import { useCallback, useEffect, useState } from 'react';
import { buildDemoCards } from '../lib/demoCards';
import { parseCards } from '../lib/parseCards';
import type { ImgMode, Place, RawCard, Skin, Tone } from '../types';

const STORAGE_KEY = 'cardnews_generator_v1';

export interface PersistedState {
  skin: Skin;
  category: string;
  title: string;
  notes: string;
  tone: Tone;
  count: number;
  handle: string;
  unsplashKey: string;
  place: Place | null;
  rawCards: RawCard[];
  resultTitle: string;
  imgMode: Record<number, ImgMode>;
  genSeed: Record<number, number>;
  genId: number;
}

const DEFAULTS: PersistedState = {
  skin: 'minimal',
  category: '경제 · 투자',
  title: '',
  notes: '',
  tone: '신뢰형',
  count: 9,
  handle: '@your_account',
  unsplashKey: '',
  place: null,
  rawCards: [],
  resultTitle: '',
  imgMode: {},
  genSeed: {},
  genId: 0,
};

function loadSaved(): PersistedState {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
    if (!saved || typeof saved !== 'object') return DEFAULTS;
    const keep: Partial<PersistedState> = {};
    (['skin', 'category', 'title', 'notes', 'tone', 'count', 'handle', 'unsplashKey', 'resultTitle', 'genId'] as const).forEach((k) => {
      if (saved[k] !== undefined) (keep as Record<string, unknown>)[k] = saved[k];
    });
    if (saved.place && typeof saved.place === 'object') keep.place = saved.place;
    if (Array.isArray(saved.rawCards)) keep.rawCards = saved.rawCards;
    if (saved.imgMode && typeof saved.imgMode === 'object') keep.imgMode = saved.imgMode;
    if (saved.genSeed && typeof saved.genSeed === 'object') keep.genSeed = saved.genSeed;
    return { ...DEFAULTS, ...keep };
  } catch {
    return DEFAULTS;
  }
}

export function useAppState() {
  const [state, setState] = useState<PersistedState>(loadSaved);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 모든 영속 상태는 변경 즉시 저장 — 새로고침·재접속에도 유지
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      /* 저장 공간 부족 등은 무시 */
    }
  }, [state]);

  const set = useCallback(<K extends keyof PersistedState>(key: K, value: PersistedState[K]) => {
    setState((s) => ({ ...s, [key]: value }));
  }, []);

  const setImgMode = useCallback((index: number, mode: ImgMode) => {
    setState((s) => ({ ...s, imgMode: { ...s.imgMode, [index]: mode } }));
  }, []);

  const bumpSeed = useCallback((index: number) => {
    setState((s) => ({ ...s, genSeed: { ...s.genSeed, [index]: (s.genSeed[index] || 1) + 1 } }));
  }, []);

  const generate = useCallback(async () => {
    if (loading) return;
    if (!state.title.trim()) {
      setError('제목(주제)을 입력해주세요.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      let rawCards: RawCard[];
      try {
        // 서버가 있으면 서버가 생성(키 있으면 실제 AI, 없으면 서버 데모).
        const r = await fetch('/api/generate', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({
            category: state.category,
            title: state.title,
            notes: state.notes,
            tone: state.tone,
            count: state.count,
            place: state.place,
          }),
        });
        const data = await r.json().catch(() => null);
        if (!r.ok) throw new Error((data && data.error) || 'HTTP ' + r.status);
        rawCards = parseCards(String(data.text ?? ''));
      } catch {
        // 서버가 없거나(정적 호스팅) 응답 실패 → 브라우저 안에서 데모 카드 생성.
        rawCards = buildDemoCards({
          category: state.category,
          title: state.title,
          tone: state.tone,
          count: state.count,
          place: state.place,
        });
      }
      // 본문 카드만 AI 이미지 기본 켬 — 커버/CTA는 스킨 배경 유지
      const imgMode: Record<number, ImgMode> = {};
      const genSeed: Record<number, number> = {};
      rawCards.forEach((_, i) => {
        imgMode[i] = i > 0 && i < rawCards.length - 1 ? 'ai' : 'none';
        genSeed[i] = 1;
      });
      setState((s) => ({
        ...s,
        rawCards,
        resultTitle: s.title.trim(),
        imgMode,
        genSeed,
        genId: Date.now(),
      }));
    } catch (e) {
      setError('생성에 실패했습니다. 잠시 후 다시 시도해주세요. (' + (e instanceof Error ? e.message : '오류') + ')');
    } finally {
      setLoading(false);
    }
  }, [loading, state]);

  return { ...state, loading, error, set, setImgMode, bumpSeed, generate };
}
