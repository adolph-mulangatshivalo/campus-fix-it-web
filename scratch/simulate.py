import urllib.request
import urllib.parse
from http.cookiejar import CookieJar

def simulate():
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    # 1. Register
    data = urllib.parse.urlencode({
        'full_name': 'Test User',
        'student_number': '12345678',
        'email': '12345678@univen.mvula.ac.za',
        'password': 'password123',
        'confirm_password': 'password123'
    }).encode('utf-8')
    print("Registering...")
    r1 = opener.open('http://127.0.0.1:5000/auth/register', data=data)
    print("Register Response URL:", r1.geturl())
    
    # 2. Login
    login_data = urllib.parse.urlencode({
        'email': '12345678@univen.mvula.ac.za',
        'password': 'password123',
        'login_role': 'student'
    }).encode('utf-8')
    print("Logging in...")
    r2 = opener.open('http://127.0.0.1:5000/auth/login', data=login_data)
    print("Login Response URL:", r2.geturl())
    
    if 'student/dashboard' in r2.geturl():
        print("LOGIN SUCCESSFUL!")
    else:
        print("LOGIN FAILED!")
        
    # Delete test user
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app import app, get_db_connection
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = '12345678@univen.mvula.ac.za'")
        conn.commit()
        conn.close()

if __name__ == '__main__':
    simulate()
