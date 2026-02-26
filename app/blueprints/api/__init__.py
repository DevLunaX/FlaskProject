from flask import Blueprint, request, jsonify, session
from datetime import datetime
from sqlalchemy import or_
from app.extensions import db
from app.models import User, Appointment, Consultation
from app.services.places import search_places

api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- USERS ---
@api_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'error': 'Bad Request', 'message': 'Email is required'}), 400
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Conflict', 'message': 'User already exists'}), 409

    new_user = User(
        name=data.get('name'),
        email=data.get('email'),
        role=data.get('role', 'paciente'),
        # Optional fields
        control_number=data.get('control_number'),
        age=data.get('age'),
        sex=data.get('sex'),
        career=data.get('career')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

# --- SEARCH ---
@api_bp.route('/patients/search', methods=['GET'])
def search_patients():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    # Buscar por nombre, email o número de control
    users = User.query.filter(
        (User.role == 'paciente') & 
        (
            User.name.ilike(f'%{query}%') | 
            User.email.ilike(f'%{query}%') | 
            User.control_number.ilike(f'%{query}%')
        )
    ).all()
    
    return jsonify([u.to_dict() for u in users])


# --- CONSULTATIONS ---
@api_bp.route('/consultations', methods=['POST'])
def create_consultation():
    data = request.get_json()
    patient_id = data.get('patient_id')
    
    if not patient_id:
        return jsonify({'error': 'Missing patient_id'}), 400
        
    nutritionist_id = session.get('user_id') if session.get('role') == 'nutriologo' else None
        
    con = Consultation(
        patient_id=patient_id,
        nutritionist_id=nutritionist_id,
        weight=data.get('weight'),
        height=data.get('height'),
        waist=data.get('waist'),
        bmi=data.get('bmi'),
        diagnosis=data.get('diagnosis'),
        diet_plan=data.get('diet_plan'),
        notes=data.get('notes')
    )
    
    # También actualizamos datos base si vienen en el payload (ej. para corregir)
    user = User.query.get(patient_id)
    if user:
         if 'age' in data: user.age = data['age']
         if 'sex' in data: user.sex = data['sex']
         if 'career' in data: user.career = data['career']
         if nutritionist_id: user.nutritionist_id = nutritionist_id # Asignar paciente al nutriólogo

    db.session.add(con)
    db.session.commit()
    return jsonify(con.to_dict()), 201

# --- APPOINTMENTS ---
@api_bp.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify([ppt.to_dict() for ppt in appointments])

@api_bp.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    
    # Simple validation
    if 'date_time' not in data or 'reason' not in data:
         return jsonify({'error': 'Bad Request', 'message': 'Missing fields (date_time, reason)'}), 400

    # Determinar patient_id: ya sea directo o buscado por email
    patient_id = data.get('patient_id')
    if not patient_id and 'email' in data:
        user = User.query.filter_by(email=data['email']).first()
        if user:
            patient_id = user.id
        else:
            # Opción: crear usuario al vuelo o rechazar
            # Para este ejemplo, rechazamos si no existe
             return jsonify({'error': 'Not Found', 'message': 'User with this email not found'}), 404
    
    if not patient_id:
        return jsonify({'error': 'Bad Request', 'message': 'patient_id or valid email is required'}), 400

    try:
        # Intentar parsear ISO format, o formatos simples
        dt_str = data['date_time']
        try:
             # Intenta formato ISO completo
             dt = datetime.fromisoformat(dt_str)
        except ValueError:
             # Fallback simple para formularios HTML datetime-local (YYYY-MM-DDTHH:MM)
             dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M')

    except ValueError:
        return jsonify({'error': 'Bad Request', 'message': 'Invalid date format'}), 400

    nutritionist_id = session.get('user_id') if session.get('role') == 'nutriologo' else None

    new_ppt = Appointment(
        patient_id=patient_id,
        nutritionist_id=nutritionist_id,
        date_time=dt,
        reason=data['reason'],
        status='pending'
    )
    
    if nutritionist_id:
        user = User.query.get(patient_id)
        if user:
            user.nutritionist_id = nutritionist_id

    db.session.add(new_ppt)
    db.session.commit()
    return jsonify(new_ppt.to_dict()), 201

@api_bp.route('/appointments/<int:appt_id>', methods=['PUT'])
def update_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    data = request.get_json()

    if 'status' in data:
        appt.status = data['status']
    
    # Validar otros campos si es necesario
    
    db.session.commit()
    return jsonify(appt.to_dict())

@api_bp.route('/appointments/<int:appt_id>', methods=['DELETE'])
def delete_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    db.session.delete(appt)
    db.session.commit()
    return jsonify({'message': 'Appointment deleted'}), 200

# --- PATIENTS (CRUD) ---
# Usamos el modelo User pero filtramos por role='paciente'

@api_bp.route('/patients', methods=['GET'])
def get_patients():
    patients = User.query.filter_by(role='paciente').all()
    return jsonify([p.to_dict() for p in patients])

@api_bp.route('/patients/<int:user_id>', methods=['DELETE'])
def delete_patient(user_id):
    user = User.query.get_or_404(user_id)
    # Opcional: Validar que sea paciente antes de borrar
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Patient deleted'}), 200

@api_bp.route('/patients/<int:user_id>', methods=['PUT'])
def update_patient(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'name' in data: user.name = data['name']
    if 'email' in data: user.email = data['email']
    # Otros campos...

    db.session.commit()
    return jsonify(user.to_dict())


# --- PLACES / GEOLOCATION ---
@api_bp.get('/places/nearby')
def get_nearby_places():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Bad Request', 'message': 'lat y lon son requeridos'}), 400

    try:
        radius = int(request.args.get('radius', 3000))
    except (TypeError, ValueError):
        radius = 3000

    raw_types = request.args.get('types', '')
    categories = [t.strip() for t in raw_types.split(',') if t.strip()]

    results = search_places(lat=lat, lon=lon, radius_m=radius, categories=categories or None)
    return jsonify(results)

