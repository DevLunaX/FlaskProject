from datetime import datetime
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # 'nutriologo', 'paciente'
    
    # Datos extendidos para perfil clínico
    control_number = db.Column(db.String(50), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    sex = db.Column(db.String(10), nullable=True)
    career = db.Column(db.String(100), nullable=True)
    
    # Relación para asignar pacientes a un nutriólogo
    nutritionist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    patients = db.relationship('User', backref=db.backref('nutritionist', remote_side=[id]), lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    appointments = db.relationship('Appointment', foreign_keys='Appointment.patient_id', backref='patient', lazy=True)
    consultations = db.relationship('Consultation', foreign_keys='Consultation.patient_id', backref='patient', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'control_number': self.control_number,
            'age': self.age,
            'sex': self.sex,
            'career': self.career
        }

class Consultation(db.Model):
    __tablename__ = 'consultations'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nutritionist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Antropometría
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    waist = db.Column(db.Float, nullable=True)
    bmi = db.Column(db.Float, nullable=True)
    
    # Diagnóstico y Plan
    diagnosis = db.Column(db.String(255), nullable=True)
    diet_plan = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date_time': self.date_time.isoformat(),
            'weight': self.weight,
            'height': self.height,
            'waist': self.waist,
            'bmi': self.bmi,
            'diagnosis': self.diagnosis,
            'diet_plan': self.diet_plan,
            'notes': self.notes
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nutritionist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    reason = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date_time': self.date_time.isoformat() if self.date_time else None,
            'status': self.status,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
