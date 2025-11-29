# Système de Réplication et Résolution de Conflits dans les Bases de Données Distribuées

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Description

Prototype expérimental d'un système de réplication distribuée avec mécanismes de détection et résolution automatique de conflits. Ce projet illustre les concepts fondamentaux des bases de données distribuées : réplication asynchrone, cohérence éventuelle, et stratégies de résolution de conflits.

## 🎯 Objectifs

- Démontrer les mécanismes de réplication multi-nœuds
- Implémenter plusieurs stratégies de résolution de conflits
- Simuler des scénarios de mise à jour concurrente
- Fournir une API REST pour la gestion et la synchronisation

## 🏗️ Architecture

```
┌─────────────────┐           ┌─────────────────┐
│   Nœud A        │           │   Nœud B        │
│  ┌──────────┐   │  Sync     │  ┌──────────┐   │
│  │ FastAPI  │◄──┼───────────┼─►│ FastAPI  │   │
│  └────┬─────┘   │   JSON    │  └────┬─────┘   │
│       │         │           │       │         │
│  ┌────▼─────┐   │           │  ┌────▼─────┐   │
│  │PostgreSQL│   │           │  │PostgreSQL│   │
│  └──────────┘   │           │  └──────────┘   │
└─────────────────┘           └─────────────────┘
         │                             │
         └─────────┬───────────────────┘
                   │
           ┌───────▼────────┐
           │  Résolution    │
           │  de Conflits   │
           │  • LWW         │
           │  • Field-wise  │
           └────────────────┘
```

## 🚀 Installation

### Prérequis

- Python 3.9 ou supérieur
- PostgreSQL 14 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-username/replication-distribuee.git
cd replication-distribuee

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration des bases de données

```bash
# Créer les bases PostgreSQL
createdb replica_a
createdb replica_b

# Configuration dans .env
cat > .env << EOF
DATABASE_URL_A=postgresql://user:password@localhost:5432/replica_a
DATABASE_URL_B=postgresql://user:password@localhost:5432/replica_b
EOF
```

## 📦 Dépendances

```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pydantic>=2.0.0
python-dotenv>=1.0.0
httpx>=0.24.0
alembic>=1.11.0
```

## 🎮 Utilisation

### Démarrage des nœuds

```bash
# Terminal 1 - Nœud A
uvicorn app.node_a:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Nœud B
uvicorn app.node_b:app --host 0.0.0.0 --port 8002 --reload
```

### API Endpoints

#### Nœud A (Port 8001)

```http
# Créer un utilisateur
POST http://localhost:8001/api/v1/users
Content-Type: application/json

{
  "nom": "Ousmane Sankhare",
  "email": "ousmane@example.com",
  "telephone": "+221771234567"
}

# Lister les utilisateurs
GET http://localhost:8001/api/v1/users

# Mettre à jour un utilisateur
PUT http://localhost:8001/api/v1/users/{id}
Content-Type: application/json

{
  "email": "nouveau@example.com"
}
```

#### Synchronisation

```http
# Synchroniser de A vers B
POST http://localhost:8001/api/v1/sync-to-b

# Synchroniser de B vers A
POST http://localhost:8002/api/v1/sync-to-a
```

#### Résolution de conflits

```http
# Résoudre avec stratégie "dernière écriture"
POST http://localhost:8001/api/v1/resolve-conflicts
Content-Type: application/json

{
  "strategy": "latest"
}

# Résoudre avec fusion champ par champ
POST http://localhost:8001/api/v1/resolve-conflicts
Content-Type: application/json

{
  "strategy": "field-wise"
}
```

## 🧪 Scénarios de test

### Test 1 : Modification concurrente simple

```bash
# 1. Créer un utilisateur sur le Nœud A
curl -X POST http://localhost:8001/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"nom": "Test User", "email": "test@example.com"}'

# 2. Synchroniser vers B
curl -X POST http://localhost:8001/api/v1/sync-to-b

# 3. Modifier sur A
curl -X PUT http://localhost:8001/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"email": "modif_a@example.com"}'

# 4. Modifier sur B (même utilisateur)
curl -X PUT http://localhost:8002/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"telephone": "+221779999999"}'

# 5. Tenter la synchronisation (conflit détecté)
curl -X POST http://localhost:8001/api/v1/sync-to-b

# 6. Résoudre le conflit
curl -X POST http://localhost:8001/api/v1/resolve-conflicts \
  -H "Content-Type: application/json" \
  -d '{"strategy": "field-wise"}'
```

