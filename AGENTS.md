# GitLab Rules Manager - Contexte Agentic

## Stack technique
- **Langage** : Python 3.12+
- **API** : GitLab REST API v4
- **Configuration** : YAML
- **CI/CD** : GitLab CI/CD
- **Tests** : pytest

## Architecture
```
project/
```
- `app/` - Logique métier
- `rules/` - Définition des règles GitLab
- `config/` - Configuration
- `tests/` - Tests
- `.gitlab-ci.yml` - Pipeline CI/CD

## Règles métier

### GitLab

- Toutes les modifications doivent être réalisées via l'API GitLab REST v4.
- Les scripts doivent être idempotents et réexécutables.
- Les règles GitLab sont définies dans le dossier `rules/`.
- La configuration doit rester séparée de la logique métier.
- Ne jamais modifier une règle déjà conforme.
- Toujours privilégier une mise à jour différentielle plutôt qu'une réécriture complète.

### Configuration

- Les paramètres sont définis dans des fichiers YAML.
- Les secrets sont fournis via les variables GitLab CI/CD ou un fichier `.env`.
- Aucun secret ne doit être écrit dans le dépôt ou dans les logs.

### Tests

- Tous les appels à l'API GitLab doivent être mockés.
- Toute nouvelle fonctionnalité doit être accompagnée de tests.
- Exécuter `pytest` avant de finaliser une modification.

## Workflow agentic

### Scrum Master (agent principal)

- Analyse les demandes.
- Découpe les fonctionnalités en tâches.
- Coordonne les sous-agents.
- Vérifie que les objectifs sont atteints.
- Valide les livrables.

### Developer

- Développe les nouvelles fonctionnalités.
- Implémente les règles GitLab.
- Respecte l'architecture du projet.
- Met à jour la documentation lorsque nécessaire.
- Signale les dépendances techniques.

### Tester

- Écrit les tests unitaires et d'intégration.
- Vérifie la non-régression.
- Valide le fonctionnement des règles GitLab.
- Remonte les anomalies détectées.

### DevOps

- Maintient les pipelines GitLab CI/CD.
- Gère le versioning Git.
- Vérifie les variables d'environnement.
- S'assure de la qualité des déploiements.

## Décisions d'architecture

- L'API GitLab est l'unique moyen de modifier la configuration GitLab.
- Toutes les règles GitLab sont décrites dans des fichiers YAML.
- Chaque type de règle est implémenté dans un module indépendant.
- Les scripts doivent rester idempotents.
- Le projet doit être facilement extensible pour accueillir de nouveaux types de règles.

### Authentification GitLab

- Les opérations sur GitLab nécessitent un token disposant des permissions appropriées.
- Utiliser un token fourni via les variables d'environnement ou les variables GitLab CI/CD.
- Ne jamais demander ou afficher un token si une opération peut être réalisée sans celui-ci.
- Si aucun token n'est disponible, informer l'utilisateur qu'une authentification est nécessaire avant toute modification via l'API GitLab.
