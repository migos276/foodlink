from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Restaurant_Plat, Menu
from users.models import Restaurant
from services.supabase_service import sync_table

@receiver(post_save, sender=Restaurant)
def sync_restaurant(sender, instance, **kwargs):
    sync_table("restaurants", {
        "id": str(instance.id),
        "nom": instance.nom,
        "logo":str(instance.logo),
        "rate": instance.rating,
        "rating_count": instance.rating_count,
        "rating_sum":instance.rating_sum,
    }, row_id=instance.id)

@receiver(post_save, sender=Restaurant_Plat)
def sync_plat(sender, instance, **kwargs):
    sync_table("plats", {
        "id": str(instance.id),
        "restaurant_id": str(instance.restaurant_id),
        "plat": instance.plat,
        "is_available": instance.is_available,
        "rating": instance.rating,
        "rating_count": instance.rating_count,
        "rating_sum":instance.rating_sum,
        "description": instance.description
    }, row_id=instance.id)

@receiver(post_save, sender=Menu)
def sync_menu_hebdo(sender, instance, **kwargs):
    sync_table("menu_hebdo", {
        "id": str(instance.id),
        "menu_hebdo_id": str(instance.menu_hebdo),
        "jour":str(instance.jour),
        "plats": [str(p.id) for p in instance.plats.all()],
    }, row_id=instance.id)

#**-------------------------

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    CommandeRestaurant, CommandeBoutique, Livraison,
    Position, Commande_Plat, Commande_Produit, Restaurant_Plat
)
from supabase_client import supabase


def send_to_supabase(table, data, id):
    """Insère ou met à jour dans Supabase"""
    try:
        existing = supabase.table(table).select("id").eq("id", id).execute()
        if existing.data:
            supabase.table(table).update(data).eq("id", id).execute()
        else:
            supabase.table(table).insert(data).execute()
    except Exception as e:
        print("⚠ Erreur Supabase:", e)


# --- POSITIONS ---
@receiver(post_save, sender=Position)
def sync_position(sender, instance, created, **kwargs):
    data = {
        "id": instance.id,
        "nom": instance.nom,
        "latitude": float(instance.latitude),
        "longitude": float(instance.longitude),
    }
    send_to_supabase("positions_realtime", data, instance.id)


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
    send_to_supabase("livraisons_realtime", data, instance.id)