"""
Калькулятор выбросов CO2 для различных видов транспорта.
"""

from api.co2_calculator import get_co2_emissions
from api.transport_logic import TransportAvailability
from db.cities_database import get_city_info


class TransportUnavailableError(Exception):
    """Исключение, возникающее когда вид транспорта недоступен для маршрута."""
    pass


def calculate_emissions(transport_type: str, distance_km: float, 
                        city_from: str = None, city_to: str = None) -> float:
    """
    Рассчитать выбросы CO2 для заданного вида транспорта и расстояния.
    
    Args:
        transport_type: Тип транспорта ('plane', 'train', 'car', 'bus')
        distance_km: Расстояние в километрах
        city_from: Название города отправления (опционально, для проверки доступности)
        city_to: Название города назначения (опционально, для проверки доступности)
        
    Returns:
        Выбросы CO2 в килограммах
        
    Raises:
        TransportUnavailableError: Если вид транспорта недоступен для данного маршрута
        ValueError: Если тип транспорта не поддерживается
    """
    # Проверяем доступность транспорта, если указаны города
    if city_from and city_to:
        city_from_info = get_city_info(city_from)
        city_to_info = get_city_info(city_to)
        
        if city_from_info and city_to_info:
            transport_availability = TransportAvailability()
            # Используем переданное расстояние для проверки доступности
            availability = transport_availability._check_transport_availability(
                transport_type, distance_km, city_from_info, city_to_info
            )
            
            if not availability['available']:
                raise TransportUnavailableError(
                    f"Вид транспорта '{transport_type}' недоступен: {availability['reason']}"
                )
    
    # Рассчитываем выбросы CO2
    try:
        emissions = get_co2_emissions(distance_km, transport_type)
        return emissions
    except ValueError as e:
        # Если тип транспорта не поддерживается, это тоже считается недоступностью
        raise TransportUnavailableError(str(e)) from e
