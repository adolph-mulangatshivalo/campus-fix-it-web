import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, get_db_connection

def delete_students():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return
        
    try:
        cursor = conn.cursor()
        
        # Delete all students (this will cascade and delete their reports too)
        cursor.execute("DELETE FROM users WHERE role = 'student'")
        print(f"Deleted {cursor.rowcount} students from the database.")
        
        conn.commit()
        
    except Exception as e:
        print(f"Failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        delete_students()
