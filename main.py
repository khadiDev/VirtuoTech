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
    print (heure)
    if time(9, 30) <= heure <= time(10, 0):
        print (heure)
        student_id = get_student_id_by_email(email)
        # student_id = student["result"].get("id")
        courses = get_all_courses()
        # if student_id is not None:
        present = is_student_in_courses(student_id, courses)
    elif time(17, 30) <= heure <= time(18, 30):
        student_id  = get_student_id_by_email(email)
        # student_id = student["result"].get("id")
        courses = get_all_courses()
        # if student_id is not None:
        present = is_student_in_courses(student_id, courses)
        # else :
        #     print ("okkk")
    else :
        student_id  = get_student_id_by_email(email)
        # student_id = student["result"].get("id")
        courses = get_all_courses()
        # return("Pas à l'heure")
        delay = alertes_delay(student_id, courses)
    # Pauses longues
    # if time(11, 45) < heure < time(15, 30):
    #     dernier = db.query(Passage).filter_by(uid=uid).order_by(Passage.horodatage.desc()).first()
    #     if dernier and (timestamp - dernier.horodatage > timedelta(minutes=15)):
    #         db.add(Alerte(uid=uid, message="Pause prolongée > 15 min"))
    #         db.commit()

    # return present
    return delay


@app.get("/utilisateurs")
def get_utilisateurs_from_edusign():
    students = get_all_students()
    result = []

    for s in students:
        result.append({
            "id": s.get("ID") or s.get("id"),
            "prenom": s.get("FIRSTNAME", ""),
            "nom": s.get("LASTNAME", ""),
            "email": s.get("EMAIL", ""),
            "formation": s.get("TRAINING_NAME", ""),
            "telephone": s.get("PHONE", ""),
            "entreprise": s.get("COMPANY", ""),
            "badge_id": s.get("BADGE_ID", ""),
            "photo": s.get("PHOTO", ""),
        })

    return result

from edusign import get_student_id_by_email
import requests

@app.get("/utilisateurs/by-email")
def get_utilisateur_by_email(email: str):
    url = f"https://ext.edusign.fr/v1/student/by-email/{email}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer f538f33b14ce5958adb324cc0dcf5b439b6689c3a50f99b0611553e8cb5e7ee0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Étudiant introuvable dans Edusign")

    data = response.json().get("result", {})

    return {
        "id": data.get("ID") or data.get("id"),
        "prenom": data.get("FIRSTNAME", ""),
        "nom": data.get("LASTNAME", ""),
        "email": data.get("EMAIL", ""),
        "formation": data.get("TRAINING_NAME", ""),
        "telephone": data.get("PHONE", ""),
        "entreprise": data.get("COMPANY", ""),
        "badge_id": data.get("BADGE_ID", ""),
        "photo": data.get("PHOTO", "")
    }

from edusign import get_all_students

@app.get("/alertes")
def get_alertes():
    db = SessionLocal()
    alertes = db.query(Alerte).order_by(Alerte.timestamp.desc()).all()

    # Récupérer tous les étudiants depuis Edusign une seule fois
    students = get_all_students()
    student_lookup = {s.get("BADGE_ID"): s for s in students}

    result = []
    for alerte in alertes:
        edusign_info = student_lookup.get(alerte.uid, {})

        result.append({
            "id": alerte.id,
            "uid": alerte.uid,
            "message": alerte.message,
            "timestamp": alerte.timestamp,
            "prenom": edusign_info.get("FIRSTNAME", ""),
            "nom": edusign_info.get("LASTNAME", ""),
            "email": edusign_info.get("EMAIL", ""),
            "photo": edusign_info.get("PHOTO", "")
        })

    return result
from fastapi import Body
