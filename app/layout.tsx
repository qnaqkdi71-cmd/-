import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "자산 막대 레이스 영상 생성기",
  description:
    "실제 주식(Yahoo)·코인(Binance) 데이터로 1080×1920 세로 영상을 만드는 막대 레이스 차트 생성기. WebCodecs로 MP4 내보내기.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
