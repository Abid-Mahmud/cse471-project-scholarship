from app.extensions import db
from flask_login import UserMixin
import datetime

class Professor(UserMixin, db.Document):
    # This explicitly creates a separate 'professors' folder in the database
    meta = {'collection': 'professors'}
    
    email = db.StringField(required=True, unique=True, max_length=255)
    password = db.StringField(required=True)
    full_name = db.StringField(required=True, max_length=255)
    role = db.StringField(default='professor')
    
    # Google Auth fields
    google_id = db.StringField(null=True)
    avatar_url = db.StringField(null=True)

    # Professor specific fields
    institution = db.StringField(null=True)
    department = db.StringField(null=True)
    
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)