## 🔬 Stratégies de résolution implémentées

### 1. Last Write Wins (LWW)

```python
def resolve_lww(record_a, record_b):
    """Conserve l'enregistrement le plus récent basé sur updated_at"""
    if record_a["updated_at"] >= record_b["updated_at"]:
        return record_a
    return record_b
```

**Avantages** : Simple, rapide, déterministe  
**Inconvénients** : Perte potentielle de données concurrentes

### 2. Field-wise Merge

```python
def resolve_merge_fields(record_a, record_b):
    """Fusionne champ par champ en gardant les valeurs les plus récentes"""
    result = {}
    for key in record_a.keys():
        if key == "updated_at":
            result[key] = max(record_a[key], record_b[key])
        elif record_a[key] != record_b[key]:
            # Logique de fusion selon le champ
            result[key] = select_most_recent(record_a, record_b, key)
        else:
            result[key] = record_a[key]
    return result
```

**Avantages** : Préserve plus de données  
**Inconvénients** : Plus complexe, peut nécessiter une logique métier

### 3. Journalisation des conflits

```python
def log_conflict(record_a, record_b):
    """Enregistre le conflit pour résolution manuelle"""
    conflict_log.append({
        "timestamp": datetime.now(),
        "record_id": record_a["id"],
        "version_a": record_a,
        "version_b": record_b,
        "status": "pending"
    })
```

**Avantages** : Aucune perte de données, traçabilité  
**Inconvénients** : Nécessite intervention humaine

## 📊 Structure du projet

```
replication-distribuee/
├── app/
│   ├── __init__.py
│   ├── models.py           # Modèles SQLAlchemy
│   ├── schemas.py          # Schémas Pydantic
│   ├── database.py         # Configuration DB
│   ├── node_a.py           # API Nœud A
│   ├── node_b.py           # API Nœud B
│   ├── sync_manager.py     # Logique de synchronisation
│   └── conflict_resolver.py # Stratégies de résolution
├── tests/
│   ├── test_sync.py
│   ├── test_conflicts.py
│   └── test_strategies.py
├── alembic/                # Migrations
├── docs/                   # Documentation
├── .env.example
├── requirements.txt
├── README.md
└── setup.py
```

## 🧰 Commandes utiles

```bash
# Lancer les tests
pytest tests/ -v

# Créer une migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Accéder à la documentation interactive
open http://localhost:8001/docs

# Réinitialiser les bases de données
python scripts/reset_databases.py
```

## 📈 Métriques et monitoring

Le système expose des métriques via l'endpoint `/metrics` :

- Nombre de synchronisations réussies
- Nombre de conflits détectés
- Temps moyen de résolution
- Taux de cohérence entre nœuds

## 🐛 Dépannage

### Erreur de connexion PostgreSQL

```bash
# Vérifier que PostgreSQL est en cours d'exécution
sudo systemctl status postgresql

# Vérifier les connexions
psql -U user -d replica_a -c "SELECT 1;"
```

### Conflits non résolus

```bash
# Consulter les logs de conflits
curl http://localhost:8001/api/v1/conflicts

# Forcer une résolution manuelle
curl -X POST http://localhost:8001/api/v1/conflicts/{id}/resolve \
  -H "Content-Type: application/json" \
  -d '{"chosen_version": "node_a"}'
```

## 📚 Ressources

- [Article complet (PDF)](docs/article.pdf)
- [Théorème CAP](https://en.wikipedia.org/wiki/CAP_theorem)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Ousmane Sankhare**  
📧 Email: ousmane.sankhare@example.com  
🔗 LinkedIn: [linkedin.com/in/ousmane-sankhare](https://linkedin.com/in/ousmane-sankhare)

## 🙏 Remerciements

- Eric Brewer pour le théorème CAP
- Gilbert et Lynch pour la formalisation du CAP
- La communauté FastAPI et SQLAlchemy

---

**⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile !**