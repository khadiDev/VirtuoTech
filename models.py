# models.py
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class UserType(str, enum.Enum):
    eleve = "eleve"
    prof = "prof"
    invite = "invite"

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    email = Column(String, nullable=False)
    type = Column(Enum(UserType), nullable=False)
    uid_carte = Column(String, unique=True, nullable=False)
    expiration_carte = Column(DateTime, nullable=True)

class Passage(Base):
    __tablename__ = "passages"
    id = Column(Integer, primary_key=True)
    uid = Column(String, nullable=False)
    horodatage = Column(DateTime, default=datetime.utcnow)

class Alerte(Base):
    __tablename__ = "alertes"
    id = Column(Integer, primary_key=True)
    uid = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
