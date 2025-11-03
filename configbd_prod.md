# Configuration de la Base de Données PostgreSQL en Production sur VPS

Ce fichier contient les commandes à exécuter pour configurer PostgreSQL en production sur votre VPS (par exemple, Hostinger ou un autre fournisseur). Assurez-vous d'avoir les droits root ou sudo pour exécuter ces commandes.

## Prérequis
- Accès SSH à votre VPS
- Ubuntu/Debian ou distribution Linux similaire
- Variables d'environnement prêtes (DB_NAME, DB_USER, DB_PASSWORD, etc.)

## Étapes de Configuration

### 1. Mise à jour du système
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Installation de PostgreSQL
```bash
# Installer PostgreSQL et ses outils
sudo apt install postgresql postgresql-contrib -y

# Vérifier la version installée
psql --version
```

### 3. Démarrage et activation du service PostgreSQL
```bash
# Démarrer le service
sudo systemctl start postgresql

# Activer le démarrage automatique au boot
sudo systemctl enable postgresql

# Vérifier le statut
sudo systemctl status postgresql
```

### 4. Configuration de l'utilisateur PostgreSQL
```bash
# Se connecter en tant que superutilisateur postgres
sudo -u postgres psql

# Dans l'invite PostgreSQL, créer un utilisateur avec mot de passe
CREATE USER votre_db_user WITH PASSWORD 'votre_mot_de_passe_securise';

# Donner les droits de création de base de données
ALTER USER votre_db_user CREATEDB;

# Quitter PostgreSQL
\q
```

### 5. Création de la base de données
```bash
# Se connecter à nouveau en tant que postgres
sudo -u postgres psql

# Créer la base de données
CREATE DATABASE votre_db_name OWNER votre_db_user;

# Donner tous les privilèges sur la base
GRANT ALL PRIVILEGES ON DATABASE votre_db_name TO votre_db_user;

# Quitter
\q
```

### 6. Configuration de PostgreSQL pour la production
```bash
# Éditer le fichier de configuration principal
sudo nano /etc/postgresql/14/main/postgresql.conf

# Modifier les paramètres suivants (ajuster selon vos besoins) :
# listen_addresses = '*'  # Écouter sur toutes les interfaces
# max_connections = 100   # Nombre maximum de connexions
# shared_buffers = 256MB  # Mémoire partagée
# work_mem = 4MB          # Mémoire de travail par connexion
# maintenance_work_mem = 64MB  # Mémoire pour maintenance
# wal_buffers = 16MB      # Buffers WAL

# Sauvegarder et quitter (Ctrl+X, Y, Enter)
```

### 7. Configuration des accès réseau (pg_hba.conf)
```bash
# Éditer le fichier d'authentification
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Ajouter à la fin du fichier (avant les lignes existantes) :
# local   votre_db_name    votre_db_user    md5
# host    votre_db_name    votre_db_user    127.0.0.1/32    md5
# host    votre_db_name    votre_db_user    ::1/128         md5

# Pour les connexions externes (si nécessaire) :
# host    votre_db_name    votre_db_user    0.0.0.0/0       md5

# Sauvegarder et quitter
```

### 8. Redémarrage de PostgreSQL
```bash
# Redémarrer le service pour appliquer les changements
sudo systemctl restart postgresql

# Vérifier les logs pour les erreurs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### 9. Test de la connexion
```bash
# Tester la connexion avec le nouvel utilisateur
psql -h localhost -U votre_db_user -d votre_db_name

# Si demandé, entrer le mot de passe

# Dans PostgreSQL, vérifier la connexion
SELECT version();

# Quitter
\q
```

### 10. Configuration du firewall (UFW)
```bash
# Installer UFW si pas déjà fait
sudo apt install ufw -y

# Autoriser SSH
sudo ufw allow ssh

# Autoriser PostgreSQL (port 5432) si nécessaire pour connexions externes
# sudo ufw allow 5432

# Activer le firewall
sudo ufw --force enable

# Vérifier le statut
sudo ufw status
```

### 11. Sauvegarde automatique (recommandé)
```bash
# Créer un script de sauvegarde
sudo nano /usr/local/bin/backup_postgres.sh

# Contenu du script :
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="votre_db_name"
DB_USER="votre_db_user"

mkdir -p $BACKUP_DIR
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/${DB_NAME}_$DATE.sql

# Garder seulement les 7 dernières sauvegardes
cd $BACKUP_DIR
ls -t *.sql | tail -n +8 | xargs rm -f

# Rendre exécutable
sudo chmod +x /usr/local/bin/backup_postgres.sh

# Ajouter à crontab pour sauvegarde quotidienne à 2h du matin
sudo crontab -e

# Ajouter la ligne :
# 0 2 * * * /usr/local/bin/backup_postgres.sh
```

### 12. Migration des données (si migration depuis SQLite)
```bash
# Si vous migrez depuis SQLite vers PostgreSQL :
# 1. Sauvegarder les données SQLite
# 2. Utiliser un outil comme pgloader ou exporter/importer manuellement
# 3. Appliquer les migrations Django :
python manage.py migrate
```

## Variables d'environnement pour votre application
Assurez-vous que votre fichier `.env` contient :
```
DB_NAME=votre_db_name
DB_USER=votre_db_user
DB_PASSWORD=votre_mot_de_passe_securise
DB_HOST=localhost
DB_PORT=5432
```

## Commandes de vérification
```bash
# Vérifier que PostgreSQL écoute sur le bon port
sudo netstat -tlnp | grep 5432

# Vérifier l'utilisation de la mémoire
sudo systemctl status postgresql

# Vérifier les connexions actives
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

## Sécurité supplémentaire
- Changez le mot de passe par défaut de l'utilisateur postgres
- Désactivez les connexions distantes si pas nécessaires
- Utilisez des mots de passe forts
- Mettez à jour régulièrement PostgreSQL
- Surveillez les logs pour les tentatives d'intrusion

## Dépannage
- Si problème de connexion : vérifiez pg_hba.conf et postgresql.conf
- Si erreur de permission : vérifiez les droits sur les fichiers
- Si le service ne démarre pas : consultez les logs détaillés
