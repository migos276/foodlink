from django.shortcuts import render
from rest_framework import viewsets,filters,status,generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework import viewsets,filters,status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from localisation.models import CommandeBoutique
from localisation.serializer import CommandeBoutiqueSerializer
from shop.models import Rayon, Produit
from shop.serializer import RayonSerializer, ProduitSerializer


# Create your views here.

class RayonViewset(viewsets.ModelViewSet):
    queryset = Rayon.objects.all()
    serializer_class = RayonSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom']

class ProduitViewset(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    search_fields = ['nom',"rayon__nom"]
    filterset_fields = ['prix']

    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            commande=serializer.save()
            return Response(self.get_serializer(commande).data,status=status.HTTP_201_CREATED)
        print("Erreur ",serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class MesProduitsView(generics.ListAPIView):
    serializer_class = ProduitSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom']

    def get_queryset(self):
        boutique_id=self.kwargs.get('boutique_id')
        queryset=Produit.objects.filter(rayon__boutique=boutique_id)
        en_stock=self.request.query_params.get('en_stock')

        if en_stock is not None:
            en_stock=en_stock.lower()in ["yes",1,"true",True]
            if en_stock:
                print("❌❌")
                queryset=queryset.filter(quantite__gt=0)
            else:
                queryset = queryset.filter(quantite=0)
        return queryset

class MesCommandeShopView(generics.ListAPIView):
    serializer_class = CommandeBoutiqueSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['statut']

    def get_queryset(self):
        boutique_id=self.kwargs.get('boutique_id')
        return CommandeBoutique.objects.filter(boutique=boutique_id)
