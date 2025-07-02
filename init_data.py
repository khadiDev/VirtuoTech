from models import Utilisateur, Base
from database import engine, SessionLocal
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)
db = SessionLocal()

db.add_all([
    Utilisateur(nom="Alice Dupont", type="eleve", uid_carte="04:A3:12:FC"),
    Utilisateur(nom="Professeur Jean", type="prof", uid_carte="AA:BB:CC:DD"),
    Utilisateur(nom="Invité Michel", type="invite", uid_carte="01:02:03:04", expiration_carte=datetime.utcnow() + timedelta(days=1)),
])
db.commit()
print("Utilisateurs initiaux créés.")
