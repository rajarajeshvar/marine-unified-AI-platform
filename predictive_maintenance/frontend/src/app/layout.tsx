import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Marine Predictive Maintenance Dashboard',
  description: 'AI-powered engine health and failure prediction platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen bg-slate-950 text-slate-50 flex flex-col">
        <header className="border-b border-slate-800 bg-slate-900 px-6 py-4">
          <h1 className="text-xl font-bold tracking-tight text-blue-400">Marine AI</h1>
        </header>
        <main className="flex-1 p-6">
          {children}
        </main>
      </body>
    </html>
  );
}
