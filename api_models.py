from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Point:
    """Точка на карте (широта и долгота)."""

    lat: float
    lon: float


@dataclass
class Route:
    """Маршрут между двумя точками (упрощённо)."""

    start: Point
    end: Point
    distance_km: float
    geometry: Optional[Any] = None  # здесь могла бы быть полилиния/GeoJSON
