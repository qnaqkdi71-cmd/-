import type { PersistedState } from '../state/useAppState';
import { CATEGORIES, SKIN_DEFS, TONES } from '../types';
import type { AppConfig, Place, Skin, Style, Tone } from '../types';
import { PlaceSearch } from './PlaceSearch';

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

const sectionLabel: Style = { fontSize: 14, fontWeight: 600, color: '#333333' };
const sectionHint: Style = { fontWeight: 400, color: '#7a7a7a' };
const section: Style = { display: 'flex', flexDirection: 'column', gap: 12 };

function chipStyle(selected: boolean): Style {
  return {
    fontSize: 14,
    padding: '9px 16px',
    borderRadius: 9999,
    cursor: 'pointer',
    border: selected ? '1px solid #0066cc' : '1px solid #e0e0e0',
    background: selected ? '#0066cc' : '#fafafc',
    color: selected ? '#ffffff' : '#333333',
    fontWeight: selected ? 600 : 400,
    lineHeight: 1.2,
  };
}

export interface InputPanelProps {
  skin: Skin;
  category: string;
  title: string;
  notes: string;
  tone: Tone;
  count: number;
  handle: string;
  unsplashKey: string;
  loading: boolean;
  error: string;
  hasCards: boolean;
  config: AppConfig | null;
  place: Place | null;
  set: <K extends keyof PersistedState>(key: K, value: PersistedState[K]) => void;
  generate: () => void;
}

