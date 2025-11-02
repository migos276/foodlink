"use client"

import { useEffect, useState, Suspense } from "react"
import { usePathname } from "next/navigation"

function SplashScreenContent({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(false)
  const pathname = usePathname()

  useEffect(() => {
    setIsLoading(true)
    const timer = setTimeout(() => setIsLoading(false), 500) // Show splash for 500ms minimum
    return () => clearTimeout(timer)
  }, [pathname])

  if (isLoading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg font-semibold text-gray-700">Chargement...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

export default function SplashScreen({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg font-semibold text-gray-700">Chargement...</p>
        </div>
      </div>
    }>
      <SplashScreenContent>{children}</SplashScreenContent>
    </Suspense>
  )
}
