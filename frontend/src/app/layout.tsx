import "./globals.css";
export const metadata = {
  title: "ITBIS | Insider Threat System",
  description: "AI-Powered Insider Threat Detection Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
