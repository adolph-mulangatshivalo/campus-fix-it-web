def create_report(conn, user_id, category_id, title, description, location, image_path):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reports (user_id, category_id, title, description, location, image_path, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'Submitted')
        """,
        (user_id, category_id, title, description, location, image_path)
    )
    conn.commit()
    report_id = cursor.lastrowid
    cursor.close()
    return report_id

def get_student_reports(conn, user_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT r.*, c.name as category_name 
        FROM reports r
        JOIN categories c ON r.category_id = c.id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
        """, 
        (user_id,)
    )
    reports = cursor.fetchall()
    cursor.close()
    return reports

def get_all_reports(conn, status_filter=None, category_filter=None, search_query=None):
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT r.*, c.name as category_name, u.full_name as student_name, w.full_name as worker_name
        FROM reports r
        JOIN categories c ON r.category_id = c.id
        JOIN users u ON r.user_id = u.id
        LEFT JOIN users w ON r.worker_id = w.id
        WHERE 1=1
    """
    params = []
    
    if status_filter:
        query += " AND r.status = %s"
        params.append(status_filter)
        
    if category_filter:
        query += " AND r.category_id = %s"
        params.append(category_filter)
        
    if search_query:
        query += " AND (r.title LIKE %s OR r.description LIKE %s OR r.location LIKE %s OR u.student_number LIKE %s)"
        search_term = f"%{search_query}%"
        params.extend([search_term, search_term, search_term, search_term])
        
    query += " ORDER BY r.created_at DESC"
    
    cursor.execute(query, tuple(params))
    reports = cursor.fetchall()
    cursor.close()
    return reports

def get_report_by_id(conn, report_id):
    cursor = conn.cursor(dictionary=True)
    
    # Get main report details
    cursor.execute(
        """
        SELECT r.*, c.name as category_name, u.full_name as student_name, u.student_number, u.email,
               w.full_name as worker_name, w.id as worker_id
        FROM reports r
        JOIN categories c ON r.category_id = c.id
        JOIN users u ON r.user_id = u.id
        LEFT JOIN users w ON r.worker_id = w.id
        WHERE r.id = %s
        """, 
        (report_id,)
    )
    report = cursor.fetchone()
    
    if not report:
        cursor.close()
        return None
        
    # Get update history
    cursor.execute(
        """
        SELECT ru.*, u.full_name as admin_name
        FROM report_updates ru
        JOIN users u ON ru.admin_id = u.id
        WHERE ru.report_id = %s
        ORDER BY ru.created_at DESC
        """,
        (report_id,)
    )
    report['updates'] = cursor.fetchall()
    
    cursor.close()
    return report

def update_report_status(conn, report_id, admin_id, status, comment):
    cursor = conn.cursor()
    try:
        # Update main report status
        cursor.execute(
            "UPDATE reports SET status = %s WHERE id = %s",
            (status, report_id)
        )
        
        # Insert into updates history
        cursor.execute(
            """
            INSERT INTO report_updates (report_id, admin_id, status, comment)
            VALUES (%s, %s, %s, %s)
            """,
            (report_id, admin_id, status, comment)
        )
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

def assign_worker_to_report(conn, report_id, worker_id, admin_id):
    cursor = conn.cursor()
    try:
        # Update main report status and worker
        cursor.execute(
            "UPDATE reports SET status = 'Assigned', worker_id = %s WHERE id = %s",
            (worker_id, report_id)
        )
        
        # Insert into updates history
        cursor.execute(
            """
            INSERT INTO report_updates (report_id, admin_id, status, comment)
            VALUES (%s, %s, 'Assigned', 'Report assigned to maintenance worker.')
            """,
            (report_id, admin_id)
        )
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

def get_worker_reports(conn, worker_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT r.*, c.name as category_name, u.full_name as student_name
        FROM reports r
        JOIN categories c ON r.category_id = c.id
        JOIN users u ON r.user_id = u.id
        WHERE r.worker_id = %s
        ORDER BY r.created_at DESC
        """, 
        (worker_id,)
    )
    reports = cursor.fetchall()
    cursor.close()
    return reports

def update_report_status_worker(conn, report_id, worker_id, status, comment):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE reports SET status = %s WHERE id = %s AND worker_id = %s",
            (status, report_id, worker_id)
        )
        
        # We reuse admin_id column for the worker_id who updated it
        cursor.execute(
            """
            INSERT INTO report_updates (report_id, admin_id, status, comment)
            VALUES (%s, %s, %s, %s)
            """,
            (report_id, worker_id, status, comment)
        )
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
