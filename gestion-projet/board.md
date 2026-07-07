# Project Board — GitLab Rules Manager

## ✅ Done

### Sprint 1 : Fondations
- [x] Structure du projet (app/, rules/, config/, tests/)
- [x] Fichier de configuration YAML (config/settings.yaml)
- [x] Module d'authentification GitLab API (app/auth.py)
- [x] Configuration du logging (app/logger.py)
- [x] Client HTTP GitLab (app/gitlab_client.py)
- [x] Fichier .gitignore
- [x] Pipeline CI/CD (.gitlab-ci.yml)

### Sprint 2 : Gestion des branches protégées
- [x] Définition YAML des règles de branches protégées (rules/rules.yaml)
- [x] Module CRUD idempotent avec diff (rules/protected_branches.py)
- [x] Tests unitaires (tests/test_protected_branches.py) — 12 tests

---

## ✅ Done (suite)

### Sprint 3 : Règles de Merge Request
- [x] Définition YAML des règles MR (rules/rules.yaml)
- [x] Module CRUD idempotent avec diff (rules/merge_requests.py)
- [x] Tests unitaires (tests/test_merge_requests.py) — 14 tests

### Sprint 4 : Règles d'approbation
- [x] Définition YAML des règles d'approbation (rules/rules.yaml)
- [x] Module CRUD idempotent avec diff + delete (rules/approvals.py)
- [x] Tests unitaires (tests/test_approvals.py) — 19 tests

---

## 📋 Backlog

### Sprint 5 : Conformité & Réapplication
- [ ] Moteur de vérification de conformité
- [ ] Réapplication différentielle
- [ ] Tests d'intégration
- [ ] Documentation finale
