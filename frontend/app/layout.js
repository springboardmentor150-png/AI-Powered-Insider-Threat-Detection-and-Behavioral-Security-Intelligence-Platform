import "./globals.css";

export const metadata = {
  title: "ITBIS | Insider Threat Detection & Security Intelligence",
  description:
    "AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900">
        <nav className="border-b border-slate-200 bg-white px-6 py-4 flex gap-6 items-center">
          
          <a
            href="/"
            className="font-bold text-slate-900 mr-2"
          >
            ITBIS
          </a>

          <a
            href="/"
            className="text-slate-600 hover:text-slate-900"
          >
            Home
          </a>

          <a
            href="/login"
            className="text-slate-600 hover:text-slate-900"
          >
            Login
          </a>

          <a
            href="/signup"
            className="text-slate-600 hover:text-slate-900"
          >
            Signup
          </a>

          <a
            href="/employees"
            className="text-slate-600 hover:text-slate-900"
          >
            Employees
          </a>

        </nav>

        <main className="p-6">
          {children}
        </main>
      </body>
    </html>
  );
}