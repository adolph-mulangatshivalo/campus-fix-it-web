import requests

session = requests.Session()
# Test 1: Worker login with wrong password
print("Testing worker login with wrong password...")
resp = session.post('http://localhost:5000/auth/login', data={
    'login_role': 'worker',
    'email': 'WOR112',
    'password': 'wrong'
}, allow_redirects=False)

print(f"Status Code: {resp.status_code}")
print(f"Redirect URL: {resp.headers.get('Location')}")

# Test 2: Student login with valid credentials (let's assume 123 for now, we don't know password)
