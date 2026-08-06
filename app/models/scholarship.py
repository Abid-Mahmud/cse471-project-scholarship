from app.extensions import db
import datetime

class Scholarship(db.Document):
    title = db.StringField(required=True)
    university = db.StringField(required=True)
    country = db.StringField(required=True)
    degree_level = db.StringField(required=True)
    minimum_gpa = db.FloatField(required=True)
    funding_amount = db.StringField(required=True)
    official_url = db.StringField(default="#")
    major = db.StringField(default="All Majors")
    institution_type = db.StringField(default="Public")
    embedding = db.ListField(db.FloatField())
    tags = db.ListField(db.StringField())

    meta = {'collection': 'scholarships'}

    created_at = db.DateTimeField(default=datetime.datetime.utcnow)