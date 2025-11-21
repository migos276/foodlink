from rest_framework_simplejwt.tokens import Token
from rest_framework import serializers
from .models import Rayon,Produit

class ProduitSerializer(serializers.ModelSerializer):
    boutique=serializers.CharField(read_only=True,source="rayon.boutique.user.username")
    boutique_id = serializers.IntegerField(read_only=True, source="rayon.boutique.id")
    quartier=serializers.CharField(read_only=True,source="rayon.boutique.user.quartier")

    class Meta:
        model=Produit
        fields=['id',"nom",'prix','unite',"quantite","rayon","image","boutique","boutique_id","quartier"]

class  RayonSerializer(serializers.ModelSerializer):
    produits=ProduitSerializer(read_only=True,many=True)

    class Meta:
        model=Rayon
        fields=['id',"nom",'boutique','produits']

