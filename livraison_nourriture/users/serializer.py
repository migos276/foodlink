from rest_framework_simplejwt.tokens import Token

from e_commerce.serializer import MenuHebdomadaireSerializer, MenuStatiqueSerializer
from shop.serializer import RayonSerializer
from .models import CustomUser, Restaurant, Livreur, Boutique,Horaire,HoraireHebdomadaire
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser
from .utils import get_unique_code_for_model

User=get_user_model()
class  CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model=CustomUser
        fields=['id','username','email','tel','profile',"password","code","a_restaurant","a_boutique","logo","quartier"]

    def validate(self, data):
        if data.get("profile")=="restaurant":
            if CustomUser.objects.filter(username=data["username"], profile="restaurant").exists():
                raise serializers.ValidationError({"username":"ce restaurant existe déjà"})
        return data
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class  LivreurSerializer(serializers.ModelSerializer):
    user=CustomUserSerializer()
    entreprise= serializers.PrimaryKeyRelatedField( queryset=User.objects.filter(profile="entreprise"),write_only=True)
    class Meta:
        model=Livreur
        fields=["id","entreprise","matricule","description","user","est_a_personne","statut"]

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user_data["profile"] = "livreur"
        user = CustomUserSerializer.create(CustomUserSerializer(), validated_data=user_data)
        livreur=Livreur.objects.create(user=user, **validated_data)
        return livreur

class HoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horaire
        fields = ["id", "ouverture", "fermeture","jour","horaire_hebdo"]

class HoraireHebdoSerializer(serializers.ModelSerializer):
    horaires = HoraireSerializer(many=True, read_only=True)
    class Meta:
        model = HoraireHebdomadaire
        fields = ["id", "horaires"]

    def create(self, validated_data):
        horaire_hebdo = super().create(validated_data)
        jours = [
            'lundi',
            'mardi',
            "mercredi",
            'jeudi',
            'vendredi',
            'samedi',
            'dimanche',
        ]
        for jour in jours:
            Horaire.objects.create(horaire_hebdo=horaire_hebdo,jour=jour)
        return horaire_hebdo

class RestaurantSerializer(serializers.ModelSerializer):
    user=CustomUserSerializer(read_only=True)
    horaire=HoraireHebdoSerializer(read_only=True)
    livreurs = LivreurSerializer(many=True, read_only=True, source="user.livreurs")
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(profile="entreprise"),
        write_only=True,
        source="user"
    )
    menu_hebdo=MenuHebdomadaireSerializer(read_only=True)
    menu_statique=MenuStatiqueSerializer(read_only=True)
    class Meta:
        model= Restaurant
        fields= [ "id","type_plat","horaire","menu_hebdo","menu_statique","user","user_id",'livreurs',"rate","est_ouvert"]
    @transaction.atomic
    def create(self, validated_data):
        # Check if user already has a restaurant
        user = validated_data.get('user')
        if Restaurant.objects.filter(user=user).exists():
            raise serializers.ValidationError({"user": "Cet utilisateur a déjà un restaurant."})

        horaire=HoraireHebdomadaire.objects.create()
        validated_data["horaire"]=horaire
        restaurant=Restaurant.objects.create(**validated_data)
        user.a_restaurant=True
        user.save()
        return restaurant

class BoutiqueSerializer(serializers.ModelSerializer):
    user=CustomUserSerializer()
    horaire = HoraireHebdoSerializer(read_only=True)
    livreurs = LivreurSerializer(many=True, read_only=True, source="user__livreurs")
    rayons=RayonSerializer(many=True,read_only=True)
    class Meta:
        model= Boutique
        fields= [ "id","couleur","user","horaire",'rayons',"est_ouvert","rate","livreurs"]

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user_data["profile"] = "entreprise"
        user = CustomUserSerializer.create(CustomUserSerializer(), validated_data=user_data)
        horaire = HoraireHebdomadaire.objects.create()
        validated_data["horaire"] = horaire
        boutique=Boutique.objects.create(user=user, **validated_data)
        user.a_boutique=True
        user.save()
        return boutique

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'  # Utiliser username au lieu d'email

    @classmethod
    def get_token(cls, user):
        token=super().get_token(user)
        token['profile']=user.profile  # Utiliser profile au lieu de role
        token['username']=user.username
        token['email']=user.email

        return token

class TypePlatSerializer(serializers.Serializer):
    type_plat = serializers.CharField()
