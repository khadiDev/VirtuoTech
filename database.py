# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 🔧 SQLite pour local — tu peux changer pour PostgreSQL si besoin
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_bGu0ief7MKJm@ep-patient-pond-a81uv360-pooler.eastus2.azure.neon.tech/nfc_presence?sslmode=require&channel_binding=require"

# connect_args est nécessaire pour SQLite en mode fichier
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session locale à utiliser dans les endpoints FastAPI
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
