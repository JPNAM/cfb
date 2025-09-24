import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NFL Cohesion",
  description: "Lineup cohesion analytics for every NFL system state"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-8">
          {children}
        </div>
      </body>
    </html>
  );
}
