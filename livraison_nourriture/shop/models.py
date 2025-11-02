from cloudinary.models import CloudinaryField
from django.db import models
from users.models import Boutique

# Create your models here.


class Rayon(models.Model):
    nom=models.CharField(max_length=300)
    boutique=models.ForeignKey(Boutique,on_delete=models.CASCADE,related_name="rayons")
    def __str__(self):
        return f"{self.nom}"

class Produit(models.Model):
    nom=models.CharField(max_length=70)
    prix=models.IntegerField()
    unite=models.CharField(max_length=30)
    image=CloudinaryField("image")
    quantite=models.IntegerField()
    rayon=models.ForeignKey(Rayon,on_delete=models.CASCADE,related_name="produits")

    def __str__(self):
        return f"{self.nom}"
