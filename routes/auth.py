from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import check_password_hash
from models.user import get_user_by_email, get_user_by_login, create_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, redirect
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        student_number = request.form.get('student_number')
        if student_number:
            student_number = student_number.strip().upper()
        email = request.form.get('email')
        if email:
            email = email.strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not full_name or not student_number or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))
            
        if not email.endswith('@univen.mvula.ac.za'):
            flash('You must use your official university email (@univen.mvula.ac.za).', 'danger')
            return redirect(url_for('auth.register'))
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
            
        # Check if email or student number already exists
        existing_user = get_user_by_email(g.db, email)
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
            
        try:
            # We enforce 'student' role here for self-registration
            create_user(g.db, full_name, student_number, email, password, 'student')
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('An error occurred during registration. Check if Student Number is unique.', 'danger')
            print(e)
            
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        login_role = request.form.get('login_role')
        
        # If it's an admin or worker, their 'email' field is actually an ID, so uppercase it. If student, lower it.
        if email:
            email = email.strip()
            if login_role in ['admin', 'worker']:
                email = email.upper()
            else:
                email = email.lower()
        
        user = get_user_by_login(g.db, email)
        
        if user and check_password_hash(user['password_hash'], password):
            if user['role'] != login_role:
                flash(f"You cannot log in as a {login_role} using a {user['role']} account.", 'danger')
                return redirect(url_for('auth.login', role=login_role))
                
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'worker':
                return redirect(url_for('worker.dashboard'))
            else:
                # Student redirect
                return redirect(url_for('student.dashboard'))
        else:
            if not user:
                if login_role == 'student':
                    flash(f"Account '{email}' not yet registered. Please create an account.", 'danger')
                else:
                    flash(f"Account '{email}' not found.", 'danger')
            else:
                flash('Invalid password. Please try again.', 'danger')
                
            return redirect(url_for('auth.login', role=login_role))
            
    role = request.args.get('role', 'student')
    return render_template('auth/login.html', active_role=role)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
