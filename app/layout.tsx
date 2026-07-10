import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "전문직 상세페이지 만들기",
  description:
    "직업만 입력하면 문의를 부르는 전문직 상세페이지가 바로 완성됩니다. 코딩 없이 미리보기 후 HTML 파일로 저장하세요.",
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
