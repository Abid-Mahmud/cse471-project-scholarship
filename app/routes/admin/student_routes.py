from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.routes.admin import admin_bp
from app.models.user import User
from app.models.scholarship import Scholarship

@admin_bp.route('/students')
@login_required
def manage_students():
    if getattr(current_user, 'role', '') != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    search_q = request.args.get('q', '').strip()

    try:
        if search_q:
            students = User.objects(full_name__icontains=search_q)
        else:
            students = User.objects().order_by('-id')
    except Exception as e:
        print(f"Database query error in students: {e}")
        students = []

    return render_template('admin/students.html', students=students, search_q=search_q)

@admin_bp.route('/delete-student/<student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    if getattr(current_user, 'role', '') == 'admin':
        u = User.objects(id=student_id).first()
        if u:
            u.delete()
            flash('Student account removed.', 'info')
    return redirect(url_for('admin.manage_students'))

# --- NEW ROUTE: Remove Tracked Scholarship ---
@admin_bp.route('/remove-tracked-scholarship/<student_id>/<scholarship_id>', methods=['POST'])
@login_required
def remove_tracked_scholarship(student_id, scholarship_id):
    if getattr(current_user, 'role', '') != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.objects(id=student_id).first()
    scholarship = Scholarship.objects(id=scholarship_id).first()

    if user and scholarship:
        changed = False
        # Handle tracked_scholarships list
        if hasattr(user, 'tracked_scholarships') and scholarship in user.tracked_scholarships:
            user.tracked_scholarships.remove(scholarship)
            changed = True
            
        # Handle saved_scholarships list (if you use this field name as well)
        if hasattr(user, 'saved_scholarships') and scholarship in user.saved_scholarships:
            user.saved_scholarships.remove(scholarship)
            changed = True
            
        if changed:
            user.save()
            flash(f'Removed "{scholarship.title}" from {user.full_name}\'s tracker.', 'success')
        else:
            flash('Scholarship was not in the tracker.', 'info')

    return redirect(url_for('admin.manage_students'))