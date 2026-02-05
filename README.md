# Proyecto Flask

Estructura base para arrancar rápido con Flask usando una factoría de aplicación y Blueprints.

## Requisitos
- Python 3.11+ (usa el `venv` ya presente si lo deseas)

## Instalación
1. Activa el entorno virtual: `.\venv\Scripts\Activate`
2. Instala dependencias: `pip install -r requirements.txt`
3. Copia variables de entorno: `copy .env.example .env`

## Ejecución
- Desarrollo: `python run.py`
- Con CLI: `flask --app run.py ping`

## Pruebas
- Ejecuta `pytest` para correr los tests.

## Estructura
- `app/` código de la aplicación
  - `blueprints/` Blueprints organizados
  - `templates/` vistas HTML
  - `static/` assets estáticos
- `tests/` pruebas con Pytest
- `config.py` configuraciones por entorno
- `run.py` entrada para desarrollo
- `wsgi.py` entrada para despliegue
