from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.routes.admin import admin_bp
from app.models.user import User
from app.models.professor import Professor
from app.models.scholarship import Scholarship

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if getattr(current_user, 'role', '') != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    return render_template('admin/admin_dashboard.html', 
                       students_count=User.objects().count(), 
                       professors_count=Professor.objects().count(), 
                       scholarships_count=Scholarship.objects().count())    