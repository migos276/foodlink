from datetime import date

from django.db.models import Count,Sum
from django.shortcuts import render, get_object_or_404
# Create your views here.
from datetime import datetime
from django.utils import timezone
from rest_framework import viewsets,filters,status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError, NotAcceptable, PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from e_commerce.models import Restaurant_Plat
from shop.models import Produit
from users.models import CustomUser, Restaurant, Livreur
from .models import Livraison, CommandeRestaurant, Commande_Plat, CommandeBoutique, Commande_Produit, LivraisonBoutique, \
    Position
from .serializer import CommandeSerializer, CommandePlatSerializer, CommandeBoutiqueSerializer, \
    CommandeProduitSerializer, LivraisonRestauSerializer, LivraisonBoutiqueSerializer, PositionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models.functions import TruncDate
from django.db.models import F
from django.utils.dateparse import parse_date


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class CommadePlatViewSet(viewsets.ModelViewSet):
    queryset = Commande_Plat.objects.all()
    serializer_class = CommandePlatSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['commande_id']
    def create(self, request, *args, **kwargs):
        plat_id=request.data.get("plat")
        try:
            plat=Restaurant_Plat.objects.get(id=plat_id)
        except Restaurant_Plat.DoesNotExist:
            raise ValidationError( "plat introuvable")
        if not plat.is_avialable:
            raise PermissionDenied(f"Le plat {plat.nom} n'est pas disponible pour le moment.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommadeProduitViewSet(viewsets.ModelViewSet):
    queryset = Commande_Produit.objects.all()
    serializer_class = CommandeProduitSerializer
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
            raise ValidationError("Impossible de supprimer cette commande car elle a déjà été validé")
        else:
            return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):

        restaurant_id=request.data.get("restaurant")
        try:
            restaurant=Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            raise ValidationError("Restaurant introuvable")

        if not restaurant.est_ouvert:
            raise NotAcceptable( "Le restaurant est actuellement fermé")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class CommandeBoutiqueViewSet(viewsets.ModelViewSet):
    queryset = CommandeBoutique.objects.all()
    serializer_class = CommandeBoutiqueSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['statut','jour','mois','annee']
    def destroy(self, request, *args, **kwargs):
        commande=self.get_object()
        if commande.statut!="attente":
            raise NotAcceptable("Impossible de supprimer cette commande car elle a déjà été validé")
        else:
            return super().destroy(request, *args, **kwargs)


class LivraisonViewSet(viewsets.ModelViewSet):
    queryset = Livraison.objects.all()
    serializer_class = LivraisonRestauSerializer
class LivraisonBoutiqueViewSet(viewsets.ModelViewSet):
    queryset = LivraisonBoutique.objects.all()
    serializer_class = LivraisonBoutiqueSerializer

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

class LivreurLivraisonsView(APIView):
    def get(self, request, livreur_id):
        etat = request.query_params.get('statut', None)

        livreur=get_object_or_404(Livreur,pk=livreur_id)
        if livreur.est_a_personne:
            livraisons_restau = Livraison.objects.filter(livreur_id__isnull=True)
            livraisons_boutique = LivraisonBoutique.objects.filter(livreur_id__isnull=True)
        else:
            livraisons_restau = Livraison.objects.filter(livreur_id=livreur_id)
            livraisons_boutique = LivraisonBoutique.objects.filter(livreur_id=livreur_id)

        if etat:
            livraisons_restau = livraisons_restau.filter(statut__iexact=etat)
            livraisons_boutique = livraisons_boutique.filter(statut__iexact=etat)

        data_restau = LivraisonRestauSerializer(livraisons_restau, many=True).data
        data_boutique = LivraisonBoutiqueSerializer(livraisons_boutique, many=True).data
        combined = sorted(data_restau + data_boutique, key=lambda x: x['commande']["id"], reverse=True)

        return Response(combined, status=status.HTTP_200_OK)
class RestaurantLivraisonsView(APIView):
    def get(self, request, restaurant_id):
        etat = request.query_params.get('statut', None)
        livraisons_restau = Livraison.objects.filter(commande__restaurant=restaurant_id).distinct()
        data_restau = LivraisonRestauSerializer(livraisons_restau, many=True).data
        combined = sorted(data_restau, key=lambda x: x['statut'], reverse=True)

        return Response(combined, status=status.HTTP_200_OK)
class BoutiqueLivraisonsView(APIView):
    def get(self, request, boutique_id):
        etat = request.query_params.get('statut', None)
        livraisons_restau = LivraisonBoutique.objects.filter(commande__boutique=boutique_id).distinct()
        data_restau = LivraisonBoutiqueSerializer(livraisons_restau, many=True).data
        combined = sorted(data_restau, key=lambda x: x['statut'])

        return Response(combined, status=status.HTTP_200_OK)

