from app.extensions import db
import datetime

class ChecklistItem(db.EmbeddedDocument):
    name = db.StringField(required=True)
    description = db.StringField()
    is_completed = db.BooleanField(default=False)

class SavedChecklist(db.Document):
    meta = {'collection': 'saved_checklists', 'strict': False}
    
    user_id = db.ReferenceField('User', required=True)
    university = db.StringField(required=True)
    country = db.StringField(required=True) # NEW FIELD
    degree_level = db.StringField(required=True)
    major = db.StringField(required=True)
    items = db.ListField(db.EmbeddedDocumentField(ChecklistItem))
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)