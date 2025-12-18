from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Protocol

from api_models import Point, Route


@dataclass
class TransportSegment:
    """Один отрезок маршрута конкретным видом транспорта.

    Это внутренняя модель, согласованная со схемой TransportSegment
    в openapi.json.
    """

    mode: str
    provider: str
    from_location: str
    to_location: str
    distance_km: float
    duration_minutes: int
    departure_datetime: datetime
    arrival_datetime: datetime
    line: Optional[str] = None
    flight_number: Optional[str] = None


@dataclass
class TransportRouteOption:
    """Вариант маршрута между двумя точками через одного провайдера."""

    id: str
    transport_type: str
    provider: str
    segments: List[TransportSegment]
    total_distance_km: float
    total_duration_minutes: int
    currency: Optional[str] = None
    price: Optional[float] = None


@dataclass
class TransportRoutesQuery:
    """Параметры запроса на поиск маршрутов для разных видов транспорта."""

    start: Point
    end: Point
    departure_datetime: Optional[datetime] = None
    allowed_transports: Optional[List[str]] = None
    max_results: int = 10


class TransportProvider(Protocol):
    """Интерфейс адаптера под конкретный внешний транспортный сервис.

    Примеры реализаций: RzdProvider, AviasalesProvider, BusProvider и т.п.
    """

    name: str

    def get_routes(self, query: TransportRoutesQuery) -> List[TransportRouteOption]:  # pragma: no cover - интерфейс
        """Вернуть список маршрутов от данного провайдера.

        Реализация должна сама вызывать внешний API, маппить ответ в
        TransportRouteOption и обрабатывать возможные ошибки.
        """


class TransportRoutesClient:
    """Агрегатор нескольких транспортных провайдеров.

    Этот класс планируется использовать из HTTP-слоя (server.py) и
    из логики расчёта выбросов CO2.
    """

    def __init__(self, providers: List[TransportProvider]):
        self._providers = providers

    def get_routes(self, query: TransportRoutesQuery) -> List[TransportRouteOption]:
        """Запросить маршруты у всех провайдеров и вернуть агрегированный список.

        Пока что это только каркас — без реальных внешних запросов.
        """

        all_routes: List[TransportRouteOption] = []

        for provider in self._providers:
            try:
                provider_routes = provider.get_routes(query)
            except Exception:
                # В реальной реализации здесь должна быть логика логирования
                # и, возможно, деградации сервиса (fallback).
                provider_routes = []

            all_routes.extend(provider_routes)

        # При необходимости можно сортировать по времени, цене, расстоянию и т.п.
        all_routes.sort(key=lambda r: r.total_duration_minutes)

        if query.max_results and query.max_results > 0:
            return all_routes[: query.max_results]
        return all_routes


# Заглушечный провайдер для разработки и тестов
class DummyTransportProvider:
    """Пример провайдера, который не ходит во внешние API, а возвращает заглушки."""

    name = "dummy"

    def get_routes(self, query: TransportRoutesQuery) -> List[TransportRouteOption]:
        # Пример: один фиктивный маршрут "поезд"
        distance_km = 650.0
        duration_minutes = 4 * 60
        now = query.departure_datetime or datetime.utcnow()
        segment = TransportSegment(
            mode="train",
            provider=self.name,
            from_location="Start city",
            to_location="End city",
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            departure_datetime=now,
            arrival_datetime=now,
            line="Dummy Express",
        )

        route_option = TransportRouteOption(
            id="dummy_train_1",
            transport_type="train",
            provider=self.name,
            segments=[segment],
            total_distance_km=distance_km,
            total_duration_minutes=duration_minutes,
            currency="USD",
            price=100.0,
        )

        return [route_option]


def create_default_transport_client() -> TransportRoutesClient:
    """Фабрика для создания клиента с набором провайдеров по умолчанию.

    Сейчас добавлен только DummyTransportProvider для разработки.
    В будущем сюда можно добавить реальные провайдеры (РЖД, Aviasales и др.).
    """

    providers: List[TransportProvider] = [DummyTransportProvider()]
    return TransportRoutesClient(providers=providers)
