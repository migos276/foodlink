# TODO: Assurer l'intégration Front-end/Back-end

## Étapes à suivre pour garantir le fonctionnement correct

### 1. Vérification et correction de la configuration CORS
- [x] Vérifier les paramètres CORS dans `livraison_nourriture/backend/settings.py`
- [x] S'assurer que les origines autorisées incluent localhost:3000 et les URLs de production
- [ ] Tester les requêtes cross-origin depuis le front-end

### 2. Vérification des URLs API
- [x] Vérifier que tous les endpoints sont correctement définis dans `livraison_nourriture/backend/urls.py`
- [x] S'assurer que les routes correspondent aux appels dans `lib/api.ts`
- [ ] Tester la résolution des URLs en développement vs production

### 3. Correction de l'authentification JWT
- [x] Vérifier la configuration JWT dans `livraison_nourriture/backend/settings.py`
- [x] Corriger la logique d'authentification dans `lib/auth.ts`
- [ ] S'assurer que les tokens sont correctement stockés et utilisés

### 4. Correction des appels API dans les hooks
- [x] Vérifier `hooks/useDashboardStats.ts` pour les appels aux statistiques
- [x] Vérifier `hooks/useAnalysis.ts` pour les données d'analyse
- [x] Vérifier `hooks/useEntityData.ts` pour la gestion des entités
- [x] S'assurer que les erreurs sont correctement gérées

### 5. Tests d'intégration
- [ ] Tester la connexion au back-end depuis le front-end
- [ ] Vérifier que les données sont correctement récupérées
- [ ] Tester l'authentification complète (login/logout)
- [ ] Vérifier les opérations CRUD sur les entités

### 6. Déploiement et production
- [ ] Vérifier la configuration pour l'environnement de production
- [ ] Tester avec Docker Compose
- [ ] S'assurer que Nginx proxy correctement les requêtes API

### 7. Fix API base URL for production
- [x] Change production base URL in `lib/api.ts` from `''` to `'/api'` to match Nginx proxy
