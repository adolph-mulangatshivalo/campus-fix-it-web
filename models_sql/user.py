from werkzeug.security import generate_password_hash, check_password_hash

def get_user_by_email(conn, email):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    return user

def get_user_by_login(conn, login_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s OR student_number = %s", (login_id, login_id))
    user = cursor.fetchone()
    cursor.close()
    return user

def get_user_by_id(conn, user_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user

def create_user(conn, full_name, id_number, email, password, role):
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    
    try:
        cursor.execute(
            "INSERT INTO users (full_name, student_number, email, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
            (full_name, id_number, email, password_hash, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        return user_id
    except Exception as e:
        conn.rollback()
        cursor.close()
        raise e

def update_user(conn, user_id, full_name, staff_id, email, role, new_password=None):
    cursor = conn.cursor()
    try:
        if new_password:
            password_hash = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE users SET full_name = %s, student_number = %s, email = %s, role = %s, password_hash = %s WHERE id = %s",
                (full_name, staff_id, email, role, password_hash, user_id)
            )
        else:
            cursor.execute(
                "UPDATE users SET full_name = %s, student_number = %s, email = %s, role = %s WHERE id = %s",
                (full_name, staff_id, email, role, user_id)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

def get_all_workers(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, email FROM users WHERE role = 'worker'")
    workers = cursor.fetchall()
    cursor.close()
    return workers

def get_all_staff(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, student_number as staff_id, email, role FROM users WHERE role IN ('admin', 'worker') ORDER BY role, full_name")
    staff = cursor.fetchall()
    cursor.close()
    return staff

def delete_user(conn, user_id):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
