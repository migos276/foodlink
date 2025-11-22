#!/bin/bash

# Script de réinitialisation complète de PostgreSQL avec l'utilisateur miguel
# Auteur: Configuration automatique
# Date: $(date)

echo "=========================================="
echo "Réinitialisation PostgreSQL"
echo "=========================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ $1${NC}"; }

# Variables
DB_NAME="camereatdb"
NEW_USER="miguel"
NEW_PASSWORD="miguel123"  # Changez si vous voulez

echo ""
print_info "Configuration:"
echo "  Base de données: $DB_NAME"
echo "  Utilisateur: $NEW_USER"
echo "  Mot de passe: $NEW_PASSWORD"
echo ""
read -p "Continuer? (o/N): " confirm
if [[ ! $confirm =~ ^[Oo]$ ]]; then
    echo "Annulé."
    exit 0
fi

# 1. Arrêter PostgreSQL
echo ""
print_info "Arrêt de PostgreSQL..."
sudo systemctl stop postgresql@17-main
print_success "PostgreSQL arrêté"

# 2. Supprimer l'ancien cluster
echo ""
print_info "Suppression de l'ancien cluster..."
sudo rm -rf /var/lib/postgresql/17/main
sudo rm -rf /etc/postgresql/17/main
print_success "Ancien cluster supprimé"

# 3. Recréer le cluster
echo ""
print_info "Création d'un nouveau cluster..."
sudo pg_createcluster 17 main --start
print_success "Nouveau cluster créé"

# 4. Configurer pg_hba.conf pour trust
echo ""
print_info "Configuration de l'authentification en mode 'trust'..."
sudo bash -c 'cat > /etc/postgresql/17/main/pg_hba.conf << EOF
# PostgreSQL Client Authentication Configuration File
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             postgres                                peer
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            trust

# IPv6 local connections:
host    all             all             ::1/128                 trust

# Allow replication connections from localhost
local   replication     all                                     peer
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
EOF'
print_success "Configuration pg_hba.conf mise à jour"

# 5. Redémarrer PostgreSQL
echo ""
print_info "Redémarrage de PostgreSQL..."
sudo systemctl restart postgresql@17-main
sleep 2
print_success "PostgreSQL redémarré"

# 6. Créer l'utilisateur miguel
echo ""
print_info "Création de l'utilisateur '$NEW_USER'..."
sudo -u postgres psql -c "CREATE USER $NEW_USER WITH PASSWORD '$NEW_PASSWORD' SUPERUSER CREATEDB CREATEROLE LOGIN;" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "Utilisateur '$NEW_USER' créé"
else
    print_info "L'utilisateur existe déjà, réinitialisation du mot de passe..."
    sudo -u postgres psql -c "ALTER USER $NEW_USER WITH PASSWORD '$NEW_PASSWORD';"
fi

# 7. Créer la base de données
echo ""
print_info "Création de la base de données '$DB_NAME'..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $NEW_USER;" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "Base de données '$DB_NAME' créée"
else
    print_info "La base existe déjà, transfert de propriété..."
    sudo -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $NEW_USER;"
fi

# 8. Tester la connexion
echo ""
print_info "Test de connexion..."
psql -h localhost -U $NEW_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Connexion réussie!"
else
    print_error "Échec de la connexion"
fi

# 9. Installer psycopg2 si nécessaire
echo ""
print_info "Vérification de psycopg2..."
if python -c "import psycopg2" 2>/dev/null; then
    print_success "psycopg2 est installé"
else
    print_info "Installation de psycopg2-binary..."
    pip install psycopg2-binary
    print_success "psycopg2-binary installé"
fi

# 10. Afficher le résumé
echo ""
echo "=========================================="
echo "Configuration terminée!"
echo "=========================================="
echo ""
echo "Configuration Django settings.py:"
echo ""
echo "DATABASES = {"
echo "    'default': {"
echo "        'ENGINE': 'django.db.backends.postgresql',"
echo "        'NAME': '$DB_NAME',"
echo "        'USER': '$NEW_USER',"
echo "        'PASSWORD': '$NEW_PASSWORD',"
echo "        'HOST': 'localhost',"
echo "        'PORT': '5432',"
echo "    }"
echo "}"
echo ""
print_info "Commandes suivantes:"
echo "  python manage.py makemigrations"
echo "  python manage.py migrate"
echo "  python manage.py runserver"
echo ""
print_info "Pour vous connecter à PostgreSQL:"
echo "  psql -h localhost -U $NEW_USER -d $DB_NAME"
echo ""
print_success "Tout est prêt! 🚀"
echo ""