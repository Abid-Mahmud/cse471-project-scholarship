import datetime
from app.extensions import db

class TimelineTask(db.EmbeddedDocument):
    task_id = db.StringField(required=True)
    column = db.StringField(required=True, choices=['todo', 'in_progress', 'done'])
    title = db.StringField(required=True)
    deadline = db.StringField()

class ApplicationTimeline(db.Document):
    user_id = db.StringField(required=True)
    scholarship_id = db.StringField(required=True)
    tasks = db.EmbeddedDocumentListField(TimelineTask)
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        'collection': 'application_timelines',
        'indexes': [
            {'fields': ['user_id', 'scholarship_id'], 'unique': True}
        ]
    }