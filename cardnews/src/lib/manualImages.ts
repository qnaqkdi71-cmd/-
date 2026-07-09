// 수동 업로드 이미지 저장소.
// 원본 프로토타입의 .image-slots.state.json 사이드카(호스트 브리지 전용)를
// 브라우저 IndexedDB로 대체 — dataURL이 커서 localStorage 5MB 한계를 피한다.
// "카드별 안정적 id(g{genId}-c{i})로 영속"이라는 계약은 그대로 유지.

const DB_NAME = 'cardnews_generator';
const STORE = 'manual-images';

let dbPromise: Promise<IDBDatabase> | null = null;

function openDb(): Promise<IDBDatabase> {
  if (!dbPromise) {
    dbPromise = new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, 1);
      req.onupgradeneeded = () => {
        if (!req.result.objectStoreNames.contains(STORE)) req.result.createObjectStore(STORE);
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }
  return dbPromise;
}

export async function getManualImage(id: string): Promise<string | null> {
  try {
    const db = await openDb();
    return await new Promise((resolve) => {
      const req = db.transaction(STORE, 'readonly').objectStore(STORE).get(id);
      req.onsuccess = () => resolve(typeof req.result === 'string' ? req.result : null);
      req.onerror = () => resolve(null);
    });
  } catch {
    return null;
  }
}

export async function setManualImage(id: string, dataUrl: string): Promise<void> {
  try {
    const db = await openDb();
    await new Promise<void>((resolve) => {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).put(dataUrl, id);
      tx.oncomplete = () => resolve();
      tx.onerror = () => resolve();
    });
  } catch {
    /* 저장 실패는 세션 내 표시만 유지 */
  }
}

export async function removeManualImage(id: string): Promise<void> {
  try {
    const db = await openDb();
    await new Promise<void>((resolve) => {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).delete(id);
      tx.oncomplete = () => resolve();
      tx.onerror = () => resolve();
    });
  } catch {
    /* noop */
  }
}

const MAX_DIM = 1200;
const ACCEPT = ['image/png', 'image/jpeg', 'image/webp', 'image/avif'];

/** 업로드 파일을 최대 1200px로 다운스케일한 WebP dataURL로 인코딩 */
export async function fileToDataUrl(file: File): Promise<string> {
  if (!ACCEPT.includes(file.type)) throw new Error('PNG, JPEG, WebP, AVIF 이미지만 넣을 수 있습니다.');
  const bitmap = await createImageBitmap(file);
  try {
    const scale = Math.min(1, MAX_DIM / Math.max(bitmap.width, bitmap.height));
    const w = Math.max(1, Math.round(bitmap.width * scale));
    const h = Math.max(1, Math.round(bitmap.height * scale));
    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    canvas.getContext('2d')!.drawImage(bitmap, 0, 0, w, h);
    return canvas.toDataURL('image/webp', 0.85);
  } finally {
    bitmap.close?.();
  }
}
