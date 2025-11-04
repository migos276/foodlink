const API_BASE_URL = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
  ? '/api' // URL relative pour la production (sera résolue par Nginx)
  : "http://127.0.0.1:8000"

export interface ApiResponse<T = any> {
  data?: T
  error?: string
  status: number
}

class ApiClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('auth-storage')
    if (token) {
      try {
        const parsed = JSON.parse(token)
        if (parsed.state?.token) {
          return {
            'Authorization': `Bearer ${parsed.state.token}`,
            'Content-Type': 'application/json',
          }
        }
      } catch (e) {
        console.warn('Failed to parse auth token')
      }
    }
    return {
      'Content-Type': 'application/json',
    }
  }

  async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`
      const headers = this.getAuthHeaders()

      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        return {
          error: data?.detail || data?.message || `HTTP ${response.status}`,
          status: response.status,
        }
      }

      return {
        data,
        status: response.status,
      }
    } catch (error) {
      console.error('API request failed:', error)
      return {
        error: 'Network error or server unavailable',
        status: 0,
      }
    }
  }

  // Méthodes spécifiques pour les entités
  async getUsers(params?: Record<string, any>) {
    const queryString = params ? `?${new URLSearchParams(params)}` : ''
    return this.request(`/utilisateur/${queryString}`)
  }

  async getRestaurants(params?: Record<string, any>) {
    const queryString = params ? `?${new URLSearchParams(params)}` : ''
    return this.request(`/restaurant/${queryString}`)
  }

  async getLivreurs(params?: Record<string, any>) {
    const queryString = params ? `?${new URLSearchParams(params)}` : ''
    return this.request(`/livreur/${queryString}`)
  }

  async getBoutiques(params?: Record<string, any>) {
    const queryString = params ? `?${new URLSearchParams(params)}` : ''
    return this.request(`/boutique/${queryString}`)
  }

  async createUser(data: { username: string; email: string; tel: number; profile: string; password: string; quartier?: string }) {
    return this.request('/utilisateur/', { method: 'POST', body: JSON.stringify(data) })
  }

  async createRestaurant(data: { user_id: number; type_plat: string }) {
    return this.request('/restaurant/', { method: 'POST', body: JSON.stringify(data) })
  }

  async createLivreur(data: { entreprise: number; matricule: string; description?: string; user: { username: string; email: string; tel: number; password: string; quartier?: string } }) {
    return this.request('/livreur/', { method: 'POST', body: JSON.stringify(data) })
  }

  async createBoutique(data: { user: { username: string; email: string; tel: number; password: string; quartier?: string }; couleur?: string }) {
    return this.request('/boutique/', { method: 'POST', body: JSON.stringify(data) })
  }

  async getCommandes(params?: Record<string, any>) {
    const queryString = params ? `?${new URLSearchParams(params)}` : ''
    return this.request(`/commande_restau/${queryString}`)
  }

  async deleteUser(id: number) {
    return this.request(`/utilisateur/${id}/`, { method: 'DELETE' })
  }

  async deleteRestaurant(id: number) {
    return this.request(`/restaurant/${id}/`, { method: 'DELETE' })
  }

  async deleteLivreur(id: number) {
    return this.request(`/livreur/${id}/`, { method: 'DELETE' })
  }

  async deleteBoutique(id: number) {
    return this.request(`/boutique/${id}/`, { method: 'DELETE' })
  }

  async updateUser(id: number, data: Partial<{ username: string; email: string; tel: number; profile: string; password: string; quartier?: string }>) {
    return this.request(`/utilisateur/${id}/`, { method: 'PUT', body: JSON.stringify(data) })
  }

  async updateRestaurant(id: number, data: Partial<{ user_id: number; type_plat: string }>) {
    return this.request(`/restaurant/${id}/`, { method: 'PUT', body: JSON.stringify(data) })
  }

  async updateLivreur(id: number, data: Partial<{ entreprise: number; matricule: string; description?: string; user: { username: string; email: string; tel: number; password: string; quartier?: string } }>) {
    return this.request(`/livreur/${id}/`, { method: 'PUT', body: JSON.stringify(data) })
  }

  async updateBoutique(id: number, data: Partial<{ user_id: number; couleur?: string; horaire_id?: number }>) {
    return this.request(`/boutique/${id}/`, { method: 'PUT', body: JSON.stringify(data) })
  }

  async getStats() {
    // Pour les stats, on peut utiliser plusieurs endpoints
    const [users, restaurants, commandes, boutiques, livreurs] = await Promise.all([
      this.getUsers(),
      this.getRestaurants(),
      this.getCommandes(),
      this.getBoutiques(),
      this.getLivreurs(),
    ])

    if (users.error || restaurants.error || commandes.error || boutiques.error || livreurs.error) {
      return {
        error: 'Failed to fetch stats',
        status: 500,
      }
    }

    // Calculate total revenue from all orders
    const totalRevenue = commandes.data?.results?.reduce((sum: number, order: any) => sum + (order.prix_total || 0), 0) || 0

    return {
      data: {
        totalUsers: users.data?.count || 0,
        totalRestaurants: restaurants.data?.count || 0,
        totalCommandes: commandes.data?.count || 0,
        totalBoutiques: boutiques.data?.count || 0,
        totalLivreurs: livreurs.data?.count || 0,
        totalRevenue: totalRevenue,
        activeDeliveries: 0, // À implémenter selon vos besoins
      },
      status: 200,
    }
  }

  async getAnalysis() {
    return this.request('/analysis/')
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
