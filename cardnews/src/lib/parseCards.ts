import type { RawCard } from '../types';

/** LLM 응답 텍스트에서 첫 {...} JSON 블록을 추출해 cards 배열을 얻는다 */
export function parseCards(text: string): RawCard[] {
  const m = String(text).match(/\{[\s\S]*\}/);
  if (!m) throw new Error('응답 형식 오류');
  const json = JSON.parse(m[0]);
  if (!Array.isArray(json.cards) || json.cards.length === 0) throw new Error('카드 없음');
  return json.cards as RawCard[];
}
