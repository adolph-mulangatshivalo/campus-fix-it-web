def get_all_categories(db):
    categories_ref = db.collection('categories')
    categories = []
    # Fetch all categories
    for doc in categories_ref.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        categories.append(data)
    
    # Sort categories by name
    categories.sort(key=lambda x: x.get('name', ''))
    return categories

def get_category_by_id(db, category_id):
    if not category_id: return None
    doc = db.collection('categories').document(str(category_id)).get()
    if doc.exists:
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    return None
