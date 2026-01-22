"""
Сервис для получения расстояния между двумя городами.
"""

from api.co2_calculator import CO2Calculator
from db.cities_database import get_city_info


def get_distance(city_from: str, city_to: str) -> float:
    """
    Получить расстояние между двумя городами в километрах.
    
    Args:
        city_from: Название города отправления
        city_to: Название города назначения
        
    Returns:
        Расстояние в километрах
        
    Raises:
        ValueError: Если один из городов не найден
    """
    city_from_info = get_city_info(city_from)
    if not city_from_info:
        raise ValueError(f"Город '{city_from}' не найден")
    
    city_to_info = get_city_info(city_to)
    if not city_to_info:
        raise ValueError(f"Город '{city_to}' не найден")
    
    lat1, lon1 = city_from_info['coordinates']
    lat2, lon2 = city_to_info['coordinates']
    
    calculator = CO2Calculator()
    distance = calculator.calculate_distance_direct(lat1, lon1, lat2, lon2)
    
    return distance
