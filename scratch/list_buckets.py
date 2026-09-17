import os
import json
from google.cloud import storage
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

def list_buckets():
    firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')
    if not firebase_creds_json:
        print("No creds")
        return
        
    cred_dict = json.loads(firebase_creds_json)
    credentials = service_account.Credentials.from_service_account_info(cred_dict)
    
    client = storage.Client(credentials=credentials, project=cred_dict['project_id'])
    
    try:
        buckets = list(client.list_buckets())
        print("Buckets found:")
        for bucket in buckets:
            print(f"- {bucket.name}")
            
        if not buckets:
            print("No buckets found. The user probably didn't enable Firebase Storage.")
    except Exception as e:
        print(f"Failed to list buckets: {e}")

if __name__ == "__main__":
    list_buckets()
