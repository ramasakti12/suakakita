from src.models.user import db
from datetime import datetime

class MelonPinterData(db.Model):
    __tablename__ = 'melon_pinter_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Student basic information
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    expression = db.Column(db.String(50), nullable=False)
    complaints = db.Column(db.Text)
    
    # Vital signs
    heart_rate = db.Column(db.Integer)
    respiration_rate = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    
    # Warnings/alerts
    warnings = db.Column(db.Text)
    
    def __repr__(self):
        return f'<MelonPinterData {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'expression': self.expression,
            'complaints': self.complaints,
            'heart_rate': self.heart_rate,
            'respiration_rate': self.respiration_rate,
            'temperature': self.temperature,
            'warnings': self.warnings
        }

