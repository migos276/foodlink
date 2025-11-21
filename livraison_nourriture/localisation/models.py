from django.db import models
from e_commerce.models import Menu_Plat, Restaurant_Plat
from shop.models import Produit
from users.models import CustomUser, Livreur, Restaurant, Boutique


# Create your models here.
class Position(models.Model):
    nom=models.CharField(max_length=70)
    latitude=models.DecimalField(max_digits=9,decimal_places=6)
    longitude=models.DecimalField(max_digits=9,decimal_places=6)
    description = models.TextField(blank=True, default='aucune consigne')

    def __str__(self):
        return self.nom

class Commande_Plat(models.Model):
    quantite = models.IntegerField()
    prix_total = models.IntegerField()
    rate=models.FloatField(default=0.0)
    description = models.TextField(blank=True, default='aucune description')
    plat_commander = models.ForeignKey(Restaurant_Plat, on_delete=models.PROTECT,related_name="commande_plat_set")
    commande=models.ForeignKey("CommandeRestaurant", on_delete=models.PROTECT,related_name="commande_plat_set")
    rating_count = models.FloatField(default=0.0)
    rating_sum = models.FloatField(default=0.0)


class CommandeRestaurant(models.Model):
    STATUTS_LIST=[
        ("Attente","attente"),
        ("Préparation","préparation"),
        ("Livraison","livraison"),
        ("Réçu","réçu"),
        ("Annulé","annulé")
    ]
    position=models.ForeignKey(Position,on_delete=models.PROTECT,related_name="commandes")
    client=models.ForeignKey(CustomUser,on_delete=models.PROTECT,related_name="commandes")
    restaurant=models.ForeignKey(Restaurant,on_delete=models.PROTECT,related_name="commandes",default=1)
    statut=models.CharField(max_length=15,choices=STATUTS_LIST,default="attente")#en attente, en livraison, terminé
    heure_de_commande=models.DateTimeField(auto_now_add=True)
    jour=models.IntegerField()
    mois=models.IntegerField()
    annee=models.IntegerField()
    type=models.CharField(default="restaurant",max_length=11)
    plats=models.ManyToManyField(Restaurant_Plat,through=Commande_Plat,related_name="commandes")
    prix_de_livraison = models.IntegerField(default=0)
    prix_total = models.IntegerField(default=0)



class Commande_Produit(models.Model):
    quantite = models.IntegerField()
    prix_total = models.IntegerField()
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT,related_name="command_produit")
    commande=models.ForeignKey("CommandeBoutique", on_delete=models.PROTECT,related_name="command_produit")


class CommandeBoutique(models.Model):
    STATUTS_LIST=[
        ("Attente","attente"),
        ("Préparation","préparation"),
        ("Livraison","livraison"),
        ("Réçu","réçu"),
        ("Annulé","annulé")
    ]
    position=models.ForeignKey(Position,on_delete=models.PROTECT,related_name="commandes_produits")
    client=models.ForeignKey(CustomUser,on_delete=models.PROTECT,related_name="commandes_produits")
    boutique = models.ForeignKey(Boutique, on_delete=models.PROTECT, related_name="commandes", default=1)
    statut=models.CharField(max_length=15,choices=STATUTS_LIST,default="attente")#en attente, en livraison, terminé
    heure_de_commande=models.DateTimeField(auto_now_add=True)
    jour=models.IntegerField()
    mois=models.IntegerField()
    annee=models.IntegerField()
    type = models.CharField(default="boutique",max_length=9)
    produits=models.ManyToManyField(Produit,through=Commande_Produit)
    prix_total = models.IntegerField(default=0)
    prix_de_livraison= models.IntegerField(default=0)

class Livraison (models.Model):
    STATUTS_LIST = [
        ("attente", "Attente"),
        ("accepter", "Accepter"),
        ("en route", "En route"),
        ("livré", "Livré"),
        ("refuser", "Refuser")
    ]
    commande=models.ForeignKey(CommandeRestaurant, on_delete=models.CASCADE, related_name="livraison")
    livreur=models.ForeignKey(Livreur,on_delete=models.CASCADE, related_name="livraison",null=True,default=None)
    statut = models.CharField(max_length=15, choices=STATUTS_LIST,default="attente")  # en attente, en livraison, terminé
    heure_de_reception = models.DateTimeField(auto_now_add=True,null=True)
    heure_de_delivrance=models.DateTimeField(null=True,default=None)
class LivraisonBoutique (models.Model):
    STATUTS_LIST = [
        ("attente", "Attente"),
        ("accepter", "Accepter"),
        ("en route", "En route"),
        ("livré", "Livré"),
        ("refuser", "Refuser")
    ]
    commande=models.ForeignKey(CommandeBoutique, on_delete=models.CASCADE, related_name="livraison")
    livreur=models.ForeignKey(Livreur,on_delete=models.CASCADE, related_name="livraison_boutique",null=True,default=None)
    statut = models.CharField(max_length=15, choices=STATUTS_LIST,
                              default="attente")  # en attente, en livraison, terminé
    heure_de_reception = models.DateTimeField(auto_now_add=True,null=True)
    heure_de_delivrance = models.DateTimeField(null=True, default=None)
