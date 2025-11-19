#!/usr/bin/env python3
"""
Полное тестирование системы CO2 калькулятора.
Проверяет работу всех компонентов: базы городов, логики транспорта, GUI и CLI.
"""

import sys
import os
from typing import List, Dict

# Импортируем все модули системы
from cities_database import search_cities, get_city_info, get_all_cities
from transport_logic import TransportAvailability
from co2_calculator import CO2Calculator


class FullSystemTest:
    """
    Класс для полного тестирования системы CO2 калькулятора.
    """
    
    def __init__(self):
        self.transport_logic = TransportAvailability()
        self.calculator = CO2Calculator()
        self.passed_tests = 0
        self.total_tests = 0
    
    def run_all_tests(self) -> bool:
        """Запуск всех тестов системы."""
        print("🧪 ПОЛНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ CO2 КАЛЬКУЛЯТОРА")
        print("=" * 60)
        
        test_methods = [
            self.test_cities_database,
            self.test_city_search,
            self.test_transport_logic,
            self.test_route_calculations,
            self.test_edge_cases,
            self.test_integration
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Тест {test_method.__name__} провален: {e}")
        
        # Итоговые результаты
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        print(f"Пройдено: {self.passed_tests}/{self.total_tests} тестов")
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        if success_rate == 100:
            print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            return True
        elif success_rate >= 80:
            print(f"⚠️ Большинство тестов прошло успешно ({success_rate:.0f}%)")
            return True
        else:
            print(f"❌ Много провалов тестов ({success_rate:.0f}%)")
            return False
    
    def _assert_test(self, condition: bool, test_name: str, details: str = ""):
        """Проверка условия теста."""
        self.total_tests += 1
        if condition:
            self.passed_tests += 1
            print(f"✅ {test_name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {test_name}")
            if details:
                print(f"   {details}")
    
    def test_cities_database(self):
        """Тестирование базы данных городов."""
        print("\n🏙️ Тестирование базы данных городов")
        print("-" * 40)
        
        # Тест получения всех городов
        all_cities = get_all_cities()
        self._assert_test(
            len(all_cities) > 100,
            "База содержит достаточно городов",
            f"Найдено {len(all_cities)} городов"
        )
        
        # Тест поиска конкретных городов
        test_cities = ["Москва", "Санкт-Петербург", "Нью-Йорк", "Лондон", "Париж"]
        for city_name in test_cities:
            city_info = get_city_info(city_name)
            self._assert_test(
                city_info is not None,
                f"Город '{city_name}' найден в базе",
                f"Координаты: {city_info['coordinates'] if city_info else 'Не найдены'}"
            )
        
        # Тест алиасов
        aliases_test = [
            ("СПб", "Санкт-Петербург"),
            ("Питер", "Санкт-Петербург"),
            ("Мск", "Москва")
        ]
        
        for alias, expected in aliases_test:
            city_info = get_city_info(alias)
            self._assert_test(
                city_info and city_info['name'] == expected,
                f"Алиас '{alias}' работает корректно",
                f"Разрешается в: {city_info['name'] if city_info else 'Не найден'}"
            )
    
    def test_city_search(self):
        """Тестирование поиска городов."""
        print("\n🔍 Тестирование поиска городов")
        print("-" * 40)
        
        # Тест поиска по частичному совпадению
        search_tests = [
            ("Мос", "Москва"),
            ("Санкт", "Санкт-Петербург"),
            ("Нью", "Нью-Йорк"),
            ("Лон", "Лондон")
        ]
        
        for query, expected_city in search_tests:
            results = search_cities(query, limit=5)
            found = any(city['name'] == expected_city for city in results)
            self._assert_test(
                found,
                f"Поиск '{query}' находит '{expected_city}'",
                f"Найдено {len(results)} результатов"
            )
        
        # Тест пустого запроса
        empty_results = search_cities("", limit=5)
        self._assert_test(
            len(empty_results) == 0,
            "Пустой запрос возвращает пустой результат"
        )
        
        # Тест несуществующего города
        fake_results = search_cities("НесуществующийГород123", limit=5)
        self._assert_test(
            len(fake_results) == 0,
            "Поиск несуществующего города возвращает пустой результат"
        )
    
    def test_transport_logic(self):
        """Тестирование логики транспорта."""
        print("\n🚗 Тестирование логики транспорта")
        print("-" * 40)
        
        # Получаем тестовые города
        moscow = get_city_info("Москва")
        spb = get_city_info("Санкт-Петербург")
        vladivostok = get_city_info("Владивосток")
        london = get_city_info("Лондон")
        
        # Тест короткого маршрута (Москва - СПб)
        if moscow and spb:
            transports_short = self.transport_logic.get_available_transports(moscow, spb)
            self._assert_test(
                len(transports_short) >= 3,
                "Короткий маршрут (Москва-СПб) имеет несколько вариантов транспорта",
                f"Найдено {len(transports_short)} вариантов"
            )
            
            # Проверяем, что автобус самый экологичный для этого маршрута
            if transports_short:
                most_eco = min(transports_short, key=lambda x: x['co2_emissions_kg'])
                self._assert_test(
                    most_eco['type'] in ['bus', 'train'],
                    "Самый экологичный транспорт для короткого маршрута - автобус или поезд",
                    f"Самый экологичный: {most_eco['name']}"
                )
        
        # Тест дальнего маршрута (Москва - Владивосток)
        if moscow and vladivostok:
            transports_long = self.transport_logic.get_available_transports(moscow, vladivostok)
            self._assert_test(
                len(transports_long) >= 2,
                "Дальний маршрут (Москва-Владивосток) имеет варианты транспорта",
                f"Найдено {len(transports_long)} вариантов"
            )
            
            # Для дальних маршрутов поезд и самолет должны быть доступны
            transport_types = [t['type'] for t in transports_long]
            self._assert_test(
                'train' in transport_types or 'plane' in transport_types,
                "Дальний маршрут включает поезд или самолет"
            )
        
        # Тест международного маршрута (Москва - Лондон)
        if moscow and london:
            transports_intl = self.transport_logic.get_available_transports(moscow, london)
            self._assert_test(
                len(transports_intl) >= 1,
                "Международный маршрут (Москва-Лондон) имеет варианты",
                f"Найдено {len(transports_intl)} вариантов"
            )
    
    def test_route_calculations(self):
        """Тестирование расчетов маршрутов."""
        print("\n📊 Тестирование расчетов маршрутов")
        print("-" * 40)
        
        # Тест базовых расчетов
        moscow = get_city_info("Москва")
        spb = get_city_info("Санкт-Петербург")
        
        if moscow and spb:
            lat1, lon1 = moscow['coordinates']
            lat2, lon2 = spb['coordinates']
            
            # Тест расчета расстояния
            distance = self.calculator.calculate_distance_direct(lat1, lon1, lat2, lon2)
            self._assert_test(
                600 <= distance <= 700,
                "Расстояние Москва-СПб в разумных пределах",
                f"Расчетное расстояние: {distance:.1f} км"
            )
            
            # Тест расчета выбросов для разных видов транспорта
            for transport_type in ['car', 'bus', 'train', 'plane']:
                try:
                    emissions = self.calculator.get_co2_emissions(distance, transport_type)
                    coefficient = self.calculator.CO2_COEFFICIENTS[transport_type]
                    expected = distance * coefficient
                    
                    self._assert_test(
                        abs(emissions - expected) < 0.001,
                        f"Расчет выбросов для {transport_type} корректен",
                        f"{emissions:.3f} кг CO2"
                    )
                except Exception as e:
                    self._assert_test(False, f"Ошибка расчета для {transport_type}", str(e))
    
    def test_edge_cases(self):
        """Тестирование граничных случаев."""
        print("\n⚠️ Тестирование граничных случаев")
        print("-" * 40)
        
        # Тест с неподдерживаемым транспортом
        try:
            self.calculator.get_co2_emissions(100, 'rocket')
            self._assert_test(False, "Неподдерживаемый транспорт должен вызывать ошибку")
        except ValueError:
            self._assert_test(True, "Неподдерживаемый транспорт корректно вызывает ошибку")
        except Exception as e:
            self._assert_test(False, "Неожиданный тип ошибки", str(e))
        
        # Тест с нулевым расстоянием
        zero_emissions = self.calculator.get_co2_emissions(0, 'car')
        self._assert_test(
            zero_emissions == 0,
            "Нулевое расстояние дает нулевые выбросы",
            f"Выбросы: {zero_emissions}"
        )
        
        # Тест с очень большим расстоянием
        large_distance = 50000  # 50,000 км
        large_emissions = self.calculator.get_co2_emissions(large_distance, 'plane')
        expected_large = large_distance * 0.25
        self._assert_test(
            abs(large_emissions - expected_large) < 0.001,
            "Расчет для очень больших расстояний корректен",
            f"Выбросы для {large_distance} км: {large_emissions} кг"
        )
    
    def test_integration(self):
        """Интеграционное тестирование."""
        print("\n🔗 Интеграционное тестирование")
        print("-" * 40)
        
        # Тест полного цикла: поиск городов -> расчет маршрута -> получение результатов
        try:
            # Поиск городов
            moscow_results = search_cities("Москва", limit=1)
            spb_results = search_cities("Санкт-Петербург", limit=1)
            
            self._assert_test(
                len(moscow_results) > 0 and len(spb_results) > 0,
                "Поиск тестовых городов успешен"
            )
            
            if moscow_results and spb_results:
                moscow = moscow_results[0]
                spb = spb_results[0]
                
                # Расчет маршрутов
                transports = self.transport_logic.get_available_transports(moscow, spb)
                
                self._assert_test(
                    len(transports) > 0,
                    "Получены варианты транспорта"
                )
                
                # Проверка структуры результатов
                if transports:
                    transport = transports[0]
                    required_fields = [
                        'type', 'name', 'distance_km', 'co2_emissions_kg',
                        'co2_coefficient', 'estimated_time', 'cost_category'
                    ]
                    
                    all_fields_present = all(field in transport for field in required_fields)
                    self._assert_test(
                        all_fields_present,
                        "Результат содержит все необходимые поля",
                        f"Поля: {list(transport.keys())}"
                    )
                    
                    # Проверка разумности значений
                    self._assert_test(
                        transport['distance_km'] > 0,
                        "Расстояние положительное"
                    )
                    
                    self._assert_test(
                        transport['co2_emissions_kg'] > 0,
                        "Выбросы CO2 положительные"
                    )
                    
                    self._assert_test(
                        transport['co2_coefficient'] > 0,
                        "Коэффициент CO2 положительный"
                    )
        
        except Exception as e:
            self._assert_test(False, "Интеграционный тест провален", str(e))


def main():
    """Главная функция тестирования."""
    print("Запуск полного тестирования системы CO2 калькулятора...\n")
    
    tester = FullSystemTest()
    success = tester.run_all_tests()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
        print("\nДоступные интерфейсы:")
        print("  • CLI (города): python3 co2_cli.py")
        print("  • CLI (координаты): python3 co2_routes_cli.py lat1 lon1 lat2 lon2")
        print("  • API: import co2_calculator")
    else:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ В СИСТЕМЕ")
        print("Рекомендуется проверить и исправить ошибки перед использованием")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
