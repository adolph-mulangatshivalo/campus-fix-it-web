import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_db_connection
from models.user import create_worker_user

def add_worker():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to db")
        return
        
    try:
        worker_id = create_worker_user(conn, "Bob Builder", "bob@campus.com", "password")
        print(f"Worker created successfully with ID: {worker_id}")
    except Exception as e:
        print(f"Error creating worker: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        add_worker()
