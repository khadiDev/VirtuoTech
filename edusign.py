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
    "Content-Type": "application/json",
    "Authorization": "Bearer f538f33b14ce5958adb324cc0dcf5b439b6689c3a50f99b0611553e8cb5e7ee0"
}


def get_student_id_by_email(email):
    url = f"{API_BASE}/student/by-email/{email}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Erreur récupération étudiants :", response.text)
        return None

    if response.status_code == 200:
        data = response.json()
        return data["result"].get("id")      
    else:
        return None


def get_all_courses():
    url = f"{API_BASE}/course"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Erreur récupération cours :", response.text)
        return []
    return response.json()

def is_student_in_courses(student_id, courses):
    
    # print("DEBUG courses:", courses)
    for course in courses.get("result", []):
        students = course.get("STUDENTS", [])
        for s in students:
            if s.get("studentId") == student_id:
                # send email
                url = f"{API_BASE}/course/send-sign-emails"
                payload = {
                    "course": s.get("courseId"),  # ou course.get("id") selon ta structure
                    "students": [student_id]
                } 
                response = requests.post(url, headers=HEADERS, json=payload)              
                if response.status_code == 200:
                    return f"Signature envoyée à l'étudiant {student_id} pour le cours : {course.get('NAME', 'Nom inconnu')}"
                else:
                    return f"Erreur lors de l'envoi de la signature : {response.text}"
    return (f"Étudiant {student_id} n'est pas inscrit au cours : {course.get('NAME', 'Nom inconnu')}")

    
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
