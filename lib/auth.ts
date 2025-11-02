"use client"

import { create } from "zustand"
import { persist } from "zustand/middleware"

// Helper function to decode base64url
function base64UrlDecode(str: string): string {
  // Replace base64url characters with base64 characters
  let base64 = str.replace(/-/g, '+').replace(/_/g, '/')
  // Add padding if necessary
  while (base64.length % 4 !== 0) {
    base64 += '='
  }
  return atob(base64)
}

interface AuthState {
  isAuthenticated: boolean
  user: { email: string; name: string; profile: string } | null
  token: string | null
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      user: null,
      token: null,
      
      login: async (username: string, password: string) => {
        try {
          const response = await fetch("http://127.0.0.1:8000/api/token/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include", // Important pour les cookies/sessions
            body: JSON.stringify({ username, password }),
          })

          if (response.ok) {
            const data = await response.json()
            const accessToken = data.access

            // Validate accessToken before decoding
            if (!accessToken || typeof accessToken !== 'string' || accessToken.split('.').length !== 3) {
              console.error("Invalid access token received:", accessToken)
              return false
            }

            // Décoder le token JWT pour obtenir les informations utilisateur
            try {
              const payload = JSON.parse(base64UrlDecode(accessToken.split('.')[1]))

              const user = {
                email: payload.email || `${username}@example.com`,
                name: payload.username || username,
                profile: payload.profile || payload.user_type || 'client'
              }

              set({
                isAuthenticated: true,
                user,
                token: accessToken,
              })

              return true
            } catch (decodeError) {
              console.error("Error decoding token:", decodeError)
              return false
            }
          } else {
            const errorData = await response.json().catch(() => ({}))
            console.error("Login failed:", response.status, errorData)
            return false
          }
        } catch (error) {
          console.error("Login error:", error)
          return false
        }
      },

      logout: () => {
        set({ isAuthenticated: false, user: null, token: null })
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        token: state.token,
      }),
    },
  ),
)