# Sprint Plan - GitLab Rules Manager

## Sprint 1 : Fondations du projet ✅
- [x] Structure du projet (app/, rules/, config/, tests/)
- [x] Fichier de configuration YAML
- [x] Module d'authentification GitLab API
- [x] Configuration du logging
- [x] Fichier .gitignore
- [ ] ~~README~~ (reporté)
- [x] Pipeline CI/CD GitLab (.gitlab-ci.yml)

## Sprint 2 : Gestion des branches protégées ✅
- [x] Définition YAML des règles de branches protégées
- [x] Module CRUD idempotent via API GitLab (avec diff)
- [x] Tests unitaires — 12 tests

## Sprint 3 : Règles de Merge Request ✅
- [x] Définition YAML des règles MR
- [x] Module CRUD idempotent via API GitLab (avec diff)
- [x] Tests unitaires — 14 tests

## Sprint 4 : Règles d'approbation ✅
- [x] Définition YAML des règles d'approbation
- [x] Module CRUD idempotent via API GitLab (avec diff + delete)
- [x] Tests unitaires — 19 tests

## Sprint 5 : Conformité & Réapplication
- Moteur de vérification de conformité
- Réapplication différentielle
- Tests d'intégration
- Documentation finale
