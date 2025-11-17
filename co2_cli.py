#!/usr/bin/env python3
"""
Интерфейс командной строки для CO2 калькулятора.
Простая альтернатива GUI для быстрых расчетов.
"""

import sys
from typing import Optional

from cities_database import search_cities, get_city_info
from transport_logic import TransportAvailability
from co2_calculator import CO2Calculator


class CO2CalculatorCLI:
    """
    Интерфейс командной строки для CO2 калькулятора.
    """
    
    def __init__(self):
        self.transport_logic = TransportAvailability()
        self.calculator = CO2Calculator()
    
    def run(self):
        """Основной цикл CLI приложения."""
        print("🌍 CO2 Калькулятор - Командная строка")
        print("=" * 50)
        print("Рассчитайте выбросы CO2 для путешествий между городами")
        print()
        
        while True:
            try:
                # Получаем города от пользователя
                from_city = self._get_city_input("Откуда")
                if not from_city:
                    continue
                
                to_city = self._get_city_input("Куда")
                if not to_city:
                    continue
                
                if from_city['name'] == to_city['name']:
                    print("❌ Города отправления и назначения не могут быть одинаковыми")
                    continue
                
                # Спрашиваем про API ключ
                api_key = input("\nAPI ключ OpenRouteService (Enter для пропуска): ").strip()
                if api_key:
                    self.transport_logic.calculator.ors_api_key = api_key
                
                # Выполняем расчет
                print("\n⏳ Выполняется расчет...")
                transports = self.transport_logic.get_available_transports(from_city, to_city)
                
                # Показываем результаты
                self._show_results(from_city, to_city, transports)
                
                # Спрашиваем о продолжении
                if not self._ask_continue():
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 До свидания!")
                break
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
                if not self._ask_continue():
                    break
    
    def _get_city_input(self, prompt: str) -> Optional[dict]:
        """
        Получить город от пользователя с автодополнением.
        
        Args:
            prompt: Текст приглашения для ввода
            
        Returns:
            Информация о городе или None при отмене
        """
        while True:
            print(f"\n{prompt}:")
            query = input("Введите название города (или 'q' для выхода): ").strip()
            
            if query.lower() in ('q', 'quit', 'exit', 'выход'):
                return None
            
            if len(query) < 2:
                print("⚠️ Введите минимум 2 символа")
                continue
            
            # Ищем города
            cities = search_cities(query, limit=10)
            
            if not cities:
                print("😔 Города не найдены. Попробуйте другое название.")
                continue
            
            # Показываем варианты
            print("\nНайденные города:")
            for i, city in enumerate(cities, 1):
                print(f"{i}. {city['display_name']}")
            
            # Получаем выбор пользователя
            try:
                choice = input(f"\nВыберите город (1-{len(cities)}) или введите новый запрос: ").strip()
                
                # Если введено число - выбираем город
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(cities):
                        selected_city = cities[index]
                        print(f"✅ Выбран: {selected_city['display_name']}")
                        return selected_city
                    else:
                        print("❌ Неверный номер города")
                        continue
                
                # Если введен новый запрос - повторяем поиск
                elif len(choice) >= 2:
                    query = choice
                    continue
                else:
                    print("⚠️ Введите номер города или новый запрос")
                    continue
                    
            except ValueError:
                print("❌ Введите корректный номер")
                continue
    
    def _show_results(self, from_city: dict, to_city: dict, transports: list):
        """Показать результаты расчета."""
        print("\n" + "=" * 60)
        print(f"🗺️  МАРШРУТ: {from_city['name']} → {to_city['name']}")
        print("=" * 60)
        
        if not transports:
            print("😔 К сожалению, не найдено доступных маршрутов")
            return
        
        print(f"\nНайдено {len(transports)} доступных способов передвижения:\n")
        
        # Показываем каждый вид транспорта
        for i, transport in enumerate(transports, 1):
            self._print_transport_info(i, transport, i == 1)
        
        # Сравнительная информация
        if len(transports) > 1:
            self._print_comparison(transports)
    
    def _print_transport_info(self, number: int, transport: dict, is_best: bool):
        """Вывести информацию о виде транспорта."""
        icons = {'Автомобиль': '🚗', 'Автобус': '🚌', 'Поезд': '🚆', 'Самолет': '✈️'}
        icon = icons.get(transport['name'], '🚶')
        
        # Заголовок
        eco_mark = " 🌱 САМЫЙ ЭКОЛОГИЧНЫЙ" if is_best else ""
        print(f"{number}. {icon} {transport['name']}{eco_mark}")
        print("-" * 40)
        
        # Основная информация
        print(f"   💨 Выбросы CO2:     {transport['co2_emissions_kg']} кг")
        print(f"   📏 Расстояние:      {transport['distance_km']} км")
        print(f"   ⏱️  Время в пути:    {transport['estimated_time']}")
        print(f"   💰 Стоимость:       {transport['cost_category']}")
        print(f"   📊 Коэффициент:     {transport['co2_coefficient']} кг/км")
        
        # Дополнительная информация
        if transport.get('availability_reason'):
            print(f"   ℹ️  Примечание:      {transport['availability_reason']}")
        
        print()
    
    def _print_comparison(self, transports: list):
        """Вывести сравнительную информацию."""
        print("📊 СРАВНЕНИЕ ЭКОЛОГИЧНОСТИ")
        print("-" * 40)
        
        best = transports[0]
        worst = transports[-1]
        
        if best['co2_emissions_kg'] != worst['co2_emissions_kg']:
            difference = worst['co2_emissions_kg'] - best['co2_emissions_kg']
            percentage = (difference / worst['co2_emissions_kg']) * 100
            
            print(f"🌱 Выбирая {best['name']} вместо {worst['name']},")
            print(f"   вы сэкономите {difference:.1f} кг CO2 ({percentage:.0f}%)")
        
        print(f"\n📍 Общее расстояние: {transports[0]['distance_km']} км")
        print()
    
    def _ask_continue(self) -> bool:
        """Спросить пользователя о продолжении."""
        while True:
            choice = input("Выполнить еще один расчет? (y/n): ").strip().lower()
            if choice in ('y', 'yes', 'да', 'д', ''):
                return True
            elif choice in ('n', 'no', 'нет', 'н'):
                return False
            else:
                print("Введите 'y' для продолжения или 'n' для выхода")


def main():
    """Главная функция CLI приложения."""
    try:
        cli = CO2CalculatorCLI()
        cli.run()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
