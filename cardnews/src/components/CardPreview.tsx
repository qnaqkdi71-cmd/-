import type { DecoratedCard, ImgMode, Style } from '../types';
import { CardView } from './CardView';

// 346/1080 ≈ 0.3204 — 실물 1080×1350 카드를 346×432 프레임에 축소
const SCALE = 0.3204;

function smallBtn(active: boolean): Style {
  return {
    fontSize: 11,
    padding: '4px 10px',
    borderRadius: 9999,
    cursor: 'pointer',
    border: '1px solid ' + (active ? '#0066cc' : '#e0e0e0'),
    background: active ? '#eaf2fd' : '#ffffff',
    color: active ? '#0066cc' : '#7a7a7a',
  };
}

export interface CardPreviewProps {
  card: DecoratedCard;
  index: number;
  placeAvailable: boolean;
  onSetMode: (index: number, mode: ImgMode) => void;
  onBumpSeed: (index: number) => void;
}

export function CardPreview({ card, index, placeAvailable, onSetMode, onBumpSeed }: CardPreviewProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, width: 346 }}>
      <div style={{ width: 346, height: 432, overflow: 'hidden', flex: 'none', borderRadius: 4, outline: '1px solid rgba(0,0,0,0.08)' }}>
        <div style={{ width: 1080, height: 1350, transform: `scale(${SCALE})`, transformOrigin: 'top left' }}>
          <CardView card={card} />
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, paddingLeft: 2, flexWrap: 'wrap' }}>
        <div style={{ fontSize: 12, color: '#7a7a7a', flex: 1, minWidth: 50 }}>{card.label}</div>
        <button onClick={() => onSetMode(index, 'ai')} style={smallBtn(card.isAi)}>
          주제 사진
        </button>
        {placeAvailable && (
          <button onClick={() => onSetMode(index, 'place')} style={smallBtn(card.isPlace)}>
            🗺 지도
          </button>
        )}
        <button onClick={() => onSetMode(index, 'manual')} style={smallBtn(card.showManualImg)}>
          직접 넣기
        </button>
        {card.imageOn && (
          <button onClick={() => onSetMode(index, 'none')} style={smallBtn(false)}>
            끄기
          </button>
        )}
      </div>
      {card.isAi && (
        <button onClick={() => onBumpSeed(index)} style={{ ...smallBtn(false), alignSelf: 'flex-start' }}>
          🔄 다른 이미지
        </button>
      )}
      {card.imageOn && (
        <div style={{ fontSize: 12, color: '#0066cc', lineHeight: 1.4, paddingLeft: 2 }}>{card.imgHintLabel}</div>
      )}
    </div>
  );
}
