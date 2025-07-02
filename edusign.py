# # edusign.py
# import requests

# EDUSIGN_TOKEN = "Bearer f538f33b14ce5958adb324cc0dcf5b439b6689c3a50f99b0611553e8cb5e7ee0"

# def send_presence_edusign(uid, email):
#     payload = {
#         "uid": uid,
#         "email": email,
#     }
#     headers = {"Authorization": f"Bearer {EDUSIGN_TOKEN}"}
#     response = requests.post("https://api.edusign.fr/presence", json=payload, headers=headers)

#     return response.status_code

import requests
from datetime import datetime, timezone
from dateutil import parser  # pip install python-dateutil

API_BASE = "https://ext.edusign.fr/v1"
HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer f538f33b14ce5958adb324cc0dcf5b439b6689c3a50f99b0611553e8cb5e7ee0"
}


def get_student_by_email(email):
    url = f"{API_BASE}/student/by-email/{email}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Erreur récupération étudiants :", response.text)
        return None

    if response.status_code == 200:
        return response.json()  
    else:
        return None


def get_all_courses():
    url = f"{API_BASE}/course"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Erreur récupération cours :", response.text)
        return []
    return response.json().get("result", [])

def send_presence(student_id, moment: str):
    """
    Envoie une signature de présence à Edusign pour l'étudiant donné.

    Args:
        student_id (str): ID de l'étudiant dans Edusign.
        moment (str): "matin" ou "soir"

    Returns:
        int: code HTTP (200 = OK)
    """
    url = f"{API_BASE}/student/{student_id}/sign"
    payload = {
        "moment": moment
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Présence envoyée ({moment}) pour étudiant {student_id}")
    else:
        print(f"❌ Erreur lors de l'envoi ({moment}) pour {student_id} → {response.status_code} : {response.text}")
    
    return response.status_code



# def is_student_scheduled_now(email):
#     student = get_student_by_email(email)
#     if not student:
#         print(f"Aucun étudiant trouvé avec l’email : {email}")
#         return False

#     student_id = student["ID"]
#     now = datetime.now(timezone.utc)

#     courses = get_all_courses()
#     for course in courses:
#         try:
#             start = parser.parse(course["START"])
#             end = parser.parse(course["END"])
#         except:
#             continue  # S'il y a une erreur de date, on passe

#         if start <= now <= end:
#             for s in course.get("STUDENTS", []):
#                 if s.get("studentId") == student_id:
#                     print(f"✅ Étudiant {email} est inscrit au cours : {course['NAME']}")
#                     return True

#     print(f"❌ Étudiant {email} n'est pas inscrit à un cours en ce moment")
#     return False
