import "./globals.css";

export const metadata = {
  title: "ITBIS - Insider Threat Detection",
  description: "AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
