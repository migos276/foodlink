# Guide de Déploiement Camer-Eat

## Prérequis

- Docker et Docker Compose installés
- Apache installé sur le serveur
- Domaine configuré (optionnel mais recommandé)

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

### 2. Configuration Apache

Copiez `apache.conf` vers votre configuration Apache :

```bash
sudo cp apache.conf /etc/apache2/sites-available/camer_eat.conf
sudo a2ensite camer_eat.conf
sudo a2enmod proxy proxy_http rewrite
sudo systemctl reload apache2
```

### 3. Déploiement avec Docker

#### Pour le développement :
```bash
docker-compose up --build
```

#### Pour la production :
```bash
docker-compose -f docker-compose.prod.yml up --build -d
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
- Utilisez HTTPS en production
- Configurez un firewall
- Mettez à jour régulièrement les images Docker
- Utilisez des secrets pour les variables sensibles

## Dépannage

### Problème de connexion à la base de données :
Vérifiez les variables d'environnement et que le conteneur PostgreSQL est démarré.

### Erreur 502 Bad Gateway :
Vérifiez que les services Django et Next.js sont accessibles sur leurs ports respectifs.

### Problème de permissions :
Assurez-vous que les volumes Docker ont les bonnes permissions.
