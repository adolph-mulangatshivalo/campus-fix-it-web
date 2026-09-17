import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, get_db_connection

def clear_students():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return
        
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE role = 'student'")
        conn.commit()
        print("Cleared student accounts so user can start fresh.")
    except Exception as e:
        print(f"Failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        clear_students()
