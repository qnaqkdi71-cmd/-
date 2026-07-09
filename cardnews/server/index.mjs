// 카드뉴스 생성기 서버 — LLM API 키는 여기(서버)에만 존재한다.
// POST /api/generate : { category, title, notes, tone, count } → { text } (LLM 원문)
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import express from 'express';
import Anthropic from '@anthropic-ai/sdk';
import { buildPrompt } from './prompt.mjs';

const PORT = Number(process.env.PORT || 8787);
// 핸드오프 문서가 지정한 모델. CARDNEWS_MODEL 환경변수로 교체 가능.
const MODEL = process.env.CARDNEWS_MODEL || 'claude-sonnet-4-5';

const app = express();
app.use(express.json({ limit: '1mb' }));

app.post('/api/generate', async (req, res) => {
  if (!process.env.ANTHROPIC_API_KEY) {
    res.status(500).json({ error: '서버에 ANTHROPIC_API_KEY가 설정되지 않았습니다.' });
    return;
  }
  const { category, title, notes, tone, count } = req.body || {};
  if (typeof title !== 'string' || !title.trim()) {
    res.status(400).json({ error: '제목(주제)이 필요합니다.' });
    return;
  }

  const client = new Anthropic();
  try {
    const response = await client.messages.create({
      model: MODEL,
      max_tokens: 8000,
      messages: [{ role: 'user', content: buildPrompt({ category, title, notes, tone, count }) }],
    });
    const text = response.content
      .filter((block) => block.type === 'text')
      .map((block) => block.text)
      .join('');
    res.json({ text });
  } catch (err) {
    if (err instanceof Anthropic.AuthenticationError) {
      res.status(500).json({ error: 'LLM API 키 인증에 실패했습니다.' });
    } else if (err instanceof Anthropic.RateLimitError) {
      res.status(429).json({ error: '요청이 많습니다. 잠시 후 다시 시도해주세요.' });
    } else if (err instanceof Anthropic.APIError) {
      res.status(502).json({ error: 'LLM 호출 실패 (' + (err.status ?? '네트워크') + ')' });
    } else {
      console.error('generate failed:', err);
      res.status(502).json({ error: 'LLM 호출에 실패했습니다.' });
    }
  }
});

// 프로덕션: 빌드 산출물 정적 서빙 (dist가 없으면 무시됨)
const dist = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'dist');
app.use(express.static(dist));
app.get(/^\/(?!api\/).*/, (_req, res, next) => {
  res.sendFile(path.join(dist, 'index.html'), (err) => err && next());
});

app.listen(PORT, () => {
  console.log(`cardnews server listening on http://localhost:${PORT} (model: ${MODEL})`);
});
