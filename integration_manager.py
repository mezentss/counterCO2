"""Integration source management for the CO2 calculation service."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type, Any, Union

from api_clients import Co2ApiClient, RouteApiClient
from api_models import Point, Route


class BaseIntegration(ABC):
    """Base class for all integration sources."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of this integration."""
        pass
    
    @abstractmethod
    def get_route_client(self) -> RouteApiClient:
        """Return a route API client for this integration."""
        pass
    
    @abstractmethod
    def get_co2_client(self) -> Co2ApiClient:
        """Return a CO2 API client for this integration."""
        pass


class DefaultIntegration(BaseIntegration):
    """Default integration using the built-in API clients."""
    
    @property
    def name(self) -> str:
        return "Default Local Integration"
    
    def get_route_client(self) -> RouteApiClient:
        return RouteApiClient()
    
    def get_co2_client(self) -> Co2ApiClient:
        return Co2ApiClient()


class IntegrationManager:
    """Manages available integration sources."""
    
    def __init__(self):
        self._integrations: Dict[str, BaseIntegration] = {}
        self._default_integration = DefaultIntegration()
        # Start with default integration selected
        self._current_integration: BaseIntegration = self._default_integration
    
    def register_integration(self, integration: BaseIntegration) -> None:
        """Register a new integration source."""
        self._integrations[integration.name] = integration
    
    def get_integration(self, name: str) -> BaseIntegration:
        """Get an integration by name."""
        return self._integrations.get(name, self._default_integration)
    
    def list_integrations(self) -> List[str]:
        """List all available integration names."""
        return list(self._integrations.keys()) + [self._default_integration.name]
    
    def set_current_integration(self, name: str) -> bool:
        """Set the current integration by name."""
        if name == self._default_integration.name:
            self._current_integration = self._default_integration
            return True
            
        if name in self._integrations:
            self._current_integration = self._integrations[name]
            return True
            
        return False
    
    def get_current_integration(self) -> BaseIntegration:
        """Get the current integration."""
        return self._current_integration or self._default_integration
    
    def get_route_client(self) -> RouteApiClient:
        """Get the route client from the current integration."""
        return self.get_current_integration().get_route_client()
    
    def get_co2_client(self) -> Co2ApiClient:
        """Get the CO2 client from the current integration."""
        return self.get_current_integration().get_co2_client()


# Global instance
integration_manager = IntegrationManager()


def register_integration(integration: BaseIntegration) -> None:
    """Register a new integration source (convenience function)."""
    integration_manager.register_integration(integration)
