import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, get_db_connection

def list_users():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, full_name, student_number, email, role FROM users")
        for u in cursor.fetchall():
            print(u)
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        list_users()
