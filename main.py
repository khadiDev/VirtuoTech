from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta, time
from models import Base, Utilisateur, Passage, Alerte
from database import engine, SessionLocal
from edusign import *

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/pointage")
def pointage(uid: str, email: str, timestamp: datetime = None):
    db = SessionLocal()
    timestamp = timestamp or datetime.utcnow()

    user = db.query(Utilisateur).filter_by(uid_carte=uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="Carte inconnue")

    if user.type == "invite" and user.expiration_carte and timestamp > user.expiration_carte:
        db.add(Alerte(uid=uid, message="Carte invitée expirée"))
        db.commit()
        return {"status": "rejeté", "alerte": "Carte expirée"}

    # Enregistrement du passage
    db.add(Passage(uid=uid, horodatage=timestamp))
    db.commit()

    heure = timestamp.time()
    if time(9, 0) <= heure <= time(12, 0):
        student = get_student_by_email(email)
        student_id = student["result"].get("id")
    elif heure >= time(17, 30):
        student  = get_student_by_email(email)
        student_id = student["result"].get("id")

    # Pauses longues
    if time(11, 45) < heure < time(15, 30):
        dernier = db.query(Passage).filter_by(uid=uid).order_by(Passage.horodatage.desc()).first()
        if dernier and (timestamp - dernier.horodatage > timedelta(minutes=15)):
            db.add(Alerte(uid=uid, message="Pause prolongée > 15 min"))
            db.commit()

    return student_id