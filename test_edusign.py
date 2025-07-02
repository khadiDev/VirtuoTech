import requests
from datetime import datetime

# Change l'URL si tu es en prod ou sur un autre port
URL = "http://127.0.0.1:8000/pointage"

data = {
    "uid": "04:A3:12:FC",  # Doit exister dans ta base locale
    "email": "etudiant@example.com",  # Doit exister dans Edusign
    "timestamp": datetime.now().isoformat()
}

response = requests.post(URL, params=data)

print("Status:", response.status_code)
print("Response:", response.json())
