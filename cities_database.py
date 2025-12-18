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


# Минимальный набор городов используется только в мок-режиме,
# когда внешнее GEO API недоступно (USE_REAL_HTTP != "1").
_CITIES: Dict[str, City] = {
    "Москва": City(name="Москва", country="Россия", coordinates=(55.7558, 37.6176)),
    "Санкт-Петербург": City(
        name="Санкт-Петербург",
        country="Россия",
        coordinates=(59.9311, 30.3609),
    ),
    "Владивосток": City(
        name="Владивосток",
        country="Россия",
        coordinates=(43.1155, 131.8855),
    ),
    "Казань": City(name="Казань", country="Россия", coordinates=(55.7887, 49.1221)),
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
    q = query.lower()
    results: List[Dict[str, object]] = []
    for city in _CITIES.values():
        if q in city.name.lower():
            results.append(
                {
                    "name": city.name,
                    "country": city.country,
                    "coordinates": city.coordinates,
                }
            )
    return results


# === Глобальные функции-обёртки, сохраняющие старый интерфейс ===

_CLIENT = GeoApiClient()


def get_city_info(name: str) -> Optional[Dict[str, object]]:
    return _CLIENT.get_city_info(name)


def get_all_cities() -> List[Dict[str, object]]:
    return _CLIENT.get_all_cities()


def search_cities(query: str) -> List[Dict[str, object]]:
    return _CLIENT.search_cities(query)
