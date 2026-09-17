import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, get_db_connection

def migrate():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect")
        return
        
    try:
        cursor = conn.cursor()
        
        # Get FK name
        cursor.execute("""
            SELECT CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'campus_fix_it'
              AND TABLE_NAME = 'report_updates'
              AND COLUMN_NAME = 'admin_id'
              AND REFERENCED_TABLE_NAME = 'users'
        """)
        result = cursor.fetchone()
        
        if result:
            fk_name = result[0]
            print(f"Dropping FK: {fk_name}")
            cursor.execute(f"ALTER TABLE report_updates DROP FOREIGN KEY {fk_name}")
        
        print("Modifying column to allow NULL")
        cursor.execute("ALTER TABLE report_updates MODIFY admin_id INT NULL")
        
        print("Adding new FK with SET NULL")
        cursor.execute("ALTER TABLE report_updates ADD FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL")
        
        conn.commit()
        print("Migration successful")
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        migrate()
