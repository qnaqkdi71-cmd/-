import { useEffect, useMemo, useState } from 'react';
import { CardPreview } from './components/CardPreview';
import { EmptyState } from './components/EmptyState';
import { InputPanel } from './components/InputPanel';
import { useCardImages } from './hooks/useCardImages';
import { decorateCards } from './lib/decorate';
import { useAppState } from './state/useAppState';
import type { AppConfig } from './types';

export default function App() {
  const app = useAppState();
  const [config, setConfig] = useState<AppConfig | null>(null);

  // 서버에 어떤 기능이 켜져 있는지 물어 UI를 맞춘다 (가게 검색·지도 노출 여부)
  useEffect(() => {
    fetch('/api/config')
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => d && setConfig(d))
      .catch(() => setConfig({ placeProviders: [], staticMap: false, keylessPhoto: true, llm: false }));
  }, []);

  const bgUrls = useCardImages(app.rawCards, app.imgMode, app.genSeed, app.unsplashKey, app.category, app.place, config);

  const hasCards = !app.loading && app.rawCards.length > 0;
  const placeAvailable = !!app.place;

  const cards = useMemo(
    () =>
      decorateCards(app.rawCards, {
        skin: app.skin,
        category: app.category,
        handle: app.handle,
        unsplashKey: app.unsplashKey,
        imgMode: app.imgMode,
        genSeed: app.genSeed,
        bgUrls,
        genId: app.genId,
      }),
    [app.rawCards, app.skin, app.category, app.handle, app.unsplashKey, app.imgMode, app.genSeed, bgUrls, app.genId],
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
        config={config}
        place={app.place}
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
                {config && !config.llm ? ' · 데모' : ''}
              </div>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, alignItems: 'flex-start' }}>
              {cards.map((card, i) => (
                <CardPreview
                  key={app.genId + '-' + i}
                  card={card}
                  index={i}
                  placeAvailable={placeAvailable}
                  onSetMode={app.setImgMode}
                  onBumpSeed={app.bumpSeed}
                />
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
