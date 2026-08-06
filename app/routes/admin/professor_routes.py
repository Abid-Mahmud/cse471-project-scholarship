from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.routes.admin import admin_bp
from app.models.professor import Professor

@admin_bp.route('/professors')
@login_required
def manage_professors():
    if getattr(current_user, 'role', '') != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    search_q = request.args.get('q', '').strip()
    
    try:
        if search_q:
            professors = Professor.objects(full_name__icontains=search_q)
        else:
            professors = Professor.objects().order_by('-id')
    except Exception as e:
        print(f"Database query error in professors: {e}")
        professors = []

    return render_template('admin/professors.html', professors=professors, search_q=search_q)

@admin_bp.route('/delete-professor/<prof_id>', methods=['POST'])
@login_required
def delete_professor(prof_id):
    if getattr(current_user, 'role', '') == 'admin':
        p = Professor.objects(id=prof_id).first()
        if p:
            p.delete()
            flash('Professor account removed.', 'info')
    return redirect(url_for('admin.manage_professors'))