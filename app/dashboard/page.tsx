"use client"

import { Card } from "@/components/ui/card"
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts"
import { TrendingUp, TrendingDown, DollarSign, ShoppingBag } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useDashboardStats } from "@/hooks/useDashboardStats"
import { useAnalysis } from "@/hooks/useAnalysis"

const COLORS = ["#6366f1", "#f59e0b", "#ef4444", "#10b981"]

export default function StatisticsPage() {
  const { stats, loading, error } = useDashboardStats()
  const { analysis } = useAnalysis()

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Statistiques</h1>
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
            <h1 className="text-3xl font-bold text-foreground">Statistiques</h1>
            <p className="text-red-500 mt-1">Erreur: {error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Statistiques</h1>
          <p className="text-muted-foreground mt-1">Vue d'ensemble de la performance globale</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Jour</Button>
          <Button variant="outline">Semaine</Button>
          <Button variant="outline">Mois</Button>
          <Button>Année</Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Commandes</p>
              <p className="text-2xl font-bold text-foreground mt-1">{stats.totalCommandes}</p>
            </div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <ShoppingBag className="h-6 w-6 text-primary" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Utilisateurs</p>
              <p className="text-2xl font-bold text-foreground mt-1">{stats.totalUsers}</p>
            </div>
            <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-green-500" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Restaurants</p>
              <p className="text-2xl font-bold text-foreground mt-1">{stats.totalRestaurants}</p>
            </div>
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <DollarSign className="h-6 w-6 text-blue-500" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Revenus Totaux</p>
              <p className="text-2xl font-bold text-foreground mt-1">{stats.totalRevenue}€</p>
            </div>
            <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
              <TrendingDown className="h-6 w-6 text-purple-500" />
            </div>
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Line Chart - Orders */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Évolution des Commandes</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analysis?.chartData?.orderData || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="month" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1a1a1a",
                  border: "1px solid #333",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="commandes" stroke="#6366f1" strokeWidth={2} name="Commandes" />
              <Line type="monotone" dataKey="paiements" stroke="#f59e0b" strokeWidth={2} name="Paiements" />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Pie Chart - Restaurants */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Répartition par Restaurant</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analysis?.chartData?.restaurantData || []}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {(analysis?.chartData?.restaurantData || []).map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1a1a1a",
                  border: "1px solid #333",
                  borderRadius: "8px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        {/* Pie Chart - Boutiques */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Répartition par Boutique</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analysis?.chartData?.boutiqueData || []}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {(analysis?.chartData?.boutiqueData || []).map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1a1a1a",
                  border: "1px solid #333",
                  borderRadius: "8px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        {/* Bar Chart - Delivery Performance */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Performance des Livreurs</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analysis?.chartData?.deliveryData || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1a1a1a",
                  border: "1px solid #333",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Bar dataKey="montant" fill="#6366f1" name="Montant (€)" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  )
}
