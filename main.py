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