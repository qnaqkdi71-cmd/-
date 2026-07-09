import type { DecoratedCard } from '../types';
import { ImageDropSlot } from './ImageDropSlot';

/** 실제 1080×1350 카드 렌더 — 배경 레이어(z:0) 위에 콘텐츠 레이어(z:1)를 얹는다 */
export function CardView({ card }: { card: DecoratedCard }) {
  return (
    <div style={card.wrapStyle}>
      {card.showAiImg && (
        <>
          <div style={card.aiImgStyle} />
          {card.scrimStyle && <div style={card.scrimStyle} />}
        </>
      )}
      {card.showManualImg && (
        <>
          <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}>
            <ImageDropSlot id={card.slotId} placeholder={card.imgHint} />
          </div>
          {card.scrimStyle && <div style={card.scrimStyle} />}
        </>
      )}

      <div style={card.contentStyle}>
        {/* header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={card.kickerStyle}>{card.kicker}</div>
          <div style={card.pageStyle}>{card.page}</div>
        </div>

        {/* cover / big */}
        {card.isBigLike && (
          <div style={card.midStyle}>
            <div style={card.headlineStyle}>{card.headline}</div>
            <div style={card.bigStyle}>{card.big}</div>
            <div style={card.subStyle}>{card.sub}</div>
          </div>
        )}

        {/* point */}
        {card.isPoint && (
          <div style={card.midStyle}>
            <div style={card.bigStyle}>{card.big}</div>
            <div style={card.headlineStyle}>{card.headline}</div>
            <div style={card.dividerStyle} />
            <div style={card.subStyle}>{card.sub}</div>
          </div>
        )}

        {/* list */}
        {card.isList && (
          <>
            <div style={card.headlineStyle}>{card.headline}</div>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 36, minHeight: 0 }}>
              {card.items.map((item, j) => (
                <div key={j} style={card.itemBgStyle}>
                  <div style={card.itemNumStyle}>{item.num}</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 14, flex: 1, minWidth: 0 }}>
                    <div style={card.itemTitleStyle}>{item.title}</div>
                    <div style={card.itemDescStyle}>{item.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* cta */}
        {card.isCta && (
          <div style={card.midStyle}>
            <div style={card.headlineStyle}>{card.headline}</div>
            <div style={card.subStyle}>{card.sub}</div>
            <div style={card.tagStyle}>
              <span style={card.accentColor}>
                <b>@@</b>
              </span>{' '}
              {card.tag}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={card.handleStyle}>{card.handle}</div>
              <div style={card.sourceStyle}>{card.source}</div>
            </div>
          </div>
        )}

        {/* footer (non-cta) */}
        {card.hasFooter && <div style={card.footStyle}>{card.source}</div>}
      </div>
    </div>
  );
}
