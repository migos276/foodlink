from django.shortcuts import render

from rest_framework import viewsets,filters,status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

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
