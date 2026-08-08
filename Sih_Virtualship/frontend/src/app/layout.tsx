import './globals.css';
import { LayoutWrapper } from '../components/layout/layout-wrapper';

export const metadata = {
  title: 'MV Titan Pro - Operations Digital Twin Console',
  description: 'Industrial SCADA operations dashboard for merchant shipping vessels.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-slate-950 text-slate-100">
      <body className="h-full antialiased overflow-hidden">
        <LayoutWrapper>{children}</LayoutWrapper>
      </body>
    </html>
  );
}
