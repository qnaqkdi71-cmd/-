import { useEffect, useRef, useState } from 'react';
import { fileToDataUrl, getManualImage, removeManualImage, setManualImage } from '../lib/manualImages';

// 카드 안에서 scale(0.3204)로 축소 렌더되므로 내부 폰트/여백은 큰 값을 쓴다.
// id(g{genId}-c{i})가 영속 키 — 같은 생성 세트의 같은 카드는 새로고침 후에도 사진 유지.
export function ImageDropSlot({ id, placeholder }: { id: string; placeholder: string }) {
  const [url, setUrl] = useState<string | null>(null);
  const [over, setOver] = useState(false);
  const [err, setErr] = useState('');
  const depth = useRef(0);
  const gen = useRef(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let alive = true;
    setUrl(null);
    getManualImage(id).then((u) => {
      if (alive) setUrl(u);
    });
    return () => {
      alive = false;
    };
  }, [id]);

  async function ingest(file: File) {
    setErr('');
    const g = ++gen.current;
    try {
      const dataUrl = await fileToDataUrl(file);
      if (g !== gen.current) return; // 더 새 드롭이 이겼음
      setUrl(dataUrl);
      void setManualImage(id, dataUrl);
    } catch (e) {
      if (g !== gen.current) return;
      setErr(e instanceof Error ? e.message : '이미지를 읽지 못했습니다.');
      setTimeout(() => setErr(''), 3000);
    }
  }

  function clear() {
    gen.current++;
    setUrl(null);
    void removeManualImage(id);
  }

  return (
    <div
      onDragEnter={(e) => {
        e.preventDefault();
        e.stopPropagation();
        depth.current++;
        setOver(true);
      }}
      onDragOver={(e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
      }}
      onDragLeave={() => {
        if (--depth.current <= 0) {
          depth.current = 0;
          setOver(false);
        }
      }}
      onDrop={(e) => {
        e.preventDefault();
        e.stopPropagation();
        depth.current = 0;
        setOver(false);
        const f = e.dataTransfer?.files?.[0];
        if (f) void ingest(f);
      }}
      style={{ position: 'relative', width: '100%', height: '100%', background: '#d9d9de', overflow: 'hidden' }}
    >
      {url ? (
        <>
          <img
            src={url}
            alt=""
            draggable={false}
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block', userSelect: 'none' }}
          />
          <div style={{ position: 'absolute', top: 24, right: 24, display: 'flex', gap: 16 }}>
            <button
              onClick={() => inputRef.current?.click()}
              style={{
                fontSize: 30,
                padding: '14px 30px',
                borderRadius: 16,
                border: 'none',
                cursor: 'pointer',
                background: 'rgba(0,0,0,0.65)',
                color: '#ffffff',
              }}
            >
              교체
            </button>
            <button
              onClick={clear}
              style={{
                fontSize: 30,
                padding: '14px 30px',
                borderRadius: 16,
                border: 'none',
                cursor: 'pointer',
                background: 'rgba(0,0,0,0.65)',
                color: '#ffffff',
              }}
            >
              제거
            </button>
          </div>
        </>
      ) : (
        <div
          onClick={() => inputRef.current?.click()}
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 24,
            textAlign: 'center',
            padding: 60,
            boxSizing: 'border-box',
            cursor: 'pointer',
            userSelect: 'none',
            color: 'rgba(0,0,0,0.55)',
            border: over ? '6px solid #0071e3' : '6px dashed rgba(0,0,0,0.25)',
            background: over ? 'rgba(0,113,227,0.10)' : 'transparent',
          }}
        >
          <div style={{ fontSize: 100, lineHeight: 1 }}>🖼️</div>
          <div style={{ fontSize: 44, fontWeight: 600, lineHeight: 1.35 }}>{placeholder}</div>
          <div style={{ fontSize: 34 }}>
            드래그해서 놓거나 <u>클릭해서 선택</u>
          </div>
        </div>
      )}
      {!!err && (
        <div
          style={{
            position: 'absolute',
            left: 24,
            right: 24,
            bottom: 24,
            fontSize: 32,
            color: '#b3261e',
            background: 'rgba(255,255,255,0.85)',
            padding: '12px 18px',
            borderRadius: 14,
            pointerEvents: 'none',
          }}
        >
          {err}
        </div>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp,image/avif"
        hidden
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) void ingest(f);
          e.target.value = '';
        }}
      />
    </div>
  );
}
