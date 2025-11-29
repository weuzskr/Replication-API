import datetime

from sqlalchemy.orm import Session
from sqlalchemy import text
from models.models import Client, LogsConflits, Utilisateur


def ping_database(session: Session):
    try:
        session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def sync_databases(session_a: Session, session_b: Session):
    """
    Synchronise tous les utilisateurs de A vers B sans écraser ceux de B.
    """
    utilisateurs_a = session_a.query(Utilisateur).all()
    utilisateurs_b = {u.id: u for u in session_b.query(Utilisateur).all()}

    for utilisateur in utilisateurs_a:
        if utilisateur.id not in utilisateurs_b:
            new_utilisateur = Utilisateur(
                id=utilisateur.id,
                nom=utilisateur.nom,
                email=utilisateur.email,
                updated_at=utilisateur.updated_at
            )
            session_b.add(new_utilisateur)

    session_b.commit()


def detect_conflicts(session_a: Session, session_b: Session):
    """
    Détecte les conflits entre les deux bases pour les utilisateurs ayant le même ID.
    """
    utilisateurs_a = {u.id: u for u in session_a.query(Utilisateur).all()}
    utilisateurs_b = {u.id: u for u in session_b.query(Utilisateur).all()}

    conflits = []

    for id_ in set(utilisateurs_a.keys()) & set(utilisateurs_b.keys()):
        a, b = utilisateurs_a[id_], utilisateurs_b[id_]
        if (
            a.nom != b.nom or
            a.email != b.email
        ):
            conflits.append({
                "id": id_,
                "utilisateur_a": {
                    "nom": a.nom,
                    "email": a.email,
                    "updated_at": a.updated_at.isoformat() if a.updated_at else None
                },
                "utilisateur_b": {
                    "nom": b.nom,
                    "email": b.email,
                    "updated_at": b.updated_at.isoformat() if b.updated_at else None
                }
            })

    return conflits


def resolve_conflicts(session_a: Session, session_b: Session, strategy: str):
    conflits = detect_conflicts(session_a, session_b)
    resolved = []

    if not strategy:
        raise ValueError("La stratégie de résolution doit être spécifiée.")

    print(f"[DEBUG] Stratégie de résolution : {strategy}")
    print(f"[DEBUG] Nombre de conflits détectés : {len(conflits)}")

    for conflit in conflits:
        id_ = conflit["id"]
        utilisateur_a = session_a.query(Utilisateur).get(id_)
        utilisateur_b = session_b.query(Utilisateur).get(id_)

        if utilisateur_a is None or utilisateur_b is None:
            print(f"[WARN] Utilisateur avec id={id_} absent dans une des bases, saut du conflit.")
            continue

        if strategy == "latest":
            # Choix de la source la plus récente
            if utilisateur_a.updated_at > utilisateur_b.updated_at:
                source = utilisateur_a
                target_session = session_b
            else:
                source = utilisateur_b
                target_session = session_a

            target = target_session.query(Utilisateur).get(id_)
            champs = ["nom", "email"]

            for champ in champs:
                ancienne_valeur = getattr(target, champ)
                nouvelle_valeur = getattr(source, champ)
                if ancienne_valeur != nouvelle_valeur:
                    log = LogsConflits(
                        client_id=id_,  # ⚠️ tu peux renommer en utilisateur_id dans ta table logs_conflits
                        champ=champ,
                        valeur_a=ancienne_valeur,
                        valeur_b=nouvelle_valeur,
                        resolution=nouvelle_valeur,
                        horodatage=datetime.datetime.utcnow()
                    )
                    target_session.add(log)

            target.nom = source.nom
            target.email = source.email
            target.updated_at = source.updated_at
            resolved.append(id_)

        elif strategy == "field-wise":

            def merge_field(field_name):
                val_a = getattr(utilisateur_a, field_name)
                val_b = getattr(utilisateur_b, field_name)
                if val_a != val_b:
                    return val_a if utilisateur_a.updated_at >= utilisateur_b.updated_at else val_b
                return val_a

            champs = ["nom", "email"]
            new_values = {champ: merge_field(champ) for champ in champs}
            new_updated_at = max(utilisateur_a.updated_at, utilisateur_b.updated_at)

            for champ in champs:
                ancienne_valeur_a = getattr(utilisateur_a, champ)
                ancienne_valeur_b = getattr(utilisateur_b, champ)
                nouvelle_valeur = new_values[champ]

                if ancienne_valeur_a != nouvelle_valeur or ancienne_valeur_b != nouvelle_valeur:
                    log_a = LogsConflits(
                        client_id=id_,  # ⚠️ idem ici
                        champ=champ,
                        valeur_a=ancienne_valeur_a,
                        valeur_b=ancienne_valeur_b,
                        resolution=nouvelle_valeur,
                        horodatage=datetime.datetime.utcnow()
                    )
                    log_b = LogsConflits(
                        client_id=id_,
                        champ=champ,
                        valeur_a=ancienne_valeur_a,
                        valeur_b=ancienne_valeur_b,
                        resolution=nouvelle_valeur,
                        horodatage=datetime.datetime.utcnow()
                    )
                    session_a.add(log_a)
                    session_b.add(log_b)

            for u in (utilisateur_a, utilisateur_b):
                u.nom = new_values["nom"]
                u.email = new_values["email"]
                u.updated_at = new_updated_at

            resolved.append(id_)

        else:
            raise ValueError(f"Stratégie inconnue : {strategy}")

    session_a.commit()
    session_b.commit()
    print(f"[DEBUG] Conflits résolus : {resolved}")
    return resolved
