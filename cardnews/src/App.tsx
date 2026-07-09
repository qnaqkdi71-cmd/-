import { useMemo } from 'react';
import { CardPreview } from './components/CardPreview';
import { EmptyState } from './components/EmptyState';
import { InputPanel } from './components/InputPanel';
import { useUnsplashUrls } from './hooks/useUnsplash';
import { decorateCards } from './lib/decorate';
import { useAppState } from './state/useAppState';

export default function App() {
  const app = useAppState();
  const imgUrls = useUnsplashUrls(app.rawCards, app.imgMode, app.genSeed, app.unsplashKey, app.category);

  const hasCards = !app.loading && app.rawCards.length > 0;

  const cards = useMemo(
    () =>
      decorateCards(app.rawCards, {
        skin: app.skin,
        category: app.category,
        handle: app.handle,
        unsplashKey: app.unsplashKey,
        imgMode: app.imgMode,
        genSeed: app.genSeed,
        imgUrls,
        genId: app.genId,
      }),
    [app.rawCards, app.skin, app.category, app.handle, app.unsplashKey, app.imgMode, app.genSeed, imgUrls, app.genId],
  );

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'flex-start',
        fontFamily: "'Pretendard', 'SF Pro Text', system-ui, -apple-system, sans-serif",
        color: '#1d1d1f',
      }}
    >
      <InputPanel
        skin={app.skin}
        category={app.category}
        title={app.title}
        notes={app.notes}
        tone={app.tone}
        count={app.count}
        handle={app.handle}
        unsplashKey={app.unsplashKey}
        loading={app.loading}
        error={app.error}
        hasCards={app.rawCards.length > 0}
        set={app.set}
        generate={app.generate}
      />

      <div
        style={{
          flex: 1,
          minWidth: 0,
          padding: '40px 44px',
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column',
          gap: 24,
        }}
      >
        {hasCards ? (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 16, flexWrap: 'wrap' }}>
              <div style={{ fontSize: 20, fontWeight: 600, letterSpacing: '-0.3px' }}>{app.resultTitle}</div>
              <div style={{ fontSize: 14, color: '#7a7a7a' }}>
                {app.rawCards.length}장 · 1080×1350 · {app.tone}
              </div>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, alignItems: 'flex-start' }}>
              {cards.map((card, i) => (
                <CardPreview key={app.genId + '-' + i} card={card} index={i} onSetMode={app.setImgMode} onBumpSeed={app.bumpSeed} />
              ))}
            </div>
          </>
        ) : (
          <EmptyState loading={app.loading} />
        )}
      </div>
    </div>
  );
}
