from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from urllib import error, request


@dataclass
class City:
    name: str
    country: str
    coordinates: Tuple[float, float]


# База данных русских городов с координатами (широта, долгота)
# Используется в мок-режиме, когда внешнее GEO API недоступно (USE_REAL_HTTP != "1").
_CITIES: Dict[str, City] = {
    # Города-миллионники и крупные города России
    "Москва": City(name="Москва", country="Россия", coordinates=(55.7558, 37.6176)),
    "Санкт-Петербург": City(
        name="Санкт-Петербург",
        country="Россия",
        coordinates=(59.9311, 30.3609),
    ),
    "Новосибирск": City(name="Новосибирск", country="Россия", coordinates=(55.0084, 82.9357)),
    "Екатеринбург": City(name="Екатеринбург", country="Россия", coordinates=(56.8431, 60.6454)),
    "Казань": City(name="Казань", country="Россия", coordinates=(55.7887, 49.1221)),
    "Нижний Новгород": City(name="Нижний Новгород", country="Россия", coordinates=(56.2965, 43.9361)),
    "Челябинск": City(name="Челябинск", country="Россия", coordinates=(55.1644, 61.4368)),
    "Самара": City(name="Самара", country="Россия", coordinates=(53.2001, 50.15)),
    "Омск": City(name="Омск", country="Россия", coordinates=(54.9885, 73.3242)),
    "Ростов-на-Дону": City(name="Ростов-на-Дону", country="Россия", coordinates=(47.2357, 39.7015)),
    "Уфа": City(name="Уфа", country="Россия", coordinates=(54.7431, 55.9678)),
    "Красноярск": City(name="Красноярск", country="Россия", coordinates=(56.0184, 92.8672)),
    "Воронеж": City(name="Воронеж", country="Россия", coordinates=(51.6720, 39.1843)),
    "Пермь": City(name="Пермь", country="Россия", coordinates=(58.0105, 56.2502)),
    "Волгоград": City(name="Волгоград", country="Россия", coordinates=(48.7194, 44.5018)),
    "Краснодар": City(name="Краснодар", country="Россия", coordinates=(45.0355, 38.9753)),
    "Саратов": City(name="Саратов", country="Россия", coordinates=(51.5336, 46.0342)),
    "Тюмень": City(name="Тюмень", country="Россия", coordinates=(57.1522, 65.5272)),
    "Тольятти": City(name="Тольятти", country="Россия", coordinates=(53.5303, 49.3461)),
    "Ижевск": City(name="Ижевск", country="Россия", coordinates=(56.8527, 53.2115)),
    "Барнаул": City(name="Барнаул", country="Россия", coordinates=(53.3606, 83.7636)),
    "Ульяновск": City(name="Ульяновск", country="Россия", coordinates=(54.3142, 48.4031)),
    "Иркутск": City(name="Иркутск", country="Россия", coordinates=(52.2864, 104.2807)),
    "Хабаровск": City(name="Хабаровск", country="Россия", coordinates=(48.4647, 135.0598)),
    "Ярославль": City(name="Ярославль", country="Россия", coordinates=(57.6266, 39.8938)),
    "Владивосток": City(
        name="Владивосток",
        country="Россия",
        coordinates=(43.1155, 131.8855),
    ),
    "Махачкала": City(name="Махачкала", country="Россия", coordinates=(42.9849, 47.5047)),
    "Томск": City(name="Томск", country="Россия", coordinates=(56.4846, 84.9482)),
    "Оренбург": City(name="Оренбург", country="Россия", coordinates=(51.7682, 55.0970)),
    "Кемерово": City(name="Кемерово", country="Россия", coordinates=(55.3549, 86.0873)),
    "Новокузнецк": City(name="Новокузнецк", country="Россия", coordinates=(53.7577, 87.1366)),
    "Рязань": City(name="Рязань", country="Россия", coordinates=(54.6269, 39.6916)),
    "Астрахань": City(name="Астрахань", country="Россия", coordinates=(46.3497, 48.0408)),
    "Набережные Челны": City(name="Набережные Челны", country="Россия", coordinates=(55.7436, 52.3958)),
    "Пенза": City(name="Пенза", country="Россия", coordinates=(53.2001, 45.0046)),
    "Липецк": City(name="Липецк", country="Россия", coordinates=(52.6088, 39.5992)),
    "Киров": City(name="Киров", country="Россия", coordinates=(58.6036, 49.6680)),
    "Чебоксары": City(name="Чебоксары", country="Россия", coordinates=(56.1439, 47.2489)),
    "Калининград": City(name="Калининград", country="Россия", coordinates=(54.7104, 20.4522)),
    "Тула": City(name="Тула", country="Россия", coordinates=(54.1931, 37.6173)),
    "Курск": City(name="Курск", country="Россия", coordinates=(51.7373, 36.1873)),
    "Сочи": City(name="Сочи", country="Россия", coordinates=(43.6028, 39.7342)),
    "Ставрополь": City(name="Ставрополь", country="Россия", coordinates=(45.0445, 41.9690)),
    "Улан-Удэ": City(name="Улан-Удэ", country="Россия", coordinates=(51.8271, 107.6062)),
    "Магнитогорск": City(name="Магнитогорск", country="Россия", coordinates=(53.4186, 59.0472)),
    "Тверь": City(name="Тверь", country="Россия", coordinates=(56.8584, 35.9006)),
    "Иваново": City(name="Иваново", country="Россия", coordinates=(57.0004, 40.9739)),
    "Брянск": City(name="Брянск", country="Россия", coordinates=(53.2434, 34.3654)),
    "Сургут": City(name="Сургут", country="Россия", coordinates=(61.2540, 73.3962)),
    "Мурманск": City(name="Мурманск", country="Россия", coordinates=(68.9792, 33.0925)),
    "Архангельск": City(name="Архангельск", country="Россия", coordinates=(64.5393, 40.5187)),
    "Владикавказ": City(name="Владикавказ", country="Россия", coordinates=(43.0246, 44.6818)),
    "Чита": City(name="Чита", country="Россия", coordinates=(52.0340, 113.4990)),
    "Смоленск": City(name="Смоленск", country="Россия", coordinates=(54.7826, 32.0453)),
    "Курган": City(name="Курган", country="Россия", coordinates=(55.4410, 65.3411)),
    "Вологда": City(name="Вологда", country="Россия", coordinates=(59.2187, 39.8887)),
    "Саранск": City(name="Саранск", country="Россия", coordinates=(54.1874, 45.1839)),
    "Череповец": City(name="Череповец", country="Россия", coordinates=(59.1265, 37.9094)),
    "Орёл": City(name="Орёл", country="Россия", coordinates=(52.9703, 36.0635)),
    "Грозный": City(name="Грозный", country="Россия", coordinates=(43.3178, 45.6988)),
    "Владимир": City(name="Владимир", country="Россия", coordinates=(56.1290, 40.4066)),
    "Нижний Тагил": City(name="Нижний Тагил", country="Россия", coordinates=(57.9101, 59.9813)),
    "Якутск": City(name="Якутск", country="Россия", coordinates=(62.0278, 129.7042)),
    "Петрозаводск": City(name="Петрозаводск", country="Россия", coordinates=(61.7850, 34.3467)),
    "Стерлитамак": City(name="Стерлитамак", country="Россия", coordinates=(53.6246, 55.9501)),
    "Кострома": City(name="Кострома", country="Россия", coordinates=(57.7678, 40.9269)),
    "Новороссийск": City(name="Новороссийск", country="Россия", coordinates=(44.7239, 37.7688)),
    "Нальчик": City(name="Нальчик", country="Россия", coordinates=(43.4853, 43.6071)),
    "Шахты": City(name="Шахты", country="Россия", coordinates=(47.7085, 40.2159)),
    "Дзержинск": City(name="Дзержинск", country="Россия", coordinates=(56.2376, 43.4599)),
    "Братск": City(name="Братск", country="Россия", coordinates=(56.1514, 101.6342)),
    "Орск": City(name="Орск", country="Россия", coordinates=(51.2296, 58.4750)),
    "Энгельс": City(name="Энгельс", country="Россия", coordinates=(51.4839, 46.1053)),
    "Ангарск": City(name="Ангарск", country="Россия", coordinates=(52.5448, 103.8885)),
    "Благовещенск": City(name="Благовещенск", country="Россия", coordinates=(50.2907, 127.5272)),
    "Южно-Сахалинск": City(name="Южно-Сахалинск", country="Россия", coordinates=(46.9591, 142.7380)),
    "Петропавловск-Камчатский": City(name="Петропавловск-Камчатский", country="Россия", coordinates=(53.0194, 158.6507)),
    "Сыктывкар": City(name="Сыктывкар", country="Россия", coordinates=(61.6688, 50.8354)),
    "Нарьян-Мар": City(name="Нарьян-Мар", country="Россия", coordinates=(67.6375, 53.0064)),
    "Ханты-Мансийск": City(name="Ханты-Мансийск", country="Россия", coordinates=(61.0032, 69.0189)),
    "Анадырь": City(name="Анадырь", country="Россия", coordinates=(64.7333, 177.5167)),
    
    # Иностранные города (для совместимости)
    "Лондон": City(name="Лондон", country="Великобритания", coordinates=(51.5074, -0.1278)),
}


