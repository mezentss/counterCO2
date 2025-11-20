import json
import os
from typing import Any, Dict
from urllib import error, request

from api_models import Point, Route


class RouteApiClient:
    """Клиент API маршрутов."""

    def get_route(self, start: Point, end: Point) -> Route:
        """Получить маршрут между двумя точками."""

        base_url = os.environ.get("ROUTE_API_BASE_URL", "https://api.routes.local/v1")
        url = f"{base_url.rstrip('/')}/routes"

        api_key = os.environ.get("ROUTE_API_KEY")
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        body: Dict[str, Any] = {
            "start": {"lat": start.lat, "lon": start.lon},
            "end": {"lat": end.lat, "lon": end.lon},
            "transport": "car",
        }

        response_data = self._send_request("POST", url, headers, body)
        distance_km = float(response_data["distance_km"])
        return Route(start=start, end=end, distance_km=distance_km)

    def _send_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Внутренний метод отправки HTTP-запроса.

        Если переменная окружения USE_REAL_HTTP установлена в "1",
        выполняется настоящий HTTP-запрос. Иначе используется мок-режим:
        параметры запроса выводятся в консоль, а возвращается
        заранее подготовленный ответ.
        """

        if os.environ.get("USE_REAL_HTTP") == "1":
            data = json.dumps(body).encode("utf-8")
            req = request.Request(url, data=data, headers=headers, method=method)
            try:
                with request.urlopen(req) as resp:
                    resp_body = resp.read().decode("utf-8")
            except error.HTTPError as exc:
                raise RuntimeError(
                    f"RouteApiClient HTTP error: {exc.code} {exc.reason}"
                ) from exc

            if not resp_body:
                return {}
            return json.loads(resp_body)

        print(f"[RouteApiClient][MOCK] {method} {url}")
        print(f"[RouteApiClient][MOCK] headers={headers}")
        print(f"[RouteApiClient][MOCK] body={body}")

        return {"distance_km": 700.0}


class Co2ApiClient:
    """Клиент API расчёта выбросов CO2."""

    def get_emissions(self, route: Route) -> Dict[str, Any]:
        """Рассчитать выбросы CO2 для заданного маршрута."""

        base_url = os.environ.get("CO2_API_BASE_URL", "https://api.co2.local/v1")
        url = f"{base_url.rstrip('/')}/emissions"

        api_key = os.environ.get("CO2_API_KEY")
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        body: Dict[str, Any] = {
            "distance_km": route.distance_km,
            "transport_type": "car",
        }

        response_data = self._send_request("POST", url, headers, body)

        return {
            "transport_type": response_data["transport_type"],
            "distance_km": response_data["distance_km"],
            "co2_emissions_kg": response_data["co2_emissions_kg"],
            "source": "co2-api",
        }

    def _send_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Внутренний метод отправки HTTP-запроса.

        Если переменная окружения USE_REAL_HTTP установлена в "1",
        выполняется настоящий HTTP-запрос. Иначе используется мок-режим:
        параметры запроса выводятся в консоль, а ответ вычисляется
        на основе тела запроса.
        """

        if os.environ.get("USE_REAL_HTTP") == "1":
            data = json.dumps(body).encode("utf-8")
            req = request.Request(url, data=data, headers=headers, method=method)
            try:
                with request.urlopen(req) as resp:
                    resp_body = resp.read().decode("utf-8")
            except error.HTTPError as exc:
                raise RuntimeError(
                    f"Co2ApiClient HTTP error: {exc.code} {exc.reason}"
                ) from exc

            if not resp_body:
                return {}
            return json.loads(resp_body)

        print(f"[Co2ApiClient][MOCK] {method} {url}")
        print(f"[Co2ApiClient][MOCK] headers={headers}")
        print(f"[Co2ApiClient][MOCK] body={body}")

        distance = float(body["distance_km"])
        co2_per_km_kg = 0.15
        total_emissions = distance * co2_per_km_kg

        return {
            "transport_type": body["transport_type"],
            "distance_km": distance,
            "co2_emissions_kg": total_emissions,
        }
