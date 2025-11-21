from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from e_commerce.models import Menu_Plat, Restaurant_Plat
from e_commerce.serializer import PlatSerializer, MenuPlatSerializer, RestaurantPlatSerializer
from shop.models import Produit
from shop.serializer import ProduitSerializer
from users.models import Restaurant, CustomUser, Livreur
from users.serializer import CustomUserSerializer, RestaurantSerializer, LivreurSerializer, BoutiqueSerializer
from .models import Position, CommandeRestaurant, Livraison, Commande_Plat, Commande_Produit, CommandeBoutique, \
    LivraisonBoutique


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ["nom","latitude","longitude","description"]

class CommandePlatSerializer(serializers.ModelSerializer):
    plat_commander = serializers.PrimaryKeyRelatedField(queryset=Restaurant_Plat.objects.all(), write_only=True)
    plat = RestaurantPlatSerializer(read_only=True, source="plat_commander")
    restaurant_id=serializers.IntegerField(source="plat_commander.restaurant.id",read_only=True,min_value=1)
    restaurant = serializers.CharField(source="plat_commander.restaurant.user.username", read_only=True)
    restaurant_tel = serializers.CharField(source="plat_commander.restaurant.user.tel", read_only=True)
    class Meta:
        model=Commande_Plat
        fields=['id',"plat_commander","plat","quantite","prix_total","rate","commande","description","restaurant_id","restaurant","restaurant_tel"]
        extra_kwargs={"commande":{"required":False,"allow_null":True}}

class CommandeProduitSerializer(serializers.ModelSerializer):
    produit_id = serializers.PrimaryKeyRelatedField(queryset=Produit.objects.all(), write_only=True,source="produit")
    produit = ProduitSerializer(read_only=True)
    commande=serializers.PrimaryKeyRelatedField( queryset=CommandeBoutique.objects.all(),write_only=True,required=False)
    boutique_id=serializers.IntegerField(source="produit.rayon.boutique.id",read_only=True,min_value=1)
    boutique = serializers.CharField(source="produit.rayon.boutique.user.username", read_only=True)
    boutique_tel = serializers.CharField(source="produit.rayon.boutique.user.tel", read_only=True)
    class Meta:
        model=Commande_Produit
        fields=['id',"produit_id","produit","quantite","prix_total","commande","boutique_id","boutique","boutique_tel"]
class CommandeSerializer(serializers.ModelSerializer):
    client_id=serializers.PrimaryKeyRelatedField( queryset=CustomUser.objects.all(),write_only=True,source="client")
    plats=CommandePlatSerializer(many=True,read_only=True,source="commande_plat_set")
    client=CustomUserSerializer(read_only=True)
    position=PositionSerializer(read_only=True)
    position_id=serializers.PrimaryKeyRelatedField( queryset=Position.objects.all(),write_only=True,source="position")
    plat_commande = CommandePlatSerializer(many=True, write_only=True,required=False)
    type=serializers.CharField(read_only=True)

    class Meta:
        model=CommandeRestaurant
        fields=['id',"client_id","client","plats","plat_commande","restaurant","position","position_id","prix_total","prix_de_livraison","statut","heure_de_commande","jour","mois","annee","type"]
        read_only_fields=["jour","mois","annee","heure_de_commande"]


    def create(self, validated_data):
        plats_data = validated_data.pop("plat_commande")
        today = timezone.localdate()
        validated_data["jour"]=today.day
        validated_data["mois"] = today.month
        validated_data["annee"] = today.year
        commande = CommandeRestaurant.objects.create(**validated_data)
        for plat_data in plats_data:
            Commande_Plat.objects.create(commande=commande, **plat_data)
        return commande

class CommandeBoutiqueSerializer(serializers.ModelSerializer):
    client_id=serializers.PrimaryKeyRelatedField( queryset=CustomUser.objects.all(),write_only=True,source="client")
    produits=CommandeProduitSerializer(many=True,read_only=True,source="command_produit")
    client=CustomUserSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all(), write_only=True,
                                                     source="position")
    type = serializers.CharField(read_only=True)

    produit_commande = CommandeProduitSerializer(many=True, write_only=True, required=False)

    class Meta:
        model=CommandeBoutique
        fields=['id',"client_id","client","produits","produit_commande","position","position_id","prix_total","prix_de_livraison","statut","heure_de_commande","jour","mois","annee","type"]
        read_only_fields=["jour","mois","annee","heure_de_commande"]


    def create(self, validated_data):
        plats_data = validated_data.pop("produit_commande") if validated_data.get("produit_commande") else []
        today = timezone.localdate()
        validated_data["jour"]=today.day
        validated_data["mois"] = today.month
        validated_data["annee"] = today.year
        commande = CommandeBoutique.objects.create( **validated_data)
        for plat_data in plats_data:
            Commande_Produit.objects.create(commande=commande, **plat_data)
        return commande

class LivraisonRestauSerializer(serializers.ModelSerializer):
    livreur_id=serializers.PrimaryKeyRelatedField(queryset=Livreur.objects.all(), write_only=True,source="livreur")
    commande_id = serializers.PrimaryKeyRelatedField(queryset=CommandeRestaurant.objects.all(), write_only=True, source="commande")

    livreur=LivreurSerializer(read_only=True)
    commande=CommandeSerializer(read_only=True)


    class Meta:
        model=Livraison
        fields=['id',"livreur_id","livreur","commande_id","commande","statut","heure_de_reception","heure_de_delivrance"]
        read_only_fields = ["heure_de_reception","heure_de_delivrance"]
    def create(self, validated_data):
        # Create the Livraison record
        livraison = Livraison.objects.create(**validated_data)

        # Update the associated CommandeRestaurant status
        commande = validated_data['commande']
        commande.statut = "Livraison"
        commande.save(update_fields=["statut"])

        return livraison
class LivraisonBoutiqueSerializer(serializers.ModelSerializer):
    livreur_id=serializers.PrimaryKeyRelatedField(queryset=Livreur.objects.all(), write_only=True,source="livreur")
    commande_id = serializers.PrimaryKeyRelatedField(queryset=CommandeBoutique.objects.all(), write_only=True, source="commande")

    livreur=LivreurSerializer(read_only=True)
    commande=CommandeBoutiqueSerializer(read_only=True)

    class Meta:
        model=LivraisonBoutique
        fields=['id',"livreur_id","livreur","commande_id","commande","statut","heure_de_reception","heure_de_delivrance"]
        read_only_fields = ["heure_de_reception","heure_de_delivrance"]
    def create(self, validated_data):
        # Create the Livraison record
        livraison = LivraisonBoutique.objects.create(**validated_data)

        # Update the associated CommandeRestaurant status
        commande = validated_data['commande']
        commande.statut = "Livraison"
        commande.save(update_fields=["statut"])

        return livraison