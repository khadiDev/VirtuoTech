import requests
from datetime import datetime, timezone
from dateutil import parser  

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
    
    for course in courses.get("result", []):
        students = course.get("STUDENTS", [])
        for s in students:
            if s.get("studentId") == student_id:
                # send email
                url = f"{API_BASE}/course/send-sign-emails"
                payload = {
                    "course": s.get("courseId"),  
                    "students": [student_id]
                } 
                response = requests.post(url, headers=HEADERS, json=payload)              
                if response.status_code == 200:
                    return f"Signature envoyée à l'étudiant {student_id} pour le cours : {course.get('NAME', 'Nom inconnu')}"
                else:
                    return f"Erreur lors de l'envoi de la signature : {response.text}"
    return (f"Étudiant {student_id} n'est pas inscrit au cours : {course.get('NAME', 'Nom inconnu')}")

def alertes_delay(student_id, courses):
    for course in courses.get("result", []):
        students = course.get("STUDENTS", [])
        for s in students:
            if s.get("studentId") == student_id:
                course_id = s.get("courseId")
                # send delay
                url = f"{API_BASE}/presential-states/set-delay/{course_id}/{student_id}"
                payload = {
                    "courseID": course_id,  
                    "studentId": [student_id],
                    "delay": 18
                } 
                response = requests.patch(url, headers=HEADERS, json=payload)  
    return "en retard"            
