from flask import Blueprint, current_app, jsonify, render_template, request

from app.services.youtube import search_videos

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("index.html", title="Inicio", active_page="dashboard")


@main_bp.get("/health")
def health():
    return jsonify(status="ok")


@main_bp.get("/register")
def register():
    return render_template("register.html", title="Registro", active_page="register")


@main_bp.get("/reports")
def reports():
    return render_template("reports.html", title="Reportes", active_page="reports")


@main_bp.get("/appointments")
def appointments():
    return render_template("appointments.html", title="Citas", active_page="appointments")


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
