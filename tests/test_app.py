import pytest

from app import create_app


@pytest.fixture()
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_youtube_search_returns_sample_when_no_api_key(client):
    response = client.get("/api/youtube/search?q=nutricion")
    assert response.status_code == 200

    data = response.get_json()
    assert data["source"] == "sample"
    assert data["items"]


def test_youtube_recommendations_require_params(client):
    response = client.get("/api/youtube/recommendations")
    assert response.status_code == 400


def test_youtube_recommendations_return_results(client):
    response = client.get("/api/youtube/recommendations?videoId=dummy")
    assert response.status_code == 200

    data = response.get_json()
    assert data["items"]
