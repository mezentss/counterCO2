#!/usr/bin/env python3
"""
Пример использования модуля CO2 калькулятора.

Демонстрирует основные возможности:
- Расчет расстояний по прямой и через API
- Вычисление выбросов CO2 для разных видов транспорта
- Сравнение результатов
"""

from co2_calculator import CO2Calculator, get_available_transport_types


def main():
    """Основная функция с примерами использования."""
    
    print("=== CO2 Калькулятор - Примеры использования ===\n")
    
    # Координаты для примера: Москва -> Санкт-Петербург
    moscow_lat, moscow_lon = 55.7558, 37.6176
    spb_lat, spb_lon = 59.9311, 30.3609
    
    print(f"Маршрут: Москва ({moscow_lat}, {moscow_lon}) -> Санкт-Петербург ({spb_lat}, {spb_lon})\n")
    
    # Создаем калькулятор без API ключа (будет использоваться прямое расстояние)
    calculator = CO2Calculator()
    
    # Показываем доступные виды транспорта
    transport_types = get_available_transport_types()
    print(f"Доступные виды транспорта: {', '.join(transport_types)}\n")
    
    # 1. Расчет прямого расстояния
    direct_distance = calculator.calculate_distance_direct(
        moscow_lat, moscow_lon, spb_lat, spb_lon
    )
    print(f"Расстояние по прямой: {direct_distance:.2f} км\n")
    
    # 2. Расчет выбросов для каждого вида транспорта
    print("=== Выбросы CO2 по видам транспорта ===")
    print(f"{'Транспорт':<10} {'Коэффициент':<12} {'Выбросы CO2':<12}")
    print("-" * 40)
    
    for transport in transport_types:
        coefficient = calculator.CO2_COEFFICIENTS[transport]
        emissions = calculator.get_co2_emissions(direct_distance, transport)
        print(f"{transport:<10} {coefficient:<12.3f} {emissions:<12.3f} кг")
    
    print()
    
    # 3. Полный расчет с детальной информацией
    print("=== Детальный расчет для автомобиля ===")
    result = calculator.calculate_full_emissions(
        moscow_lat, moscow_lon, spb_lat, spb_lon, 'car', use_api=False
    )
    
    for key, value in result.items():
        if isinstance(value, (int, float)):
            print(f"{key}: {value}")
        else:
            print(f"{key}: {value}")
    
    print()
    
    # 4. Сравнение разных видов транспорта
    print("=== Сравнение экологичности транспорта ===")
    results = []
    
    for transport in transport_types:
        result = calculator.calculate_full_emissions(
            moscow_lat, moscow_lon, spb_lat, spb_lon, transport, use_api=False
        )
        results.append((transport, result['co2_emissions_kg']))
    
    # Сортируем по выбросам CO2
    results.sort(key=lambda x: x[1])
    
    print("От самого экологичного к наименее экологичному:")
    for i, (transport, emissions) in enumerate(results, 1):
        print(f"{i}. {transport.capitalize()}: {emissions:.3f} кг CO2")
    
    print()
    
    # 5. Пример с API ключом (закомментировано, так как требует реальный ключ)
    print("=== Пример с OpenRouteService API ===")
    print("Для использования API получите бесплатный ключ на https://openrouteservice.org")
    print("Раскомментируйте код ниже и вставьте ваш API ключ:\n")
    
    print("""
# Пример с API:
# api_key = "ваш_api_ключ_здесь"
# calculator_with_api = CO2Calculator(api_key)
# 
# api_result = calculator_with_api.calculate_full_emissions(
#     moscow_lat, moscow_lon, spb_lat, spb_lon, 'car', use_api=True
# )
# print("Результат с API:", api_result)
""")


def demo_different_routes():
    """Демонстрация расчетов для разных маршрутов."""
    
    print("\n=== Примеры других маршрутов ===\n")
    
    routes = [
        ("Москва -> Казань", 55.7558, 37.6176, 55.8304, 49.0661),
        ("Москва -> Сочи", 55.7558, 37.6176, 43.6028, 39.7342),
        ("Москва -> Владивосток", 55.7558, 37.6176, 43.1056, 131.8735),
    ]
    
    calculator = CO2Calculator()
    
    for route_name, lat1, lon1, lat2, lon2 in routes:
        print(f"--- {route_name} ---")
        
        distance = calculator.calculate_distance_direct(lat1, lon1, lat2, lon2)
        print(f"Расстояние: {distance:.0f} км")
        
        # Выбросы для самолета (наиболее актуально для дальних расстояний)
        plane_emissions = calculator.get_co2_emissions(distance, 'plane')
        train_emissions = calculator.get_co2_emissions(distance, 'train')
        
        print(f"CO2 самолет: {plane_emissions:.1f} кг")
        print(f"CO2 поезд: {train_emissions:.1f} кг")
        print(f"Экономия при выборе поезда: {plane_emissions - train_emissions:.1f} кг CO2")
        print()


if __name__ == "__main__":
    main()
    demo_different_routes()
