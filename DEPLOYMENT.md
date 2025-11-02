# Guide de Déploiement Camer-Eat

## Prérequis

- Docker et Docker Compose installés sur le VPS Hostinger
- Nginx installé sur le serveur
- Domaine configuré (foodlink237.org)
- Certificats SSL (Let's Encrypt recommandé)

## Configuration pour la Production

### 1. Variables d'environnement

Copiez le fichier `.env.example` vers `.env` et configurez les valeurs :

```bash
cp .env.example .env
```

Éditez `.env` avec vos valeurs de production :
- Changez `SECRET_KEY` pour une clé sécurisée
- Définissez `DEBUG=False`
- Configurez `ALLOWED_HOSTS` avec votre domaine
- Définissez un mot de passe sécurisé pour PostgreSQL

### 2. Configuration Nginx pour Hostinger

Sur votre VPS Hostinger, copiez la configuration Nginx :

```bash
# Copier la configuration
sudo cp nginx.conf /etc/nginx/sites-available/foodlink237

# Créer un lien symbolique vers sites-enabled
sudo ln -s /etc/nginx/sites-available/foodlink237 /etc/nginx/sites-enabled/

# Supprimer la configuration par défaut
sudo rm /etc/nginx/sites-enabled/default

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl reload nginx
```

### 3. Déploiement avec Docker

#### Pour le développement :
```bash
docker-compose up --build
```

#### Pour la production sur Hostinger :
```bash
# Construire et démarrer les services
docker compose -f docker-compose.prod.yml up --build -d

# Vérifier que les conteneurs tournent
docker-compose -f docker-compose.prod.yml ps
```

### 4. Migration de la base de données

Si vous migrez depuis SQLite vers PostgreSQL :

```bash
# Arrêter les conteneurs
docker-compose down

# Sauvegarder les données SQLite (si nécessaire)
# Créer un dump des données

# Démarrer avec PostgreSQL
docker-compose -f docker-compose.prod.yml up --build -d

# Appliquer les migrations
docker-compose -f docker-compose.prod.yml exec django python manage.py migrate
```

### 5. Collecte des fichiers statiques

```bash
docker-compose -f docker-compose.prod.yml exec django python manage.py collectstatic --noinput
```

## Vérification du Déploiement

### 1. Vérifier que les conteneurs tournent :
```bash
docker-compose ps
```

### 2. Vérifier les logs :
```bash
docker-compose logs django
docker-compose logs nextjs
docker-compose logs db
```

### 3. Tester l'API :
```bash
curl http://your-domain.com/api/
```

### 4. Tester le frontend :
Accédez à `http://your-domain.com` dans votre navigateur.

## Maintenance

### Sauvegarde de la base de données :
```bash
docker-compose exec db pg_dump -U postgres camer_eat > backup.sql
```

### Mise à jour de l'application :
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up --build -d
```

### Monitoring :
- Surveillez les logs Apache : `/var/log/apache2/`
- Surveillez les logs Docker : `docker-compose logs`

## Sécurité

- Changez les mots de passe par défaut
- Utilisez HTTPS en production (SSL configuré dans nginx.conf)
- Configurez un firewall (ufw sur Ubuntu)
- Mettez à jour régulièrement les images Docker
- Utilisez des secrets pour les variables sensibles
- Installez Let's Encrypt pour les certificats SSL gratuits

## Configuration SSL avec Let's Encrypt (Hostinger)

```bash
# Installer Certbot pour Nginx
sudo apt install certbot python3-certbot-nginx

# Obtenir le certificat
sudo certbot --nginx -d foodlink237.org -d www.foodlink237.org

# Le certificat sera automatiquement configuré dans Nginx
# Les chemins dans nginx.conf seront mis à jour automatiquement
```

## Commandes de déploiement finales pour Hostinger (Nginx)

```bash
# 1. Cloner le projet
git clone <your-repo-url>
cd camer-eat-main

# 2. Créer le fichier .env avec vos variables de production
cp .env.example .env
# Éditez .env avec vos vraies valeurs

# 3. Construire et démarrer les services Docker
docker-compose -f docker-compose.prod.yml up --build -d

# 4. Vérifier que les conteneurs tournent
docker-compose -f docker-compose.prod.yml ps

# 5. Configurer Nginx
sudo cp nginx.conf /etc/nginx/sites-available/foodlink237
sudo ln -s /etc/nginx/sites-available/foodlink237 /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# 6. Configurer SSL avec Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d foodlink237.org -d www.foodlink237.org

# 7. Vérifier le déploiement
curl https://foodlink237.org
curl https://foodlink237.org/api/

# 8. Configurer le firewall (optionnel mais recommandé)
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## Dépannage

### Problème de connexion à la base de données :
Vérifiez les variables d'environnement et que le conteneur PostgreSQL est démarré.

### Erreur 502 Bad Gateway :
Vérifiez que les services Django et Next.js sont accessibles sur leurs ports respectifs (3000 et 8000).

### Erreur 504 Gateway Timeout :
Augmentez les timeouts dans nginx.conf si nécessaire.

### Problème de permissions :
Assurez-vous que les volumes Docker ont les bonnes permissions.

### SSL ne fonctionne pas :
Vérifiez que les certificats Let's Encrypt ont été générés correctement avec `sudo certbot certificates`.
