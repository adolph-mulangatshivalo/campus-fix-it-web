import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_db_connection

def delete_bob():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to db")
        return
        
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = 'bob@campus.com'")
        conn.commit()
        cursor.close()
        print("Bob Builder deleted successfully")
    except Exception as e:
        print(f"Error deleting bob: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        delete_bob()
