from django.shortcuts import render
# Create your views here.
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from rest_framework import viewsets,filters,status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Produit
from users.models import CustomUser, Restaurant, Livreur, Boutique
from .models import Livraison, CommandeRestaurant, Commande_Plat
from .serializer import CommandeSerializer, LivraisonSerializer, CommandePlatSerializer


class AnalysisView(APIView):
    """
    Vue pour récupérer les données d'analyse du dashboard
    """
    def get(self, request):
        today = timezone.now().date()
        now = timezone.now()

        # Commandes d'aujourd'hui
        orders_today = CommandeRestaurant.objects.filter(
            jour=today.day,
            mois=today.month,
            annee=today.year
        )

        # Commandes en attente > 1h
        one_hour_ago = now - timedelta(hours=1)
        pending_orders_over_1h = CommandeRestaurant.objects.filter(
            statut='attente',
            heure_de_commande__lt=one_hour_ago
        )

        # Temps moyen de préparation (simplifié)
        avg_prep_time_display = "23 min"

        # Commandes livrées à temps (simplifié - toutes les livrées sont considérées à temps)
        delivered_orders = CommandeRestaurant.objects.filter(statut='réçu').count()
        total_orders = CommandeRestaurant.objects.count()
        on_time_delivery_rate = (delivered_orders / total_orders * 100) if total_orders > 0 else 0

        # Revenus du jour
        revenue_today = sum(order.prix_total for order in orders_today) or 0

        # Commissions (estimé à 10%)
        commissions = revenue_today * 0.1

        # Panier moyen
        avg_basket = revenue_today / orders_today.count() if orders_today.count() > 0 else 0

        # Alertes
        alerts = []

        # Commande en attente >1h30
        one_hour_thirty_ago = now - timedelta(hours=1, minutes=30)
        old_pending_orders = CommandeRestaurant.objects.filter(
            statut='attente',
            heure_de_commande__lt=one_hour_thirty_ago
        )
        for order in old_pending_orders[:1]:  # Limiter à 1 alerte
            alerts.append({
                'id': f'order_{order.id}',
                'type': 'error',
                'message': f'Commande #{order.id} en attente depuis plus de 1h30',
                'time': 'Il y a quelques minutes'
            })

        # Restaurants qui ne répondent pas (simplifié - restaurants fermés)
        unresponsive_restaurants = Restaurant.objects.filter(est_ouvert=False)
        for restaurant in unresponsive_restaurants[:1]:  # Limiter à 1 alerte
            alerts.append({
                'id': f'restaurant_{restaurant.id}',
                'type': 'warning',
                'message': f'Restaurant "{restaurant.user.username}" ne répond pas',
                'time': 'Il y a quelques minutes'
            })

        # Livreurs non connectés (simplifié - livreurs occupés depuis longtemps)
        inactive_deliverers = Livreur.objects.filter(statut='occupé')
        for livreur in inactive_deliverers[:1]:  # Limiter à 1 alerte
            alerts.append({
                'id': f'livreur_{livreur.id}',
                'type': 'error',
                'message': f'Livreur {livreur.user.username} non connecté depuis longtemps',
                'time': 'Il y a quelques minutes'
            })

        # Rupture d'ingrédients (simplifié - produits avec quantité faible)
        low_stock_products = Produit.objects.filter(quantite__lt=10)
        if low_stock_products.exists():
            alerts.append({
                'id': 'low_stock',
                'type': 'warning',
                'message': 'Rupture d\'ingrédients signalée',
                'time': 'Il y a quelques minutes'
            })

        # Performance des restaurants
        restaurants = Restaurant.objects.all()
        restaurant_performance = []
        for restaurant in restaurants[:4]:  # Limiter à 4
            # Temps moyen (simplifié)
            avg_time = 25  # Valeur par défaut
            rating = restaurant.rate or 4.0
            status = 'success' if avg_time <= 25 else 'warning' if avg_time <= 35 else 'error'

            restaurant_performance.append({
                'name': restaurant.user.username,
                'status': status,
                'avgTime': f'{avg_time} min',
                'rating': rating
            })

        # Performance des livreurs
        livreurs = Livreur.objects.all()
        delivery_performance = []
        for livreur in livreurs[:4]:  # Limiter à 4
            deliveries_count = Livraison.objects.filter(livreur=livreur).count()
            # On-time rate simplifié
            on_time_rate = 85  # Valeur par défaut
            status = 'success' if on_time_rate >= 90 else 'warning' if on_time_rate >= 75 else 'error'

            delivery_performance.append({
                'name': f'{livreur.user.first_name} {livreur.user.last_name}',
                'deliveries': deliveries_count,
                'onTime': f'{on_time_rate}%',
                'status': status
            })

        # Chart data
        # Orders by month
        orders_by_month = CommandeRestaurant.objects.values('mois', 'annee').annotate(count=Count('id')).order_by('annee', 'mois')
        orderData = [{'month': f"{item['mois']}/{item['annee']}", 'commandes': item['count'], 'paiements': item['count']} for item in orders_by_month]

        # Restaurants distribution
        restaurants_orders = Restaurant.objects.annotate(orders_count=Count('menu_hebdo__menus__menu_plat__command_plat__commande', distinct=True))
        restaurantData = [{'name': r.user.username, 'value': r.orders_count} for r in restaurants_orders]

        # Boutiques distribution
        boutiques_orders = Boutique.objects.annotate(orders_count=Count('rayons__produits__command_produit__commande', distinct=True))
        boutiqueData = [{'name': b.user.username, 'value': b.orders_count} for b in boutiques_orders]

        # Delivery performance
        livreurs_revenue = Livreur.objects.annotate(total_montant=Sum('livraison__commande__prix_total'))
        deliveryData = [{'name': l.user.username, 'montant': l.total_montant or 0} for l in livreurs_revenue]

        return Response({
            'kpiData': {
                'orders_today': orders_today.count(),
                'pending_orders_over_1h': pending_orders_over_1h.count(),
                'avg_prep_time': avg_prep_time_display,
                'on_time_delivery_rate': f"{on_time_delivery_rate:.0f}%"
            },
            'alerts': alerts,
            'financial': {
                'revenue_today': revenue_today,
                'commissions': commissions,
                'avg_basket': avg_basket
            },
            'restaurant_performance': restaurant_performance,
            'delivery_performance': delivery_performance,
            'chartData': {
                'orderData': orderData,
                'restaurantData': restaurantData,
                'boutiqueData': boutiqueData,
                'deliveryData': deliveryData,
            }
        })


