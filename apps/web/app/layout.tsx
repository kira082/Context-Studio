import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Context Studio | No-Code Builder',
  description: 'Plug and play memory agent builder',
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
