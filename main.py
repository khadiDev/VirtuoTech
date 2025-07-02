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
        return {
            "status": "rejeté",
            "alerte": "Carte invitée expirée",
            "timestamp": timestamp
        }

    # Enregistrement du passage
    db.add(Passage(uid=uid, horodatage=timestamp))
    db.commit()

    heure = timestamp.time()
    student_id = None
    message = "Passage enregistré"
    statut = "ok"

    # Présence matin ou soir
    if time(9, 0) <= heure <= time(12, 0) or heure >= time(17, 30):
        student = get_student_by_email(email)
        if student:
            student_id = student["result"].get("id")
            moment = "matin" if time(9, 0) <= heure <= time(12, 0) else "soir"
            send_presence(student_id, moment)
            message = f"Présence {moment} envoyée"
        else:
            message = "Étudiant non trouvé dans Edusign"
            statut = "alerte"

    # Pause prolongée
    if time(11, 45) < heure < time(15, 30):
        dernier = db.query(Passage).filter_by(uid=uid).order_by(Passage.horodatage.desc()).first()
        if dernier and (timestamp - dernier.horodatage > timedelta(minutes=15)):
            db.add(Alerte(uid=uid, message="Pause prolongée > 15 min"))
            db.commit()
            message = "Alerte : pause prolongée"
            statut = "alerte"

    # Passage hors horaires autorisés
    if user.type == "eleve":
        if not (
            time(9, 0) <= heure <= time(12, 0)
            or heure >= time(17, 30)
            or time(11, 30) <= heure <= time(11, 45)
            or time(15, 30) <= heure <= time(15, 45)
        ):
            db.add(Alerte(uid=uid, message="Passage hors plage horaire autorisée"))
            db.commit()
            message = "Alerte : passage hors horaire autorisé"
            statut = "alerte"

    return {
        "status": statut,
        "message": message,
        "student_id": student_id,
        "timestamp": timestamp
    }




@app.get("/utilisateurs")
def get_utilisateurs():
    db = SessionLocal()
    users = db.query(Utilisateur).all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "nom": user.nom,
            "email": user.email,
            "type": user.type,
            "uid_carte": user.uid_carte,
            "expiration_carte": user.expiration_carte
        })
    return result

@app.post("/utilisateurs")
def create_utilisateur(nom: str, email: str, type: str, uid_carte: str, expiration_carte: datetime = None):
    db = SessionLocal()
    if db.query(Utilisateur).filter_by(uid_carte=uid_carte).first():
        raise HTTPException(status_code=400, detail="UID déjà existant")
    user = Utilisateur(
        nom=nom,
        email=email,
        type=type,
        uid_carte=uid_carte,
        expiration_carte=expiration_carte
    )
    db.add(user)
    db.commit()
    return {"message": "Utilisateur ajouté"}

@app.put("/utilisateurs/{uid}")
def update_utilisateur(uid: str, nom: str = None, email: str = None, type: str = None, expiration_carte: datetime = None):
    db = SessionLocal()
    user = db.query(Utilisateur).filter_by(uid_carte=uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if nom: user.nom = nom
    if email: user.email = email
    if type: user.type = type
    if expiration_carte: user.expiration_carte = expiration_carte

    db.commit()
    return {"message": "Utilisateur mis à jour"}

@app.delete("/utilisateurs/{uid}")
def delete_utilisateur(uid: str):
    db = SessionLocal()
    user = db.query(Utilisateur).filter_by(uid_carte=uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    db.delete(user)
    db.commit()
    return {"message": "Utilisateur supprimé"}

@app.get("/alertes")
def get_alertes():
    db = SessionLocal()
    alertes = db.query(Alerte).order_by(Alerte.timestamp.desc()).all()
    result = []
    for alerte in alertes:
        result.append({
            "id": alerte.id,
            "uid": alerte.uid,
            "message": alerte.message,
            "timestamp": alerte.timestamp
        })
    return result

