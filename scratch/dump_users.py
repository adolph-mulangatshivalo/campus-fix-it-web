import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv

load_dotenv()

def dump_users():
    firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')
    if firebase_creds_json:
        cred_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(cred_dict)
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)
    else:
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app()
            
    db = firestore.client()
    
    users = db.collection('users').get()
    print("--- ALL USERS IN DB ---")
    for u in users:
        d = u.to_dict()
        print(f"ID: {u.id}, Email: {d.get('email')}, Role: {d.get('role')}, StudentNo: {d.get('student_number')}")
        
if __name__ == "__main__":
    dump_users()
