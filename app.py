from flask import Flask, jsonify, g, render_template, session, redirect, url_for, send_from_directory
import os
from config import Config
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Import blueprints
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp
from routes.worker import worker_bp

app = Flask(__name__)
app.config.from_object(Config)

# Configure Uploads
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except OSError:
    # Vercel has a read-only filesystem, so we ignore this error.
    # Note: Local image uploads will not persist on Vercel's standard plan.
    pass

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(worker_bp, url_prefix='/worker')

# Initialize Firebase
firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')
db = None
try:
    if firebase_creds_json:
        cred_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(cred_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', 'campus-fix-it.appspot.com')
            })
    else:
        if not firebase_admin._apps:
            firebase_admin.initialize_app(options={
                'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', 'campus-fix-it.appspot.com')
            })
    db = firestore.client()
except Exception as e:
    print(f"Firebase Initialization Error: {e}")

@app.before_request
def before_request():
    """Make Firestore client available to routes."""
    g.db = db

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif session.get('role') == 'worker':
            return redirect(url_for('worker.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/test-db')
def test_db():
    if g.db:
        return jsonify({"status": "success", "message": "Successfully connected to Firebase!"})
    else:
        return jsonify({"status": "error", "message": "Failed to connect to Firebase."}), 500

if __name__ == '__main__':
    app.run(debug=True)
