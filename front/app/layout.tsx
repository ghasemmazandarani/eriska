import type { Metadata } from "next";
import { Vazirmatn } from "next/font/google";
import "./globals.css";

const vazirmatn = Vazirmatn({
  subsets: ["arabic", "latin"],
  variable: "--font-vazirmatn",
});

export const metadata: Metadata = {
  title: "Eriska Security Agent | امنیت هوشمند IoT",
  description: "ایجنت هوشمند امنیت شبکه و اینترنت اشیاء",
  icons: {
    icon: '/favicon.ico',
    apple: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl">
      <body
        className={`${vazirmatn.variable} antialiased bg-slate-900 text-slate-50`}
      >
        {children}
      </body>
    </html>
  );
}
