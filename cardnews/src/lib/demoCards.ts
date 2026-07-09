// 클라이언트용 데모 카드 생성 — 백엔드(서버)가 없거나 응답에 실패할 때 폴백.
// 서버의 server/demo.mjs 와 같은 결과를 내도록 맞춰 둔 사본이다(둘 다 수정 시 함께).
// 덕분에 서버 없이 웹만 올려도(정적 호스팅) 카드 생성이 그대로 동작한다.
import type { RawCard, Tone } from '../types';

function splitTwo(s: string): string {
  const t = String(s || '').trim();
  if (t.length <= 10) return t;
  const mid = Math.floor(t.length / 2);
  let cut = t.lastIndexOf(' ', mid);
  if (cut < 4) cut = t.indexOf(' ', mid);
  if (cut < 0) cut = mid;
  return t.slice(0, cut).trim() + '\n' + t.slice(cut).trim();
}

const TONE_SUB: Record<string, string> = {
  신뢰형: '핵심만 차분하게 정리했습니다.',
  친근형: '어렵지 않게, 하나씩 알려드릴게요.',
  트렌디형: '스압 없이 딱 필요한 것만.',
};

export interface DemoInput {
  category: string;
  title: string;
  tone: Tone;
  count: number;
  place?: { name: string; category?: string; roadAddress?: string; address?: string } | null;
}

export function buildDemoCards({ category, title, tone, count, place }: DemoInput): RawCard[] {
  const n = Math.min(10, Math.max(6, Number(count) || 9));
  const cat = String(category || '카드뉴스');
  const t = String(title || '').trim() || cat;
  const toneSub = TONE_SUB[tone] || TONE_SUB['신뢰형'];
  const kw = (extra: string) => (place ? place.name + ' ' + (extra || '') : cat + ' ' + (extra || '')).trim();

  const cards: RawCard[] = [];

  cards.push({
    type: 'cover',
    kicker: place ? place.category || cat : cat,
    headline: splitTwo(t),
    big: '지금 정리',
    sub: '끝까지 보면 한눈에 들어와요 →',
    source: place ? place.roadAddress || place.address || '' : '',
    img: kw('대표 이미지'),
  });

  cards.push({
    type: 'big',
    kicker: 'POINT',
    headline: '먼저 결론부터',
    big: '핵심 3가지',
    sub: toneSub,
    source: '',
    img: kw('핵심 요약'),
  });

  const bodyTemplates: ((i: number) => RawCard)[] = [
    () => ({
      type: 'list',
      kicker: 'CHECK',
      headline: '이것부터\n확인하세요',
      items: [
        { num: '01', title: '무엇을 원하는지', desc: '목표를 한 문장으로 적어봅니다.' },
        { num: '02', title: '지금 상태 파악', desc: '현재 위치를 솔직하게 점검합니다.' },
        { num: '03', title: '가장 쉬운 한 걸음', desc: '오늘 바로 할 수 있는 것부터.' },
      ],
      source: '',
      img: kw('체크리스트'),
    }),
    (i) => ({
      type: 'point',
      kicker: 'STEP ' + i,
      big: 'STEP ' + i,
      headline: '한 번에\n하나씩',
      sub: '작게 시작할수록 오래 갑니다.',
      source: '',
      img: kw('단계'),
    }),
    () => ({
      type: 'list',
      kicker: 'TIP',
      headline: '자주 하는\n실수 3가지',
      items: [
        { num: '01', title: '너무 크게 시작', desc: '작게 시작해도 충분합니다.' },
        { num: '02', title: '남과 비교', desc: '어제의 나와만 비교하세요.' },
        { num: '03', title: '기록 안 함', desc: '기록이 방향을 만들어 줍니다.' },
      ],
      source: '',
      img: kw('실수'),
    }),
    (i) => ({
      type: 'point',
      kicker: 'KEEP',
      big: '꾸준히',
      headline: '멈추지만\n않으면',
      sub: '작은 반복이 결국 큰 차이를 만듭니다.',
      source: '',
      img: kw('꾸준함 ' + i),
    }),
  ];

  const bodyCount = n - 3;
  for (let i = 0; i < bodyCount; i++) {
    cards.push(bodyTemplates[i % bodyTemplates.length](i + 1));
  }

  cards.push({
    type: 'cta',
    kicker: '',
    headline: splitTwo(t) + '\n저장해두세요',
    sub: '나중에 다시 보면 도움이 됩니다',
    tag: '함께 보면 좋은 친구를 태그하세요',
    source: place ? place.name : '',
    img: kw('마무리'),
  });

  return cards.slice(0, n);
}
