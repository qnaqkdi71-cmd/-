"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import ChartPreview from "../components/ChartPreview";
import type {
  ChartVideoProject,
  ReturnDisplay,
  ThemeName,
} from "../lib/chart/types";
import { createDefaultProject } from "../lib/chart/defaultProject";
import { ASSET_PRESETS } from "../lib/market/assets";
import { buildAllSeries } from "../lib/market/fetchSeries";
import { exportAndDownload, isExportSupported } from "../lib/export/exportMp4";
import { ensureFonts } from "../lib/export/fonts";

interface AssetRow {
  symbol: string;
  name: string;
  color: string;
}

const ACCENTS = ["#2997ff", "#0A84FF", "#30D158", "#FFD60A", "#BF5AF2"];

export default function Home() {
  const [project, setProject] = useState<ChartVideoProject>(() =>
    createDefaultProject(),
  );
  const [progress, setProgress] = useState(0);
  const [playing, setPlaying] = useState(false);

  // 자산 편집용 로우
  const [rows, setRows] = useState<AssetRow[]>(() =>
    createDefaultProject().series.map((s) => ({
      symbol: s.symbol,
      name: s.name,
      color: s.color,
    })),
  );
  const [startYear, setStartYear] = useState(2016);
  const [endYear, setEndYear] = useState(2026);

  const [loading, setLoading] = useState(false);
  const [loadMsg, setLoadMsg] = useState<string | null>(null);
  const [errors, setErrors] = useState<string[]>([]);

  const [exporting, setExporting] = useState(false);
  const [exportPct, setExportPct] = useState(0);
  const [exportMsg, setExportMsg] = useState<string | null>(null);

  // ---- 재생 루프 ----
  const rafRef = useRef<number | null>(null);
  const lastRef = useRef<number | null>(null);
  useEffect(() => {
    if (!playing) {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      lastRef.current = null;
      return;
    }
    const loop = (now: number) => {
      if (lastRef.current == null) lastRef.current = now;
      const dt = now - lastRef.current;
      lastRef.current = now;
      setProgress((p) => {
        const np = p + dt / (project.durationSec * 1000);
        if (np >= 1) {
          setPlaying(false);
          return 1;
        }
        return np;
      });
      rafRef.current = requestAnimationFrame(loop);
    };
    rafRef.current = requestAnimationFrame(loop);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [playing, project.durationSec]);

  useEffect(() => {
    ensureFonts();
  }, []);

  function patch(p: Partial<ChartVideoProject>) {
    setProject((prev) => ({ ...prev, ...p }));
  }

  const years = useMemo(() => {
    const ys: number[] = [];
    for (let y = startYear; y <= endYear; y++) ys.push(y);
    return ys;
  }, [startYear, endYear]);

  // ---- 실제 시장 데이터 불러오기 ----
  async function loadRealData() {
    if (!rows.length) return;
    setLoading(true);
    setErrors([]);
    setLoadMsg("실제 시장 데이터를 불러오는 중…");
    try {
      const { series, errors } = await buildAllSeries(
        rows.map((r) => ({
          symbol: r.symbol.trim(),
          name: r.name.trim() || undefined,
          color: r.color,
        })),
        { years, initialInvestment: project.initialInvestment },
      );
      if (series.length) {
        setProject((prev) => ({
          ...prev,
          series,
          frames: years.map(String),
        }));
        setProgress(0);
        setPlaying(false);
      }
      setErrors(errors);
      setLoadMsg(
        series.length
          ? `불러오기 완료 · 자산 ${series.length}개`
          : "불러온 자산이 없습니다.",
      );
    } catch (e) {
      setErrors([(e as Error).message]);
      setLoadMsg(null);
    } finally {
      setLoading(false);
    }
  }

  // ---- MP4 내보내기 ----
  async function doExport() {
    if (exporting) return;
    if (!isExportSupported()) {
      setExportMsg(
        "이 브라우저는 WebCodecs 내보내기를 지원하지 않습니다. 데스크톱 크롬에서 열어 주세요.",
      );
      return;
    }
    setExporting(true);
    setExportPct(0);
    setExportMsg("숨겨진 캔버스에 프레임을 그려 인코딩하는 중…");
    setPlaying(false);
    try {
      await exportAndDownload(project, {
        fileName: `asset-race-${project.width}x${project.height}.mp4`,
        onProgress: (done, total) =>
          setExportPct(Math.round((done / total) * 100)),
      });
      setExportMsg("완료! MP4 파일이 다운로드되었습니다.");
    } catch (e) {
      setExportMsg("내보내기 실패: " + (e as Error).message);
    } finally {
      setExporting(false);
    }
  }

  // ---- 자산 로우 조작 ----
  function updateRow(i: number, patchRow: Partial<AssetRow>) {
    setRows((rs) => rs.map((r, idx) => (idx === i ? { ...r, ...patchRow } : r)));
  }
  function removeRow(i: number) {
    setRows((rs) => rs.filter((_, idx) => idx !== i));
  }
  function addPreset(symbol: string) {
    const p = ASSET_PRESETS.find((a) => a.symbol === symbol);
    if (!p) return;
    if (rows.some((r) => r.symbol.toUpperCase() === symbol.toUpperCase())) return;
    setRows((rs) => [...rs, { symbol: p.symbol, name: p.name, color: p.color }]);
  }
  function addBlank() {
    setRows((rs) => [
      ...rs,
      { symbol: "", name: "", color: ACCENTS[rs.length % ACCENTS.length] },
    ]);
  }

  return (
    <main style={styles.page}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.h1}>자산 막대 레이스 · 영상 생성기</h1>
          <p style={styles.sub}>
            실제 주식(Yahoo Finance)·코인(Binance) 데이터로 1080×1920 세로 영상을
            만듭니다. 미리보기와 같은 렌더러로 숨겨진 캔버스를 프레임 단위로
            인코딩해 MP4로 저장합니다.
          </p>
        </div>
      </header>

      <div style={styles.layout}>
        {/* 좌: 미리보기 */}
        <section style={styles.previewCol}>
          <ChartPreview project={project} progress={progress} displayWidth={360} />

          <div style={styles.transport}>
            <button
              style={styles.playBtn}
              onClick={() => {
                if (progress >= 1) setProgress(0);
                setPlaying((v) => !v);
              }}
            >
              {playing ? "❚❚" : "▶"}
            </button>
            <input
              type="range"
              min={0}
              max={1000}
              value={Math.round(progress * 1000)}
              onChange={(e) => {
                setPlaying(false);
                setProgress(Number(e.target.value) / 1000);
              }}
              style={{ flex: 1 }}
            />
            <button
              style={styles.iconBtn}
              onClick={() => {
                setProgress(0);
                setPlaying(true);
              }}
              title="처음부터"
            >
              ↺
            </button>
          </div>

          <button
            style={{
              ...styles.exportBtn,
              opacity: exporting ? 0.7 : 1,
            }}
            onClick={doExport}
            disabled={exporting}
          >
            {exporting ? `내보내는 중… ${exportPct}%` : "🎬 MP4로 내보내기 (1080×1920 · 60fps)"}
          </button>
          {exporting && (
            <div style={styles.progressTrack}>
              <div style={{ ...styles.progressFill, width: `${exportPct}%` }} />
            </div>
          )}
          {exportMsg && <p style={styles.note}>{exportMsg}</p>}
        </section>

        {/* 우: 설정 */}
        <section style={styles.settingsCol}>
          {/* 자산 */}
          <Panel title="자산">
            {rows.map((r, i) => (
              <div key={i} style={styles.assetRow}>
                <input
                  type="color"
                  value={r.color}
                  onChange={(e) => updateRow(i, { color: e.target.value })}
                  style={styles.colorInput}
                  title="막대 색"
                />
                <input
                  value={r.symbol}
                  placeholder="티커/심볼 (예: AAPL, BTC, 005930.KS)"
                  onChange={(e) => updateRow(i, { symbol: e.target.value })}
                  style={{ ...styles.input, flex: 1.2 }}
                />
                <input
                  value={r.name}
                  placeholder="표시 이름"
                  onChange={(e) => updateRow(i, { name: e.target.value })}
                  style={{ ...styles.input, flex: 1 }}
                />
                <button style={styles.removeBtn} onClick={() => removeRow(i)}>
                  ✕
                </button>
              </div>
            ))}
            <div style={styles.chipRow}>
              {ASSET_PRESETS.slice(0, 12).map((p) => (
                <button
                  key={p.key}
                  style={styles.chip}
                  onClick={() => addPreset(p.symbol)}
                >
                  ＋ {p.name}
                </button>
              ))}
              <button style={styles.chipAlt} onClick={addBlank}>
                ＋ 직접 입력
              </button>
            </div>

            <div style={styles.yearRow}>
              <label style={styles.label}>기간</label>
              <input
                type="number"
                value={startYear}
                onChange={(e) => setStartYear(Number(e.target.value))}
                style={styles.yearInput}
              />
              <span style={{ color: "var(--muted)" }}>~</span>
              <input
                type="number"
                value={endYear}
                onChange={(e) => setEndYear(Number(e.target.value))}
                style={styles.yearInput}
              />
              <label style={styles.label}>초기 투자금</label>
              <input
                type="number"
                value={project.initialInvestment}
                onChange={(e) =>
                  patch({ initialInvestment: Number(e.target.value) })
                }
                style={{ ...styles.yearInput, width: 130 }}
              />
              <span style={{ color: "var(--muted)" }}>원</span>
            </div>

            <button
              style={styles.loadBtn}
              onClick={loadRealData}
              disabled={loading}
            >
              {loading ? "불러오는 중…" : "⟳ 실제 시장 데이터 불러오기"}
            </button>
            {loadMsg && <p style={styles.note}>{loadMsg}</p>}
            {errors.length > 0 && (
              <div style={styles.errBox}>
                {errors.map((e, i) => (
                  <div key={i}>⚠ {e}</div>
                ))}
              </div>
            )}
          </Panel>

          {/* 텍스트 */}
          <Panel title="텍스트">
            <Field label="작은 제목 (kicker)">
              <input
                value={project.kicker}
                onChange={(e) => patch({ kicker: e.target.value })}
                style={styles.input}
              />
            </Field>
            <Field label="큰 제목">
              <input
                value={project.title}
                onChange={(e) => patch({ title: e.target.value })}
                style={styles.input}
              />
            </Field>
            <Field label="강조 문구">
              <input
                value={project.titleHighlight}
                onChange={(e) => patch({ titleHighlight: e.target.value })}
                style={styles.input}
              />
            </Field>
            <Field label="계정 핸들">
              <input
                value={project.handle}
                onChange={(e) => patch({ handle: e.target.value })}
                style={styles.input}
              />
            </Field>
            <Field label="각주">
              <textarea
                value={project.footnote}
                onChange={(e) => patch({ footnote: e.target.value })}
                style={{ ...styles.input, height: 72, resize: "vertical" }}
              />
            </Field>
          </Panel>

          {/* 표시 옵션 */}
          <Panel title="표시 · 영상">
            <div style={styles.optGrid}>
              <Field label="테마">
                <select
                  value={project.theme}
                  onChange={(e) =>
                    patch({ theme: e.target.value as ThemeName })
                  }
                  style={styles.input}
                >
                  <option value="dark">다크</option>
                  <option value="light">라이트</option>
                </select>
              </Field>
              <Field label="수익률 표시">
                <select
                  value={project.returnDisplay}
                  onChange={(e) =>
                    patch({ returnDisplay: e.target.value as ReturnDisplay })
                  }
                  style={styles.input}
                >
                  <option value="percent">퍼센트</option>
                  <option value="multiple">배수</option>
                  <option value="hidden">숨김</option>
                </select>
              </Field>
              <Field label={`재생 길이 (${project.durationSec}초)`}>
                <input
                  type="range"
                  min={6}
                  max={60}
                  step={1}
                  value={project.durationSec}
                  onChange={(e) =>
                    patch({ durationSec: Number(e.target.value) })
                  }
                  style={{ width: "100%" }}
                />
              </Field>
              <Field label="막대 글로우">
                <select
                  value={project.barGlow ? "on" : "off"}
                  onChange={(e) => patch({ barGlow: e.target.value === "on" })}
                  style={styles.input}
                >
                  <option value="on">켜기</option>
                  <option value="off">끄기</option>
                </select>
              </Field>
            </div>
            <Field label="강조색">
              <div style={styles.chipRow}>
                {ACCENTS.map((c) => (
                  <button
                    key={c}
                    onClick={() => patch({ accent: c })}
                    style={{
                      ...styles.swatch,
                      background: c,
                      outline:
                        project.accent === c ? "3px solid #fff" : "none",
                    }}
                  />
                ))}
              </div>
            </Field>
          </Panel>
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
    <div style={{ marginBottom: 12 }}>
      <div style={styles.label}>{label}</div>
      {children}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: { maxWidth: 1120, margin: "0 auto", padding: "28px 20px 80px" },
  header: { marginBottom: 24 },
  h1: { fontSize: 26, fontWeight: 800, margin: "0 0 8px" },
  sub: { color: "var(--muted)", fontSize: 14, lineHeight: 1.6, margin: 0, maxWidth: 720 },
  layout: { display: "flex", gap: 28, alignItems: "flex-start", flexWrap: "wrap" },
  previewCol: {
    position: "sticky",
    top: 20,
    display: "flex",
    flexDirection: "column",
    gap: 14,
    width: 360,
  },
  settingsCol: { flex: 1, minWidth: 360, display: "flex", flexDirection: "column", gap: 18 },
  transport: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    background: "var(--panel)",
    border: "1px solid var(--border)",
    borderRadius: 14,
    padding: "10px 14px",
  },
  playBtn: {
    width: 46,
    height: 46,
    borderRadius: "50%",
    border: "none",
    background: "var(--accent)",
    color: "#fff",
    fontSize: 16,
  },
  iconBtn: {
    width: 46,
    height: 46,
    borderRadius: "50%",
    border: "1px solid var(--border)",
    background: "transparent",
    color: "var(--text)",
    fontSize: 20,
  },
  exportBtn: {
    border: "none",
    borderRadius: 14,
    padding: "16px 18px",
    background: "var(--accent-2)",
    color: "#04120a",
    fontWeight: 800,
    fontSize: 15,
  },
  progressTrack: {
    height: 8,
    borderRadius: 8,
    background: "var(--panel-2)",
    overflow: "hidden",
  },
  progressFill: { height: "100%", background: "var(--accent)" },
  note: { color: "var(--muted)", fontSize: 13, margin: 0 },
  panel: {
    background: "var(--panel)",
    border: "1px solid var(--border)",
    borderRadius: 16,
    padding: 18,
  },
  panelTitle: { fontWeight: 800, fontSize: 15, marginBottom: 14 },
  assetRow: { display: "flex", gap: 8, alignItems: "center", marginBottom: 8 },
  colorInput: {
    width: 38,
    height: 38,
    padding: 0,
    border: "1px solid var(--border)",
    borderRadius: 8,
    background: "transparent",
  },
  input: {
    width: "100%",
    minHeight: 40,
    background: "var(--panel-2)",
    border: "1px solid var(--border)",
    borderRadius: 10,
    color: "var(--text)",
    padding: "8px 12px",
    fontSize: 14,
  },
  removeBtn: {
    width: 38,
    height: 38,
    borderRadius: 8,
    border: "1px solid var(--border)",
    background: "transparent",
    color: "var(--danger)",
  },
  chipRow: { display: "flex", flexWrap: "wrap", gap: 8, marginTop: 10 },
  chip: {
    border: "1px solid var(--border)",
    background: "var(--panel-2)",
    color: "var(--text)",
    borderRadius: 9999,
    padding: "6px 12px",
    fontSize: 13,
  },
  chipAlt: {
    border: "1px dashed var(--accent)",
    background: "transparent",
    color: "var(--accent)",
    borderRadius: 9999,
    padding: "6px 12px",
    fontSize: 13,
  },
  yearRow: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    marginTop: 14,
    flexWrap: "wrap",
  },
  yearInput: {
    width: 90,
    minHeight: 40,
    background: "var(--panel-2)",
    border: "1px solid var(--border)",
    borderRadius: 10,
    color: "var(--text)",
    padding: "8px 10px",
    fontSize: 14,
  },
  label: { fontSize: 12, color: "var(--muted)", marginBottom: 6 },
  loadBtn: {
    marginTop: 14,
    width: "100%",
    border: "none",
    borderRadius: 12,
    padding: "13px",
    background: "var(--accent)",
    color: "#fff",
    fontWeight: 700,
    fontSize: 14,
  },
  errBox: {
    marginTop: 10,
    background: "rgba(255,69,58,0.1)",
    border: "1px solid rgba(255,69,58,0.3)",
    borderRadius: 10,
    padding: "10px 12px",
    color: "#ff8a80",
    fontSize: 13,
    lineHeight: 1.6,
  },
  optGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 12,
  },
  swatch: {
    width: 34,
    height: 34,
    borderRadius: "50%",
    border: "1px solid var(--border)",
  },
};
