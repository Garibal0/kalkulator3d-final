import firebase_admin
from firebase_admin import credentials, db
import os
import json

# 🔐 Wczytujemy dane klucza z ENV jako JSON (zamiast z pliku!)
cred_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
cred_dict = json.loads(cred_json)

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://kalkulator3d-default-rtdb.europe-west1.firebasedatabase.app/'
    })

def get_data(path):
    ref = db.reference(path)
    return ref.get() or []

def set_data(path, value):
    ref = db.reference(path)
    ref.set(value)

def load_filaments():
    return get_data("/filamenty")

def save_filaments(data):
    set_data("/filamenty", data)

def load_historia():
    return get_data("/historia")

def save_historia(data):
    set_data("/historia", data)
