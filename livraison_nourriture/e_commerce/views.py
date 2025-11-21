from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets,filters,status,generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from localisation.models import CommandeRestaurant, CommandeBoutique
from localisation.serializer import CommandeSerializer
from shop.models import Produit
from users.models import Restaurant, Boutique
from users.serializer import RestaurantSerializer, BoutiqueSerializer
from .models import Menu, Plat, MenuHebdomadaire, Menu_Plat, MenuStatique, Restaurant_Plat, MenuStatique_Plat
from .serializer import MenuSerializer, PlatSerializer, MenuHebdomadaireSerializer, MenuPlatSerializer, \
    CurrentMenuSerializer, MenuStatiqueSerializer, RestaurantPlatSerializer, MenuStatiquePlatSerializer


class PlatViewSet(viewsets.ModelViewSet):
    queryset = Plat.objects.all()
    serializer_class = PlatSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields=["nom","id"]

class MenuPlatViewSet(viewsets.ModelViewSet):
    queryset = Menu_Plat.objects.all()
    serializer_class = MenuPlatSerializer

class MenuStatiquePlatViewSet(viewsets.ModelViewSet):
    queryset = MenuStatique_Plat.objects.all()
    serializer_class = MenuStatiquePlatSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['plat__plat__nom', 'description']
    filterset_fields = ['prix', 'plat__rate']

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['plats__menu_plat__plat__nom']
    filterset_fields = ['jour']

class MenuHebdomadaireViewSet(viewsets.ModelViewSet):
    queryset = MenuHebdomadaire.objects.all()
    serializer_class = MenuHebdomadaireSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['menus__plats__plat__nom','menus__jour']
    filterset_fields = ['menus__jour', 'restaurant__id']
class CurrentMenuView(APIView):

    def get(self,request):
        quartier = request.query_params.get('quartier', None)
        type_cuisine = request.query_params.get('type_cuisine', None)
        search = request.query_params.get('search', None)
        ouvert = request.query_params.get('ouvert', None)
        prix = request.query_params.get('prix', None)
        jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        today_index = timezone.localdate().weekday()  # plus sûr que datetime.today()
        today_str = jours[today_index]
        print("😁",today_str)
        queryset =Menu_Plat.objects.filter(menu__jour=today_str)
        queryset =queryset.filter(plat__is_avialable=True)

        if search:
            queryset = queryset.filter(Q(plat__plat__nom__icontains=search) | Q(description__icontains=search))

            if quartier:
                queryset = queryset.filter(menu__menu_hebdo__restaurant__user__quartier__icontains=quartier)
            if type_cuisine:
                queryset = queryset.filter(menu__menu_hebdo__restaurant__type_plat__iexact=type_cuisine)
            if ouvert is not None:
                if ouvert.lower == "true":
                    queryset = queryset.filter(menu__menu_hebdo__restaurant__est_ouvert=True)
                else:
                    queryset = queryset.filter(menu__menu_hebdo__restaurant__est_ouvert=False)
            if prix:
                queryset = queryset.filter(prix__lte=int(prix))

            queryset = queryset.distinct()
        serializer = CurrentMenuSerializer(queryset, many=True)
        return Response(serializer.data)


class MenuStatiqueViewSet(viewsets.ModelViewSet):
    queryset = MenuStatique.objects.all()
    serializer_class = MenuStatiqueSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['restaurant__id']
    search_fields = ['plats__plat__nom','plats__description']



class RestaurantPlatViewSet(viewsets.ModelViewSet):
    queryset = Restaurant_Plat.objects.all()
    serializer_class = RestaurantPlatSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['restaurant__id','plat__id']
    search_fields = ['plat__nom']

class MesPlatsView(generics.ListAPIView):
    serializer_class = RestaurantPlatSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['plat__nom']

    def get_queryset(self):
        restaurant_id=self.kwargs.get('restaurant_id')
        return Restaurant_Plat.objects.filter(restaurant_id=restaurant_id)

class MesCommandeRestauView(generics.ListAPIView):
    serializer_class = CommandeSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['statut']

    def get_queryset(self):
        restaurant_id=self.kwargs.get('restaurant_id')
        return CommandeRestaurant.objects.filter(restaurant=restaurant_id)

class UserCommandeRestauView(generics.ListAPIView):
    serializer_class = CommandeSerializer
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter]
    filterset_fields = ['statut']

    def get_queryset(self):
        user_id=self.kwargs.get('user_id')
        return CommandeRestaurant.objects.filter(client=user_id)

class UserCommandeShopView(generics.ListAPIView):
    serializer_class = CommandeSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['statut']

    def get_queryset(self):
        user_id=self.kwargs.get('user_id')
        return CommandeBoutique.objects.filter(client=user_id)


