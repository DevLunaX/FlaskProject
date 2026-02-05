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

## API de YouTube
- Endpoints JSON:
  - `GET /api/youtube/search?q=<texto>&max=6`
  - `GET /api/youtube/recommendations?videoId=<id>&max=6`
- Opcional: define `YOUTUBE_API_KEY` para usar la API real. Sin clave, la app responde con datos de ejemplo locales para desarrollo y pruebas.

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
