"""Tests for the integration manager."""
import pytest
from integration_manager import IntegrationManager, BaseIntegration
from api_clients import RouteApiClient, Co2ApiClient

class TestIntegration(BaseIntegration):
    """Test integration for testing purposes."""
    
    @property
    def name(self) -> str:
        return "Test Integration"
    
    def get_route_client(self) -> RouteApiClient:
        """Return a test route client."""
        class TestRouteClient(RouteApiClient):
            def get_route(self, start, end):
                return {"distance_km": 150.0, "duration_minutes": 90}
        return TestRouteClient()
    
    def get_co2_client(self) -> Co2ApiClient:
        """Return a test CO2 client."""
        class TestCo2Client(Co2ApiClient):
            def get_emissions(self, route, transport_type="car"):
                return {"co2_kg": 31.5, "transport_type": transport_type}
        return TestCo2Client()

def test_register_and_select_integration():
    """Test registering and selecting an integration."""
    manager = IntegrationManager()
    test_integration = TestIntegration()
    
    # Test registration
    manager.register_integration(test_integration)
    assert test_integration.name in manager.list_integrations()
    
    # Test selection
    assert manager.set_current_integration(test_integration.name)
    assert manager.get_current_integration().name == test_integration.name

def test_default_integration():
    """Test that default integration is always available."""
    manager = IntegrationManager()
    assert len(manager.list_integrations()) >= 1  # At least default integration
    assert manager.get_current_integration() is not None

def test_integration_flow():
    """Test the full flow of using an integration."""
    manager = IntegrationManager()
    test_integration = TestIntegration()
    manager.register_integration(test_integration)
    manager.set_current_integration(test_integration.name)
    
    # Test route client
    route_client = manager.get_route_client()
    route = route_client.get_route(None, None)
    assert route["distance_km"] == 150.0
    
    # Test CO2 client
    co2_client = manager.get_co2_client()
    emissions = co2_client.get_emissions(None)
    assert emissions["co2_kg"] == 31.5
