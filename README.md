# FlaskProject

Aplicación web desarrollada con **Flask** que utiliza **Supabase** como backend (Base de Datos/Auth/Storage según aplique).  
Este repositorio contiene el código fuente del proyecto, junto con instrucciones para instalarlo y ejecutarlo localmente.

---

## Características (resumen)
- Backend con Flask (Python).
- Integración con Supabase.
- Interfaz web (si aplica: templates/ + static/).
- (Opcional) Autenticación y/o operaciones CRUD conectadas a Supabase.

> Nota: Ajusta esta lista con las funcionalidades reales de tu sistema (login, registro, CRUD de entidades, dashboard, etc.).

---

## Requisitos
- **Python 3.10+** (recomendado)
- **pip**
- Cuenta/proyecto en **Supabase**
- (Recomendado) Entorno virtual: `venv`

---

## Instalación (local)

### 1) Clonar el repositorio
```bash
git clone https://github.com/DevLunaX/FlaskProject.git
cd FlaskProject
```

### 2) Crear y activar entorno virtual
**Windows (PowerShell):**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## Configuración (Supabase)

Crea un archivo `.env` en la raíz del proyecto (no lo subas al repo) con tus credenciales de Supabase.

Ejemplo de variables (ajusta los nombres a tu implementación real):

```env
SUPABASE_URL="https://TU-PROYECTO.supabase.co"
SUPABASE_ANON_KEY="TU_ANON_KEY"
# Si tu proyecto usa Service Role (NO recomendado en frontend / apps públicas):
# SUPABASE_SERVICE_ROLE_KEY="TU_SERVICE_ROLE_KEY"

# Flask
FLASK_ENV="development"
FLASK_DEBUG="1"
SECRET_KEY="cambia-esto-por-una-clave-segura"
```

### ¿Dónde obtengo SUPABASE_URL y SUPABASE_ANON_KEY?
En tu panel de Supabase:
- **Project Settings** → **API**
- Copia:
  - `Project URL` → `SUPABASE_URL`
  - `anon public` → `SUPABASE_ANON_KEY`

---

## Ejecución

Para iniciar la aplicación:

```bash
python run.py
```

Luego abre en el navegador la URL que muestre la terminal (comúnmente):
- http://127.0.0.1:5000

> Si tu app usa un puerto distinto, actualiza esta sección.

---

## Estructura del proyecto (referencial)
La estructura puede variar según tu implementación, pero típicamente:

- `run.py` — punto de entrada del proyecto
- `requirements.txt` — dependencias
- `templates/` — vistas HTML (Jinja2)
- `static/` — CSS/JS/imagenes
- `app/` o `src/` — lógica del proyecto (rutas, servicios, etc.)

---

## Capturas de pantalla

Agrega tus capturas en una carpeta llamada `screenshots/` en la raíz del proyecto y enlázalas aquí.

**(Placeholder) Pantalla principal**
![Pantalla principal](screenshots/home.png)

**(Placeholder) Funcionalidad 1**
![Funcionalidad 1](screenshots/feature-1.png)

**(Placeholder) Funcionalidad 2**
![Funcionalidad 2](screenshots/feature-2.png)

> Puedes renombrar los archivos o agregar más capturas según necesites.

---

## Notas de seguridad
- No subas tu archivo `.env` al repositorio.
- No publiques `SUPABASE_SERVICE_ROLE_KEY` en proyectos cliente o repos públicos.
- Usa `SECRET_KEY` segura en producción.

---

## Autor
- DevLunaX
