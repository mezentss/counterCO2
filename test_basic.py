#!/usr/bin/env python3
"""
Базовые тесты для CO2 калькулятора.
Простая проверка основного функционала без использования внешних библиотек.
"""

from co2_calculator import CO2Calculator, get_available_transport_types


def test_distance_calculation():
    """Тест расчета расстояния по формуле Хаверсина."""
    calculator = CO2Calculator()
    
    # Москва -> Санкт-Петербург (известное расстояние ~635 км)
    distance = calculator.calculate_distance_direct(55.7558, 37.6176, 59.9311, 30.3609)
    
    # Проверяем, что расстояние в разумных пределах (630-640 км)
    assert 630 <= distance <= 640, f"Неожиданное расстояние: {distance} км"
    print(f"✓ Расчет расстояния: {distance:.2f} км")


def test_co2_emissions():
    """Тест расчета выбросов CO2."""
    calculator = CO2Calculator()
    
    # Тестируем для расстояния 100 км
    test_distance = 100.0
    
    # Проверяем выбросы для каждого вида транспорта
    expected_emissions = {
        'car': 21.0,    # 100 * 0.21
        'bus': 3.0,     # 100 * 0.03
        'train': 6.0,   # 100 * 0.06
        'plane': 25.0   # 100 * 0.25
    }
    
    for transport, expected in expected_emissions.items():
        emissions = calculator.get_co2_emissions(test_distance, transport)
        assert abs(emissions - expected) < 0.001, f"Неверные выбросы для {transport}: {emissions}"
        print(f"✓ CO2 {transport}: {emissions} кг")


def test_available_transports():
    """Тест получения списка доступных транспортов."""
    transports = get_available_transport_types()
    expected_transports = {'car', 'bus', 'train', 'plane'}
    
    assert set(transports) == expected_transports, f"Неожиданный список транспортов: {transports}"
    print(f"✓ Доступные транспорты: {transports}")


def test_full_calculation():
    """Тест полного расчета выбросов."""
    calculator = CO2Calculator()
    
    # Москва -> Казань
    result = calculator.calculate_full_emissions(
        55.7558, 37.6176,  # Москва
        55.8304, 49.0661,  # Казань
        'car', use_api=False
    )
    
    # Проверяем структуру результата
    required_keys = {'distance_km', 'transport_type', 'co2_coefficient', 'co2_emissions_kg', 'calculation_method'}
    assert set(result.keys()) == required_keys, f"Неожиданные ключи в результате: {result.keys()}"
    
    # Проверяем типы данных
    assert isinstance(result['distance_km'], (int, float)), "distance_km должно быть числом"
    assert result['transport_type'] == 'car', "Неверный тип транспорта"
    assert result['co2_coefficient'] == 0.21, "Неверный коэффициент для автомобиля"
    assert result['calculation_method'] == 'Прямая линия', "Неверный метод расчета"
    
    print(f"✓ Полный расчет: {result['distance_km']} км, {result['co2_emissions_kg']} кг CO2")


def test_error_handling():
    """Тест обработки ошибок."""
    calculator = CO2Calculator()
    
    # Тест неподдерживаемого транспорта
    try:
        calculator.get_co2_emissions(100, 'rocket')
        assert False, "Должно было быть исключение для неподдерживаемого транспорта"
    except ValueError as e:
        assert "неподдерживаемый тип транспорта" in str(e).lower()
        print("✓ Обработка ошибки неподдерживаемого транспорта")
    
    # Тест API без ключа (должен переключиться на прямой расчет)
    distance = calculator.calculate_distance_route(55.7558, 37.6176, 59.9311, 30.3609, 'car')
    assert distance > 0, "Расстояние должно быть положительным"
    print("✓ Fallback на прямой расчет при отсутствии API ключа")


def run_all_tests():
    """Запуск всех тестов."""
    print("=== Запуск базовых тестов CO2 калькулятора ===\n")
    
    tests = [
        test_distance_calculation,
        test_co2_emissions,
        test_available_transports,
        test_full_calculation,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ Тест {test_func.__name__} провален: {e}")
    
    print(f"\n=== Результаты тестирования ===")
    print(f"Пройдено: {passed}/{total} тестов")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно!")
        return True
    else:
        print("❌ Некоторые тесты провалены")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
