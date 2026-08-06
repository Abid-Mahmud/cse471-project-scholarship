from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin-portal')

# Import sub-routes to register them on the blueprint
from app.routes.admin import auth_routes
from app.routes.admin import dashboard_routes
from app.routes.admin import student_routes
from app.routes.admin import professor_routes
from app.routes.admin import scholarship_routes