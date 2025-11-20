from typing import List

from api_clients import Co2ApiClient, RouteApiClient
from api_models import Point


def select_points_on_map() -> List[Point]:
    """Заглушка выбора двух точек на карте."""

    # Пример: Москва и Санкт‑Петербург
    point_a = Point(lat=55.7558, lon=37.6176)
    point_b = Point(lat=59.9311, lon=30.3609)
    return [point_a, point_b]


def main() -> None:
    """Демонстрационный сценарий интеграции с API маршрутов и CO₂."""
    # 1. Выбор точек на "карте"
    point_a, point_b = select_points_on_map()
    print("Выбраны точки:")
    print(f"  A: lat={point_a.lat}, lon={point_a.lon}")
    print(f"  B: lat={point_b.lat}, lon={point_b.lon}\n")

    # 2. Инициализируем клиентов API
    route_api = RouteApiClient()
    co2_api = Co2ApiClient()

    # 3. Запрашиваем маршрут у сервиса маршрутов
    route = route_api.get_route(point_a, point_b)

    # 4. Запрашиваем расчёт выбросов CO2 для этого маршрута
    emissions = co2_api.get_emissions(route)

    # 5. Показываем результат пользователю
    print("\n=== Результаты ===")
    print(f"Тип транспорта: {emissions['transport_type']}")
    print(f"Расстояние: {emissions['distance_km']:.1f} км")
    print(f"Выбросы CO2: {emissions['co2_emissions_kg']:.2f} кг")


if __name__ == "__main__":
    main()
