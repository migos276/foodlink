import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import SplashScreen from "@/components/SplashScreen"
import "./globals.css"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Camer Eat - Admin Dashboard",
  description: "Tableau de bord administrateur pour la gestion de la plateforme de livraison",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="fr">
      <body className={`font-sans antialiased`}>
        <SplashScreen>
          {children}
        </SplashScreen>
        <Analytics />
      </body>
    </html>
  )
}
