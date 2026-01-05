import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { MantineProvider, ColorSchemeScript, createTheme } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const theme = createTheme({
  primaryColor: "blue", // Back to Apple Blue default concept
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
  headings: {
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    fontWeight: "600",
  },
  defaultRadius: "lg", // Larger radius for Apple look
});

export const metadata: Metadata = {
  title: "Crypto Dashboard | 암호화폐 포트폴리오",
  description: "업비트와 바이낸스 암호화폐 포트폴리오를 한눈에 확인하세요",
  keywords: ["crypto", "dashboard", "upbit", "binance", "bitcoin", "portfolio"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <ColorSchemeScript defaultColorScheme="light" />
      </head>
      <body className={`${inter.variable}`}>
        <MantineProvider defaultColorScheme="light" theme={theme}>
          <Notifications position="top-right" />
          {children}
        </MantineProvider>
      </body>
    </html>
  );
}
