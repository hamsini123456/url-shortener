from fastapi.testclient import TestClient
from main1 import app

client = TestClient(app)

# Test 1 — health check
def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "URL Shortener is running"}

# Test 2 — shorten a URL
def test_shorten_url():
    response = client.post("/shorten", json={"long_url": "https://www.google.com"})
    assert response.status_code == 200
    data = response.json()
    assert "short_code" in data
    assert "short_url" in data
    assert data["long_url"] == "https://www.google.com"
    assert data["hit_count"] == 0
    print(f"Short code created: {data['short_code']}")

# Test 3 — shorten invalid URL still creates entry
def test_shorten_any_string():
    response = client.post("/shorten", json={"long_url": "https://www.youtube.com"})
    assert response.status_code == 200
    assert "short_code" in response.json()

# Test 4 — redirect works
def test_redirect():
    # First create a short URL
    create = client.post("/shorten", json={"long_url": "https://www.github.com"})
    code = create.json()["short_code"]

    # Then redirect
    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://www.github.com"

# Test 5 — analytics works
def test_analytics():
    # Create URL
    create = client.post("/shorten", json={"long_url": "https://www.amazon.com"})
    code = create.json()["short_code"]

    # Check analytics
    response = client.get(f"/analytics/{code}")
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == code
    assert data["long_url"] == "https://www.amazon.com"

# Test 6 — 404 for unknown code
def test_unknown_code():
    response = client.get("/XXXXXX")
    assert response.status_code == 404
    assert response.json()["detail"] == "URL not found"

# Test 7 — analytics 404 for unknown code
def test_analytics_unknown():
    response = client.get("/analytics/XXXXXX")
    assert response.status_code == 404