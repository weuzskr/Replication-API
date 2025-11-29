from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# === Client côté lecture ===
class ClientOut(BaseModel):
    id: int
    nom: Optional[str]
    email: Optional[str]
    telephone: Optional[str]
    updated_at: datetime

    class Config:
        orm_mode = True


# === Conflit détecté ===
class Conflit(BaseModel):
    client_id: int
    champ: str
    valeur_a: Optional[str]
    valeur_b: Optional[str]
    resolution: Optional[str] = None
    horodatage: Optional[datetime] = None

    class Config:
        orm_mode = True


# === Requête pour résoudre un conflit ===
class ConflitResolutionRequest(BaseModel):
    client_id: int
    champ: str
    resolution: str  # par exemple 'valeur_a', 'valeur_b', ou une valeur fusionnée personnalisée
