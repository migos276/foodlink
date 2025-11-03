# Création d'un Super Utilisateur Django

Ce guide explique comment créer un super utilisateur pour accéder à l'interface d'administration Django de votre application Camer-Eat.

## Prérequis

- Les conteneurs Docker doivent être en cours d'exécution
- La base de données doit être configurée et les migrations appliquées

## Méthode 1 : Création Interactive (Recommandée)

### 1. Accéder au conteneur Django
```bash
# Pour la production
docker-compose -f docker-compose.prod.yml exec django bash

# Ou pour le développement
docker-compose exec django bash
```

### 2. Créer le super utilisateur
```bash
cd /app
python manage.py createsuperuser
```

### 3. Suivre les invites
Le système vous demandera :
- **Username** : Choisissez un nom d'utilisateur (ex: admin)
- **Email address** : Entrez une adresse email valide
- **Password** : Choisissez un mot de passe sécurisé
- **Password (again)** : Confirmez le mot de passe

## Méthode 2 : Création Non-Interactive (Automatisée)

Si vous voulez créer le super utilisateur de manière automatisée (utile pour les scripts de déploiement) :

```bash
# Depuis l'extérieur du conteneur
docker compose -f docker-compose.prod.yml exec django python manage.py createsuperuser \
  --username Fotso \
  --email admin@foodlink237.org \
  --noinput

# Puis définir le mot de passe
docker-compose -f docker-compose.prod.yml exec django python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='admin')
user.set_password('votre_mot_de_passe_securise')
user.save()
"
```

## Méthode 3 : Via un Script Python (Recommandé pour CustomUser)

Si votre modèle utilisateur personnalisé (`CustomUser`) a des champs requis supplémentaires, utilisez cette méthode :

```python
#!/usr/bin/env python
import os
import django
from django.core.management import execute_from_command_line

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Créer le super utilisateur avec tous les champs requis
if not User.objects.filter(username='Fotso').exists():
    try:
        user = User.objects.create_superuser(
            username='Fotso',
            email='admin@foodlink237.org',
            password='admin123',
            first_name='Admin',
            last_name='Fotso',
            tel=123456789  # Champ requis pour CustomUser
        )
        print("Super utilisateur créé avec succès!")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
    except Exception as e:
        print(f"Erreur lors de la création: {e}")
else:
    print("Le super utilisateur existe déjà.")
```

Puis exécutez-le :
```bash
docker-compose -f docker-compose.prod.yml exec django python create_superuser.py
```

### Méthode 4 : Création Directe via Shell Django

Pour une création rapide en production :
```bash
docker-compose -f docker-compose.prod.yml exec django python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_superuser(
    username='Fotso',
    email='admin@foodlink237.org',
    password='admin123',
    first_name='Admin',
    last_name='Fotso',
    tel=123456789
)
print('Superuser created successfully!')
"
```

## Accès à l'Interface d'Administration

### 1. URL d'accès
Une fois le super utilisateur créé, accédez à l'interface d'administration via :
- **Développement** : http://localhost:8000/admin/
- **Production** : https://votre-domaine.com/admin/

### 2. Connexion
Utilisez les identifiants du super utilisateur que vous venez de créer.

## Gestion des Super Utilisateurs

### Lister les super utilisateurs existants
```bash
docker-compose -f docker-compose.prod.yml exec django python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
superusers = User.objects.filter(is_superuser=True)
for user in superusers:
    print(f'Username: {user.username}, Email: {user.email}')
"
```

### Changer le mot de passe d'un super utilisateur
```bash
docker-compose -f docker-compose.prod.yml exec django python manage.py changepassword admin
```

### Supprimer un super utilisateur
```bash
docker-compose -f docker-compose.prod.yml exec django python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    user = User.objects.get(username='admin')
    user.delete()
    print('Super utilisateur supprimé.')
except User.DoesNotExist:
    print('Super utilisateur non trouvé.')
"
```

## Sécurité

⚠️ **Important** :
- Utilisez toujours un mot de passe fort pour le super utilisateur
- Ne partagez jamais les identifiants du super utilisateur
- En production, assurez-vous que l'accès à `/admin/` est sécurisé (HTTPS obligatoire)
- Considérez l'utilisation de variables d'environnement pour les identifiants en production

## Dépannage

### Erreur : "no such table: auth_user"
Assurez-vous que les migrations ont été appliquées :
```bash
docker-compose -f docker-compose.prod.yml exec django python manage.py migrate
```

### Erreur : "null value in column 'tel' of relation 'users_customuser' violates not-null constraint"
Cette erreur survient lorsque votre modèle `CustomUser` a des champs requis (comme `tel`) qui ne sont pas fournis lors de la création du super utilisateur. Utilisez la **Méthode 3** ou **Méthode 4** qui incluent tous les champs requis.

### Erreur : "User with this username already exists"
Le nom d'utilisateur existe déjà. Choisissez un autre nom ou supprimez l'utilisateur existant.

### Erreur : "could not translate host name 'db' to address: Temporary failure in name resolution"
- Vérifiez que le conteneur de base de données est en cours d'exécution : `docker-compose -f docker-compose.prod.yml ps`
- Assurez-vous que les migrations ont été appliquées
- Vérifiez les variables d'environnement de base de données dans votre fichier `.env`

### Impossible d'accéder à /admin/
- Vérifiez que le serveur Django fonctionne
- Assurez-vous que `DEBUG=False` en production et que `ALLOWED_HOSTS` est correctement configuré
- Vérifiez les logs Django pour les erreurs
- En production, assurez-vous que Nginx proxy correctement les requêtes vers Django

## Variables d'Environnement Recommandées

Ajoutez ces variables à votre fichier `.env` pour une meilleure sécurité :

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@foodlink237.org
DJANGO_SUPERUSER_PASSWORD=votre_mot_de_passe_securise
```

Puis utilisez-les dans vos scripts de déploiement.
