import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.security import generate_password_hash
import getpass
import os
import json

def create_admin():
    print("--- Create Admin Account ---")
    admin_id = input("Enter Admin ID (e.g. SADM111): ")
    full_name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    password = getpass.getpass("Enter Password: ")
    
    # Initialize Firebase
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')
        if firebase_creds_json:
            cred_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
            
    db = firestore.client()
    
    password_hash = generate_password_hash(password)
    
    # Check if exists
    docs = db.collection('users').where('student_number', '==', admin_id).limit(1).get()
    if len(docs) > 0:
        print(f"Error: Admin ID {admin_id} is already registered!")
        return
        
    db.collection('users').add({
        'full_name': full_name,
        'student_number': admin_id,
        'email': email,
        'password_hash': password_hash,
        'role': 'admin'
    })
    print(f"Success! Admin account for {email} has been created in Firebase.")

if __name__ == "__main__":
    create_admin()