export function InputPanel(p: InputPanelProps) {
  const generateLabel = p.loading ? '생성 중… (10~30초)' : p.hasCards ? '다시 생성하기' : '카드뉴스 생성하기';
  return (
    <div
      style={{
        width: 420,
        flex: 'none',
        position: 'sticky',
        top: 0,
        height: '100vh',
        overflowY: 'auto',
        background: '#ffffff',
        borderRight: '1px solid #e0e0e0',
        boxSizing: 'border-box',
        padding: '40px 36px',
        display: 'flex',
        flexDirection: 'column',
        gap: 30,
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ fontSize: 28, fontWeight: 600, letterSpacing: '-0.4px' }}>카드뉴스 생성기</div>
        <div style={{ fontSize: 15, color: '#7a7a7a', lineHeight: 1.5 }}>
          주제와 제목을 입력하면 인스타그램 캐러셀 카드뉴스를 자동으로 완성합니다.
        </div>
      </div>

      {/* 1. 디자인 스킨 */}
      <div style={section}>
        <div style={sectionLabel}>
          1 · 디자인 스킨 <span style={sectionHint}>(생성 후에도 변경 가능)</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {SKIN_DEFS.map((k) => {
            const sel = k.id === p.skin;
            return (
              <button
                key={k.id}
                onClick={() => p.set('skin', k.id)}
                style={{
                  textAlign: 'left',
                  padding: '12px 14px',
                  borderRadius: 11,
                  cursor: 'pointer',
                  border: sel ? '2px solid #0066cc' : '1px solid #e0e0e0',
                  background: '#fafafc',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 4,
                }}
              >
                <div style={{ fontSize: 14, fontWeight: 600, color: sel ? '#0066cc' : '#1d1d1f' }}>{k.name}</div>
                <div style={{ fontSize: 12, color: '#7a7a7a', lineHeight: 1.35, textAlign: 'left' }}>{k.desc}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. 주제 분야 */}
      <div style={section}>
        <div style={sectionLabel}>2 · 주제 분야</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {CATEGORIES.map((name) => (
            <button key={name} onClick={() => p.set('category', name)} style={chipStyle(name === p.category)}>
              {name}
            </button>
          ))}
        </div>
      </div>

      {/* 가게 검색 (검색 API가 설정된 경우에만) */}
      {p.config && p.config.placeProviders.length > 0 && (
        <PlaceSearch
          config={p.config}
          place={p.place}
          onSelect={(place) => p.set('place', place)}
          onClear={() => p.set('place', null)}
        />
      )}

      {/* 3. 제목 */}
      <div style={section}>
        <div style={sectionLabel}>3 · 제목 (주제)</div>
        <input
          value={p.title}
          onChange={(e) => p.set('title', e.target.value)}
          placeholder="예: 초보 투자자가 첫 달에 하는 실수 7가지"
          style={inputStyle}
        />
      </div>

      {/* 4. 내용 · 요구사항 */}
      <div style={section}>
        <div style={sectionLabel}>
          4 · 내용 · 요구사항 <span style={sectionHint}>(선택)</span>
        </div>
        <textarea
          value={p.notes}
          onChange={(e) => p.set('notes', e.target.value)}
          rows={4}
          placeholder="꼭 들어갈 내용, 수치, 강조하고 싶은 메시지 등. 비워두면 알아서 구성합니다."
          style={{ ...inputStyle, resize: 'vertical', lineHeight: 1.5 }}
        />
      </div>

      {/* 5. 카드 수 */}
      <div style={section}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <div style={sectionLabel}>5 · 카드 수</div>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#0066cc' }}>{p.count}장</div>
        </div>
        <input
          type="range"
          min={6}
          max={10}
          step={1}
          value={p.count}
          onChange={(e) => p.set('count', Number(e.target.value))}
          style={{ width: '100%' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#7a7a7a' }}>
          <span>6장</span>
          <span>10장</span>
        </div>
      </div>

      {/* 6. 톤 */}
      <div style={section}>
        <div style={sectionLabel}>6 · 톤</div>
        <div style={{ display: 'flex', gap: 8 }}>
          {TONES.map((name) => (
            <button
              key={name}
              onClick={() => p.set('tone', name)}
              style={{ ...chipStyle(name === p.tone), flex: 1, textAlign: 'center' }}
            >
              {name}
            </button>
          ))}
        </div>
      </div>

      {/* 7. 계정 핸들 */}
      <div style={section}>
        <div style={sectionLabel}>7 · 계정 핸들</div>
        <input value={p.handle} onChange={(e) => p.set('handle', e.target.value)} style={inputStyle} />
      </div>

      {/* 8. Unsplash 키 */}
      <div style={section}>
        <div style={sectionLabel}>
          8 · Unsplash 키 <span style={sectionHint}>(선택 · 실사진)</span>
        </div>
        <input
          value={p.unsplashKey}
          onChange={(e) => p.set('unsplashKey', e.target.value)}
          placeholder="Access Key 붙여넣기"
          style={inputStyle}
        />
        <div style={{ fontSize: 12, color: '#7a7a7a', lineHeight: 1.55 }}>
          비워두면 예시 사진이 즉시 뜹니다. 키를 넣으면 카드 키워드에 맞는 <b>실제 사진</b>으로 자동 교체됩니다.{' '}
          <a href="https://unsplash.com/developers" target="_blank" rel="noopener noreferrer">
            무료 키 발급 →
          </a>
        </div>
      </div>

      <button
        onClick={p.generate}
        style={{
          fontSize: 17,
          fontWeight: 600,
          padding: '16px 24px',
          borderRadius: 9999,
          border: 'none',
          cursor: p.loading ? 'default' : 'pointer',
          background: p.loading ? '#7a7a7a' : '#0066cc',
          color: '#ffffff',
          width: '100%',
        }}
      >
        {generateLabel}
      </button>

      {!!p.error && (
        <div style={{ fontSize: 14, color: '#bf1a1a', lineHeight: 1.5, background: '#fdf1f1', borderRadius: 11, padding: '14px 16px' }}>
          {p.error}
        </div>
      )}

      {p.config && !p.config.llm && (
        <div style={{ fontSize: 12.5, color: '#8a6d1a', lineHeight: 1.55, background: '#fdf6e3', border: '1px solid #f0e2b8', borderRadius: 11, padding: '12px 14px' }}>
          <b>데모 모드</b> · 서버에 API 키가 없어 예시 카드로 생성됩니다. 레이아웃·스킨·이미지 기능은 그대로 써볼 수
          있어요. 서버 환경변수 <code>ANTHROPIC_API_KEY</code>를 넣으면 실제 AI 생성으로 바뀝니다.
        </div>
      )}

      <div style={{ fontSize: 12, color: '#7a7a7a', lineHeight: 1.6, borderTop: '1px solid #e0e0e0', paddingTop: 20 }}>
        1080×1350 (4:5) · 카드마다 "사진 배경"을 켜고 이미지를 드래그해서 넣을 수 있습니다. AI가 카드별 추천 이미지를
        제안합니다.
      </div>
    </div>
  );
}
