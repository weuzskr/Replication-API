from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import SessionA, SessionB
from .crud.sychronisation import ping_database, sync_databases, detect_conflicts, resolve_conflicts
router = APIRouter()

@router.get("/ping-db")
def ping():
    """
        Vérifie la connexion aux deux bases de données.

        - **db_a**: état de la base A (`OK` ou `Échec`)
        - **db_b**: état de la base B (`OK` ou `Échec`)
        """
    ok_a = ping_database(SessionA())
    ok_b = ping_database(SessionB())
    return {
        "db_a": "🟢 OK" if ok_a else "🔴 Échec",
        "db_b": "🟢 OK" if ok_b else "🔴 Échec"
    }

@router.post("/sync")
def manual_sync():
    """
       Synchronise tous les clients de la base A vers la base B, sans écraser les données existantes dans B.
       """
    sync_databases(SessionA(), SessionB())
    return {"message": "Synchronisation terminée"}

@router.get("/detect-conflits")
def detect():
    """
       Détecte les conflits de données entre les deux bases pour les clients avec le même ID.

       Retourne la liste des clients en conflit avec leurs informations respectives dans chaque base.
       """
    result = detect_conflicts(SessionA(), SessionB())
    return {"conflits": result}



from enum import Enum

class StrategyEnum(str, Enum):
    latest = "latest"
    field_wise = "field-wise"


@router.post("/resolve-conflits")
def resolve(strategy: StrategyEnum = Query(
    ...,
    description="Stratégie de résolution des conflits. Options : 'latest' ou 'field-wise'."
)):
    """
    Résout les conflits détectés selon la stratégie choisie.

    - **strategy**: méthode de résolution
      - `"latest"` : garde la donnée la plus récente (tout l'enregistrement)
      - `"field-wise"` : fusion champ par champ, selon la valeur la plus récente par champ
    """
    result = resolve_conflicts(SessionA(), SessionB(), strategy)
    return {"résolution": result}