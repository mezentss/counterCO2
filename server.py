#!/usr/bin/env python3
"""FastAPI-сервер с API для расчёта маршрута и выбросов CO2.

Сервер предоставляет несколько эндпоинтов:

- GET /api/integrations - список доступных источников интеграции
- POST /api/integrations/select - выбор источника интеграции
- POST /api/route - расчёт маршрута
- POST /api/emissions - расчёт выбросов CO2
- POST /api/full - комбинированный запрос (маршрут + CO2)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import uvicorn

from api_models import Point
from integration_manager import integration_manager

app = FastAPI(
    title="CO2 Calculator API",
    description="API для расчёта выбросов CO2 с поддержкой нескольких источников интеграции",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Создаем директорию для статических файлов, если её нет
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class IntegrationModel(BaseModel):
    name: str

class RouteRequest(BaseModel):
    start: Point
    end: Point

class EmissionsRequest(BaseModel):
    distance_km: float
    transport_type: str = "car"

@app.get("/api/integrations", response_model=List[str])
async def list_integrations():
    """Получить список доступных источников интеграции."""
    return integration_manager.list_integrations()

@app.post("/api/integrations/select")
async def select_integration(integration: IntegrationModel):
    """Выбрать текущий источник интеграции."""
    success = integration_manager.set_current_integration(integration.name)
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found")
    return {"status": "success", "selected": integration.name}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница с веб-интерфейсом."""
    return """
    <!doctype html>
    <html>
    <head>
        <title>CO2 Calculator</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>CO2 Calculator</h1>
            <div class="card mt-4">
                <div class="card-header">
                    <h5>Источник интеграции</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <label class="form-label">Выберите источник данных:</label>
                        <select id="integrationSelect" class="form-select">
                            <option value="">Загрузка...</option>
                        </select>
                    </div>
                    <button id="selectIntegration" class="btn btn-primary">Выбрать</button>
                    <div id="status" class="mt-3"></div>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h5>Текущий источник</h5>
                </div>
                <div class="card-body">
                    <p id="currentIntegration">Не выбран</p>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h5>Документация API</h5>
                </div>
                <div class="card-body">
                    <p>Доступные эндпоинты:</p>
                    <ul>
                        <li><code>GET /api/integrations</code> - список источников</li>
                        <li><code>POST /api/integrations/select</code> - выбор источника</li>
                        <li><code>POST /api/route</code> - расчёт маршрута</li>
                        <li><code>POST /api/emissions</code> - расчёт выбросов</li>
                        <li><code>POST /api/full</code> - полный запрос</li>
                    </ul>
                    <p>Документация по API: <a href="/docs" target="_blank">Swagger UI</a></p>
                </div>
            </div>
        </div>
        
        <script>
            // Функция для обновления отображения текущего источника
            function updateCurrentIntegration() {
                fetch('/api/integrations')
                    .then(response => response.json())
                    .then(integrations => {
                        const current = integrations[0]; // Источник по умолчанию первый
                        document.getElementById('currentIntegration').textContent = current || 'Не выбран';
                    });
            }
            
            // Загрузка доступных источников
            fetch('/api/integrations')
                .then(response => response.json())
                .then(integrations => {
                    const select = document.getElementById('integrationSelect');
                    select.innerHTML = '';
                    
                    integrations.forEach(integration => {
                        const option = document.createElement('option');
                        option.value = integration;
                        option.textContent = integration;
                        select.appendChild(option);
                    });
                    
                    // Обновляем отображение текущего источника
                    updateCurrentIntegration();
                });

            // Обработка выбора источника
            document.getElementById('selectIntegration').addEventListener('click', () => {
                const select = document.getElementById('integrationSelect');
                const integration = select.value;
                const statusDiv = document.getElementById('status');
                
                if (!integration) {
                    statusDiv.innerHTML = '<div class="alert alert-warning">Выберите источник интеграции</div>';
                    return;
                }
                
                statusDiv.innerHTML = '<div class="alert alert-info">Переключение источника...</div>';
                
                fetch('/api/integrations/select', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name: integration })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Ошибка при переключении источника');
                    }
                    return response.json();
                })
                .then(data => {
                    statusDiv.innerHTML = `<div class="alert alert-success">Выбран источник: ${data.selected}</div>`;
                    document.getElementById('currentIntegration').textContent = data.selected;
                    
                    // Очищаем статус через 3 секунды
                    setTimeout(() => {
                        statusDiv.innerHTML = '';
                    }, 3000);
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                    statusDiv.innerHTML = `<div class="alert alert-danger">Ошибка: ${error.message}</div>`;
                });
            });
        </script>
    </body>
    </html>
    """

@app.post("/api/route")
async def get_route(route_request: RouteRequest):
    """Получить маршрут между двумя точками."""
    try:
        print(f"Getting route from {route_request.start} to {route_request.end}")
        route_client = integration_manager.get_route_client()
        print(f"Using route client: {route_client.__class__.__name__}")
        route = route_client.get_route(route_request.start, route_request.end)
        print(f"Route received: {route}")
        
        # Handle both Pydantic v1 and v2
        if hasattr(route, 'model_dump'):  # Pydantic v2
            result = route.model_dump()
        else:  # Pydantic v1
            result = route.dict() if hasattr(route, 'dict') else route.__dict__
            
        print(f"Returning: {result}")
        return result
    except Exception as e:
        import traceback
        error_details = f"Error in get_route: {str(e)}\n{traceback.format_exc()}"
        print(error_details, file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/emissions")
async def get_emissions(emissions_request: EmissionsRequest):
    """Рассчитать выбросы CO2."""
    try:
        from api_models import Route
        dummy_route = Route(
            start=Point(lat=0, lon=0),
            end=Point(lat=0, lon=0),
            distance_km=emissions_request.distance_km
        )
        result = integration_manager.get_co2_client().get_emissions(
            dummy_route,
            transport_type=emissions_request.transport_type
        )
        return result
    except Exception as e:
        import traceback
        error_details = f"Error in get_emissions: {str(e)}\n{traceback.format_exc()}"
        print(error_details, file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/full")
async def get_full_route(route_request: RouteRequest):
    """Полный запрос: маршрут + выбросы CO2."""
    try:
        # Получаем маршрут
        route = integration_manager.get_route_client().get_route(
            route_request.start, 
            route_request.end
        )
        
        # Рассчитываем выбросы
        emissions = integration_manager.get_co2_client().get_emissions(route)
        
        # Handle both Pydantic v1 and v2
        def to_dict(obj):
            if hasattr(obj, 'model_dump'):  # Pydantic v2
                return obj.model_dump()
            return obj.dict() if hasattr(obj, 'dict') else obj.__dict__
        
        return {
            "route": to_dict(route),
            "emissions": emissions
        }
    except Exception as e:
        import traceback
        error_details = f"Error in get_full_route: {str(e)}\n{traceback.format_exc()}"
        print(error_details, file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Запустить HTTP-сервер."""
    print(f"Запуск сервера на http://{host}:{port}")
    print("Нажмите Ctrl+C для остановки")
    uvicorn.run("server:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    run_server()
