from rest_framework_simplejwt.tokens import Token
import cloudinary
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
    password = serializers.CharField(write_only=True, min_length=8,required=False)
    class Meta:
        model=CustomUser
        fields=['id','username','email','tel','profile',"password","code","a_restaurant","a_boutique","logo","quartier"]

    def validate(self, data):
        if data.get("profile")=="restaurant":
            if CustomUser.objects.filter(username=data["username"], profile="restaurant").exists():
                raise serializers.ValidationError({"username":"ce restaurant existe déjà"})
        return data
    def create(self, validated_data):
        password=validated_data.pop('password')
        user=CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        new_logo = validated_data.get("logo", None)
        if new_logo and instance.logo:
            try:
                cloudinary.uploader.destroy(instance.logo.public_id, resource_type="image")
            except:
                pass  # éviter crash si déjà supprimé


        password = validated_data.pop("password", None)

        # Mettre à jour les autres champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Mettre à jour le password seulement s’il est fourni
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class  LivreurSerializer(serializers.ModelSerializer):
    user=CustomUserSerializer(read_only=True,required=False)
    entreprise_nom=serializers.CharField(read_only=True,source="entreprise.username",allow_null=True,allow_blank=True)
    class Meta:
        model=Livreur
        fields=["id","entreprise","entreprise_nom","matricule","description","user","est_a_personne","statut"]



class CreateLivreurSerializer(serializers.ModelSerializer):
    entreprise=serializers.IntegerField(allow_null=True,default=None,required=False)
    matricule=serializers.CharField(max_length=10)
    description=serializers.CharField(max_length=3000)
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'tel', 'profile', "password", "code", "a_restaurant", "a_boutique", "logo",
                  "quartier","entreprise","matricule","description"]


    @transaction.atomic
    def create(self, validated_data):
        entreprise = validated_data.pop("entreprise")
        matricule=validated_data.pop("matricule")
        description=validated_data.pop("description")
        validated_data["profile"] = "livreur"
        user = CustomUserSerializer.create(CustomUserSerializer(), validated_data=validated_data)
        if not entreprise:
            est_a_personne = True
        else:
            est_a_personne = False
        livreur = Livreur.objects.create(user=user,entreprise=entreprise,matricule=matricule,description=description,est_a_personne=est_a_personne)
        return {"user": user, "livreur": livreur}
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
    horaire_id= serializers.PrimaryKeyRelatedField(
        queryset=HoraireHebdomadaire.objects.all(),
        write_only=True,
        source="horaire"
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(profile="entreprise"),
        write_only=True,
        source="user"
    )
    menu_hebdo=MenuHebdomadaireSerializer(read_only=True)
    menu_statique=MenuStatiqueSerializer(read_only=True)
    class Meta:
        model= Restaurant
        fields= [ "id","type_plat","horaire","horaire_id","menu_hebdo","menu_statique","user","user_id",'livreurs',"rate","est_ouvert"]
    @transaction.atomic
    def create(self, validated_data):
        horaire=HoraireHebdomadaire.objects.create()
        validated_data["horaire_id"]=horaire.id
        restaurant=Restaurant.objects.create(**validated_data)
        user = restaurant.user
        user.a_restaurant=True
        user.save()
        return restaurant

class BoutiqueSerializer(serializers.ModelSerializer):
    user=CustomUserSerializer(read_only=True)
    horaire = HoraireHebdoSerializer(read_only=True)
    livreurs = LivreurSerializer(many=True, read_only=True, source="user.livreurs")

    horaire_id=serializers.PrimaryKeyRelatedField(
        queryset=HoraireHebdomadaire.objects.all(),
        write_only=True,
        source="horaire"
    )

    user_id =serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        write_only=True,
        source="user"
    )
    rayons=RayonSerializer(many=True,read_only=True)
    class Meta:
        model= Boutique
        fields= [ "id","couleur" ,"user_id","user","horaire","horaire_id",'rayons',"est_ouvert","type","rate","livreurs"]
        read_only_fields = ["user","horaire",'rayons',"est_ouvert","rate","livreurs"]
    def create(self, validated_data):
        horaire = HoraireHebdomadaire.objects.create()
        validated_data["horaire_id"] = horaire.id
        print(validated_data)
        boutique=Boutique.objects.create(**validated_data)
        user = boutique.user
        user.a_boutique=True
        user.save()
        return boutique

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # ✅ Claims personnalisées
        token["profile"] = user.profile
        token["username"] = user.username

        return token

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # ✅ Authentifier via email
        user = authenticate(
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                {"detail": "Identifiants incorrects ou compte inactif."}
            )

        # ✅ Appeler SimpleJWT pour générer refresh / access
        data = super().validate(attrs)

        # ✅ Ajouter infos utilisateur dans la réponse
        data["user"] = {
            "id": user.id,
            "email": user.email,
            "profile": user.profile,
            "username": user.username,
        }

        return data
class TypePlatSerializer(serializers.Serializer):
    type_plat = serializers.CharField()
class TypeBoutiqueSerializer(serializers.Serializer):
    type = serializers.CharField()