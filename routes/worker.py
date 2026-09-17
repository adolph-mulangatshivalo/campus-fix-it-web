from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from utils.decorators import worker_required
from models.report import get_worker_reports, get_report_by_id, update_report_status_worker

worker_bp = Blueprint('worker', __name__)

@worker_bp.route('/dashboard')
@worker_required
def dashboard():
    reports = get_worker_reports(g.db, session['user_id'])
    
    total = len(reports)
    in_progress = sum(1 for r in reports if r['status'] in ['Assigned', 'In Progress'])
    fixed = sum(1 for r in reports if r['status'] == 'Fixed')
    
    return render_template('worker/dashboard.html', 
                           reports=reports,
                           total=total,
                           in_progress=in_progress,
                           resolved=fixed)

@worker_bp.route('/report/<string:report_id>', methods=['GET', 'POST'])
@worker_required
def manage_report(report_id):
    report = get_report_by_id(g.db, report_id)
    
    if not report or report['worker_id'] != session['user_id']:
        flash('Report not found or not assigned to you.', 'danger')
        return redirect(url_for('worker.dashboard'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        comment = request.form.get('comment', '')
        
        try:
            if action == 'start':
                update_report_status_worker(g.db, report_id, session['user_id'], 'In Progress', 'Worker started the job.')
                flash('Report status updated to In Progress!', 'success')
            if action == 'resolve':
                update_report_status_worker(g.db, report_id, session['user_id'], 'Fixed', comment or 'Worker marked job as Fixed.')
                flash('Task marked as fixed.', 'success')
            
            return redirect(url_for('worker.manage_report', report_id=report_id))
        except Exception as e:
            flash('An error occurred while updating the report.', 'danger')
            print(e)
            
    return render_template('worker/manage_report.html', report=report)
