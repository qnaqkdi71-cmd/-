// 스킨 스타일링 엔진 — 핸드오프 문서 부록 A의 decorate()를 그대로 포팅.
// 카피(rawCards)는 원본 그대로 두고, 렌더마다 이 함수가 스킨 스타일을 다시 입힌다.
// 스킨 전환 시 재생성 없이 즉시 갈아입는 것이 이 구조의 핵심.
import type { DecoratedCard, ImgMode, RawCard, Skin, Style } from '../types';

export interface DecorateCtx {
  skin: Skin;
  category: string;
  handle: string;
  unsplashKey: string;
  imgMode: Record<number, ImgMode>;
  genSeed: Record<number, number>;
  // 카드별로 해석된 배경 URL(주제 사진/지도). 없으면 picsum 예시로 폴백.
  bgUrls: Record<number, string>;
  genId: number;
}

export function hexToRgba(hex: string, a: number): string {
  const n = parseInt(String(hex).replace('#', ''), 16);
  return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')';
}

/** pop 스킨의 두꺼운 글자 외곽선 — 16 + 8방향 text-shadow 스택 */
export function outline(color: string, w: number): string {
  const arr: string[] = [];
  for (let a = 0; a < 16; a++) {
    const r = (a * Math.PI) / 8;
    arr.push((Math.cos(r) * w).toFixed(1) + 'px ' + (Math.sin(r) * w).toFixed(1) + 'px 0 ' + color);
  }
  for (let a = 0; a < 8; a++) {
    const r = (a * Math.PI) / 4;
    const h = w * 0.55;
    arr.push((Math.cos(r) * h).toFixed(1) + 'px ' + (Math.sin(r) * h).toFixed(1) + 'px 0 ' + color);
  }
  return arr.join(', ');
}

interface SkinStyles {
  tint?: string;
  wrapStyle: Style;
  midStyle: Style;
  kickerStyle: Style;
  pageStyle: Style;
  headlineStyle: Style;
  bigStyle: Style;
  subStyle: Style;
  dividerStyle: Style;
  itemBgStyle: Style;
  itemNumStyle: Style;
  itemTitleStyle: Style;
  itemDescStyle: Style;
  tagStyle: Style;
  accentColor: Style;
  handleStyle: Style;
  sourceStyle: Style;
  footStyle: Style;
  scrimStyle?: Style;
}

const TYPE_LABEL: Record<string, string> = {
  cover: '커버',
  big: '데이터',
  list: '리스트',
  point: '포인트',
  cta: 'CTA',
};

const PRE_LINE_KEYS = [
  'headlineStyle',
  'bigStyle',
  'subStyle',
  'itemTitleStyle',
  'itemDescStyle',
  'tagStyle',
  'sourceStyle',
  'footStyle',
] as const;

