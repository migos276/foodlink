import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'

interface EntityData {
  user: any
  type_plat: string
  rate: number
  est_ouvert: any
  id: number
  name?: string
  email?: string
  profile?: string
  quartier?: string
  status?: string
  username?: string
}

interface UseEntityDataReturn {
  data: EntityData[]
  loading: boolean
  error: string | null
  refetch: () => void
  deleteEntity: (id: number) => Promise<boolean>
  createEntity: (data: any) => Promise<boolean>
  updateEntity: (id: number, data: any) => Promise<boolean>
  getEntrepriseUsers: () => Promise<EntityData[]>
}

export function useEntityData(entityType: string): UseEntityDataReturn {
  const [data, setData] = useState<EntityData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      let response
      switch (entityType) {
        case 'users':
          response = await apiClient.getUsers()
          break
        case 'restaurants':
          response = await apiClient.getRestaurants()
          break
        case 'livreurs':
          response = await apiClient.getLivreurs()
          break
        case 'boutiques':
          response = await apiClient.getBoutiques()
          break
        default:
          throw new Error(`Unknown entity type: ${entityType}`)
      }

      if (response.error) {
        setError(response.error)
      } else if (response.data) {
        // Assuming the API returns an array or an object with results
        const entities = Array.isArray(response.data) ? response.data : response.data.results || []
        setData(entities)
      }
    } catch (err) {
      setError('Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  const deleteEntity = async (id: number): Promise<boolean> => {
    try {
      let response
      switch (entityType) {
        case 'users':
          response = await apiClient.deleteUser(id)
          break
        case 'restaurants':
          response = await apiClient.deleteRestaurant(id)
          break
        case 'livreurs':
          response = await apiClient.deleteLivreur(id)
          break
        case 'boutiques':
          response = await apiClient.deleteBoutique(id)
          break
        default:
          throw new Error(`Unknown entity type: ${entityType}`)
      }

      if (response.error) {
        setError(`Failed to delete entity: ${response.error}`)
        return false
      } else {
        // Remove the deleted entity from the local state
        setData(prevData => prevData.filter(item => item.id !== id))
        return true
      }
    } catch (err) {
      setError('Failed to delete entity')
      return false
    }
  }

  const createEntity = async (entityData: any): Promise<boolean> => {
    try {
      let response
      switch (entityType) {
        case 'users':
          response = await apiClient.createUser(entityData)
          break
        case 'restaurants':
          response = await apiClient.createRestaurant(entityData)
          break
        case 'livreurs':
          response = await apiClient.createLivreur(entityData)
          break
        case 'boutiques':
          response = await apiClient.createBoutique(entityData)
          break
        default:
          throw new Error(`Unknown entity type: ${entityType}`)
      }

      if (response.error) {
        setError(`Failed to create entity: ${response.error}`)
        return false
      } else {
        // Add the new entity to the local state
        if (response.data) {
          setData(prevData => [...prevData, response.data])
        }
        return true
      }
    } catch (err) {
      setError('Failed to create entity')
      return false
    }
  }

  const updateEntity = async (id: number, entityData: any): Promise<boolean> => {
    try {
      let response
      switch (entityType) {
        case 'users':
          response = await apiClient.updateUser(id, entityData)
          break
        case 'restaurants':
          response = await apiClient.updateRestaurant(id, entityData)
          break
        case 'livreurs':
          response = await apiClient.updateLivreur(id, entityData)
          break
        case 'boutiques':
          response = await apiClient.updateBoutique(id, entityData)
          break
        default:
          throw new Error(`Unknown entity type: ${entityType}`)
      }

      if (response.error) {
        setError(`Failed to update entity: ${response.error}`)
        return false
      } else {
        // Update the entity in the local state
        if (response.data) {
          setData(prevData => prevData.map(item => item.id === id ? response.data : item))
        }
        return true
      }
    } catch (err) {
      setError('Failed to update entity')
      return false
    }
  }

  useEffect(() => {
    fetchData()
  }, [entityType])

  const getEntrepriseUsers = async (): Promise<EntityData[]> => {
    try {
      const response = await apiClient.getUsers({ profile: 'entreprise' })
      if (response.error) {
        setError(`Failed to fetch entreprise users: ${response.error}`)
        return []
      } else if (response.data) {
        const users = Array.isArray(response.data) ? response.data : response.data.results || []
        return users
      }
      return []
    } catch (err) {
      setError('Failed to fetch entreprise users')
      return []
    }
  }

  return { data, loading, error, refetch: fetchData, deleteEntity, createEntity, updateEntity, getEntrepriseUsers }
}
