from werkzeug.security import generate_password_hash
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime

def get_user_by_email(db, email):
    users_ref = db.collection('users')
    query = users_ref.where(filter=FieldFilter('email', '==', email)).limit(1)
    for doc in query.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    return None

def get_user_by_login(db, login_id):
    users_ref = db.collection('users')
    # Query email
    query = users_ref.where(filter=FieldFilter('email', '==', login_id)).limit(1)
    for doc in query.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        return data
        
    # Query student_number
    query = users_ref.where(filter=FieldFilter('student_number', '==', login_id)).limit(1)
    for doc in query.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        return data
        
    return None

def get_user_by_id(db, user_id):
    if not user_id: return None
    doc = db.collection('users').document(str(user_id)).get()
    if doc.exists:
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    return None

def create_user(db, full_name, id_number, email, password, role):
    password_hash = generate_password_hash(password)
    user_data = {
        'full_name': full_name,
        'student_number': id_number,
        'email': email,
        'password_hash': password_hash,
        'role': role,
        'created_at': datetime.now()
    }
    _, doc_ref = db.collection('users').add(user_data)
    return doc_ref.id

def update_user(db, user_id, full_name, staff_id, email, role, new_password=None):
    user_ref = db.collection('users').document(str(user_id))
    update_data = {
        'full_name': full_name,
        'student_number': staff_id,
        'email': email,
        'role': role
    }
    if new_password:
        update_data['password_hash'] = generate_password_hash(new_password)
    user_ref.update(update_data)

def get_all_workers(db):
    users_ref = db.collection('users')
    query = users_ref.where(filter=FieldFilter('role', '==', 'worker'))
    workers = []
    for doc in query.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        workers.append(data)
    return workers

def get_all_staff(db):
    users_ref = db.collection('users')
    query = users_ref.where(filter=FieldFilter('role', 'in', ['admin', 'worker']))
    staff = []
    for doc in query.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        data['staff_id'] = data.get('student_number', '')
        staff.append(data)
    staff.sort(key=lambda x: (x.get('role', ''), x.get('full_name', '')))
    return staff

def delete_user(db, user_id):
    db.collection('users').document(str(user_id)).delete()
