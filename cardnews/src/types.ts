import type { CSSProperties } from 'react';

export type Skin = 'minimal' | 'hand' | 'bold' | 'pop';
export type Tone = '신뢰형' | '친근형' | '트렌디형';
export type CardType = 'cover' | 'big' | 'list' | 'point' | 'cta';
export type ImgMode = 'none' | 'ai' | 'manual';

// text-wrap은 아직 csstype에 없을 수 있어 확장해 둔다 (React는 그대로 전달함)
export type Style = CSSProperties & { textWrap?: 'balance' | 'pretty' | 'wrap' };

export interface RawCardItem {
  num?: string;
  title?: string;
  desc?: string;
}

/** LLM이 반환하는 카드 원본 — 스타일링 전 상태로 저장·영속화된다 */
export interface RawCard {
  type?: string;
  kicker?: string;
  headline?: string;
  big?: string;
  sub?: string;
  items?: RawCardItem[];
  tag?: string; // cta 친구 태그 문구
  source?: string; // 출처/각주
  img?: string; // 배경 사진용 스톡포토식 검색어
}

export interface DecoratedItem {
  num: string;
  title: string;
  desc: string;
}

/** decorate()가 rawCard + 스킨으로부터 만들어내는 렌더링용 카드 */
export interface DecoratedCard {
  kicker: string;
  headline: string;
  big: string;
  sub: string;
  tag: string;
  source: string;
  handle: string;
  page: string;
  label: string;
  items: DecoratedItem[];
  isBigLike: boolean;
  isPoint: boolean;
  isList: boolean;
  isCta: boolean;
  hasFooter: boolean;
  imageOn: boolean;
  showAiImg: boolean;
  showManualImg: boolean;
  genImgUrl: string;
  slotId: string;
  imgHint: string;
  imgHintLabel: string;
  aiImgStyle: Style;
  scrimStyle: Style | null;
  wrapStyle: Style;
  contentStyle: Style;
  midStyle: Style;
  kickerStyle: Style;
  pageStyle: Style;
  headlineStyle: Style;
  bigStyle: Style;
  subStyle: Style;
  dividerStyle: Style;
  itemBgStyle: Style;
  itemNumStyle: Style;
  itemTitleStyle: Style;
  itemDescStyle: Style;
  tagStyle: Style;
  accentColor: Style;
  handleStyle: Style;
  sourceStyle: Style;
  footStyle: Style;
}

export const CATEGORIES = [
  '경제 · 투자',
  '음식 · 맛집',
  '연애 · 관계',
  '여행',
  '건강 · 운동',
  '커리어 · 직장',
  '자기계발',
  'IT · 테크',
  '패션 · 뷰티',
  '육아 · 교육',
  '심리',
  '취미 · 라이프',
] as const;

export const TONES: Tone[] = ['신뢰형', '친근형', '트렌디형'];

export const SKIN_DEFS: { id: Skin; name: string; desc: string }[] = [
  { id: 'minimal', name: '미니멀', desc: '애플풍 다크·라이트, 정보 신뢰형' },
  { id: 'hand', name: '손글씨 감성', desc: '모눈종이 + 손글씨, 공감형' },
  { id: 'bold', name: '볼드 매거진', desc: '초대형 타이포 + 포인트 컬러' },
  { id: 'pop', name: '팝 캐주얼', desc: '테두리 글씨 + 비비드, 핫플형' },
];
