// 프롬프트 계약 — 핸드오프 문서의 buildPrompt()를 그대로 유지한다.
// 카드 스키마/규칙 문구를 바꾸면 클라이언트의 parseCards 계약이 깨질 수 있음.

const TONE_GUIDE = {
  신뢰형: '차분한 리포트체. 과장 없이 데이터와 근거 중심. 문장 끝은 "~합니다" 체.',
  친근형: '다정하고 부드러운 존댓말. 친구가 알려주듯 쉽게.',
  트렌디형: 'Z세대 감성의 짧고 위트있는 문장. 단, 유행어 남발 금지.',
};

export function buildPrompt({ category, title, notes, tone, count }) {
  const safeTone = TONE_GUIDE[tone] ? tone : '신뢰형';
  const safeCount = Math.min(10, Math.max(6, Number(count) || 9));
  return [
    '당신은 인스타그램 카드뉴스 전문 카피라이터입니다. 아래 요청으로 캐러셀 카드뉴스 카피를 작성하세요.',
    '',
    '주제 분야: ' + String(category || ''),
    '제목(주제): ' + String(title || ''),
    '추가 요구사항: ' + (String(notes || '').trim() || '없음 — 알아서 최적의 구성을 만드세요'),
    '톤: ' + safeTone + ' — ' + TONE_GUIDE[safeTone],
    '카드 수: 정확히 ' + safeCount + '장',
    '',
    '반드시 아래 스키마의 순수 JSON만 출력하세요. 코드펜스, 설명 금지.',
    '{"cards":[ ... ]}',
    '',
    '카드 type 종류와 필드:',
    '- "cover" (반드시 1번째 카드): kicker(시리즈명, 짧게), headline(2줄 이내 훅), big(핵심 숫자나 7자 이내 초강력 훅), sub(스와이프 유도 문구, "→"로 끝내기), source(한 줄 각주 또는 "")',
    '- "big" (핵심 수치/사실 강조): kicker(예: DATA 01), headline, big(숫자나 7자 이내 키워드), sub(해석 한 문장), source(출처 또는 "")',
    '- "list" (항목 나열): kicker, headline, items(정확히 3개, 각 {num:"01"형식, title:12자 이내, desc:한 문장}), source("")',
    '- "point" (메시지 하나 강조): kicker, big(번호나 짧은 강조어), headline(8자 이내씩 2줄 이내), sub(2문장 이내), source("")',
    '- "cta" (반드시 마지막 카드): headline(여운 있는 마무리 문장, 3줄 이내), sub(저장 유도 문구), tag(친구 태그 유도 문구, "@@" 없이), source(출처 요약 또는 "")',
    '- 모든 카드에 "img" 필드 포함: 그 카드 내용에 어울리는 배경 사진을 스톡포토 검색어처럼 구체적으로 한 줄 묘사 (예: "하락하는 주식 차트를 보며 머리를 감싼 남성")',
    '',
    '규칙:',
    '1. 한 카드에 메시지 하나. 모바일에서 읽기 쉽게 짧게.',
    '2. big/list/point를 섞어 리듬을 만들 것. big 타입 최소 1장 포함.',
    '3. 확실히 아는 실제 통계만 출처와 함께 사용. 불확실하면 수치를 지어내지 말고 일반 표현으로.',
    '4. headline은 한 줄 최대 12자 내외, 줄바꿈은 \\n 사용.',
    '5. 초보자도 바로 이해되는 표현. 전문용어는 풀어서.',
    '6. 저장하고 싶어지는 실용 정보 위주.',
  ].join('\n');
}
