from app.extensions import db
from flask_login import UserMixin
import datetime

class Admin(UserMixin, db.Document):
    meta = {'collection': 'admins'}
    
    email = db.StringField(required=True, unique=True, max_length=255)
    password = db.StringField(required=True)
    full_name = db.StringField(required=True, max_length=255)
    role = db.StringField(default='admin')
    
    # OTP Verification Fields
    otp_code = db.StringField(null=True)
    otp_expiry = db.DateTimeField(null=True)
    
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)