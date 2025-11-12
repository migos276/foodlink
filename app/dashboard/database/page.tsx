"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Users, Store, ShoppingBag, Truck, Search, Plus, Edit, Trash2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { useEntityData } from "@/hooks/useEntityData"
import { useToast } from "@/hooks/use-toast"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"

const entities = [
  { id: "users", name: "Utilisateurs", icon: Users, count: 0 },
  { id: "restaurants", name: "Restaurants", icon: Store, count: 0 },
  { id: "boutiques", name: "Boutiques", icon: ShoppingBag, count: 0 },
  { id: "livreurs", name: "Livreurs", icon: Truck, count: 0 },
]

export default function DatabasePage() {
  const [selectedEntity, setSelectedEntity] = useState("users")
  const [searchQuery, setSearchQuery] = useState("")
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [editingEntity, setEditingEntity] = useState<any>(null)
  const [formData, setFormData] = useState<any>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [entrepriseUsers, setEntrepriseUsers] = useState<any[]>([])
  const [entityCounts, setEntityCounts] = useState<{[key: string]: number}>({
    users: 0,
    restaurants: 0,
    boutiques: 0,
    livreurs: 0,
  })

  const { toast } = useToast()
  const {
    data,
    loading,
    error,
    deleteEntity,
    createEntity,
    updateEntity,
    getEntrepriseUsers,
  } = useEntityData(selectedEntity)

  // Mise à jour des compteurs d'entités
  const updatedEntities = entities.map((entity) => ({
    ...entity,
    count: entityCounts[entity.id] || 0,
  }))

  // Charger les compteurs au montage et changement d'entité
  useEffect(() => {
    const loadEntityCounts = async () => {
      const counts: {[key: string]: number} = {}
      const entityMappings = {
        users: 'utilisateur',
        restaurants: 'restaurant',
        boutiques: 'boutique',
        livreurs: 'livreur'
      }

      for (const entity of entities) {
        try {
          const endpoint = entityMappings[entity.id as keyof typeof entityMappings]
          const apiUrl = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
            ? `/api${endpoint}/`
            : `http://127.0.0.1:8000${endpoint}/`

          const response = await fetch(apiUrl, {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('auth-storage') ? JSON.parse(localStorage.getItem('auth-storage')!).state.token : ''}`
            }
          })
          if (response.ok) {
            const data = await response.json()
            counts[entity.id] = Array.isArray(data) ? data.length : data.count || 0
          } else {
            counts[entity.id] = 0
          }
        } catch (error) {
          console.error(`Erreur lors du chargement des ${entity.id}:`, error)
          counts[entity.id] = 0
        }
      }
      setEntityCounts(counts)
    }

    loadEntityCounts()
  }, [])

  // Filtrage des données
  const filteredData = data.filter((item) => {
    const searchLower = searchQuery.toLowerCase()

    if (selectedEntity === "restaurants") {
      return (
        (item.user?.username && item.user.username.toLowerCase().includes(searchLower)) ||
        (item.user?.email && item.user.email.toLowerCase().includes(searchLower)) ||
        (item.type_plat && item.type_plat.toLowerCase().includes(searchLower))
      )
    } else if (selectedEntity === "livreurs") {
      return (
        (item.user?.username && item.user.username.toLowerCase().includes(searchLower)) ||
        (item.user?.email && item.user.email.toLowerCase().includes(searchLower)) ||
        (item.matricule && item.matricule.toLowerCase().includes(searchLower))
      )
    } else if (selectedEntity === "boutiques") {
      return (
        (item.user?.username && item.user.username.toLowerCase().includes(searchLower)) ||
        (item.user?.email && item.user.email.toLowerCase().includes(searchLower))
      )
    } else {
      // users
      return (
        (item.name && item.name.toLowerCase().includes(searchLower)) ||
        (item.email && item.email.toLowerCase().includes(searchLower)) ||
        (item.username && item.username.toLowerCase().includes(searchLower)) ||
        (item.profile && item.profile.toLowerCase().includes(searchLower))
      )
    }
  })

  // Fonction pour recharger les compteurs
  const loadEntityCounts = async () => {
    const counts: {[key: string]: number} = {}
    const entityMappings = {
      users: 'utilisateur',
      restaurants: 'restaurant',
      boutiques: 'boutique',
      livreurs: 'livreur'
    }

    for (const entity of entities) {
      try {
        const endpoint = entityMappings[entity.id as keyof typeof entityMappings]
        const apiUrl = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
          ? `/api${endpoint}/`
          : `http://127.0.0.1:8000${endpoint}/`

        const response = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth-storage') ? JSON.parse(localStorage.getItem('auth-storage')!).state.token : ''}`
          }
        })
        if (response.ok) {
          const data = await response.json()
          counts[entity.id] = Array.isArray(data) ? data.length : data.count || 0
        } else {
          counts[entity.id] = 0
        }
      } catch (error) {
        console.error(`Erreur lors du chargement des ${entity.id}:`, error)
        counts[entity.id] = 0
      }
    }
    setEntityCounts(counts)
  }

  // Création d'une entité
  const handleAddEntity = async () => {
    setIsSubmitting(true)
    try {
      const success = await createEntity(formData)
      if (success) {
        toast({
          title: "Succès",
          description: "L'entité a été créée avec succès.",
        })
        setIsAddModalOpen(false)
        setFormData({})
        // Recharger les compteurs après création
        await loadEntityCounts()
      } else {
        toast({
          title: "Erreur",
          description: "Une erreur s'est produite lors de la création.",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Une erreur inattendue s'est produite.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  // Modification d'une entité
  const handleEditEntity = async () => {
    if (!editingEntity) return
    setIsSubmitting(true)
    try {
      const success = await updateEntity(editingEntity.id, formData)
      if (success) {
        toast({
          title: "Succès",
          description: "L'entité a été modifiée avec succès.",
        })
        setIsEditModalOpen(false)
        setEditingEntity(null)
        setFormData({})
        // Recharger les compteurs après modification
        await loadEntityCounts()
      } else {
        toast({
          title: "Erreur",
          description: "Une erreur s'est produite lors de la modification.",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Une erreur inattendue s'est produite.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const openEditModal = (entity: any) => {
    setEditingEntity(entity)
    setFormData(entity)
    setIsEditModalOpen(true)
  }

  const loadEntrepriseUsers = async () => {
    const users = await getEntrepriseUsers()
    setEntrepriseUsers(users)
  }

  useEffect(() => {
    if (selectedEntity === "restaurants") {
      loadEntrepriseUsers()
    }
  }, [selectedEntity])

  // Rendu des champs du formulaire selon l'entité
  const renderFormFields = () => {
    switch (selectedEntity) {
      case "users":
        return (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="username">Nom d'utilisateur</Label>
                <Input
                  id="username"
                  value={formData.username || ""}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="Entrez le nom d'utilisateur"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email || ""}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="Entrez l'email"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="tel">Téléphone</Label>
                <Input
                  id="tel"
                  type="number"
                  value={formData.tel || ""}
                  onChange={(e) => setFormData({ ...formData, tel: parseInt(e.target.value) || "" })}
                  placeholder="Entrez le numéro de téléphone"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="profile">Profil</Label>
                <Select value={formData.profile || ""} onValueChange={(value) => setFormData({ ...formData, profile: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un profil" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="client">Client</SelectItem>
                    <SelectItem value="entreprise">Entreprise</SelectItem>
                    <SelectItem value="livreur">Livreur</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="password">Mot de passe</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password || ""}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="Entrez le mot de passe"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="quartier">Quartier</Label>
                <Input
                  id="quartier"
                  value={formData.quartier || ""}
                  onChange={(e) => setFormData({ ...formData, quartier: e.target.value })}
                  placeholder="Entrez le quartier"
                />
              </div>
            </div>
          </>
        )

      case "restaurants":
        return (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="user_id">Utilisateur Entreprise</Label>
                <Select
                  value={formData.user_id?.toString() || ""}
                  onValueChange={(value) => setFormData({ ...formData, user_id: parseInt(value) })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un utilisateur entreprise" />
                  </SelectTrigger>
                  <SelectContent>
                    {entrepriseUsers.map((user) => (
                      <SelectItem key={user.id} value={user.id.toString()}>
                        {user.username} ({user.email})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="type_plat">Type de plat</Label>
                <Input
                  id="type_plat"
                  value={formData.type_plat || ""}
                  onChange={(e) => setFormData({ ...formData, type_plat: e.target.value })}
                  placeholder="Entrez le type de plat"
                />
              </div>
            </div>
          </>
        )

      case "livreurs":
        return (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="entreprise">ID Entreprise</Label>
                <Input
                  id="entreprise"
                  type="number"
                  value={formData.entreprise || ""}
                  onChange={(e) => setFormData({ ...formData, entreprise: parseInt(e.target.value) || "" })}
                  placeholder="Entrez l'ID de l'entreprise"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="matricule">Matricule</Label>
                <Input
                  id="matricule"
                  value={formData.matricule || ""}
                  onChange={(e) => setFormData({ ...formData, matricule: e.target.value })}
                  placeholder="Entrez le matricule"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description || ""}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Entrez une description"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="user_username">Nom d'utilisateur</Label>
                <Input
                  id="user_username"
                  value={formData.user?.username || ""}
                  onChange={(e) => setFormData({ ...formData, user: { ...formData.user, username: e.target.value } })}
                  placeholder="Entrez le nom d'utilisateur"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="user_email">Email</Label>
                <Input
                  id="user_email"
                  type="email"
                  value={formData.user?.email || ""}
                  onChange={(e) => setFormData({ ...formData, user: { ...formData.user, email: e.target.value } })}
                  placeholder="Entrez l'email"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="user_tel">Téléphone</Label>
                <Input
                  id="user_tel"
                  type="number"
                  value={formData.user?.tel || ""}
                  onChange={(e) => setFormData({ ...formData, user: { ...formData.user, tel: parseInt(e.target.value) || "" } })}
                  placeholder="Entrez le numéro de téléphone"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="user_password">Mot de passe</Label>
                <Input
                  id="user_password"
                  type="password"
                  value={formData.user?.password || ""}
                  onChange={(e) => setFormData({ ...formData, user: { ...formData.user, password: e.target.value } })}
                  placeholder="Entrez le mot de passe"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="user_quartier">Quartier</Label>
              <Input
                id="user_quartier"
                value={formData.user?.quartier || ""}
                onChange={(e) => setFormData({ ...formData, user: { ...formData.user, quartier: e.target.value } })}
                placeholder="Entrez le quartier"
              />
            </div>
          </>
        )

      case "boutiques":
        return (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="user_username_boutique">Nom d'utilisateur</Label>
                <Input
                  id="user_username_boutique"
                  value={formData.user?.username || ""}
                  onChange={(e) => setFormData({ ...formData, user: { ...formData.user, username: e.target.value } })}
                  placeholder="Entrez le nom d'utilisateur"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="user_email_boutique">Email</Label>
                <Input
                  id="user_email_boutique"
                  type="email"
                  value={formData.user?.email || ""}
                  onChange={(e) => setFormData({ ...formData, user: { ...formData.user, email: e.target.value } })}
                  placeholder="Entrez l'email"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="user_tel_boutique">Téléphone</Label>
                <Input
                  id="user_tel_boutique"
                  type="number"
                  value={formData.user?.tel || ""}
                  onChange={(e) => setFormData({ ...formData, user: { ...formData.user, tel: parseInt(e.target.value) || "" } })}
                  placeholder="Entrez le numéro de téléphone"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="user_quartier_boutique">Quartier</Label>
                <Input
                  id="user_quartier_boutique"
                  value={formData.user?.quartier || ""}
                  onChange={(e) => setFormData({ ...formData, user: { ...formData.user, quartier: e.target.value } })}
                  placeholder="Entrez le quartier"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="user_password_boutique">Mot de passe</Label>
                <Input
                  id="user_password_boutique"
                  type="password"
                  value={formData.user?.password || ""}
                  onChange={(e) => setFormData({ ...formData, user: { ...formData.user, password: e.target.value } })}
                  placeholder="Entrez le mot de passe"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="couleur">Couleur</Label>
                <Input
                  id="couleur"
                  value={formData.couleur || ""}
                  onChange={(e) => setFormData({ ...formData, couleur: e.target.value })}
                  placeholder="Entrez la couleur (ex: #ffffff)"
                />
              </div>
            </div>
          </>
        )

      default:
        return null
    }
  }

  // États de chargement et d'erreur
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Database</h1>
            <p className="text-muted-foreground mt-1">Chargement des données...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Database</h1>
            <p className="text-red-500 mt-1">Erreur: {error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header avec bouton Ajouter */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Database</h1>
          <p className="text-muted-foreground mt-1">Gestion des entités de la plateforme</p>
        </div>

        {/* Modal Ajouter */}
        <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Ajouter
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>
                Ajouter un {entities.find((e) => e.id === selectedEntity)?.name.toLowerCase()}
              </DialogTitle>
              <DialogDescription>
                Remplissez les informations pour créer un nouveau{" "}
                {entities.find((e) => e.id === selectedEntity)?.name.toLowerCase()}.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">{renderFormFields()}</div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddModalOpen(false)}>
                Annuler
              </Button>
              <Button onClick={handleAddEntity} disabled={isSubmitting}>
                {isSubmitting ? "Création..." : "Créer"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Modal Modifier (caché mais prêt) */}
        <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>
                Modifier un {entities.find((e) => e.id === selectedEntity)?.name.toLowerCase()}
              </DialogTitle>
              <DialogDescription>
                Modifiez les informations du{" "}
                {entities.find((e) => e.id === selectedEntity)?.name.toLowerCase()}.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">{renderFormFields()}</div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
                Annuler
              </Button>
              <Button onClick={handleEditEntity} disabled={isSubmitting}>
                {isSubmitting ? "Modification..." : "Modifier"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Cartes d'entités */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {updatedEntities.map((entity) => (
          <Card
            key={entity.id}
            className={`p-6 cursor-pointer transition-all hover:border-primary ${
              selectedEntity === entity.id ? "border-primary bg-primary/5" : ""
            }`}
            onClick={() => setSelectedEntity(entity.id)}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{entity.name}</p>
                <p className="text-2xl font-bold text-foreground mt-1">{entity.count}</p>
              </div>
              <entity.icon className="h-8 w-8 text-muted-foreground" />
            </div>
          </Card>
        ))}
      </div>

      {/* Barre de recherche et tableau */}
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <div className="border border-border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                {selectedEntity === "restaurants" ? (
                  <>
                    <TableHead>ID</TableHead>
                    <TableHead>Propriétaire</TableHead>
                    <TableHead>Type de plat</TableHead>
                    <TableHead>Note</TableHead>
                    <TableHead>Ouvert</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </>
                ) : (
                  <>
                    <TableHead>ID</TableHead>
                    <TableHead>Nom</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Profile</TableHead>
                    <TableHead>Quartier</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </>
                )}
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredData.map((item) => (
                <TableRow key={item.id}>
                  {selectedEntity === "restaurants" ? (
                    <>
                      <TableCell className="font-mono text-sm">#{item.id}</TableCell>
                      <TableCell className="font-medium">
                        {item.user?.username || item.username || "N/A"}
                        {item.user?.email && (
                          <div className="text-sm text-muted-foreground">{item.user.email}</div>
                        )}
                      </TableCell>
                      <TableCell className="text-muted-foreground">{item.type_plat || "N/A"}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{item.rate || 0}/5</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={item.est_ouvert ? "default" : "secondary"}
                          className={item.est_ouvert ? "bg-success/10 text-success border-success/20" : ""}
                        >
                          {item.est_ouvert ? "Ouvert" : "Fermé"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="icon" onClick={() => openEditModal(item)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <Trash2 className="h-4 w-4 text-error" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Confirmer la suppression</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Annuler</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={async () => {
                                    const success = await deleteEntity(item.id)
                                    if (success) {
                                      toast({
                                        title: "Suppression réussie",
                                        description: "L'élément a été supprimé avec succès.",
                                      })
                                    } else {
                                      toast({
                                        title: "Erreur",
                                        description: "Une erreur s'est produite lors de la suppression.",
                                        variant: "destructive",
                                      })
                                    }
                                  }}
                                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                >
                                  Supprimer
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </TableCell>
                    </>
                  ) : (
                    <>
                      <TableCell className="font-mono text-sm">#{item.id}</TableCell>
                      <TableCell className="font-medium">{item.name || item.username || "N/A"}</TableCell>
                      <TableCell className="text-muted-foreground">{item.email || "N/A"}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{item.profile || "N/A"}</Badge>
                      </TableCell>
                      <TableCell>{item.quartier || "N/A"}</TableCell>
                      <TableCell>
                        <Badge
                          variant={item.status === "Actif" ? "default" : "secondary"}
                          className={item.status === "Actif" ? "bg-success/10 text-success border-success/20" : ""}
                        >
                          {item.status || "N/A"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="icon" onClick={() => openEditModal(item)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <Trash2 className="h-4 w-4 text-error" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Confirmer la suppression</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Annuler</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={async () => {
                                    const success = await deleteEntity(item.id)
                                    if (success) {
                                      toast({
                                        title: "Suppression réussie",
                                        description: "L'élément a été supprimé avec succès.",
                                      })
                                      // Recharger les compteurs après suppression
                                      await loadEntityCounts()
                                    } else {
                                      toast({
                                        title: "Erreur",
                                        description: "Une erreur s'est produite lors de la suppression.",
                                        variant: "destructive",
                                      })
                                    }
                                  }}
                                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                >
                                  Supprimer
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </TableCell>
                    </>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  )
}