export function decorateCards(rawCards: RawCard[], ctx: DecorateCtx): DecoratedCard[] {
  const skin = ctx.skin || 'minimal';
  const total = rawCards.length;

  return rawCards.map((c, i) => {
    const type = ['cover', 'big', 'list', 'point', 'cta'].includes(c.type ?? '')
      ? (c.type as 'cover' | 'big' | 'list' | 'point' | 'cta')
      : 'point';
    const nl = (s: unknown) => String(s == null ? '' : s);
    const mode: ImgMode = ctx.imgMode[i] || 'none';
    const imageOn = mode !== 'none';
    const seed = ctx.genSeed[i] || 1;
    const imgKw = nl(c.img) || ctx.category + ' 관련 사진';
    // 키워드+시드의 결정적 해시 → 같은 카드는 항상 같은 예시 사진, 🔄가 seed를 올림
    let ihash = 0;
    const istr = imgKw + '|' + seed;
    for (let h = 0; h < istr.length; h++) {
      ihash = (ihash * 31 + istr.charCodeAt(h)) % 100000;
    }
    const hasKey = ctx.unsplashKey.trim().length > 0;
    // 해석된 URL(주제 사진 or 지도)이 있으면 사용, 없으면 picsum 예시로 폴백.
    const genImgUrl = ctx.bgUrls[i] || 'https://picsum.photos/seed/' + ihash + '/1080/1350';
    const isAi = mode === 'ai';
    const isPlace = mode === 'place';

    let sub = nl(c.sub);
    if (skin === 'bold' && sub && (type === 'cover' || type === 'big' || type === 'point')) {
      sub = ': ' + sub;
    }

    const base = {
      kicker: nl(c.kicker) || (type === 'cta' ? '' : 'CARD NEWS'),
      headline: nl(c.headline),
      big: nl(c.big),
      sub,
      tag: nl(c.tag) || '함께 볼 친구를 태그하세요',
      source: nl(c.source),
      handle: ctx.handle || '@your_account',
      page: i + 1 + '/' + total,
      label: i + 1 + ' · ' + (TYPE_LABEL[type] || type),
      isBigLike: type === 'cover' || type === 'big',
      isPoint: type === 'point',
      isList: type === 'list',
      isCta: type === 'cta',
      hasFooter: type !== 'cta' && !!nl(c.source),
      items: (Array.isArray(c.items) ? c.items : []).slice(0, 3).map((it, j) => ({
        num: nl(it.num) || '0' + (j + 1),
        title: nl(it.title),
        desc: nl(it.desc),
      })),
      imageOn,
      isAi,
      isPlace,
      showBgImg: isAi || isPlace,
      showManualImg: mode === 'manual',
      genImgUrl,
      slotId: 'g' + (ctx.genId || 0) + '-c' + i,
      imgHint: nl(c.img) ? '이미지: ' + nl(c.img) : '이미지를 드래그해서 넣으세요',
      imgHintLabel: isPlace
        ? '가게 위치 지도'
        : (hasKey ? '실사진 키워드: ' : '주제 사진: ') + (nl(c.img) || '내용에 어울리는 사진'),
      aiImgStyle: {
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        backgroundColor: '#d9d9de',
        backgroundImage: 'url("' + genImgUrl + '")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      } as Style,
    };

    const wrapBase: Style = {
      width: 1080,
      height: 1350,
      display: 'flex',
      flexDirection: 'column',
      padding: '90px 88px',
      boxSizing: 'border-box',
    };
    const mid: Style = {
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      gap: 48,
      minHeight: 0,
    };
    let S: SkinStyles;

    if (skin === 'hand') {
      const themes = [
        { bg: '#f7e9d7', line: 'rgba(202,150,104,0.45)', ink: '#4a3b2f', muted: '#8a7563', accent: '#c95f3d', item: 'rgba(255,255,255,0.62)' },
        { bg: '#fbe7ea', line: 'rgba(222,145,160,0.4)', ink: '#503741', muted: '#96707d', accent: '#cf5f7a', item: 'rgba(255,255,255,0.62)' },
        { bg: '#fbf4dd', line: 'rgba(196,168,106,0.45)', ink: '#4c4331', muted: '#8b7f5f', accent: '#a97f24', item: 'rgba(255,255,255,0.68)' },
      ];
      const t = type === 'cover' ? themes[0] : type === 'cta' ? themes[1] : themes[i % 3];
      S = {
        tint: t.bg,
        wrapStyle: {
          ...wrapBase,
          background: t.bg,
          color: t.ink,
          textAlign: 'center',
          backgroundImage:
            'linear-gradient(' + t.line + ' 2px, transparent 2px), linear-gradient(90deg, ' + t.line + ' 2px, transparent 2px)',
          backgroundSize: '54px 54px',
          fontFamily: "'Gaegu','Pretendard',sans-serif",
        },
        midStyle: { ...mid, alignItems: 'center', gap: 44 },
        kickerStyle: { fontSize: 38, fontWeight: 700, color: t.accent, letterSpacing: '2px' },
        pageStyle: { fontSize: 32, color: 'rgba(0,0,0,0.35)' },
        headlineStyle:
          type === 'list'
            ? { fontSize: 80, fontWeight: 700, lineHeight: 1.3, marginTop: 48, textWrap: 'balance' }
            : { fontSize: 100, fontWeight: 700, lineHeight: 1.3, textWrap: 'balance' },
        bigStyle:
          type === 'point'
            ? { fontSize: 130, fontWeight: 700, lineHeight: 1.1, color: t.accent }
            : { fontSize: 160, fontWeight: 700, lineHeight: 1.15, color: t.accent, textWrap: 'balance' },
        subStyle: { fontSize: 54, lineHeight: 1.5, color: t.muted, textWrap: 'pretty' },
        dividerStyle: { width: 150, height: 8, background: t.accent, borderRadius: 8 },
        itemBgStyle: { background: t.item, borderRadius: 28, padding: '40px 48px', display: 'flex', gap: 36, alignItems: 'flex-start', textAlign: 'left', width: '100%', boxSizing: 'border-box' },
        itemNumStyle: { fontSize: 56, fontWeight: 700, lineHeight: 1, flex: 'none', color: t.accent },
        itemTitleStyle: { fontSize: 52, fontWeight: 700, lineHeight: 1.25 },
        itemDescStyle: { fontSize: 40, lineHeight: 1.45, color: t.muted },
        tagStyle: { fontSize: 46, lineHeight: 1.4 },
        accentColor: { color: t.accent },
        handleStyle: { fontSize: 40, fontWeight: 700 },
        sourceStyle: { fontSize: 26, color: 'rgba(0,0,0,0.4)', lineHeight: 1.45 },
        footStyle: { fontSize: 28, color: 'rgba(0,0,0,0.4)', lineHeight: 1.4 },
      };
    } else if (skin === 'bold') {
      const dark = { bg: '#121212', ink: '#ffffff', muted: '#a8a8a8', accent: '#35d07f', item: '#1f1f1f', pg: '#6a6a6a' };
      const light = { bg: '#ffffff', ink: '#111111', muted: '#555555', accent: '#0e8a48', item: '#f4f4f2', pg: '#9a9a9a' };
      const stone = { bg: '#f2f2ef', ink: '#111111', muted: '#555555', accent: '#0e8a48', item: '#ffffff', pg: '#9a9a9a' };
      const t = type === 'cover' || type === 'cta' ? dark : [light, dark, stone][i % 3];
      S = {
        wrapStyle: { ...wrapBase, background: t.bg, color: t.ink, fontFamily: "'Pretendard',system-ui,-apple-system,sans-serif" },
        midStyle: { ...mid, gap: 40 },
        kickerStyle: { fontSize: 28, fontWeight: 800, color: t.accent, letterSpacing: '5px' },
        pageStyle: { fontSize: 28, fontWeight: 600, color: t.pg },
        headlineStyle:
          type === 'list'
            ? { fontSize: 82, fontWeight: 800, lineHeight: 1.08, letterSpacing: '-2.5px', marginTop: 56, textWrap: 'balance' }
            : type === 'point'
              ? { fontSize: 104, fontWeight: 800, lineHeight: 1.06, letterSpacing: '-3px', textWrap: 'balance' }
              : { fontSize: 92, fontWeight: 800, lineHeight: 1.08, letterSpacing: '-2.5px', textWrap: 'balance' },
        bigStyle:
          type === 'point'
            ? { fontSize: 150, fontWeight: 800, letterSpacing: '-5px', lineHeight: 1, color: t.accent }
            : { fontSize: 200, fontWeight: 800, letterSpacing: '-7px', lineHeight: 1, color: t.accent, textWrap: 'balance' },
        subStyle: { fontSize: 40, lineHeight: 1.5, color: t.muted, textWrap: 'pretty' },
        dividerStyle: { width: 120, height: 10, background: t.accent },
        itemBgStyle: { background: t.item, borderRadius: 8, padding: '42px 48px', display: 'flex', gap: 40, alignItems: 'flex-start' },
        itemNumStyle: { fontSize: 50, fontWeight: 800, color: t.accent, flex: 'none', lineHeight: 1 },
        itemTitleStyle: { fontSize: 48, fontWeight: 800, letterSpacing: '-1px', lineHeight: 1.2 },
        itemDescStyle: { fontSize: 34, lineHeight: 1.45, color: t.muted },
        tagStyle: { fontSize: 42, lineHeight: 1.4 },
        accentColor: { color: t.accent },
        handleStyle: { fontSize: 34, fontWeight: 800 },
        sourceStyle: { fontSize: 24, color: t.pg, lineHeight: 1.45 },
        footStyle: { fontSize: 26, color: t.pg, lineHeight: 1.4 },
      };
    } else if (skin === 'pop') {
      const themes = [
        { bg: '#79c7f0', stroke: '#1d4e79' },
        { bg: '#ffd23e', stroke: '#8a5400' },
        { bg: '#8fdcc0', stroke: '#1c6b4f' },
        { bg: '#ff9db0', stroke: '#93283f' },
      ];
      const t = type === 'cover' ? themes[0] : type === 'cta' ? themes[3] : themes[(i + 1) % 4];
      const ol = (w: number) => outline(t.stroke, w);
      S = {
        tint: t.bg,
        wrapStyle: { ...wrapBase, background: t.bg, color: '#333333', textAlign: 'center', fontFamily: "'Jua','Pretendard',sans-serif" },
        midStyle: { ...mid, alignItems: 'center', gap: 44 },
        kickerStyle: { fontSize: 34, color: '#ffffff', textShadow: ol(6), letterSpacing: '2px' },
        pageStyle: { fontSize: 30, color: 'rgba(0,0,0,0.35)' },
        headlineStyle:
          type === 'list'
            ? { fontSize: 84, lineHeight: 1.3, color: '#ffffff', textShadow: ol(10), marginTop: 48 }
            : { fontSize: 108, lineHeight: 1.3, color: '#ffffff', textShadow: ol(12) },
        bigStyle: { fontSize: type === 'point' ? 140 : 180, lineHeight: 1.15, color: '#ffffff', textShadow: ol(14) },
        subStyle: { fontSize: 48, lineHeight: 1.5, color: '#3f3f3f', background: 'rgba(255,255,255,0.75)', borderRadius: 20, padding: '18px 36px' },
        dividerStyle: { width: 150, height: 10, background: '#ffffff', borderRadius: 10 },
        itemBgStyle: { background: 'rgba(255,255,255,0.88)', borderRadius: 28, padding: '40px 48px', display: 'flex', gap: 36, alignItems: 'flex-start', textAlign: 'left' },
        itemNumStyle: { fontSize: 54, color: t.stroke, flex: 'none', lineHeight: 1 },
        itemTitleStyle: { fontSize: 50, lineHeight: 1.25, color: '#333333' },
        itemDescStyle: { fontSize: 36, lineHeight: 1.45, color: '#666666' },
        tagStyle: { fontSize: 46, color: '#3f3f3f' },
        accentColor: { color: t.stroke },
        handleStyle: { fontSize: 38, color: '#ffffff', textShadow: ol(6) },
        sourceStyle: { fontSize: 26, color: 'rgba(0,0,0,0.45)', lineHeight: 1.45 },
        footStyle: { fontSize: 28, color: 'rgba(0,0,0,0.45)', lineHeight: 1.4 },
      };
    } else {
      // minimal (기본)
      const themes = {
        dark: { bg: '#272729', fg: '#ffffff', muted: '#cccccc', accent: '#2997ff', item: '#3a3a3c' },
        dark2: { bg: '#2a2a2c', fg: '#ffffff', muted: '#cccccc', accent: '#2997ff', item: '#3a3a3c' },
        light: { bg: '#ffffff', fg: '#1d1d1f', muted: '#333333', accent: '#0066cc', item: '#f5f5f7' },
        parch: { bg: '#f5f5f7', fg: '#1d1d1f', muted: '#333333', accent: '#0066cc', item: '#ffffff' },
      };
      const t = type === 'cover' || type === 'cta' ? themes.dark : [themes.light, themes.dark2, themes.parch][i % 3];
      S = {
        wrapStyle: { ...wrapBase, background: t.bg, color: t.fg, fontFamily: "'Pretendard','SF Pro Display',system-ui,-apple-system,sans-serif" },
        midStyle: mid,
        kickerStyle: { fontSize: 30, fontWeight: 600, color: t.accent, letterSpacing: '1px' },
        pageStyle: { fontSize: 30, color: '#7a7a7a' },
        headlineStyle:
          type === 'list'
            ? { fontSize: 68, fontWeight: 600, lineHeight: 1.16, letterSpacing: '-1.2px', marginTop: 56, textWrap: 'pretty' }
            : type === 'point'
              ? { fontSize: 96, fontWeight: 600, lineHeight: 1.14, letterSpacing: '-2px', textWrap: 'pretty' }
              : type === 'cta'
                ? { fontSize: 92, fontWeight: 600, lineHeight: 1.15, letterSpacing: '-2px', textWrap: 'pretty' }
                : { fontSize: 78, fontWeight: 600, lineHeight: 1.16, letterSpacing: '-1.5px', textWrap: 'pretty' },
        bigStyle:
          type === 'point'
            ? { fontSize: 140, fontWeight: 700, lineHeight: 1, letterSpacing: '-4px', color: t.accent }
            : { fontSize: 185, fontWeight: 700, lineHeight: 1.05, letterSpacing: '-6px', color: t.accent },
        subStyle: { fontSize: type === 'point' ? 48 : type === 'cta' ? 46 : 44, lineHeight: 1.47, color: t.muted, letterSpacing: '-0.4px', textWrap: 'pretty' },
        dividerStyle: { width: 110, height: 6, background: t.accent },
        itemBgStyle: { background: t.item, borderRadius: 18, padding: '42px 48px', display: 'flex', gap: 40, alignItems: 'flex-start' },
        itemNumStyle: { fontSize: 54, fontWeight: 700, lineHeight: 1, flex: 'none', color: t.accent },
        itemTitleStyle: { fontSize: 48, fontWeight: 600, letterSpacing: '-0.8px', lineHeight: 1.2 },
        itemDescStyle: { fontSize: 34, lineHeight: 1.45, color: t.muted },
        tagStyle: { fontSize: 42, lineHeight: 1.4 },
        accentColor: { color: t.accent },
        handleStyle: { fontSize: 34, fontWeight: 600 },
        sourceStyle: { fontSize: 24, color: '#7a7a7a', lineHeight: 1.45 },
        footStyle: { fontSize: 26, color: '#7a7a7a', lineHeight: 1.4 },
      };
    }

    // 텍스트 처리: 카피 요소만 \n 보존(pre-line), 킥커/페이지는 한 줄 고정
    S.kickerStyle = { lineHeight: 1.2, ...S.kickerStyle, whiteSpace: 'nowrap' };
    S.pageStyle = { lineHeight: 1.2, ...S.pageStyle, whiteSpace: 'nowrap' };
    PRE_LINE_KEYS.forEach((k) => {
      S[k] = { ...S[k], whiteSpace: 'pre-line' };
    });

    // 사진 배경 모드 오버라이드
    if (imageOn) {
      const pmAccent = skin === 'bold' ? '#35d07f' : '#2997ff';
      const sh = '0 4px 28px rgba(0,0,0,0.55)';
      if (skin !== 'pop' && skin !== 'hand') {
        // minimal/bold: 다크 스크림 + 텍스트 흰색 전환
        S.wrapStyle = { ...S.wrapStyle, color: '#ffffff' };
        S.kickerStyle = { ...S.kickerStyle, color: pmAccent, textShadow: sh };
        S.pageStyle = { ...S.pageStyle, color: 'rgba(255,255,255,0.8)' };
        S.headlineStyle = { ...S.headlineStyle, color: '#ffffff', textShadow: sh };
        S.bigStyle = { ...S.bigStyle, color: pmAccent, textShadow: sh };
        S.subStyle = { ...S.subStyle, color: 'rgba(255,255,255,0.92)', textShadow: sh, background: 'none' };
        S.dividerStyle = { ...S.dividerStyle, background: pmAccent };
        S.accentColor = { color: pmAccent };
        S.itemBgStyle = { ...S.itemBgStyle, background: 'rgba(15,15,15,0.55)' };
        S.itemNumStyle = { ...S.itemNumStyle, color: pmAccent };
        S.itemTitleStyle = { ...S.itemTitleStyle, color: '#ffffff' };
        S.itemDescStyle = { ...S.itemDescStyle, color: 'rgba(255,255,255,0.88)' };
        S.tagStyle = { ...S.tagStyle, color: '#ffffff', textShadow: sh };
        S.handleStyle = { ...S.handleStyle, color: '#ffffff', textShadow: sh };
        S.sourceStyle = { ...S.sourceStyle, color: 'rgba(255,255,255,0.78)' };
        S.footStyle = { ...S.footStyle, color: 'rgba(255,255,255,0.78)' };
      }
      const scrimBase: Style = { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: 0, pointerEvents: 'none' };
      if (skin === 'hand' || skin === 'pop') {
        // 컬러 틴트 스크림: 사진이 테마색 사이로 은은하게 비침
        const tint = S.tint || '#f5f5f7';
        const strong = skin === 'hand' ? 0.9 : 0.82;
        const soft = skin === 'hand' ? 0.74 : 0.6;
        S.scrimStyle = {
          ...scrimBase,
          background:
            'linear-gradient(180deg, ' + hexToRgba(tint, strong) + ', ' + hexToRgba(tint, soft) + ' 45%, ' + hexToRgba(tint, strong) + ')',
        };
      } else {
        S.scrimStyle = {
          ...scrimBase,
          background: 'linear-gradient(180deg, rgba(0,0,0,0.55), rgba(0,0,0,0.35) 45%, rgba(0,0,0,0.62))',
        };
      }
    }

    // 레이어 분리: wrap = 풀블리드 배경 호스트, content = 패딩 입은 콘텐츠 층
    const contentStyle: Style = {
      position: 'relative',
      zIndex: 1,
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      padding: S.wrapStyle.padding as string,
      boxSizing: 'border-box',
      pointerEvents: 'none',
    };
    S.wrapStyle = { ...S.wrapStyle, padding: 0, display: 'block', position: 'relative', overflow: 'hidden' };

    const { tint: _tint, scrimStyle, ...styles } = S;
    void _tint;
    return { ...base, ...styles, contentStyle, scrimStyle: scrimStyle ?? null };
  });
}
