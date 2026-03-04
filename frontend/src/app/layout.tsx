import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "UniCompass",
  description: "AI-powered university advisor for Singapore students",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        <header className="border-b bg-white px-4 py-3">
          <nav className="mx-auto flex max-w-6xl items-center gap-6">
            <Link href="/" className="text-lg font-bold tracking-tight">
              Uni<span className="text-blue-600">Compass</span>
            </Link>
            <Link
              href="/profile"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Profile
            </Link>
            <Link
              href="/scholarships"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Scholarships
            </Link>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
