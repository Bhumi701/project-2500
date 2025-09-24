from app.extensions import db
from datetime import datetime

class Grievance(db.Model):
    __tablename__ = 'grievances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(10), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    response = db.Column(db.Text)
    assigned_to = db.Column(db.String(100))
    
    # Relationship
    user = db.relationship('User', backref=db.backref('grievances', lazy=True, order_by='Grievance.created_at.desc()'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'response': self.response,
            'assigned_to': self.assigned_to
        }
    
    
        # Relationship
    user = db.relationship('User', backref=db.backref('grievances', lazy=True, order_by='Grievance.created_at.desc()'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'response': self.response,
            'assigned_to': self.assigned_to
        }
    
    # Relationship
    user = db.relationship('User', backref=db.backref('grievances', lazy=True, order_by='Grievance.created_at.desc()'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'response': self.response,
            'assigned_to': self.assigned_to
        }
    
    # Relationship
    user = db.relationship('User', backref=db.backref('grievances', lazy=True, order_by='Grievance.created_at.desc()'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'response': self.response,
            'assigned_to': self.assigned_to
        }
    
    # Relationship
    user = db.relationship('User', backref=db.backref('grievances', lazy=True, order_by='Grievance.created_at.desc()'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'response': self.response,
            'assigned_to': self.assigned_to
        }

    def __repr__(self):
        return f'<Grievance {self.id}: {self.subject}>'
