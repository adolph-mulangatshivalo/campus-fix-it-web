import sys
import os

# Add parent directory to path to import app and config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_db_connection

def apply_migration():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to db")
        return
        
    cursor = conn.cursor()
    
    with open(os.path.join(os.path.dirname(__file__), '../database/migration_worker.sql'), 'r') as f:
        sql = f.read()
        
    for statement in sql.split(';'):
        if statement.strip():
            try:
                print(f"Executing: {statement.strip()}")
                cursor.execute(statement)
                conn.commit()
            except Exception as e:
                print(f"Error: {e}")
                
    cursor.close()
    conn.close()
    print("Migration finished.")

if __name__ == '__main__':
    with app.app_context():
        apply_migration()