class CommadePlatViewSet(viewsets.ModelViewSet):
    queryset = Commande_Plat.objects.all()
    serializer_class = CommandePlatSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['commande_id']
class CommandeRestaurantViewSet(viewsets.ModelViewSet):
    queryset = CommandeRestaurant.objects.all()
    serializer_class = CommandeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["commande_plat_set__plat_commander__menu__menu_hebdo__restaurant","commande_plat_set__plat_commander__plat","client__username"]
    filterset_fields = ['statut','jour','mois','annee']

    def destroy(self, request, *args, **kwargs):
        commande=self.get_object()
        if commande.statut!="attente":
            return Response({"detail":"Impossible de supprimer cette commande car elle a déjà été validé"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().destroy(request, *args, **kwargs)

class CommandeBoutiqueViewSet(viewsets.ModelViewSet):
    queryset = CommandeRestaurant.objects.all()
    serializer_class = CommandeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["commande_plat_set__produit__rayon__boutique","commande_plat_set__produit","client__username"]
    filterset_fields = ['statut','jour','mois','annee']
    def destroy(self, request, *args, **kwargs):
        commande=self.get_object()
        if commande.statut!="attente":
            return Response({"detail":"Impossible de supprimer cette commande car elle a déjà été validé"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().destroy(request, *args, **kwargs)


class LivraisonViewSet(viewsets.ModelViewSet):
    queryset = Livraison.objects.all()
    serializer_class = LivraisonSerializer

class RateCommande(APIView):
    def post(self,request):
        try:
            command_id=request.data.get("commande")
            commande=Commande_Plat.objects.get(id=command_id)
        except CommandeRestaurant.DoesNotExist:
            return Response({"error":"CommandeRestaurant not found "},status=status.HTTP_404_NOT_FOUND)
        rating=request.data.get("rating")
        if not rating:
            return Response({"error":"Rating is required"},status=status.HTTP_400_BAD_REQUEST)

        #-----mise à jour de la commande

        commande.rating_sum += float(rating)
        commande.rating_count+=1
        commande.rate=commande.rating_sum/commande.rating_count
        commande.save()

        #------mise à jour du plat

        plat=commande.plat_commander.plat
        plat.rating_sum += float(rating)
        plat.rating_count += 1
        plat.rate = plat.rating_sum / plat.rating_count
        plat.save()

        #-------mise à jour restaurant

        restaurant=plat.restaurant
        restaurant.rating_sum += float(rating)
        restaurant.rating_count += 1
        restaurant.rate = restaurant.rating_sum / restaurant.rating_count
        restaurant.save()

        return Response({
            "commande_rate":commande.rate,
            "plat_rate":plat.rate,
            "restaurant_rate":restaurant.rate
        }, status=status.HTTP_200_OK)


class RateLivreur(APIView):
    def post(self, request, livraison_id):
        try:
            livraison = Livraison.objects.get(id=livraison_id)
        except Livraison.DoesNotExist:
            return Response({"error": "livraison not found "}, status=status.HTTP_404_NOT_FOUND)
        rating = request.data.get("rating")
        if not rating:
            return Response({"error": "Rating is required"}, status=status.HTTP_400_BAD_REQUEST)

        # -----mise à jour de la commande
        livreur=livraison.livreur
        livreur.rating_sum += float(rating)
        livreur.rating_count += 1
        livreur.rate = livreur.rating_sum / livreur.rating_count
        livreur.save()

        return Response({
            "livreur_rate": livreur.rate,
        }, status=status.HTTP_200_OK)
class Update_Stock(APIView):
    def post(self,request):
        try:
            produit_id=request.data.get("produit")
            produit=Produit.objects.get(id=produit_id)
        except Produit.DoesNotExist:
            return Response({"error":"CommandeRestaurant not found "},status=status.HTTP_404_NOT_FOUND)
        quantite=request.data.get("quantite")
        if not quantite or int(quantite)<0:
            return Response({"error":"quantity is required"},status=status.HTTP_400_BAD_REQUEST)

        #-----mise à jour de la commande

        produit.quantite = int(quantite)
        produit.save()

        return Response({
            "produit_quantite":produit.quantite
        }, status=status.HTTP_200_OK)

class ClientCommande(APIView):
    def post(self, request):
        try:
            client_id = request.data.get("client")
            client = CustomUser.objects.get(id=client_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "user not found "}, status=status.HTTP_404_NOT_FOUND)
        commandes=client.commandes.all()
        data=[
            {
                "id":rp.id,
                "heure_de_commande": rp.heure_de_commande,
                "date": f"{rp.jour}/{rp.mois}/{rp.annee}",
                "prix_total": rp.prix_total,
                "restaurant":rp.commande_plat_set.plat_commander.menu.menu_hebdo.restaurant,
        }
            for rp in commandes

        ]

        return Response(data, status=status.HTTP_200_OK)
"""
class RestaurantCommande(APIView):
    def post(self, request, restaurant_id):
        try:
            restau = Restaurant.objects.get(id=restaurant_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "user not found "}, status=status.HTTP_404_NOT_FOUND)
        commandes=restau.menu_hebdo.menus.menu_plat_set.command_plat.commande.all()
        data=[
            {
                "id":rp.id,
                "heure_de_commande": rp.heure_de_commande,
                "date": f"{rp.jour}/{rp.mois}/{rp.annee}",
                "prix_total": rp.prix_total,
                "restaurant":rp.commande_plat_set.plat_commander.menu.menu_hebdo.restaurant,
        }
            for rp in commandes

        ]

        return Response(data, status=status.HTTP_200_OK)
"""