class ClearMenuView(APIView):
    def delete(self,request,id):
        try:
            menu=Menu.objects.get(id=id)
            menu.menu_plat.all().delete()
            return Response({"message":"Tous les plats ont été supprimés"},status=status.HTTP_200_OK)
        except Menu.DoesNotExist:
            return Response({"error":"Menu introuvable."},status=status.HTTP_404_NOT_FOUND)

class ClearMenuStatiqueView(APIView):
    def delete(self,request,id):
        try:
            menu=MenuStatique.objects.get(id=id)
            menu.plats.all().delete()
            return Response({"message":"Tous les plats ont été supprimés"},status=status.HTTP_200_OK)
        except MenuStatique.DoesNotExist:
            return Response({"error":"Menu introuvable."},status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def plats_pas_cher_menu_du_jour(request):
    prix_max = request.data.get('prix_max', 2000)
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    today_index = timezone.localdate().weekday()  # plus sûr que datetime.today()
    today_str = jours[today_index]
    plats = Menu_Plat.objects.filter(
        prix__lte=prix_max,
        menu__jour=today_str
    ).distinct()

    serializer = MenuPlatSerializer(plats, many=True)
    return Response(serializer.data)

class RestaurantFilterAPIView(APIView):
    def get(self,request):
        quartier=request.query_params.get('quartier',None)
        type_cuisine = request.query_params.get('type_cuisine', None)
        search = request.GET.get('search', None)
        rate = request.query_params.get('rate', None)
        ouvert = request.query_params.get('ouvert', None)
        queryset=Restaurant.objects.all()
        if search:
            queryset=queryset.filter(user__username__icontains=search)
            if quartier:
                queryset=queryset.filter(user__quartier__icontains=quartier)
            if type_cuisine:
                queryset = queryset.filter(type_plat__icontains=type_cuisine)
            if ouvert is not None:
                if ouvert.lower == "true":
                    queryset = queryset.filter(est_ouvert=True)
                else:
                    queryset = queryset.filter(est_ouvert=False)
        queryset = queryset.distinct()
        serializer=RestaurantSerializer(queryset,many=True)
        return Response(serializer.data)


class BoutiqueFilterAPIView(APIView):
    def get(self, request):
        quartier = request.query_params.get('quartier', None)
        search = request.query_params.get('search', None)
        rate = request.query_params.get('rate', None)
        ouvert = request.query_params.get('ouvert', None)
        prix = request.query_params.get('prix', None)
        queryset = Boutique.objects.all()
        if search:
            queryset = queryset.filter(user__username__icontains=search)
            if quartier:
                queryset = queryset.filter(user__quartier__icontains=quartier)
            if ouvert is not None:
                if ouvert.lower == "true":
                    queryset = queryset.filter(est_ouvert=True)
                else:
                    queryset = queryset.filter(est_ouvert=False)
            queryset = queryset.distinct()
            serializer = BoutiqueSerializer(queryset, many=True)
            return Response(serializer.data)

class PlatFilterAPIView(APIView):
    def get(self, request):
        quartier = request.query_params.get('quartier', None)
        type_cuisine = request.query_params.get('type_cuisine', None)
        search = request.query_params.get('search', None)
        ouvert = request.query_params.get('ouvert', None)
        prix = request.query_params.get('prix', None)
        queryset = MenuStatique_Plat.objects.all()
        if search:
            queryset = queryset.filter(Q(plat__plat__nom__icontains=search)| Q(description__icontains=search))

            if quartier:
                queryset = queryset.filter(menu__restaurant__user__quartier__icontains=quartier)
            if type_cuisine:
                queryset = queryset.filter(menu__restaurant__type_plat__iexact=type_cuisine)
            if ouvert is not None:
                if ouvert.lower == "true":
                    queryset = queryset.filter(menu__restaurant__est_ouvert=True)
                else:
                    queryset = queryset.filter(menu__restaurant__est_ouvert=False)
            if prix:
                queryset = queryset.filter(prix__lte=int(prix))


            queryset = queryset.distinct()
            serializer = MenuStatiquePlatSerializer(queryset, many=True)
            return Response(serializer.data)


class ProduitFilterAPIView(APIView):
    def get(self, request):
        quartier = request.query_params.get('quartier', None)
        search = request.query_params.get('search', None)
        ouvert = request.query_params.get('ouvert', None)
        prix = request.query_params.get('prix', None)
        queryset = Produit.objects.all()
        if search:
            queryset = queryset.filter(Q(rayon__nom__icontains=search) | Q(nom__icontains=search))

            if quartier:
                queryset = queryset.filter(rayon__boutique__user__quartier__icontains=quartier)
            if ouvert is not None:
                if ouvert.lower == "true":
                    queryset = queryset.filter(rayon__boutique__est_ouvert=True)
                else:
                    queryset = queryset.filter(rayon__boutique__est_ouvert=False)
            if prix:
                queryset = queryset.filter(prix__lte=int(prix))

            queryset = queryset.distinct()
            serializer = MenuStatiquePlatSerializer(queryset, many=True)
            return Response(serializer.data)
