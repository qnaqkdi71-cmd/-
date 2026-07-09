# 카드뉴스 생성기 — 단일 컨테이너. 한 포트(8787)에서 사이트 + API를 서빙한다.
# 빌드 단계: 프론트(dist) 생성. 런타임 단계: 서버만 얇게 설치해 실행.

# ── build ──
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ── runtime ──
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8787
# 런타임 의존성만 (express + @anthropic-ai/sdk). react/vite 등 빌드 전용 제외.
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY server ./server
COPY --from=build /app/dist ./dist
EXPOSE 8787
CMD ["node", "server/index.mjs"]
