def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200 and response.json()["status"] == "ok"


def test_analyze_and_dna(client):
    body = {"brand_name": "Glowify", "industry": "Skincare", "target_audience": "Gen Z"}
    report = client.post("/api/v1/brand/analyze", json=body)
    assert report.status_code == 200
    assert report.json()["schema_version"] == "1.0.0"
    assert client.post("/api/v1/brand/analyze-dna", json=body).status_code == 200


def test_invalid_request(client):
    assert client.post("/api/v1/brand/analyze", json={"industry": "Skincare"}).status_code == 422


def test_competitor_endpoint(client):
    response = client.post("/api/v1/brand/competitors", json={"brand": {"brand_name": "Glowify", "industry": "Skincare"}, "competitor_names": ["Example"]})
    assert response.status_code == 200
    assert response.json()["direct_competitors"][0]["name"] == "Example"
