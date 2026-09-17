import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, get_db_connection
from werkzeug.security import generate_password_hash

def setup_superadmin():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return
        
    try:
        cursor = conn.cursor()
        
        # Delete all existing admins and workers
        cursor.execute("DELETE FROM users WHERE role IN ('admin', 'worker')")
        print("Deleted all existing workers and admins.")
        
        # Create Super Admin
        full_name = "Super Admin"
        email = "superadmin@campus.com"
        student_number = "SADM111"
        
        # Get password from environment variable instead of hardcoding
        password = os.environ.get("SUPERADMIN_PASSWORD", "ChangeThisSuperSecretPassword123!")
        password_hash = generate_password_hash(password)
        role = "admin"
        
        cursor.execute(
            "INSERT INTO users (full_name, student_number, email, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
            (full_name, student_number, email, password_hash, role)
        )
        
        conn.commit()
        print(f"Super admin {student_number} created successfully!")
        
    except Exception as e:
        print(f"Failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        setup_superadmin()
