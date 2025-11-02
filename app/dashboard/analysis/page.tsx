"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Clock, TrendingUp, AlertTriangle, CheckCircle2, XCircle, Users, DollarSign } from "lucide-react"
import { useAnalysis } from "@/hooks/useAnalysis"

export default function AnalysisPage() {
  const { analysis: analysisData, loading: isLoading, error } = useAnalysis()

  const kpiData = [
    {
      title: "Commandes Aujourd'hui",
      value: analysisData?.kpiData?.orders_today?.toString() || "0",
      status: "success",
      icon: CheckCircle2,
    },
    {
      title: "Commandes en Attente >1h",
      value: analysisData?.kpiData?.pending_orders_over_1h?.toString() || "0",
      status: "error",
      icon: AlertTriangle,
    },
    {
      title: "Temps Moyen de Préparation",
      value: analysisData?.kpiData?.avg_prep_time || "N/A",
      status: "success",
      icon: Clock,
    },
    {
      title: "Commandes Livrées à Temps",
      value: analysisData?.kpiData?.on_time_delivery_rate || "N/A",
      status: "success",
      icon: TrendingUp,
    },
  ]

  const alerts = analysisData?.alerts || []

  const restaurantPerformance = analysisData?.restaurant_performance || []

  const deliveryPerformance = analysisData?.delivery_performance || []

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Analyse</h1>
          <p className="text-muted-foreground mt-1">Chargement des données...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Analyse</h1>
          <p className="text-error mt-1">Erreur lors du chargement des données</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Analyse</h1>
        <p className="text-muted-foreground mt-1">Suivi en temps réel de la performance opérationnelle</p>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiData.map((kpi, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{kpi.title}</p>
                <p className="text-2xl font-bold text-foreground mt-1">{kpi.value}</p>
              </div>
              <div
                className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  kpi.status === "success"
                    ? "bg-success/10"
                    : kpi.status === "warning"
                      ? "bg-warning/10"
                      : "bg-error/10"
                }`}
              >
                <kpi.icon
                  className={`h-6 w-6 ${
                    kpi.status === "success" ? "text-success" : kpi.status === "warning" ? "text-warning" : "text-error"
                  }`}
                />
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alerts */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">Alertes & Anomalies</h3>
            <Badge variant="destructive">{alerts.length}</Badge>
          </div>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-lg border ${
                  alert.type === "error" ? "border-error/20 bg-error/5" : "border-warning/20 bg-warning/5"
                }`}
              >
                <div className="flex items-start gap-3">
                  {alert.type === "error" ? (
                    <XCircle className="h-5 w-5 text-error flex-shrink-0 mt-0.5" />
                  ) : (
                    <AlertTriangle className="h-5 w-5 text-warning flex-shrink-0 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm text-foreground">{alert.message}</p>
                    <p className="text-xs text-muted-foreground mt-1">{alert.time}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Financial Overview */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Finances & Revenus</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-success/10 rounded-lg flex items-center justify-center">
                  <DollarSign className="h-5 w-5 text-success" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Revenu Total du Jour</p>
                  <p className="text-xl font-bold text-foreground">{analysisData?.financial?.revenue_today ? `${analysisData.financial.revenue_today}€` : 'N/A'}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Commissions Plateforme</p>
                  <p className="text-xl font-bold text-foreground">{analysisData?.financial?.commissions ? `${analysisData.financial.commissions}€` : 'N/A'}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                  <Users className="h-5 w-5 text-accent" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Moyenne Panier Client</p>
                  <p className="text-xl font-bold text-foreground">{analysisData?.financial?.avg_basket ? `${analysisData.financial.avg_basket}€` : 'N/A'}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Restaurant Performance */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Performance des Restaurants</h3>
          <div className="space-y-3">
            {restaurantPerformance.map((restaurant, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      restaurant.status === "success"
                        ? "bg-success"
                        : restaurant.status === "warning"
                          ? "bg-warning"
                          : "bg-error"
                    }`}
                  />
                  <div>
                    <p className="font-medium text-foreground">{restaurant.name}</p>
                    <p className="text-sm text-muted-foreground">Temps moyen: {restaurant.avgTime}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1">
                    <span className="text-sm font-medium text-foreground">{restaurant.rating}</span>
                    <svg className="w-4 h-4 text-accent" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Delivery Performance */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Performance des Livreurs</h3>
          <div className="space-y-3">
            {deliveryPerformance.map((delivery, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-primary-foreground">
                      {delivery.name.split(" ")[0][0]}
                      {delivery.name.split(" ")[1][0]}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium text-foreground">{delivery.name}</p>
                    <p className="text-sm text-muted-foreground">{delivery.deliveries} livraisons</p>
                  </div>
                </div>
                <Badge
                  variant={
                    delivery.status === "success"
                      ? "default"
                      : delivery.status === "warning"
                        ? "secondary"
                        : "destructive"
                  }
                  className={
                    delivery.status === "success"
                      ? "bg-success/10 text-success border-success/20"
                      : delivery.status === "warning"
                        ? "bg-warning/10 text-warning border-warning/20"
                        : ""
                  }
                >
                  {delivery.onTime} à temps
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
