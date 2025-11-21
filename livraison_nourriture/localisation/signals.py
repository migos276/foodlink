from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CommandeRestaurant
from services.supabase_service import send_to_supabase
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import  CommandeRestaurant, CommandeBoutique, Livraison,Commande_Plat, Commande_Produit
from supabase_client import supabase

'''
# --- POSITIONS ---

# --- COMMANDES RESTAURANT ---
@receiver(post_save, sender=CommandeRestaurant)
def sync_commande_restaurant(sender, instance, created, **kwargs):
    data = {
        "id": instance.id,
        "client_id": instance.client.id,
        "restaurant_id": instance.restaurant.id,
        "position_id": instance.position.id,
        "statut": instance.statut,
        "prix_total": instance.prix_total,
        "jour": instance.jour,
        "mois": instance.mois,
        "annee": instance.annee,
    }
    send_to_supabase("commandes_restaurant_realtime", data, instance.id)


# --- COMMANDES BOUTIQUE ---
@receiver(post_save, sender=CommandeBoutique)
def sync_commande_boutique(sender, instance, created, **kwargs):
    data = {
        "id": instance.id,
        "client_id": instance.client.id,
        "boutique_id": instance.boutique.id,
        "position_id": instance.position.id,
        "statut": instance.statut,
        "prix_total": instance.prix_total,
        "jour": instance.jour,
        "mois": instance.mois,
        "annee": instance.annee,
    }
    send_to_supabase("commandes_boutique_realtime", data, instance.id)


# --- COMMANDES PLATS ---
@receiver(post_save, sender=Commande_Plat)
def sync_commande_plat(sender, instance, created, **kwargs):
    data = {
        "id": instance.id,
        "commande_id": instance.commande.id,
        "plat_id": instance.plat_commander.id,
        "quantite": instance.quantite,
        "prix_total": instance.prix_total,
        "rate": instance.rate,
    }
    send_to_supabase("commande_plats_realtime", data, instance.id)


# --- COMMANDES PRODUITS ---
@receiver(post_save, sender=Commande_Produit)
def sync_commande_produit(sender, instance, created, **kwargs):
    data = {
        "id": instance.id,
        "commande_id": instance.commande.id,
        "produit_id": instance.produit.id,
        "quantite": instance.quantite,
        "prix_total": instance.prix_total,
    }
    send_to_supabase("commande_produits_realtime", data, instance.id)


# --- LIVRAISONS ---
@receiver(post_save, sender=Livraison)
def sync_livraison(sender, instance, created, **kwargs):
    data = {
        "id": instance.id,
        "commande_id": instance.commande.id,
        "livreur_id": instance.livreur.id,
    }
    send_to_supabase("livraisons_realtime", data, instance.id)'''