from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime

def create_report(db, user_id, category_id, title, description, location, image_path):
    # Fetch user details for denormalization
    user_doc = db.collection('users').document(str(user_id)).get()
    student_name = ""
    student_number = ""
    email = ""
    if user_doc.exists:
        u_data = user_doc.to_dict()
        student_name = u_data.get('full_name', '')
        student_number = u_data.get('student_number', '')
        email = u_data.get('email', '')

    # Fetch category details
    cat_doc = db.collection('categories').document(str(category_id)).get()
    category_name = ""
    if cat_doc.exists:
        category_name = cat_doc.to_dict().get('name', '')

    report_data = {
        'user_id': str(user_id),
        'student_name': student_name,
        'student_number': student_number,
        'email': email,
        
        'category_id': str(category_id),
        'category_name': category_name,
        
        'title': title,
        'description': description,
        'location': location,
        'image_path': image_path,
        
        'status': 'Submitted',
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        
        'worker_id': None,
        'worker_name': None
    }
    
    _, doc_ref = db.collection('reports').add(report_data)
    return doc_ref.id

def get_student_reports(db, user_id):
    query = db.collection('reports').where(filter=FieldFilter('user_id', '==', str(user_id)))
    reports = []
    for doc in query.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        reports.append(data)
    reports.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
    return reports

def get_all_reports(db, status_filter=None, category_filter=None, search_query=None):
    query = db.collection('reports')
    
    if status_filter:
        query = query.where(filter=FieldFilter('status', '==', status_filter))
    if category_filter:
        query = query.where(filter=FieldFilter('category_id', '==', str(category_filter)))
        
    reports = []
    for doc in query.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        
        if search_query:
            sq = search_query.lower()
            matches = (
                sq in data.get('title', '').lower() or
                sq in data.get('description', '').lower() or
                sq in data.get('location', '').lower() or
                sq in data.get('student_number', '').lower()
            )
            if not matches:
                continue
                
        reports.append(data)
        
    reports.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
    return reports

def get_report_by_id(db, report_id):
    if not report_id: return None
    doc = db.collection('reports').document(str(report_id)).get()
    if not doc.exists:
        return None
        
    report = doc.to_dict()
    report['id'] = doc.id
    
    updates_query = db.collection('report_updates').where(filter=FieldFilter('report_id', '==', str(report_id)))
    updates = []
    for u_doc in updates_query.stream():
        u_data = u_doc.to_dict()
        u_data['id'] = u_doc.id
        updates.append(u_data)
        
    updates.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
    report['updates'] = updates
    
    return report

def update_report_status(db, report_id, admin_id, status, comment):
    admin_doc = db.collection('users').document(str(admin_id)).get()
    admin_name = admin_doc.to_dict().get('full_name', '') if admin_doc.exists else ''
    
    db.collection('reports').document(str(report_id)).update({
        'status': status,
        'updated_at': datetime.now()
    })
    
    db.collection('report_updates').add({
        'report_id': str(report_id),
        'admin_id': str(admin_id),
        'admin_name': admin_name,
        'status': status,
        'comment': comment,
        'created_at': datetime.now()
    })

def assign_worker_to_report(db, report_id, worker_id, admin_id):
    worker_doc = db.collection('users').document(str(worker_id)).get()
    worker_name = worker_doc.to_dict().get('full_name', '') if worker_doc.exists else ''
    
    admin_doc = db.collection('users').document(str(admin_id)).get()
    admin_name = admin_doc.to_dict().get('full_name', '') if admin_doc.exists else ''

    db.collection('reports').document(str(report_id)).update({
        'status': 'Assigned',
        'worker_id': str(worker_id),
        'worker_name': worker_name,
        'updated_at': datetime.now()
    })
    
    db.collection('report_updates').add({
        'report_id': str(report_id),
        'admin_id': str(admin_id),
        'admin_name': admin_name,
        'status': 'Assigned',
        'comment': 'Report assigned to maintenance worker.',
        'created_at': datetime.now()
    })

def get_worker_reports(db, worker_id):
    query = db.collection('reports').where(filter=FieldFilter('worker_id', '==', str(worker_id)))
    reports = []
    for doc in query.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        reports.append(data)
    reports.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
    return reports

def update_report_status_worker(db, report_id, worker_id, status, comment):
    worker_doc = db.collection('users').document(str(worker_id)).get()
    worker_name = worker_doc.to_dict().get('full_name', '') if worker_doc.exists else ''

    db.collection('reports').document(str(report_id)).update({
        'status': status,
        'updated_at': datetime.now()
    })
    
    db.collection('report_updates').add({
        'report_id': str(report_id),
        'admin_id': str(worker_id),
        'admin_name': worker_name,
        'status': status,
        'comment': comment,
        'created_at': datetime.now()
    })
