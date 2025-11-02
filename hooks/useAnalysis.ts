import { useState, useEffect, ReactNode, Key } from 'react'
import { apiClient } from '@/lib/api'

interface AnalysisData {
  kpiData: {
    orders_today: number
    pending_orders_over_1h: number
    avg_prep_time: string
    on_time_delivery_rate: string
  }
  alerts: Array<{
    id: Key | null | undefined
    time: ReactNode
    type: string
    message: string
    severity: string
  }>
  financial: {
    revenue_today: number
    commissions: number
    avg_basket: number
  }
  restaurant_performance: Array<{
    avgTime: ReactNode
    status: string
    name: string
    orders: number
    rating: number
  }>
  delivery_performance: Array<{
    onTime: ReactNode
    status: string
    name: string
    deliveries: number
    rating: number
  }>
  chartData: {
    orderData: Array<{
      month: string
      commandes: number
      paiements: number
    }>
    restaurantData: Array<{
      name: string
      value: number
    }>
    boutiqueData: Array<{
      name: string
      value: number
    }>
    deliveryData: Array<{
      name: string
      montant: number
    }>
  }
}

export function useAnalysis() {
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true)
        const response = await apiClient.getAnalysis()

        if (response.error) {
          setError(response.error)
        } else if (response.data) {
          setAnalysis(response.data)
        }
      } catch (err) {
        setError('Failed to fetch analysis data')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalysis()
  }, [])

  return { analysis, loading, error }
}
