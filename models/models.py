from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    nom = Column(String)
    email = Column(String)
    telephone = Column(String)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
class LogsConflits(Base):
    __tablename__ = 'logs_conflits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    champ = Column(String, nullable=False)
    valeur_a = Column(String, nullable=True)
    valeur_b = Column(String, nullable=True)
    resolution = Column(String, nullable=True)
    horodatage = Column(DateTime, default=datetime.datetime.utcnow)

class Utilisateur(Base):
        __tablename__ = 'utilisateurs'

        id = Column(Integer, primary_key=True, autoincrement=True)
        nom = Column(String, nullable=False)
        email = Column(String, unique=True, nullable=False)
        updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

        def __repr__(self):
            return f"<Utilisateur(id={self.id}, nom='{self.nom}', email='{self.email}')>"
