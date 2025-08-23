import './globals.css'

export const metadata = {
  title: 'Rippley Viewer',
  description: 'AI-Powered Modular App Builder UI',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="description" content={metadata.description} />
        <title>{metadata.title}</title>
      </head>
      <body>
        {children}
      </body>
    </html>
  )
}
