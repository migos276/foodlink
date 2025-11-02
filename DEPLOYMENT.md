# Guide de Déploiement Camer-Eat

## Prérequis

- Docker et Docker Compose installés sur le VPS Hostinger
- Apache2 installé sur le serveur
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

### 2. Configuration Apache pour Hostinger

Sur votre VPS Hostinger, copiez la configuration Apache :

```bash
# Copier la configuration
sudo cp apache.conf /etc/apache2/sites-available/foodlink237.conf

# Activer le site
sudo a2ensite foodlink237.conf

# Activer les modules nécessaires
sudo a2enmod proxy proxy_http rewrite ssl

# Désactiver le site par défaut si nécessaire
sudo a2dissite 000-default.conf

# Redémarrer Apache
sudo systemctl reload apache2
```

### 3. Déploiement avec Docker

#### Pour le développement :
```bash
docker-compose up --build
```

#### Pour la production sur Hostinger :
```bash
# Construire et démarrer les services
docker-compose -f docker-compose.prod.yml up --build -d

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
- Utilisez HTTPS en production (SSL configuré dans apache.conf)
- Configurez un firewall (ufw sur Ubuntu)
- Mettez à jour régulièrement les images Docker
- Utilisez des secrets pour les variables sensibles
- Installez Let's Encrypt pour les certificats SSL gratuits

## Configuration SSL avec Let's Encrypt (Hostinger)

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-apache

# Obtenir le certificat
sudo certbot --apache -d foodlink237.org -d www.foodlink237.org

# Le certificat sera automatiquement configuré dans Apache
# Les chemins dans apache.conf seront mis à jour automatiquement
```

## Commandes de déploiement finales pour Hostinger

```bash
# 1. Cloner le projet
git clone <your-repo-url>
cd camer-eat-main

# 2. Créer le fichier .env avec vos variables de production
cp .env.example .env
# Éditez .env avec vos vraies valeurs

# 3. Construire et démarrer
docker-compose -f docker-compose.prod.yml up --build -d

# 4. Configurer Apache
sudo cp apache.conf /etc/apache2/sites-available/foodlink237.conf
sudo a2ensite foodlink237.conf
sudo a2enmod proxy proxy_http rewrite ssl
sudo a2dissite 000-default.conf
sudo systemctl reload apache2

# 5. Configurer SSL
sudo certbot --apache -d foodlink237.org -d www.foodlink237.org

# 6. Vérifier
curl https://foodlink237.org
```

## Dépannage

### Problème de connexion à la base de données :
Vérifiez les variables d'environnement et que le conteneur PostgreSQL est démarré.

### Erreur 502 Bad Gateway :
Vérifiez que les services Django et Next.js sont accessibles sur leurs ports respectifs.

### Problème de permissions :
Assurez-vous que les volumes Docker ont les bonnes permissions.
