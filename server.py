#!/usr/bin/env python3
"""Простой HTTP-сервер с API для расчёта маршрута и выбросов CO2.

Сервер предоставляет несколько эндпоинтов:

- POST /api/route
  Тело (JSON):
    {
      "start": {"lat": <float>, "lon": <float>},
      "end":   {"lat": <float>, "lon": <float>}
    }
  Ответ (JSON): описание маршрута, полученного через RouteApiClient.

- POST /api/emissions
  Тело (JSON):
    {
      "distance_km": <float>,
      "transport_type": "car"
    }
  Ответ (JSON): расчёт выбросов CO2 от Co2ApiClient.

- POST /api/full
  Тело (JSON):
    {
      "start": {"lat": <float>, "lon": <float>},
      "end":   {"lat": <float>, "lon": <float>}
    }
  Ответ (JSON): комбинированный результат (маршрут + CO2).

Все вычисления происходят внутри процесса: сервер не делает внешних HTTP-запросов.
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from example import Point, RouteApiClient, Co2ApiClient


class ApiHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов для простого JSON API."""

    route_client = RouteApiClient()
    co2_client = Co2ApiClient()

    def _read_json_body(self) -> Dict[str, Any]:
        """Считать и распарсить JSON-тело запроса.

        При ошибке парсинга возвращает пустой словарь.
        """

        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length == 0:
            return {}

        raw_body = self.rfile.read(content_length)
        try:
            return json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _send_json(self, status_code: int, payload: Dict[str, Any]) -> None:
        """Отправить JSON-ответ с заданным статусом."""

        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status_code: int, html: str) -> None:
        """Отправить простой HTML-ответ."""

        body = html.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        """Обработка GET-запросов.

        При обращении к корню ("/") возвращает простую страницу с описанием API.
        """

        if self.path == "/":
            html = """<!doctype html>
<html lang=\"ru\">
  <head>
    <meta charset=\"utf-8\" />
    <title>CO2 API Server</title>
    <style>
      body { font-family: system-ui, -apple-system, sans-serif; margin: 2rem; }
      code { background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }
      pre { background: #f5f5f5; padding: 1rem; border-radius: 4px; }
    </style>
  </head>
  <body>
    <h1>CO2 API Server</h1>
    <p>Сервер запущен. Доступны следующие эндпоинты:</p>
    <ul>
      <li><code>POST /api/route</code> — расчёт маршрута по двум точкам.</li>
      <li><code>POST /api/emissions</code> — расчёт выбросов CO2 по расстоянию.</li>
      <li><code>POST /api/full</code> — маршрут + расчёт выбросов CO2.</li>
    </ul>
    <p>Пример запроса с помощью <code>curl</code>:</p>
    <pre><code>curl -X POST http://127.0.0.1:8000/api/full \
  -H \"Content-Type: application/json\" \
  -d '{"start": {"lat": 55.7558, "lon": 37.6176}, "end": {"lat": 59.9311, "lon": 30.3609}}'</code></pre>
  </body>
</html>
"""
            self._send_html(200, html)
        else:
            self._send_html(404, "<h1>404 Not Found</h1>")

    def do_POST(self) -> None:  # noqa: N802 (имя метода задано стандартной библиотекой)
        """Обработка POST-запросов."""

        if self.path == "/api/route":
            self._handle_route()
        elif self.path == "/api/emissions":
            self._handle_emissions()
        elif self.path == "/api/full":
            self._handle_full()
        else:
            self._send_json(404, {"error": "Not found"})

    # Маршруты

    def _handle_route(self) -> None:
        data = self._read_json_body()

        try:
            start_data = data["start"]
            end_data = data["end"]
            start = Point(lat=float(start_data["lat"]), lon=float(start_data["lon"]))
            end = Point(lat=float(end_data["lat"]), lon=float(end_data["lon"]))
        except (KeyError, TypeError, ValueError):
            self._send_json(400, {"error": "Invalid payload for /api/route"})
            return

        route = self.route_client.get_route(start, end)
        response = {
            "start": {"lat": route.start.lat, "lon": route.start.lon},
            "end": {"lat": route.end.lat, "lon": route.end.lon},
            "distance_km": route.distance_km,
        }
        self._send_json(200, response)

    def _handle_emissions(self) -> None:
        data = self._read_json_body()

        try:
            distance_km = float(data["distance_km"])
            transport_type = str(data.get("transport_type", "car"))
        except (KeyError, TypeError, ValueError):
            self._send_json(400, {"error": "Invalid payload for /api/emissions"})
            return

        dummy_start = Point(lat=0.0, lon=0.0)
        dummy_end = Point(lat=0.0, lon=0.0)
        from example import Route  # локальный импорт, чтобы избежать циклов при импорте

        route = Route(start=dummy_start, end=dummy_end, distance_km=distance_km)

        emissions = self.co2_client.get_emissions(route)

        # При желании можно заменить тип транспорта, если он пришёл в запросе
        emissions["transport_type"] = transport_type
        self._send_json(200, emissions)

    def _handle_full(self) -> None:
        data = self._read_json_body()

        try:
            start_data = data["start"]
            end_data = data["end"]
            start = Point(lat=float(start_data["lat"]), lon=float(start_data["lon"]))
            end = Point(lat=float(end_data["lat"]), lon=float(end_data["lon"]))
        except (KeyError, TypeError, ValueError):
            self._send_json(400, {"error": "Invalid payload for /api/full"})
            return

        route = self.route_client.get_route(start, end)
        emissions = self.co2_client.get_emissions(route)

        response = {
            "route": {
                "start": {"lat": route.start.lat, "lon": route.start.lon},
                "end": {"lat": route.end.lat, "lon": route.end.lon},
                "distance_km": route.distance_km,
            },
            "emissions": emissions,
        }
        self._send_json(200, response)

    # Отключим лишние логи, чтобы не засорять вывод
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 (совпадает с BaseHTTPRequestHandler)
        return


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Запустить HTTP-сервер."""

    server_address = (host, port)
    httpd = HTTPServer(server_address, ApiHandler)
    print(f"Serving API on http://{host}:{port}")
    print("Endpoints:")
    print("  POST /api/route")
    print("  POST /api/emissions")
    print("  POST /api/full")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
