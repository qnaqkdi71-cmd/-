// 자동 동기화 — 일정 간격으로 origin에서 fast-forward pull 한다.
// npm run dev:sync 로 dev 서버와 함께 돌리면, 원격에 새 커밋이 올라올 때마다
// 로컬이 알아서 받아오고 Vite HMR이 화면을 갱신한다. (수동 다운로드 불필요)
//
// 간격: SYNC_INTERVAL 초 (기본 10). 로컬에서 직접 수정 중이면 ff-only라 방해하지 않음.
import { execSync } from 'node:child_process';

const interval = (Number(process.env.SYNC_INTERVAL) || 10) * 1000;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

console.log(`[sync] origin 자동 동기화 시작 (${interval / 1000}s 간격). Ctrl+C로 종료.`);

for (;;) {
  try {
    const out = execSync('git pull --ff-only', { stdio: ['ignore', 'pipe', 'pipe'] }).toString();
    if (!/up to date|최신 상태/i.test(out)) {
      console.log('[sync] 새 변경을 받았습니다:\n' + out.trim());
    }
  } catch (e) {
    // 로컬에 커밋 안 된 변경이 있어 ff가 막히거나(직접 수정 중), 일시 네트워크 오류.
    const msg = (e && e.stderr && e.stderr.toString()) || (e && e.message) || '';
    if (msg.trim()) console.log('[sync] 건너뜀: ' + msg.trim().split('\n')[0]);
  }
  await sleep(interval);
}
