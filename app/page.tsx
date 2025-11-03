"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"

export default function SplashScreen() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const timer = setTimeout(() => {
      router.push("/login")
    }, 3000)

    return () => clearTimeout(timer)
  }, [router])

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-background flex items-center justify-center overflow-hidden">
      <div className="relative">
        {/* Animated rings */}
        <motion.div
          className="absolute inset-0 -m-20"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1.2, opacity: 0.1 }}
          transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, repeatType: "reverse" }}
        >
          <div className="w-full h-full rounded-full border-2 border-primary" />
        </motion.div>

        <motion.div
          className="absolute inset-0 -m-12"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1.1, opacity: 0.2 }}
          transition={{ duration: 2, delay: 0.3, repeat: Number.POSITIVE_INFINITY, repeatType: "reverse" }}
        >
          <div className="w-full h-full rounded-full border-2 border-accent" />
        </motion.div>

        {/* Logo and app name */}
        <motion.div
          className="relative z-10 text-center"
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <motion.div
            className="mb-6"
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
          >
            <div className="w-24 h-24 mx-auto bg-gradient-to-br from-primary to-accent rounded-2xl flex items-center justify-center">
              <svg className="w-12 h-12 text-primary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </motion.div>

          <motion.h1
            className="text-4xl font-bold text-foreground mb-2"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            FoodLink
          </motion.h1>

          <motion.p
            className="text-muted-foreground text-lg"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            Admin Dashboard
          </motion.p>

          <motion.div
            className="mt-8 flex justify-center gap-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.6 }}
          >
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse delay-150" />
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse delay-300" />
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}
