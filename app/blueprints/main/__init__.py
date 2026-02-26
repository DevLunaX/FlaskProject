from flask import Blueprint, current_app, jsonify, render_template, request, redirect, url_for, session
from sqlalchemy import desc
from app.models import Appointment, User, Consultation
from app.services.youtube import search_videos
from app.extensions import db

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    return render_template("home.html", title="Inicio", active_page="home")


@main_bp.get("/nutriologo/login")
def nutri_login():
    return render_template("nutri_login.html", title="Portal Nutriólogo", active_page="nutri_login")


@main_bp.post("/nutriologo/login")
def nutri_login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    
    user = User.query.filter_by(email=email, role='nutriologo').first()
    
    # Si el usuario existe pero no tiene contraseña (ej. seed data), permitimos el login sin contraseña por ahora
    # o si la contraseña es correcta
    if user and (not user.password_hash or user.check_password(password)):
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('main.dashboard'))
        
    return render_template("nutri_login.html", title="Portal Nutriólogo", error="Credenciales incorrectas o usuario no autorizado.", active_page="nutri_login")


@main_bp.get("/nutriologo/registro")
def nutri_register():
    return render_template("nutri_register.html", title="Registro Nutriólogo", active_page="nutri_register")


@main_bp.post("/nutriologo/registro")
def nutri_register_post():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if User.query.filter_by(email=email).first():
        return render_template("nutri_register.html", title="Registro Nutriólogo", error="El correo ya está registrado.", active_page="nutri_register")

    new_user = User(name=name, email=email, role='nutriologo')
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    session['user_id'] = new_user.id
    session['role'] = new_user.role
    return redirect(url_for('main.dashboard'))


@main_bp.get("/dashboard")
def dashboard():
    if 'user_id' not in session or session.get('role') != 'nutriologo':
        return redirect(url_for('main.nutri_login'))
        
    user = User.query.get_or_404(session['user_id'])
    
    # Estadísticas para el dashboard (solo pacientes y citas de este nutriólogo)
    total_patients = User.query.filter_by(role='paciente', nutritionist_id=user.id).count()
    pending_appointments = Appointment.query.filter_by(status='pending', nutritionist_id=user.id).count()
    
    # Próximas 5 citas
    upcoming_appointments = Appointment.query.filter(
        Appointment.nutritionist_id == user.id,
        Appointment.status != 'completed', 
        Appointment.status != 'cancelled'
    ).order_by(Appointment.date_time.asc()).limit(5).all()

    return render_template(
        "index.html", 
        title="Panel", 
        active_page="dashboard",
        user=user,
        stats={
            'patients': total_patients,
            'pending_appointments': pending_appointments
        },
        appointments=upcoming_appointments
    )


@main_bp.get("/health")
def health():
    return jsonify(status="ok")


@main_bp.get("/register")
def register():
    if 'user_id' not in session or session.get('role') != 'nutriologo':
        return redirect(url_for('main.nutri_login'))
    user = User.query.get_or_404(session['user_id'])
    return render_template("register.html", title="Registro", active_page="register", user=user)


@main_bp.get("/reports")
def reports():
    if 'user_id' not in session or session.get('role') != 'nutriologo':
        return redirect(url_for('main.nutri_login'))
    user = User.query.get_or_404(session['user_id'])
    return render_template("reports.html", title="Reportes", active_page="reports", user=user)


@main_bp.get("/appointments")
def appointments():
    if 'user_id' not in session or session.get('role') != 'nutriologo':
        return redirect(url_for('main.nutri_login'))
        
    user = User.query.get_or_404(session['user_id'])
    
    # Obtener todas las citas del nutriólogo ordenadas por fecha más reciente
    all_appointments = Appointment.query.filter_by(nutritionist_id=user.id).order_by(Appointment.date_time.desc()).all()
    return render_template(
        "appointments.html", 
        title="Citas", 
        active_page="appointments",
        user=user,
        appointments=all_appointments
    )


@main_bp.get("/solicitar-cita")
def appointments_request():
    if 'user_id' not in session or session.get('role') != 'paciente':
        return redirect(url_for('main.student_login'))
    user = User.query.get_or_404(session['user_id'])
    return render_template("request_appointment.html", title="Solicitar Cita", active_page="request_appointment", user=user)


@main_bp.get("/alumno/login")
def student_login():
    return render_template("student_login.html", title="Portal Alumno", active_page="student_login")


@main_bp.post("/alumno/login")
def student_login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    
    user = User.query.filter_by(email=email, role='paciente').first()
    
    if user and (not user.password_hash or user.check_password(password)):
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('main.student_profile'))
        
    return render_template("student_login.html", title="Portal Alumno", error="Credenciales incorrectas.", active_page="student_login")


@main_bp.get("/alumno/registro")
def student_register():
    return render_template("student_register.html", title="Registro Alumno", active_page="student_register")


@main_bp.post("/alumno/registro")
def student_register_post():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    control_number = request.form.get("control_number")
    career = request.form.get("career")

    if User.query.filter_by(email=email).first():
        return render_template("student_register.html", title="Registro Alumno", error="El correo ya está registrado.", active_page="student_register")

    new_user = User(
        name=name, 
        email=email, 
        role='paciente',
        control_number=control_number,
        career=career
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    session['user_id'] = new_user.id
    session['role'] = new_user.role
    return redirect(url_for('main.student_profile'))


@main_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for('main.home'))


@main_bp.get("/alumno/perfil")
def student_profile():
    if 'user_id' not in session or session.get('role') != 'paciente':
        return redirect(url_for('main.student_login'))
        
    user = User.query.get_or_404(session['user_id'])
    appointments = Appointment.query.filter_by(patient_id=user.id).order_by(Appointment.date_time.desc()).all()
    consultations = Consultation.query.filter_by(patient_id=user.id).order_by(Consultation.date_time.desc()).all()
    return render_template("student_profile.html", title="Mi Perfil", user=user, appointments=appointments, consultations=consultations, active_page="student_profile")


@main_bp.get("/api/youtube/search")
def youtube_search():
    query = (request.args.get("q") or "").strip()
    if not query:
        return jsonify(error="query_required", message="Agrega el parametro 'q' para buscar"), 400

    max_results = _parse_limit(request.args.get("max"), default=6)
    results = search_videos(
        query=query,
        api_key=current_app.config.get("YOUTUBE_API_KEY"),
        max_results=max_results,
    )
    return jsonify(results)


@main_bp.get("/api/youtube/recommendations")
def youtube_recommendations():
    video_id = (request.args.get("videoId") or "").strip()
    query = (request.args.get("q") or "").strip() or "videos recomendados"

    if not video_id and not query:
        return jsonify(error="params_required", message="Incluye 'videoId' o un parametro 'q'"), 400

    max_results = _parse_limit(request.args.get("max"), default=6)
    results = search_videos(
        query=query,
        related_to=video_id or None,
        api_key=current_app.config.get("YOUTUBE_API_KEY"),
        max_results=max_results,
    )
    return jsonify(results)


def _parse_limit(raw: str | None, default: int = 6) -> int:
    try:
        return max(1, min(int(raw), 15)) if raw is not None else default
    except (TypeError, ValueError):
        return default
