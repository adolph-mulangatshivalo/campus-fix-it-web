from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from utils.decorators import admin_required
from models.report import get_all_reports, get_report_by_id, update_report_status, assign_worker_to_report
from models.category import get_all_categories
from models.user import get_all_workers, get_all_staff, delete_user, create_user, get_user_by_id, update_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Get filters
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    search_query = request.args.get('search')
    
    reports = get_all_reports(g.db, status_filter, category_filter, search_query)
    categories = get_all_categories(g.db)
    
    # Calculate overall stats
    all_reports = get_all_reports(g.db)
    total = len(all_reports)
    new_reports = sum(1 for r in all_reports if r['status'] == 'Submitted')
    in_progress = sum(1 for r in all_reports if r['status'] in ['In Progress', 'Assigned', 'Under Review'])
    fixed = sum(1 for r in all_reports if r['status'] == 'Fixed')
    
    return render_template('admin/dashboard.html', 
                           reports=reports, 
                           categories=categories,
                           total=total,
                           new_reports=new_reports,
                           in_progress=in_progress,
                           resolved=fixed)

@admin_bp.route('/report/<string:report_id>', methods=['GET', 'POST'])
@admin_required
def manage_report(report_id):
    report = get_report_by_id(g.db, report_id)
    workers = get_all_workers(g.db)
    
    if not report:
        flash('Report not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'assign_worker':
                worker_id = request.form.get('worker_id')
                if worker_id:
                    assign_worker_to_report(g.db, report_id, worker_id, session['user_id'])
                    flash('Worker assigned successfully!', 'success')
                else:
                    flash('Please select a worker.', 'warning')
            else:
                new_status = request.form.get('status')
                comment = request.form.get('comment')
                update_report_status(g.db, report_id, session['user_id'], new_status, comment)
                flash('Report status updated successfully!', 'success')
                
            return redirect(url_for('admin.manage_report', report_id=report_id))
        except Exception as e:
            flash('An error occurred while updating the report.', 'danger')
            print(e)
            
    return render_template('admin/manage_report.html', report=report, workers=workers)

@admin_bp.route('/manage_staff', methods=['GET', 'POST'])
@admin_required
def manage_staff():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_staff':
            full_name = request.form.get('full_name')
            staff_id = request.form.get('staff_id')
            if staff_id:
                staff_id = staff_id.upper()
            email = request.form.get('email')
            if email:
                email = email.lower()
            password = request.form.get('password')
            role = request.form.get('role')
            
            if not all([full_name, staff_id, email, password, role]):
                flash('All fields are required.', 'danger')
            elif role == 'admin' and not staff_id.startswith('ADM'):
                flash('Admin ID must start with ADM (e.g. ADM111).', 'danger')
            elif role == 'worker' and not staff_id.startswith('WOR'):
                flash('Worker ID must start with WOR (e.g. WOR111).', 'danger')
            else:
                try:
                    create_user(g.db, full_name, staff_id, email, password, role)
                    flash(f'{role.capitalize()} created successfully!', 'success')
                except Exception as e:
                    flash('Error creating staff member. ID or Email might already exist.', 'danger')
                    
        elif action == 'delete_staff':
            staff_user_id = request.form.get('user_id')
            # Prevent admin from deleting themselves
            if str(staff_user_id) == str(session.get('user_id')):
                flash('You cannot delete your own account.', 'danger')
            else:
                user_to_delete = get_user_by_id(g.db, staff_user_id)
                if user_to_delete and user_to_delete['student_number'] == 'SADM111':
                    flash('You cannot delete the Super Admin.', 'danger')
                else:
                    try:
                        delete_user(g.db, staff_user_id)
                        flash('Staff member deleted successfully.', 'success')
                    except Exception as e:
                        flash('Error deleting staff member.', 'danger')
                        
        elif action == 'edit_staff':
            current_admin = get_user_by_id(g.db, session.get('user_id'))
            if not current_admin or current_admin['student_number'] != 'SADM111':
                flash('Only the Super Admin is authorized to edit staff details.', 'danger')
                return redirect(url_for('admin.manage_staff'))
                
            staff_user_id = request.form.get('user_id')
            full_name = request.form.get('full_name')
            staff_id = request.form.get('staff_id')
            if staff_id:
                staff_id = staff_id.upper()
            email = request.form.get('email')
            if email:
                email = email.lower()
            role = request.form.get('role')
            password = request.form.get('password') # optional
            
            if not all([staff_user_id, full_name, staff_id, email, role]):
                flash('All required fields must be filled out.', 'danger')
            elif role == 'admin' and not staff_id.startswith('ADM'):
                flash('Admin ID must start with ADM (e.g. ADM111).', 'danger')
            elif role == 'worker' and not staff_id.startswith('WOR'):
                flash('Worker ID must start with WOR (e.g. WOR111).', 'danger')
            else:
                user_to_edit = get_user_by_id(g.db, staff_user_id)
                if user_to_edit and user_to_edit['student_number'] == 'SADM111' and staff_id != 'SADM111':
                    flash('You cannot change the ID of the Super Admin.', 'danger')
                elif user_to_edit and user_to_edit['student_number'] == 'SADM111' and role != 'admin':
                    flash('You cannot change the role of the Super Admin.', 'danger')
                else:
                    try:
                        update_user(g.db, staff_user_id, full_name, staff_id, email, role, new_password=password)
                        flash('Staff member updated successfully.', 'success')
                    except Exception as e:
                        flash('Error updating staff member. ID or Email might conflict with another user.', 'danger')
                        
        return redirect(url_for('admin.manage_staff'))
        
    staff_members = get_all_staff(g.db)
    current_user = get_user_by_id(g.db, session.get('user_id'))
    return render_template('admin/manage_staff.html', staff=staff_members, current_user=current_user)
