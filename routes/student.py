import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, current_app
from werkzeug.utils import secure_filename
import requests
from utils.decorators import login_required
from models.category import get_all_categories
from models.report import create_report, get_student_reports, get_report_by_id

student_bp = Blueprint('student', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@student_bp.route('/dashboard')
@login_required
def dashboard():
    reports = get_student_reports(g.db, session['user_id'])
    
    # Calculate stats
    total = len(reports)
    in_progress = sum(1 for r in reports if r['status'] in ['In Progress', 'Assigned', 'Under Review'])
    fixed = sum(1 for r in reports if r['status'] == 'Fixed')
    
    return render_template('student/dashboard.html', 
                           reports=reports, 
                           total=total, 
                           in_progress=in_progress, 
                           resolved=fixed)

@student_bp.route('/report/new', methods=['GET', 'POST'])
@login_required
def submit_report():
    if request.method == 'POST':
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        location = request.form.get('location')
        
        # Handle file upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Secure the filename and add a unique ID to prevent overwriting
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
                
                try:
                    # Upload to Catbox (no API key required, 100% free forever)
                    response = requests.post(
                        'https://catbox.moe/user/api.php',
                        data={'reqtype': 'fileupload'},
                        files={'fileToUpload': (filename, file.read(), file.content_type)}
                    )
                    if response.status_code == 200:
                        image_path = response.text.strip()
                    else:
                        print(f"Catbox upload failed: {response.text}")
                        image_path = None
                except Exception as e:
                    print(f"Image upload failed: {e}")
                    image_path = None
        
        try:
            create_report(g.db, session['user_id'], category_id, title, description, location, image_path)
            flash('Your maintenance report has been successfully submitted.', 'success')
            return redirect(url_for('student.dashboard'))
        except Exception as e:
            flash('Error submitting report. Please try again.', 'danger')
            print(e)
            
    categories = get_all_categories(g.db)
    return render_template('student/submit_report.html', categories=categories)

@student_bp.route('/report/<string:report_id>')
@login_required
def view_report(report_id):
    report = get_report_by_id(g.db, report_id)
    
    # Security check: Ensure this student owns this report
    if not report or report['user_id'] != session['user_id']:
        flash('Report not found or access denied.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    return render_template('student/view_report.html', report=report)
