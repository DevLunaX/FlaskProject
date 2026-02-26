from app import create_app
from app.extensions import db
from app.models import User, Appointment
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        print("🌱 Sembrando datos de prueba...")
        
        # Crear usuarios nutricionistas
        nutri1 = User(name='Dra. Ana García', email='ana@nutriinst.edu', role='nutriologo')
        
        # Crear usuarios pacientes
        paciente1 = User(name='Carlos López', email='carlos.lopez@alumno.edu', role='paciente')
        paciente2 = User(name='María Rodríguez', email='maria.rod@alumno.edu', role='paciente')

        # Verificar si ya existen para no duplicar (por email)
        for user in [nutri1, paciente1, paciente2]:
            existing = User.query.filter_by(email=user.email).first()
            if not existing:
                db.session.add(user)
                print(f"   Created user: {user.name}")
            else:
                print(f"   User {user.name} already exists")
        
        db.session.commit()

        # Obtener IDs reales
        p1 = User.query.filter_by(email='carlos.lopez@alumno.edu').first()
        
        # Crear citas dummy
        if p1:
            cita1 = Appointment(
                patient_id=p1.id,
                date_time=datetime.now() + timedelta(days=2),
                reason='Evaluación inicial',
                status='pending'
            )
            db.session.add(cita1)
            print("   Created appointment for Carlos")

        db.session.commit()
        print("✅ Base de datos poblada con éxito.")

if __name__ == '__main__':
    seed_database()
