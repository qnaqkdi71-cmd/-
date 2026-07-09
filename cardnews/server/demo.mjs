// 데모 카드 생성 — 서버에 ANTHROPIC_API_KEY가 없을 때 사용.
// 키 없이도 앱을 끝까지 써볼 수 있도록 입력(제목/분야/톤/가게)에 맞춰 카드 세트를 만든다.
// 원칙: 데모라도 구체적 통계·수치를 지어내지 않는다(정성적 문구만). 실제 생성은 LLM이 담당.

function splitTwo(s) {
  const t = String(s || '').trim();
  if (t.length <= 10) return t;
  const mid = Math.floor(t.length / 2);
  let cut = t.lastIndexOf(' ', mid);
  if (cut < 4) cut = t.indexOf(' ', mid);
  if (cut < 0) cut = mid;
  return t.slice(0, cut).trim() + '\n' + t.slice(cut).trim();
}

const TONE_SUB = {
  신뢰형: '핵심만 차분하게 정리했습니다.',
  친근형: '어렵지 않게, 하나씩 알려드릴게요.',
  트렌디형: '스압 없이 딱 필요한 것만.',
};

export function buildDemoCards({ category, title, tone, count, place }) {
  const n = Math.min(10, Math.max(6, Number(count) || 9));
  const cat = String(category || '카드뉴스');
  const t = String(title || '').trim() || cat;
  const toneSub = TONE_SUB[tone] || TONE_SUB['신뢰형'];
  const kw = (extra) => (place ? place.name + ' ' + (extra || '') : cat + ' ' + (extra || '')).trim();

  const cards = [];

  // 1) cover
  cards.push({
    type: 'cover',
    kicker: place ? place.category || cat : cat,
    headline: splitTwo(t),
    big: '지금 정리',
    sub: '끝까지 보면 한눈에 들어와요 →',
    source: place ? place.roadAddress || place.address || '' : '',
    img: kw('대표 이미지'),
  });

  // 2) big — 핵심 요약 (수치 대신 정성적 강조)
  cards.push({
    type: 'big',
    kicker: 'POINT',
    headline: '먼저 결론부터',
    big: '핵심 3가지',
    sub: toneSub,
    source: '',
    img: kw('핵심 요약'),
  });

  // 가운데를 point / list 로 채워 리듬을 만든다 (필요 개수만큼)
  const bodyTemplates = [
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

  const bodyCount = n - 3; // cover + big + cta 를 제외한 본문 수
  for (let i = 0; i < bodyCount; i++) {
    cards.push(bodyTemplates[i % bodyTemplates.length](i + 1));
  }

  // 마지막) cta
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
