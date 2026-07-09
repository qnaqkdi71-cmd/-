import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { viteSingleFile } from 'vite-plugin-singlefile';

// SINGLE_FILE=1 이면 모든 JS/CSS를 index.html 한 파일에 인라인한다.
// → 더블클릭만으로 브라우저에서 열리는 "파일 하나짜리 프로그램"을 만든다.
const single = !!process.env.SINGLE_FILE;

export default defineConfig({
  plugins: [react(), ...(single ? [viteSingleFile()] : [])],
  server: {
    proxy: {
      '/api': 'http://localhost:8787',
    },
  },
});
