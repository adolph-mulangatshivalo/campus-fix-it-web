import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv

# Load env variables so we can test locally
load_dotenv()

def create_categories():
    print("--- Creating Default Categories ---")
    
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
    
    categories = [
        {'name': 'Plumbing', 'description': 'Leaks, blocked toilets, broken sinks, water issues'},
        {'name': 'Electrical', 'description': 'Power outages, broken outlets, exposed wires'},
        {'name': 'Furniture', 'description': 'Broken chairs, desks, or other furniture'},
        {'name': 'Buildings', 'description': 'Broken windows, structural issues, roof leaks'},
        {'name': 'Toilets', 'description': 'Restroom supplies, cleanliness, broken dispensers'},
        {'name': 'Lighting', 'description': 'Burnt out bulbs, broken light fixtures'},
        {'name': 'Doors/Locks', 'description': 'Broken locks, doors won\'t close or open'},
        {'name': 'Cleaning', 'description': 'Spills, trash overflow, general cleaning needed'},
        {'name': 'Grounds/Landscaping', 'description': 'Fallen branches, pathway issues'},
        {'name': 'Other', 'description': 'Any other physical maintenance issues'}
    ]
    
    for cat in categories:
        # Check if exists
        docs = db.collection('categories').where('name', '==', cat['name']).limit(1).get()
        if len(docs) == 0:
            db.collection('categories').add(cat)
            print(f"Added category: {cat['name']}")
        else:
            print(f"Category already exists: {cat['name']}")
            
    print("Success! Categories are ready.")

if __name__ == "__main__":
    create_categories()
