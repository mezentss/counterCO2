#!/usr/bin/env python3
"""Минимальный пример архитектуры сервиса расчёта CO2.

Сценарий:
- пользователь выбирает две точки на карте (точка A и точка B);
- сервис обращается к API маршрутов, чтобы получить маршрут между точками;
- затем обращается к API расчёта выбросов CO2 по этому маршруту;
- результат выводится пользователю.

Файл демонстрирует упрощённую структуру кода для такого сценария.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


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


class RouteApiClient:
    """Клиент API маршрутов.

    В реальном приложении здесь могут быть HTTP-запросы к внешнему сервису
    (например, OpenRouteService, Google Maps и т.п.). В этом примере
    используется упрощённая реализация.
    """

    def get_route(self, start: Point, end: Point) -> Route:
        """Получить маршрут между двумя точками."""

        distance_km = 700.0
        return Route(start=start, end=end, distance_km=distance_km)


class Co2ApiClient:
    """Клиент API расчёта выбросов CO2.

    В реальной жизни мог бы использовать внешний сервис или внутренний
    микросервис. В этом примере используется упрощённая формула.
    """

    def get_emissions(self, route: Route) -> Dict[str, Any]:
        """Рассчитать выбросы CO2 для заданного маршрута."""

        co2_per_km_kg = 0.15  # условный коэффициент для автомобиля
        total_emissions = route.distance_km * co2_per_km_kg

        return {
            "transport_type": "car",
            "distance_km": route.distance_km,
            "co2_emissions_kg": total_emissions,
            "source": "co2-api",
        }


def select_points_on_map() -> List[Point]:
    """Заглушка выбора двух точек на карте.

    В реальном приложении это был бы UI/виджет карты, где пользователь
    кликает по карте и выбирает точку A и точку B.

    Сейчас просто возвращаем две заранее заданные точки.
    """

    # Пример: Москва и Санкт‑Петербург
    point_a = Point(lat=55.7558, lon=37.6176)
    point_b = Point(lat=59.9311, lon=30.3609)
    return [point_a, point_b]


def main() -> None:
    """Главный сценарий работы приложения (концепт)."""
    # 1. Выбор точек на "карте"
    point_a, point_b = select_points_on_map()
    print("Выбраны точки:")
    print(f"  A: lat={point_a.lat}, lon={point_a.lon}")
    print(f"  B: lat={point_b.lat}, lon={point_b.lon}\n")

    # 2. Инициализируем клиентов API (пока это просто объекты-заглушки)
    route_api = RouteApiClient()
    co2_api = Co2ApiClient()

    # 3. «Запрашиваем» маршрут у сервиса маршрутов
    route = route_api.get_route(point_a, point_b)

    # 4. «Запрашиваем» расчёт выбросов CO2 для этого маршрута
    emissions = co2_api.get_emissions(route)

    # 5. Показываем результат пользователю
    print("\n=== Результаты ===")
    print(f"Тип транспорта: {emissions['transport_type']}")
    print(f"Расстояние: {emissions['distance_km']:.1f} км")
    print(f"Выбросы CO2: {emissions['co2_emissions_kg']:.2f} кг")
    print(f"Источник данных: {emissions['source']}")


if __name__ == "__main__":
    main()
