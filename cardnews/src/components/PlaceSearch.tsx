import { useState } from 'react';
import type { AppConfig, Place, PlaceProvider, Style } from '../types';

const inputStyle: Style = {
  fontSize: 15,
  padding: '14px 16px',
  border: '1px solid #e0e0e0',
  borderRadius: 11,
  background: '#fafafc',
  color: '#1d1d1f',
  boxSizing: 'border-box',
  width: '100%',
};

function pill(active: boolean): Style {
  return {
    fontSize: 13,
    padding: '6px 12px',
    borderRadius: 9999,
    cursor: 'pointer',
    border: active ? '1px solid #0066cc' : '1px solid #e0e0e0',
    background: active ? '#0066cc' : '#fafafc',
    color: active ? '#ffffff' : '#333333',
    fontWeight: active ? 600 : 400,
  };
}

export interface PlaceSearchProps {
  config: AppConfig;
  place: Place | null;
  onSelect: (place: Place) => void;
  onClear: () => void;
}

export function PlaceSearch({ config, place, onSelect, onClear }: PlaceSearchProps) {
  const providers = config.placeProviders;
  const [provider, setProvider] = useState<PlaceProvider>(providers[0] || 'kakao');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Place[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function search() {
    const q = query.trim();
    if (!q) return;
    setLoading(true);
    setError('');
    setResults([]);
    try {
      const r = await fetch('/api/place?provider=' + provider + '&q=' + encodeURIComponent(q));
      const d = await r.json().catch(() => null);
      if (!r.ok) throw new Error((d && d.error) || 'HTTP ' + r.status);
      setResults(Array.isArray(d.results) ? d.results : []);
      if (!d.results || !d.results.length) setError('검색 결과가 없습니다.');
    } catch (e) {
      setError('검색 실패: ' + (e instanceof Error ? e.message : '오류'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ fontSize: 14, fontWeight: 600, color: '#333333' }}>
        가게 검색 <span style={{ fontWeight: 400, color: '#7a7a7a' }}>(선택 · 맛집/장소용)</span>
      </div>

      {place ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, background: '#eaf2fd', border: '1px solid #cfe1fb', borderRadius: 11, padding: '12px 14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 }}>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#0a4b9c' }}>{place.name}</div>
            <button onClick={onClear} style={{ fontSize: 12, color: '#0066cc', background: 'none', border: 'none', cursor: 'pointer', flex: 'none' }}>
              해제
            </button>
          </div>
          {!!place.category && <div style={{ fontSize: 12, color: '#5b7fae' }}>{place.category}</div>}
          <div style={{ fontSize: 12, color: '#5b7fae', lineHeight: 1.45 }}>{place.roadAddress || place.address}</div>
          {!!place.phone && <div style={{ fontSize: 12, color: '#5b7fae' }}>{place.phone}</div>}
        </div>
      ) : (
        <>
          {providers.length > 1 && (
            <div style={{ display: 'flex', gap: 6 }}>
              {providers.map((pr) => (
                <button key={pr} onClick={() => setProvider(pr)} style={pill(pr === provider)}>
                  {pr === 'kakao' ? '카카오' : '네이버'}
                </button>
              ))}
            </div>
          )}
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') void search();
              }}
              placeholder="상호 또는 지역+상호"
              style={inputStyle}
            />
            <button
              onClick={() => void search()}
              style={{
                fontSize: 14,
                fontWeight: 600,
                padding: '0 18px',
                borderRadius: 11,
                border: 'none',
                cursor: loading ? 'default' : 'pointer',
                background: loading ? '#7a7a7a' : '#0066cc',
                color: '#fff',
                flex: 'none',
              }}
            >
              {loading ? '…' : '검색'}
            </button>
          </div>
          {!!error && <div style={{ fontSize: 12, color: '#bf1a1a' }}>{error}</div>}
          {results.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 260, overflowY: 'auto' }}>
              {results.map((p, i) => (
                <button
                  key={i}
                  onClick={() => {
                    onSelect(p);
                    setResults([]);
                    setQuery('');
                  }}
                  style={{
                    textAlign: 'left',
                    padding: '10px 12px',
                    borderRadius: 9,
                    border: '1px solid #e0e0e0',
                    background: '#fafafc',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 3,
                  }}
                >
                  <div style={{ fontSize: 14, fontWeight: 600, color: '#1d1d1f' }}>{p.name}</div>
                  <div style={{ fontSize: 12, color: '#7a7a7a', lineHeight: 1.4 }}>
                    {[p.category, p.roadAddress || p.address].filter(Boolean).join(' · ')}
                  </div>
                </button>
              ))}
            </div>
          )}
          <div style={{ fontSize: 12, color: '#7a7a7a', lineHeight: 1.55 }}>
            가게를 선택하면 상호·주소·분류가 카피에 반영되고, 카드마다 <b>🗺 지도</b> 배경을 쓸 수 있습니다. 별점·리뷰는
            수집하지 않습니다.
          </div>
        </>
      )}
    </div>
  );
}