class GeoApiClient:
    """Клиент внешнего GEO API для работы с городами.

    При USE_REAL_HTTP="1" выполняются реальные HTTP-запросы к внешнему API
    (базовый URL и ключ берутся из переменных окружения GEO_API_BASE_URL
    и GEO_API_KEY). В противном случае используется мок-режим
    на основе встроенного словаря _CITIES.
    """

    def __init__(self) -> None:
        self.base_url = os.environ.get("GEO_API_BASE_URL", "https://api.geo.local/v1")
        self.api_key = os.environ.get("GEO_API_KEY")

    # ==== Публичные методы (используются transport_logic и тестами) ====

    def get_city_info(self, name: str) -> Optional[Dict[str, object]]:
        if os.environ.get("USE_REAL_HTTP") == "1":
            return self._get_city_info_http(name)
        return _get_city_info_mock(name)

    def get_all_cities(self) -> List[Dict[str, object]]:
        if os.environ.get("USE_REAL_HTTP") == "1":
            return self._get_all_cities_http()
        return _get_all_cities_mock()

    def search_cities(self, query: str) -> List[Dict[str, object]]:
        if os.environ.get("USE_REAL_HTTP") == "1":
            return self._search_cities_http(query)
        return _search_cities_mock(query)

    # ==== HTTP-реализация (заглушка под реальное внешнее API) ====

    def _send_request(self, path: str, params: Dict[str, str]) -> Dict[str, object]:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

        if params:
            query_str = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query_str}"

        headers: Dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = request.Request(url, headers=headers, method="GET")
        try:
            with request.urlopen(req) as resp:
                body = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            raise RuntimeError(f"GeoApiClient HTTP error: {exc.code} {exc.reason}") from exc

        if not body:
            return {}
        return json.loads(body)

    def _get_city_info_http(self, name: str) -> Optional[Dict[str, object]]:
        data = self._send_request("cities/by-name", {"q": name})
        if not data:
            return None
        # Структура ответа здесь предполагаемая и может быть адаптирована
        # под конкретное внешнее GEO API.
        return {
            "name": data["name"],
            "country": data["country"],
            "coordinates": (float(data["lat"]), float(data["lon"])),
        }

    def _get_all_cities_http(self) -> List[Dict[str, object]]:
        data = self._send_request("cities", {})
        results: List[Dict[str, object]] = []
        for item in data.get("items", []):
            results.append(
                {
                    "name": item["name"],
                    "country": item["country"],
                    "coordinates": (float(item["lat"]), float(item["lon"])),
                }
            )
        return results

    def _search_cities_http(self, query: str) -> List[Dict[str, object]]:
        data = self._send_request("cities/search", {"q": query})
        results: List[Dict[str, object]] = []
        for item in data.get("items", []):
            results.append(
                {
                    "name": item["name"],
                    "country": item["country"],
                    "coordinates": (float(item["lat"]), float(item["lon"])),
                }
            )
        return results


