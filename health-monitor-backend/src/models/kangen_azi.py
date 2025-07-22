from src.models.user import db
from datetime import datetime

class KangenAziData(db.Model):
    __tablename__ = 'kangen_azi_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Athlete basic information
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sport = db.Column(db.String(50), nullable=False)
    
    # BMI and analysis
    bmi = db.Column(db.Float, nullable=False)
    bmi_category = db.Column(db.String(50), nullable=False)
    bmi_status = db.Column(db.String(100), nullable=False)
    
    # Diet recommendations
    diet_recommendations = db.Column(db.Text)
    
    def __repr__(self):
        return f'<KangenAziData BMI:{self.bmi}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'weight': self.weight,
            'height': self.height,
            'age': self.age,
            'sport': self.sport,
            'bmi': self.bmi,
            'bmi_category': self.bmi_category,
            'bmi_status': self.bmi_status,
            'diet_recommendations': self.diet_recommendations
        }

