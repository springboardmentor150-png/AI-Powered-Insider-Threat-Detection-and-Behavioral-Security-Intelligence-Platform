import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ITBIS — Insider Threat Behavioral Intelligence System",
  description: "AI-Powered Insider Threat & Behavioral Intelligence Platform for Security Operations Centers (SOC)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased font-sans">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