# === Мок-реализации, использующие встроенный словарь _CITIES ===


def _get_city_info_mock(name: str) -> Optional[Dict[str, object]]:
    city = _CITIES.get(name)
    if not city:
        return None
    return {
        "name": city.name,
        "country": city.country,
        "coordinates": city.coordinates,
    }


def _get_all_cities_mock() -> List[Dict[str, object]]:
    return [
        {
            "name": city.name,
            "country": city.country,
            "coordinates": city.coordinates,
        }
        for city in _CITIES.values()
    ]


def _search_cities_mock(query: str) -> List[Dict[str, object]]:
    """Поиск городов по частичному совпадению названия (без учета регистра)."""
    q = query.lower().strip()
    results: List[Dict[str, object]] = []
    
    # Точное совпадение имеет приоритет
    exact_matches = []
    partial_matches = []
    
    for city in _CITIES.values():
        city_name_lower = city.name.lower()
        if city_name_lower == q:
            exact_matches.append({
                "name": city.name,
                "country": city.country,
                "coordinates": city.coordinates,
            })
        elif q in city_name_lower:
            partial_matches.append({
                "name": city.name,
                "country": city.country,
                "coordinates": city.coordinates,
            })
    
    # Сначала точные совпадения, затем частичные
    results = exact_matches + partial_matches
    return results


# === Глобальные функции-обёртки, сохраняющие старый интерфейс ===

_CLIENT = GeoApiClient()


def get_city_info(name: str) -> Optional[Dict[str, object]]:
    return _CLIENT.get_city_info(name)


def get_all_cities() -> List[Dict[str, object]]:
    return _CLIENT.get_all_cities()


def search_cities(query: str) -> List[Dict[str, object]]:
    return _CLIENT.search_cities(query)
