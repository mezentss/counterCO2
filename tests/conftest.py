"""Configuration for pytest."""
import pytest
from fastapi.testclient import TestClient
from server import app
from integration_manager import integration_manager

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_integration():
    """Fixture to mock integration for testing."""
    class MockIntegration:
        name = "Mock Integration"
        
        def get_route_client(self):
            class MockRouteClient:
                def get_route(self, start, end):
                    from api_models import Route, Point
                    return Route(
                        start=Point(lat=start.lat, lon=start.lon),
                        end=Point(lat=end.lat, lon=end.lon),
                        distance_km=100.0
                    )
            return MockRouteClient()
            
        def get_co2_client(self):
            class MockCo2Client:
                def get_emissions(self, route, transport_type="car"):
                    return {"co2_kg": 21.0, "transport_type": transport_type}
            return MockCo2Client()
    
    # Register and select the mock integration
    integration = MockIntegration()
    integration_manager.register_integration(integration)
    integration_manager.set_current_integration(integration.name)
    return integration
