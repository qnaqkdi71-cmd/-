"use client";

import { useMemo, useState } from "react";
import type { GenerateInput, Tone } from "../lib/detail/types";
import { generatePage, PROFESSION_SUGGESTIONS } from "../lib/detail/library";
import { renderPageHtml } from "../lib/detail/renderHtml";

const ACCENTS = [
  { c: "#2563eb", name: "신뢰 블루" },
  { c: "#0f766e", name: "차분 그린" },
  { c: "#7c3aed", name: "프리미엄 퍼플" },
  { c: "#c2410c", name: "따뜻 오렌지" },
  { c: "#be123c", name: "임팩트 레드" },
  { c: "#0f172a", name: "모던 블랙" },
];

const TONES: { value: Tone; label: string }[] = [
  { value: "trust", label: "신뢰감 있게" },
  { value: "friendly", label: "친근하게" },
  { value: "premium", label: "고급스럽게" },
];

export default function Home() {
  const [profession, setProfession] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [region, setRegion] = useState("");
  const [years, setYears] = useState("");
  const [phone, setPhone] = useState("");
  const [kakao, setKakao] = useState("");
  const [strengths, setStrengths] = useState("");
  const [accent, setAccent] = useState(ACCENTS[0].c);
  const [tone, setTone] = useState<Tone>("trust");
  const [device, setDevice] = useState<"mobile" | "desktop">("mobile");
  const [saved, setSaved] = useState(false);

  const input: GenerateInput = useMemo(
    () => ({
      profession,
      businessName,
      region,
      years,
      phone,
      kakao,
      strengths: strengths.split("\n").filter((s) => s.trim()),
      accent,
      tone,
    }),
    [profession, businessName, region, years, phone, kakao, strengths, accent, tone],
  );

  const html = useMemo(() => renderPageHtml(generatePage(input)), [input]);
  const hasProfession = profession.trim().length > 0;

  function download() {
    const blob = new Blob([html], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const safe = (profession.trim() || "상세페이지").replace(/[^\w가-힣]+/g, "-");
    a.href = url;
    a.download = `${safe}-상세페이지.html`;
    a.click();
    URL.revokeObjectURL(url);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  }

  async function copyHtml() {
    await navigator.clipboard.writeText(html);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  }

  return (
    <main style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.h1}>전문직 상세페이지 만들기</h1>
        <p style={styles.sub}>
          직업만 입력하면 문의를 부르는 상세페이지가 바로 완성됩니다. 코딩은 전혀 필요 없어요.
        </p>
      </header>

      <div style={styles.layout}>
        {/* 왼쪽: 입력 */}
        <section style={styles.form}>
          <Panel title="① 어떤 직업인가요? (필수)">
            <input
              value={profession}
              onChange={(e) => setProfession(e.target.value)}
              placeholder="예: 변호사, 세무사, 인테리어, 심리상담…"
              style={styles.bigInput}
              autoFocus
            />
            <div style={styles.chips}>
              {PROFESSION_SUGGESTIONS.map((p) => (
                <button
                  key={p}
                  style={{
                    ...styles.chip,
                    ...(profession === p ? styles.chipActive : {}),
                  }}
                  onClick={() => setProfession(p)}
                >
                  {p}
                </button>
              ))}
            </div>
            <p style={styles.hint}>
              목록에 없는 직업도 괜찮아요. 무엇을 넣든 그에 맞는 페이지가 만들어집니다.
            </p>
          </Panel>

          <Panel title="② 기본 정보 (선택 — 넣으면 더 정확해져요)">
            <Field label="상호명 / 이름">
              <input
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                placeholder="예: OO법률사무소, 김세무사"
                style={styles.input}
              />
            </Field>
            <div style={styles.row2}>
              <Field label="지역">
                <input
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                  placeholder="예: 서울 강남"
                  style={styles.input}
                />
              </Field>
              <Field label="경력">
                <input
                  value={years}
                  onChange={(e) => setYears(e.target.value)}
                  placeholder="예: 15"
                  style={styles.input}
                />
              </Field>
            </div>
          </Panel>

          <Panel title="③ 문의받을 연락처 (선택)">
            <Field label="전화번호">
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="예: 010-1234-5678"
                style={styles.input}
              />
            </Field>
            <Field label="카카오톡 채널 / 오픈채팅 링크">
              <input
                value={kakao}
                onChange={(e) => setKakao(e.target.value)}
                placeholder="예: http://pf.kakao.com/_xxxxx"
                style={styles.input}
              />
            </Field>
            <p style={styles.hint}>
              연락처를 넣으면 페이지의 “전화 상담 · 카카오톡 상담” 버튼이 실제로 연결됩니다.
            </p>
          </Panel>

          <Panel title="④ 강조하고 싶은 강점 (선택)">
            <textarea
              value={strengths}
              onChange={(e) => setStrengths(e.target.value)}
              placeholder={"한 줄에 하나씩 적어주세요.\n예) 대형 로펌 15년 경력\n예) 야간·주말 상담 가능\n예) 성공 보수제 운영"}
              style={styles.textarea}
            />
          </Panel>

          <Panel title="⑤ 디자인">
            <Field label="색상">
              <div style={styles.chips}>
                {ACCENTS.map((a) => (
                  <button
                    key={a.c}
                    onClick={() => setAccent(a.c)}
                    title={a.name}
                    style={{
                      ...styles.swatch,
                      background: a.c,
                      outline: accent === a.c ? "3px solid #fff" : "none",
                      boxShadow:
                        accent === a.c ? `0 0 0 2px ${a.c}` : "none",
                    }}
                  />
                ))}
              </div>
            </Field>
            <Field label="말투">
              <div style={styles.chips}>
                {TONES.map((t) => (
                  <button
                    key={t.value}
                    onClick={() => setTone(t.value)}
                    style={{
                      ...styles.chip,
                      ...(tone === t.value ? styles.chipActive : {}),
                    }}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </Field>
          </Panel>
        </section>

        {/* 오른쪽: 미리보기 */}
        <section style={styles.previewCol}>
          <div style={styles.previewBar}>
            <div style={styles.deviceToggle}>
              <button
                onClick={() => setDevice("mobile")}
                style={{
                  ...styles.deviceBtn,
                  ...(device === "mobile" ? styles.deviceBtnActive : {}),
                }}
              >
                📱 모바일
              </button>
              <button
                onClick={() => setDevice("desktop")}
                style={{
                  ...styles.deviceBtn,
                  ...(device === "desktop" ? styles.deviceBtnActive : {}),
                }}
              >
                🖥 넓게
              </button>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button style={styles.ghostBtn} onClick={copyHtml} disabled={!hasProfession}>
                코드 복사
              </button>
              <button style={styles.downloadBtn} onClick={download} disabled={!hasProfession}>
                ⬇ 페이지 저장
              </button>
            </div>
          </div>

          {saved && <div style={styles.savedToast}>✓ 완료되었습니다!</div>}

          {hasProfession ? (
            <div style={styles.frameWrap}>
              <iframe
                title="상세페이지 미리보기"
                srcDoc={html}
                style={{
                  ...styles.frame,
                  width: device === "mobile" ? 390 : "100%",
                }}
              />
            </div>
          ) : (
            <div style={styles.empty}>
              <div style={{ fontSize: 44, marginBottom: 12 }}>👈</div>
              왼쪽에 직업을 입력하면
              <br />
              여기에 상세페이지가 바로 나타납니다.
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={styles.panel}>
      <div style={styles.panelTitle}>{title}</div>
      {children}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={styles.label}>{label}</div>
      {children}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: { maxWidth: 1240, margin: "0 auto", padding: "32px 20px 80px" },
  header: { marginBottom: 26 },
  h1: { fontSize: 28, fontWeight: 800, margin: "0 0 8px" },
  sub: { color: "var(--muted)", fontSize: 15, lineHeight: 1.6, margin: 0 },
  layout: { display: "flex", gap: 28, alignItems: "flex-start", flexWrap: "wrap" },
  form: { flex: "1 1 420px", minWidth: 340, display: "flex", flexDirection: "column", gap: 16 },
  panel: {
    background: "var(--panel)",
    border: "1px solid var(--border)",
    borderRadius: 16,
    padding: 20,
  },
  panelTitle: { fontWeight: 800, fontSize: 15, marginBottom: 14 },
  bigInput: {
    width: "100%",
    minHeight: 52,
    background: "var(--panel-2)",
    border: "1px solid var(--border)",
    borderRadius: 12,
    color: "var(--text)",
    padding: "12px 16px",
    fontSize: 17,
    fontWeight: 600,
  },
  input: {
    width: "100%",
    minHeight: 44,
    background: "var(--panel-2)",
    border: "1px solid var(--border)",
    borderRadius: 10,
    color: "var(--text)",
    padding: "10px 14px",
    fontSize: 15,
  },
  textarea: {
    width: "100%",
    minHeight: 110,
    background: "var(--panel-2)",
    border: "1px solid var(--border)",
    borderRadius: 10,
    color: "var(--text)",
    padding: "12px 14px",
    fontSize: 15,
    lineHeight: 1.6,
    resize: "vertical",
    fontFamily: "inherit",
  },
  row2: { display: "flex", gap: 12 },
  chips: { display: "flex", flexWrap: "wrap", gap: 8, marginTop: 10 },
  chip: {
    border: "1px solid var(--border)",
    background: "var(--panel-2)",
    color: "var(--text)",
    borderRadius: 9999,
    padding: "8px 14px",
    fontSize: 14,
  },
  chipActive: {
    background: "var(--accent)",
    borderColor: "var(--accent)",
    color: "#fff",
    fontWeight: 700,
  },
  swatch: {
    width: 34,
    height: 34,
    borderRadius: "50%",
    border: "none",
    cursor: "pointer",
  },
  hint: { color: "var(--muted)", fontSize: 13, margin: "12px 0 0", lineHeight: 1.6 },
  label: { fontSize: 13, color: "var(--muted)", marginBottom: 6 },

  previewCol: {
    flex: "1 1 460px",
    minWidth: 340,
    position: "sticky",
    top: 20,
    display: "flex",
    flexDirection: "column",
    gap: 12,
  },
  previewBar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
    flexWrap: "wrap",
  },
  deviceToggle: {
    display: "flex",
    gap: 4,
    background: "var(--panel-2)",
    borderRadius: 10,
    padding: 4,
  },
  deviceBtn: {
    border: "none",
    background: "transparent",
    color: "var(--muted)",
    borderRadius: 8,
    padding: "8px 14px",
    fontSize: 13,
    fontWeight: 600,
  },
  deviceBtnActive: { background: "var(--panel)", color: "var(--text)" },
  ghostBtn: {
    border: "1px solid var(--border)",
    background: "transparent",
    color: "var(--text)",
    borderRadius: 10,
    padding: "10px 16px",
    fontSize: 14,
    fontWeight: 600,
  },
  downloadBtn: {
    border: "none",
    background: "var(--accent-2)",
    color: "#04120a",
    borderRadius: 10,
    padding: "10px 18px",
    fontSize: 14,
    fontWeight: 800,
  },
  savedToast: {
    background: "rgba(48,209,88,0.14)",
    border: "1px solid rgba(48,209,88,0.4)",
    color: "#5ee08a",
    borderRadius: 10,
    padding: "10px 14px",
    fontSize: 14,
    fontWeight: 600,
  },
  frameWrap: {
    background: "#0a0d14",
    border: "1px solid var(--border)",
    borderRadius: 18,
    padding: 16,
    display: "flex",
    justifyContent: "center",
    overflow: "hidden",
  },
  frame: {
    height: 760,
    maxWidth: "100%",
    border: "none",
    borderRadius: 12,
    background: "#fff",
    boxShadow: "0 20px 60px rgba(0,0,0,0.4)",
  },
  empty: {
    background: "var(--panel)",
    border: "1px dashed var(--border)",
    borderRadius: 18,
    padding: "80px 24px",
    textAlign: "center",
    color: "var(--muted)",
    fontSize: 16,
    lineHeight: 1.7,
    minHeight: 400,
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },
};
