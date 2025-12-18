"""Tests for the API endpoints."""

def test_list_integrations(client):
    """Test listing available integrations."""
    response = client.get("/api/integrations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_select_integration(client, mock_integration):
    """Test selecting an integration."""
    response = client.post(
        "/api/integrations/select",
        json={"name": "Mock Integration"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["selected"] == "Mock Integration"

def test_get_route(client, mock_integration):
    """Test getting a route."""
    response = client.post(
        "/api/route",
        json={
            "start": {"lat": 55.7558, "lon": 37.6176},
            "end": {"lat": 59.9311, "lon": 30.3609}
        }
    )
    
    # Print response content for debugging
    print("\nResponse status code:", response.status_code)
    print("Response content:", response.text)
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert "distance_km" in data
    assert "start" in data
    assert "end" in data
    assert data["start"]["lat"] == 55.7558
    assert data["end"]["lat"] == 59.9311

def test_get_emissions(client, mock_integration):
    """Test getting emissions."""
    response = client.post(
        "/api/emissions",
        json={"distance_km": 100.0, "transport_type": "car"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "co2_kg" in data
    assert data["transport_type"] == "car"

def test_full_route(client, mock_integration):
    """Test full route calculation with emissions."""
    response = client.post(
        "/api/full",
        json={
            "start": {"lat": 55.7558, "lon": 37.6176},
            "end": {"lat": 59.9311, "lon": 30.3609}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "route" in data
    assert "emissions" in data
    assert "distance_km" in data["route"]
    assert "co2_kg" in data["emissions"]
