import os
import json
import firebase_admin
from firebase_admin import credentials, storage
from werkzeug.datastructures import FileStorage
import io
from dotenv import load_dotenv

load_dotenv()

def test():
    firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')
    if firebase_creds_json:
        cred_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(cred_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'campus-fix-it.appspot.com'
            })
    else:
        print("No FIREBASE_CREDENTIALS found.")
        return

    bucket = storage.bucket()
    blob = bucket.blob('reports/test_image.txt')
    
    # Mock a FileStorage object
    dummy_file = io.BytesIO(b"Hello world!")
    file_storage = FileStorage(stream=dummy_file, filename="test_image.txt", content_type="text/plain")
    
    try:
        blob.upload_from_file(file_storage.stream, content_type=file_storage.content_type)
        blob.make_public()
        print(f"Success! URL: {blob.public_url}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test()
