from flask import Blueprint, render_template, request

# Creamos (o referenciamos) el Blueprint 'main'
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Aquí procesarías los datos más adelante
        return "Guardando datos..."
    return render_template('register.html', title="Nuevo Paciente")