# GitLab Rules Manager

Automatisation de la gestion des règles d'un ou plusieurs projets GitLab via l'API REST v4.

## Fonctionnalités

- **Branches protégées** — Création, mise à jour et suppression des règles de protection
- **Merge Requests** — Configuration des paramètres de fusion (méthode, pipeline, discussions)
- **Règles d'approbation** — Gestion des approvers par branche
- **Vérification de conformité** — Audit de l'état actuel vs état désiré
- **Réapplication différentielle** — Seules les règles non conformes sont modifiées

## Architecture

```
├── app/
│   ├── auth.py              # Authentification GitLab API
│   ├── compliance.py        # Moteur de vérification de conformité
│   ├── config.py            # Configuration YAML + variables d'environnement
│   ├── gitlab_client.py     # Client HTTP GitLab REST API v4
│   ├── logger.py            # Configuration du logging
│   └── apply_rules.py       # Point d'entrée principal
├── rules/
│   ├── protected_branches.py  # Module branches protégées
│   ├── merge_requests.py      # Module règles de merge request
│   ├── approvals.py           # Module règles d'approbation
│   └── rules.yaml             # Définition des règles
├── config/
│   └── settings.yaml          # Configuration générale
└── tests/                     # Tests unitaires et d'intégration
```

## Installation

```bash
git clone https://github.com/zlatanarondelpiekarz/devops-ia.git
cd devops-ia
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

### Variables d'environnement

| Variable | Description |
|---|---|
| `GITLAB_URL` | URL de l'instance GitLab (défaut: `https://gitlab.com`) |
| `GITLAB_TOKEN` | Token d'authentification GitLab |
| `GITLAB_PROJECT_ID` | ID du projet GitLab |

### Fichier YAML

Créez un fichier `.env` à la racine :

```env
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your_token_here
GITLAB_PROJECT_ID=your_project_id_here
```

Ou utilisez `config/settings.yaml` :

```yaml
gitlab:
  url: "https://gitlab.com"
  project_id: "your_project_id"
  token: "your_token"
```

## Utilisation

### Appliquer les règles

```bash
python -m app.apply_rules
```

### Vérifier la conformité sans appliquer

```bash
python -m app.apply_rules --check-only
```

Retourne `0` si tout est conforme, `1` sinon.

### CI/CD (GitLab CI)

Le pipeline est défini dans `.gitlab-ci.yml` :
- **test** : exécute les tests avec couverture
- **deploy** : applique les règles sur la branche `main`

## Définition des règles

Les règles sont définies dans `rules/rules.yaml` :

```yaml
protected_branches:
  - name: main
    push_access_level: 40
    merge_access_level: 40
    allow_force_push: false
    code_owner_approval_required: true

merge_requests:
  merge_method: merge
  pipeline_required: true
  discussions_resolved: true
  remove_source_branch: true

approval_rules:
  - name: main-approval
    approvals_required: 2
    rule_type: regular
    branch_name: main
```

## Tests

```bash
pytest
```

Avec couverture :

```bash
pytest --cov=app --cov=rules
```

## Développement

1. Chaque type de règle est implémenté dans un module indépendant sous `rules/`
2. Les modules sont idempotents : ils comparent l'état actuel avant de modifier
3. Tout nouveau module doit être accompagné de tests unitaires
4. Exécuter `pytest` avant toute validation
