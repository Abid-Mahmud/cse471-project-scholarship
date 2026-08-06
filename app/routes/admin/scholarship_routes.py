from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.routes.admin import admin_bp
from app.models.scholarship import Scholarship

@admin_bp.route('/scholarships')
@login_required
def manage_scholarships():
    if getattr(current_user, 'role', '') != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    search_q = request.args.get('q', '').strip()

    try:
        if search_q:
            scholarships = Scholarship.objects(title__icontains=search_q)
        else:
            scholarships = Scholarship.objects().order_by('title')
    except Exception as e:
        print(f"Database query error in scholarships: {e}")
        scholarships = []

    return render_template('admin/scholarships.html', scholarships=scholarships, search_q=search_q)

@admin_bp.route('/delete-scholarship/<scholarship_id>', methods=['POST'])
@login_required
def delete_scholarship(scholarship_id):
    if getattr(current_user, 'role', '') == 'admin':
        s = Scholarship.objects(id=scholarship_id).first()
        if s:
            s.delete()
            flash('Scholarship removed from database.', 'info')
    return redirect(url_for('admin.manage_scholarships'))