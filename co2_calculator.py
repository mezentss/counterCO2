import math
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Tuple


class CO2Calculator:
    """
    Модуль для расчета выбросов CO2 между двумя географическими точками.
    
    Поддерживает расчет расстояний по прямой (формула Хаверсина) и через
    OpenRouteService API для получения реальных маршрутов.
    """
    
    # Коэффициенты выбросов CO2 в кг/пассажиро-км
    CO2_COEFFICIENTS = {
        'car': 0.21,
        'bus': 0.03,
        'train': 0.06,
        'plane': 0.25
    }
    
    # Профили транспорта для OpenRouteService API
    TRANSPORT_PROFILES = {
        'car': 'driving-car',
        'bus': 'driving-car',  # Автобусы используют автомобильные дороги
        'train': 'driving-car',  # Приблизительно через автодороги
        'plane': None  # Для самолетов используем прямое расстояние
    }
    
    def __init__(self, ors_api_key: Optional[str] = None):
        """
        Инициализация калькулятора.
        
        Args:
            ors_api_key: API ключ для OpenRouteService (опционально)
        """
        self.ors_api_key = ors_api_key
        self.ors_base_url = "https://api.openrouteservice.org/v2/directions"
    
    def calculate_distance_direct(self, lat1: float, lon1: float, 
                                lat2: float, lon2: float) -> float:
        """
        Расчет расстояния между двумя точками по прямой (формула Хаверсина).
        
        Args:
            lat1, lon1: Широта и долгота первой точки
            lat2, lon2: Широта и долгота второй точки
            
        Returns:
            Расстояние в километрах
        """
        # Радиус Земли в километрах
        R = 6371.0
        
        # Преобразование градусов в радианы
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Разности координат
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Формула Хаверсина
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def calculate_distance_route(self, lat1: float, lon1: float, 
                               lat2: float, lon2: float, 
                               transport_type: str) -> float:
        """
        Расчет расстояния через OpenRouteService API для реальных маршрутов.
        
        Args:
            lat1, lon1: Широта и долгота первой точки
            lat2, lon2: Широта и долгота второй точки
            transport_type: Тип транспорта ('car', 'bus', 'train', 'plane')
            
        Returns:
            Расстояние в километрах
            
        Raises:
            ValueError: Если тип транспорта не поддерживается
            Exception: При ошибках API запроса
        """
        if transport_type not in self.TRANSPORT_PROFILES:
            raise ValueError(f"Неподдерживаемый тип транспорта: {transport_type}")
        
        # Для самолетов используем прямое расстояние
        if transport_type == 'plane':
            return self.calculate_distance_direct(lat1, lon1, lat2, lon2)
        
        if not self.ors_api_key:
            print("Предупреждение: API ключ не предоставлен, используется прямое расстояние")
            return self.calculate_distance_direct(lat1, lon1, lat2, lon2)
        
        profile = self.TRANSPORT_PROFILES[transport_type]
        coordinates = f"{lon1},{lat1};{lon2},{lat2}"
        
        url = f"{self.ors_base_url}/{profile}?coordinates={coordinates}"
        
        try:
            headers = {
                'Authorization': self.ors_api_key,
                'Content-Type': 'application/json'
            }
            
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode())
                
            # Извлекаем расстояние из ответа (в метрах, конвертируем в км)
            distance_m = data['routes'][0]['summary']['distance']
            distance_km = distance_m / 1000.0
            
            return distance_km
            
        except Exception as e:
            print(f"Ошибка при запросе к OpenRouteService API: {e}")
            print("Используется расчет по прямой")
            return self.calculate_distance_direct(lat1, lon1, lat2, lon2)
    
    def get_co2_emissions(self, distance_km: float, transport_type: str) -> float:
        """
        Вычисление выбросов CO2 на основе расстояния и типа транспорта.
        
        Args:
            distance_km: Расстояние в километрах
            transport_type: Тип транспорта
            
        Returns:
            Выбросы CO2 в килограммах
            
        Raises:
            ValueError: Если тип транспорта не поддерживается
        """
        if transport_type not in self.CO2_COEFFICIENTS:
            raise ValueError(f"Неподдерживаемый тип транспорта: {transport_type}")
        
        coefficient = self.CO2_COEFFICIENTS[transport_type]
        emissions = distance_km * coefficient
        
        return emissions
    
    def get_available_transport_types(self) -> List[str]:
        """
        Получение списка доступных типов транспорта.
        
        Returns:
            Список доступных типов транспорта
        """
        return list(self.CO2_COEFFICIENTS.keys())
    
    def calculate_full_emissions(self, lat1: float, lon1: float, 
                               lat2: float, lon2: float, 
                               transport_type: str, 
                               use_api: bool = True) -> Dict[str, float]:
        """
        Полный расчет выбросов CO2 с возвращением детальной информации.
        
        Args:
            lat1, lon1: Широта и долгота первой точки
            lat2, lon2: Широта и долгота второй точки
            transport_type: Тип транспорта
            use_api: Использовать ли API для расчета маршрута
            
        Returns:
            Словарь с результатами расчета
        """
        if use_api:
            distance = self.calculate_distance_route(lat1, lon1, lat2, lon2, transport_type)
            method = "API маршрут"
        else:
            distance = self.calculate_distance_direct(lat1, lon1, lat2, lon2)
            method = "Прямая линия"
        
        emissions = self.get_co2_emissions(distance, transport_type)
        coefficient = self.CO2_COEFFICIENTS[transport_type]
        
        return {
            'distance_km': round(distance, 2),
            'transport_type': transport_type,
            'co2_coefficient': coefficient,
            'co2_emissions_kg': round(emissions, 3),
            'calculation_method': method
        }


# Функции для удобного использования модуля
def calculate_distance_direct(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Удобная функция для расчета расстояния по прямой.
    """
    calculator = CO2Calculator()
    return calculator.calculate_distance_direct(lat1, lon1, lat2, lon2)


def calculate_distance_route(lat1: float, lon1: float, lat2: float, lon2: float, 
                           transport_type: str, api_key: Optional[str] = None) -> float:
    """
    Удобная функция для расчета расстояния через API.
    """
    calculator = CO2Calculator(api_key)
    return calculator.calculate_distance_route(lat1, lon1, lat2, lon2, transport_type)


def get_co2_emissions(distance_km: float, transport_type: str) -> float:
    """
    Удобная функция для расчета выбросов CO2.
    """
    calculator = CO2Calculator()
    return calculator.get_co2_emissions(distance_km, transport_type)


def get_available_transport_types() -> List[str]:
    """
    Удобная функция для получения списка доступных транспортных средств.
    """
    calculator = CO2Calculator()
    return calculator.get_available_transport_types()
