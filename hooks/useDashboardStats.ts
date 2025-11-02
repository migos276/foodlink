import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'

interface DashboardStats {
  totalUsers: number
  totalRestaurants: number
  totalCommandes: number
  totalBoutiques: number
  totalLivreurs: number
  totalRevenue: number
  activeDeliveries: number
}

export function useDashboardStats() {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 0,
    totalRestaurants: 0,
    totalCommandes: 0,
    totalBoutiques: 0,
    totalLivreurs: 0,
    totalRevenue: 0,
    activeDeliveries: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const response = await apiClient.getStats()

        if (response.error) {
          setError(response.error)
        } else if (response.data) {
          setStats(response.data)
        }
      } catch (err) {
        setError('Failed to fetch dashboard stats')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  return { stats, loading, error }
}
