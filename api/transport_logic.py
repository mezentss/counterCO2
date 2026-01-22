"""
Логика определения доступных видов транспорта для маршрутов.
Учитывает расстояние, географические особенности и практичность использования.
"""

from api.co2_calculator import CO2Calculator


class TransportAvailability:
    """
    Класс для определения доступности различных видов транспорта
    между двумя точками на основе расстояния и географических факторов.
    """
    
    def __init__(self):
        self.calculator = CO2Calculator()
        
        # Пороговые значения расстояний для разных видов транспорта (в км)
        self.distance_thresholds = {
            'car': {
                'min': 0,
                'max': 3000,  # Практический предел для автомобильных поездок
                'optimal_max': 1500  # Оптимальное расстояние
            },
            'bus': {
                'min': 10,  # Минимальное расстояние для междугородних автобусов
                'max': 2000,  # Максимальное расстояние для автобусных маршрутов
                'optimal_max': 800
            },
            'train': {
                'min': 50,  # Минимальное расстояние для поездов дальнего следования
                'max': 10000,  # Поезда могут покрывать очень большие расстояния
                'optimal_max': 3000
            },
            'plane': {
                'min': 200,  # Минимальное расстояние, при котором имеет смысл лететь
                'max': 20000,  # Максимальное расстояние для коммерческих рейсов
                'optimal_max': 15000
            }
        }
        
        # Страны с хорошо развитой транспортной инфраструктурой
        self.developed_transport_countries = {
            'Россия', 'Германия', 'Франция', 'Япония', 'Южная Корея',
            'Швейцария', 'Нидерланды', 'Бельгия', 'Австрия', 'Швеция',
            'Норвегия', 'Дания', 'Финляндия', 'США', 'Канада',
            'Великобритания', 'Италия', 'Испания', 'Чехия', 'Польша'
        }
    
    def get_available_transports(self, city_from: dict, city_to: dict) -> list:
        """
        Определяет доступные виды транспорта между двумя городами.
        
        Args:
            city_from: Информация о городе отправления
            city_to: Информация о городе назначения
            
        Returns:
            Список доступных видов транспорта с дополнительной информацией
        """
        lat1, lon1 = city_from['coordinates']
        lat2, lon2 = city_to['coordinates']
        
        # Рассчитываем расстояние
        distance = self.calculator.calculate_distance_direct(lat1, lon1, lat2, lon2)
        
        available_transports = []
        
        # Проверяем каждый вид транспорта
        for transport_type in ['car', 'bus', 'train', 'plane']:
            availability = self._check_transport_availability(
                transport_type, distance, city_from, city_to
            )
            
            if availability['available']:
                # Рассчитываем выбросы CO2
                emissions = self.calculator.get_co2_emissions(distance, transport_type)
                
                transport_info = {
                    'type': transport_type,
                    'name': self._get_transport_name(transport_type),
                    'distance_km': round(distance, 1),
                    'co2_emissions_kg': round(emissions, 3),
                    'co2_coefficient': self.calculator.CO2_COEFFICIENTS[transport_type],
                    'availability_reason': availability['reason'],
                    'practicality': availability['practicality'],
                    'estimated_time': self._estimate_travel_time(transport_type, distance),
                    'cost_category': self._estimate_cost_category(transport_type, distance)
                }
                
                available_transports.append(transport_info)
        
        # Сортируем по экологичности (меньше выбросов = лучше)
        available_transports.sort(key=lambda x: x['co2_emissions_kg'])
        
        return available_transports
    
    def _check_transport_availability(self, transport_type: str, distance: float, 
                                    city_from: dict, city_to: dict) -> dict:
        """
        Проверяет доступность конкретного вида транспорта.
        
        Returns:
            Словарь с информацией о доступности
        """
        thresholds = self.distance_thresholds[transport_type]
        
        # Базовая проверка по расстоянию
        if distance < thresholds['min']:
            return {
                'available': False,
                'reason': f"Слишком короткое расстояние для {self._get_transport_name(transport_type)}",
                'practicality': 'low'
            }
        
        if distance > thresholds['max']:
            return {
                'available': False,
                'reason': f"Слишком большое расстояние для {self._get_transport_name(transport_type)}",
                'practicality': 'low'
            }
        
        # Специфические проверки для каждого вида транспорта
        if transport_type == 'car':
            return self._check_car_availability(distance, city_from, city_to)
        elif transport_type == 'bus':
            return self._check_bus_availability(distance, city_from, city_to)
        elif transport_type == 'train':
            return self._check_train_availability(distance, city_from, city_to)
        elif transport_type == 'plane':
            return self._check_plane_availability(distance, city_from, city_to)
        
        return {'available': False, 'reason': 'Неизвестный тип транспорта', 'practicality': 'low'}
    
    def _check_car_availability(self, distance: float, city_from: dict, city_to: dict) -> dict:
        """Проверка доступности автомобиля."""
        same_country = city_from['country'] == city_to['country']
        
        if distance <= 100:
            practicality = 'high'
            reason = "Оптимальное расстояние для автомобиля"
        elif distance <= 500:
            practicality = 'high'
            reason = "Хорошее расстояние для автомобиля"
        elif distance <= 1500:
            practicality = 'medium'
            reason = "Возможно на автомобиле, но требует остановок"
        else:
            practicality = 'low'
            reason = "Очень дальняя поездка на автомобиле"
        
        # Международные поездки сложнее
        if not same_country:
            if city_from['country'] in self.developed_transport_countries and \
               city_to['country'] in self.developed_transport_countries:
                reason += " (международная поездка возможна)"
            else:
                practicality = 'low'
                reason += " (международная поездка может быть сложной)"
        
        return {
            'available': True,
            'reason': reason,
            'practicality': practicality
        }
    
    def _check_bus_availability(self, distance: float, city_from: dict, city_to: dict) -> dict:
        """Проверка доступности автобуса."""
        same_country = city_from['country'] == city_to['country']
        
        if distance <= 200:
            practicality = 'high'
            reason = "Отличное расстояние для автобуса"
        elif distance <= 800:
            practicality = 'high'
            reason = "Хорошее расстояние для автобуса"
        elif distance <= 1500:
            practicality = 'medium'
            reason = "Дальний автобусный маршрут"
        else:
            practicality = 'low'
            reason = "Очень дальний автобусный маршрут"
        
        # Международные автобусные маршруты
        if not same_country:
            if city_from['country'] in self.developed_transport_countries and \
               city_to['country'] in self.developed_transport_countries:
                reason += " (международный маршрут)"
            else:
                return {
                    'available': False,
                    'reason': "Международные автобусные маршруты ограничены",
                    'practicality': 'low'
                }
        
        return {
            'available': True,
            'reason': reason,
            'practicality': practicality
        }
    
    def _check_train_availability(self, distance: float, city_from: dict, city_to: dict) -> dict:
        """Проверка доступности поезда."""
        same_country = city_from['country'] == city_to['country']
        
        # Поезда особенно хороши для средних и дальних расстояний
        if distance <= 300:
            practicality = 'medium'
            reason = "Поезд доступен, но может быть медленнее автомобиля"
        elif distance <= 1000:
            practicality = 'high'
            reason = "Отличное расстояние для поезда"
        elif distance <= 3000:
            practicality = 'high'
            reason = "Хорошее расстояние для поезда дальнего следования"
        else:
            practicality = 'medium'
            reason = "Очень дальний железнодорожный маршрут"
        
        # Проверяем развитость железнодорожной сети
        if same_country:
            if city_from['country'] in ['Россия', 'Германия', 'Франция', 'Япония', 'Швейцария']:
                reason += " (развитая железнодорожная сеть)"
            elif city_from['country'] in self.developed_transport_countries:
                pass  # Обычная доступность
            else:
                practicality = 'low'
                reason = "Ограниченная железнодорожная сеть"
        else:
            # Международные поезда
            europe_countries = {
                'Германия', 'Франция', 'Италия', 'Испания', 'Австрия',
                'Швейцария', 'Нидерланды', 'Бельгия', 'Чехия', 'Польша'
            }
            
            if city_from['country'] in europe_countries and city_to['country'] in europe_countries:
                reason += " (европейская железнодорожная сеть)"
            elif city_from['country'] == 'Россия' and city_to['country'] in ['Беларусь', 'Казахстан']:
                reason += " (постсоветская железнодорожная сеть)"
            else:
                return {
                    'available': False,
                    'reason': "Нет прямого железнодорожного сообщения",
                    'practicality': 'low'
                }
        
        return {
            'available': True,
            'reason': reason,
            'practicality': practicality
        }
    
    def _check_plane_availability(self, distance: float, city_from: dict, city_to: dict) -> dict:
        """Проверка доступности самолета."""
        if distance <= 300:
            practicality = 'low'
            reason = "Короткое расстояние, самолет неэффективен"
        elif distance <= 1000:
            practicality = 'medium'
            reason = "Среднее расстояние, самолет быстрее наземного транспорта"
        elif distance <= 5000:
            practicality = 'high'
            reason = "Оптимальное расстояние для авиаперелета"
        else:
            practicality = 'high'
            reason = "Дальний авиаперелет, возможны пересадки"
        
        # Самолеты доступны практически везде для международных рейсов
        # и в большинстве крупных городов для внутренних
        
        return {
            'available': True,
            'reason': reason,
            'practicality': practicality
        }
    
    def _get_transport_name(self, transport_type: str) -> str:
        """Получает русское название вида транспорта."""
        names = {
            'car': 'Автомобиль',
            'bus': 'Автобус',
            'train': 'Поезд',
            'plane': 'Самолет'
        }
        return names.get(transport_type, transport_type)
    
    def _estimate_travel_time(self, transport_type: str, distance: float) -> str:
        """Оценивает примерное время в пути."""
        # Примерные скорости (км/ч)
        speeds = {
            'car': 80,      # С учетом остановок и пробок
            'bus': 60,      # Медленнее из-за остановок
            'train': 100,   # Средняя скорость поездов
            'plane': 500    # С учетом времени в аэропорту
        }
        
        speed = speeds.get(transport_type, 50)
        hours = distance / speed
        
        # Добавляем время на подготовку
        if transport_type == 'plane':
            hours += 3  # Время в аэропорту
        elif transport_type == 'train':
            hours += 1  # Время на вокзале
        
        if hours < 1:
            return f"{int(hours * 60)} мин"
        elif hours < 24:
            return f"{hours:.1f} ч"
        else:
            days = int(hours / 24)
            remaining_hours = hours % 24
            if remaining_hours < 1:
                return f"{days} дн"
            else:
                return f"{days} дн {remaining_hours:.0f} ч"
    
    def _estimate_cost_category(self, transport_type: str, distance: float) -> str:
        """Оценивает категорию стоимости."""
        # Примерная стоимость за км (условные единицы)
        cost_per_km = {
            'car': 8,       # Бензин + износ
            'bus': 3,       # Самый дешевый
            'train': 5,     # Средняя стоимость
            'plane': 12     # Самый дорогой на короткие расстояния
        }
        
        # Для самолетов стоимость за км снижается на дальних расстояниях
        if transport_type == 'plane' and distance > 2000:
            cost_per_km['plane'] = 8
        
        total_cost = cost_per_km.get(transport_type, 5) * distance
        
        if total_cost < 2000:
            return "Низкая"
        elif total_cost < 8000:
            return "Средняя"
        else:
            return "Высокая"


if __name__ == "__main__":
    # Тестирование логики транспорта
    from cities_database import get_city_info
    
    transport_logic = TransportAvailability()
    
    # Тестовые маршруты
    test_routes = [
        ("Москва", "Санкт-Петербург"),
        ("Москва", "Владивосток"),
        ("Москва", "Лондон"),
        ("Москва", "Казань"),
    ]
    
    for city_from_name, city_to_name in test_routes:
        city_from = get_city_info(city_from_name)
        city_to = get_city_info(city_to_name)
        
        if city_from and city_to:
            print(f"\n=== {city_from_name} → {city_to_name} ===")
            
            transports = transport_logic.get_available_transports(city_from, city_to)
            
            for transport in transports:
                print(f"{transport['name']}: {transport['co2_emissions_kg']} кг CO2, "
                      f"{transport['estimated_time']}, {transport['cost_category']} стоимость")
                print(f"  {transport['availability_reason']}")
        else:
            print(f"Не найден город: {city_from_name} или {city_to_name}")
