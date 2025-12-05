import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ICASA-GEO | Sistema de Gestión Estratégica Organizacional',
  description: 'Sistema centralizado para la gestión del Manual de Organización de ICASA',
  keywords: 'ICASA, gestión organizacional, manual de organización, documentos corporativos',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="bg-gray-50 font-sans antialiased">
        {children}
      </body>
    </html>
  )
}