class RestaurantAnalyseAPIView(APIView):
    def get(self,request,restaurant_id):
        today=date.today()
        commandes=CommandeRestaurant.objects.filter(restaurant=restaurant_id,heure_de_commande__date=today,statut="Réçu")
        data={"total_montant":commandes.aggregate(total=Sum("prix_total"))["total"] or 0,"total_vente":commandes.aggregate(count=Count('id'))["count"] or 0,}
        return Response(data,status=status.HTTP_200_OK)
class BoutiqueAnalyseAPIView(APIView):
    def get(self,request,boutique_id):
        today=date.today()
        commandes=CommandeBoutique.objects.filter(boutique=boutique_id,heure_de_commande__date=today,statut="Réçu")
        data={"total_montant":commandes.aggregate(total=Sum("prix_total"))["total"] or 0,"total_vente":commandes.aggregate(count=Count('id'))["count"] or 0,}
        return Response(data,status=status.HTTP_200_OK)

class RestaurantOrderHistoryAPIView(APIView):
    """
    Returns orders grouped by date:
    {
        "2025-11-09": [...],
        "2025-11-08": [...],
        ...
    }
    """

    def get(self, request, restaurant_id):
        # Filter by restaurant
        #queryset = CommandeRestaurant.objects.filter(restaurant=restaurant_id,statut="Réçu")
        queryset = CommandeRestaurant.objects.filter(restaurant=restaurant_id)

        # Optional: filter by start and end dates
        start_date = request.query_params.get("start")
        end_date = request.query_params.get("end")

        if start_date:
            queryset = queryset.filter(heure_de_commande__date__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(heure_de_commande__date__lte=parse_date(end_date))

        # Group by date
        queryset = queryset.annotate(date=TruncDate("heure_de_commande")).order_by("-date")

        # Serializer
        serializer = CommandeSerializer(queryset, many=True)

        # Build grouped response
        grouped = {}
        for order in serializer.data:
            order_date = order["heure_de_commande"][:10]  # "YYYY-MM-DD"
            if order_date not in grouped:
                grouped[order_date] = []
            grouped[order_date].append(order)

        return Response(grouped, status=status.HTTP_200_OK)


class BoutiqueOrderHistoryAPIView(APIView):
    """
    Returns orders grouped by date:
    {
        "2025-11-09": [...],
        "2025-11-08": [...],
        ...
    }
    """

    def get(self, request, boutique_id):
        # Filter by restaurant
        #queryset = CommandeRestaurant.objects.filter(restaurant=restaurant_id,statut="Réçu")
        queryset = CommandeBoutique.objects.filter(boutique=boutique_id)

        # Optional: filter by start and end dates
        start_date = request.query_params.get("start")
        end_date = request.query_params.get("end")

        if start_date:
            queryset = queryset.filter(heure_de_commande__date__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(heure_de_commande__date__lte=parse_date(end_date))

        # Group by date
        queryset = queryset.annotate(date=TruncDate("heure_de_commande")).order_by("-date")

        # Serializer
        serializer = CommandeBoutiqueSerializer(queryset, many=True)

        # Build grouped response
        grouped = {}
        for order in serializer.data:
            order_date = order["heure_de_commande"][:10]  # "YYYY-MM-DD"
            if order_date not in grouped:
                grouped[order_date] = []
            grouped[order_date].append(order)

        return Response(grouped, status=status.HTTP_200_OK)

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

# dans views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Livraison
from notifications.models import Notification
from services.supabase_service import supabase

class SignalerClientAPIView(APIView):
    def post(self, request, livraison_id):
        try:
            livreur = request.user.livreur
            livraison = Livraison.objects.get(id=livraison_id)

            # Crée une notification dans la base Django
            notification = Notification.objects.create(
                type="signalement de commande ",
                message=f"Le livreur de la commande{livraison.commande.id}, vous signale de venir la recupérer",
                cible=livraison.commande.client.user.id
            )

            # Envoie la notification dans Supabase (Realtime)
            data = {
                "type": notification.type,
                "message": notification.message,
                "cible": notification.cible,
                "timestamp": timezone.now().isoformat(),
            }

            response = supabase.table("notifications").insert(data).execute()

            return Response({
                "success": True,
                "message": "Signal envoyé",
                "supabase_response": response.data
            }, status=status.HTTP_200_OK)

        except Livraison.DoesNotExist:
            return Response({"error": "Livraison introuvable"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
