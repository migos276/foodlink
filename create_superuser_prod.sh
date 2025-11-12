#!/bin/bash

# Script pour créer un super utilisateur et des données d'exemple en production
# Utilisation: ./create_superuser_prod.sh

echo "Création d'un super utilisateur et de données d'exemple en production..."

# Variables du super utilisateur
SUPER_USERNAME="Fotso"
SUPER_EMAIL="admin@foodlink237.org"
SUPER_PASSWORD="admin123"
SUPER_TEL="123456789"
SUPER_PROFILE="entreprise"

# Commande pour créer le super utilisateur et des données d'exemple via Docker
docker-compose -f docker-compose.prod.yml exec -T django python manage.py shell -c "
from django.contrib.auth import get_user_model
from users.models import Restaurant, Boutique, Livreur
import os

User = get_user_model()

print('=== CRÉATION DU SUPER UTILISATEUR ===')
# Vérifier si le super utilisateur existe déjà
if User.objects.filter(username='$SUPER_USERNAME').exists():
    print('Le super utilisateur $SUPER_USERNAME existe déjà.')
    superuser = User.objects.get(username='$SUPER_USERNAME')
else:
    try:
        # Créer le super utilisateur avec tous les champs requis
        superuser = User.objects.create_superuser(
            username='$SUPER_USERNAME',
            email='$SUPER_EMAIL',
            password='$SUPER_PASSWORD',
            tel=$SUPER_TEL,
            profile='$SUPER_PROFILE'
        )
        print('Super utilisateur créé avec succès!')
        print(f'Username: {superuser.username}')
        print(f'Email: {superuser.email}')
        print(f'Profile: {superuser.profile}')
        print(f'Téléphone: {superuser.tel}')
    except Exception as e:
        print(f'Erreur lors de la création du superuser: {e}')
        exit(1)

print('')
print('=== CRÉATION DES UTILISATEURS D\'EXEMPLE ===')

# Créer des utilisateurs entreprise pour les restaurants et boutiques
entreprises_data = [
    {'username': 'resto1', 'email': 'resto1@example.com', 'tel': 111111111, 'quartier': 'Centre-ville'},
    {'username': 'resto2', 'email': 'resto2@example.com', 'tel': 222222222, 'quartier': 'Plateau'},
    {'username': 'boutique1', 'email': 'boutique1@example.com', 'tel': 333333333, 'quartier': 'Bonapriso'},
]

entreprises = []
for data in entreprises_data:
    if not User.objects.filter(username=data['username']).exists():
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password='password123',
            tel=data['tel'],
            profile='entreprise',
            quartier=data['quartier']
        )
        entreprises.append(user)
        print(f'Utilisateur entreprise créé: {user.username}')
    else:
        user = User.objects.get(username=data['username'])
        entreprises.append(user)
        print(f'Utilisateur entreprise existe déjà: {user.username}')

print('')
print('=== CRÉATION DES RESTAURANTS ===')

restaurants_data = [
    {'user': entreprises[0], 'type_plat': 'Pizza Italienne'},
    {'user': entreprises[1], 'type_plat': 'Cuisine Camerounaise'},
]

for data in restaurants_data:
    if not Restaurant.objects.filter(user=data['user']).exists():
        restaurant = Restaurant.objects.create(
            user=data['user'],
            type_plat=data['type_plat'],
            est_ouvert=True
        )
        print(f'Restaurant créé: {restaurant.user.username} - {restaurant.type_plat}')
    else:
        restaurant = Restaurant.objects.get(user=data['user'])
        print(f'Restaurant existe déjà: {restaurant.user.username} - {restaurant.type_plat}')

print('')
print('=== CRÉATION DES BOUTIQUES ===')

boutiques_data = [
    {'user': entreprises[2], 'couleur': '#FF6B6B'},
]

for data in boutiques_data:
    if not Boutique.objects.filter(user=data['user']).exists():
        boutique = Boutique.objects.create(
            user=data['user'],
            couleur=data['couleur'],
            est_ouvert=True
        )
        print(f'Boutique créée: {boutique.user.username} - Couleur: {boutique.couleur}')
    else:
        boutique = Boutique.objects.get(user=data['user'])
        print(f'Boutique existe déjà: {boutique.user.username} - Couleur: {boutique.couleur}')

print('')
print('=== CRÉATION DES LIVREURS ===')

# Créer des utilisateurs livreur
livreurs_data = [
    {'username': 'livreur1', 'email': 'livreur1@example.com', 'tel': 444444444, 'matricule': 'LIV001', 'entreprise': entreprises[0]},
    {'username': 'livreur2', 'email': 'livreur2@example.com', 'tel': 555555555, 'matricule': 'LIV002', 'entreprise': entreprises[1]},
]

for data in livreurs_data:
    if not User.objects.filter(username=data['username']).exists():
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password='password123',
            tel=data['tel'],
            profile='livreur',
            quartier='Centre-ville'
        )
        if not Livreur.objects.filter(user=user).exists():
            livreur = Livreur.objects.create(
                user=user,
                matricule=data['matricule'],
                entreprise=data['entreprise'],
                description=f'Livreur expérimenté - {data["matricule"]}'
            )
            print(f'Livreur créé: {livreur.user.username} - Matricule: {livreur.matricule}')
        else:
            livreur = Livreur.objects.get(user=user)
            print(f'Livreur existe déjà: {livreur.user.username} - Matricule: {livreur.matricule}')
    else:
        user = User.objects.get(username=data['username'])
        if not Livreur.objects.filter(user=user).exists():
            livreur = Livreur.objects.create(
                user=user,
                matricule=data['matricule'],
                entreprise=data['entreprise'],
                description=f'Livreur expérimenté - {data["matricule"]}'
            )
            print(f'Livreur créé: {livreur.user.username} - Matricule: {livreur.matricule}')
        else:
            livreur = Livreur.objects.get(user=user)
            print(f'Livreur existe déjà: {livreur.user.username} - Matricule: {livreur.matricule}')

print('')
print('=== CRÉATION DES CLIENTS ===')

clients_data = [
    {'username': 'client1', 'email': 'client1@example.com', 'tel': 666666666, 'quartier': 'Akwa'},
    {'username': 'client2', 'email': 'client2@example.com', 'tel': 777777777, 'quartier': 'Deido'},
]

for data in clients_data:
    if not User.objects.filter(username=data['username']).exists():
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password='password123',
            tel=data['tel'],
            profile='client',
            quartier=data['quartier']
        )
        print(f'Client créé: {user.username} - {user.quartier}')
    else:
        user = User.objects.get(username=data['username'])
        print(f'Client existe déjà: {user.username} - {user.quartier}')

print('')
print('=== RÉSUMÉ DES DONNÉES CRÉÉES ===')
print(f'Utilisateurs totaux: {User.objects.count()}')
print(f'Restaurants: {Restaurant.objects.count()}')
print(f'Boutiques: {Boutique.objects.count()}')
print(f'Livreurs: {Livreur.objects.count()}')
print('')
print('Script terminé avec succès!')
"

echo "Script de création des données terminé."
