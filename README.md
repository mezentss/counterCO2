## CO2 Calculator

Минимальный учебный проект для расчета выбросов CO₂ и демонстрации интеграции с внешними API.

## Telegram-бот

Проект включает Telegram-бота для расчёта выбросов CO₂ между двумя городами. Подробная инструкция по запуску и использованию находится в файле [TELEGRAM_BOT_README.md](TELEGRAM_BOT_README.md).

**Быстрый старт:**
1. Установите зависимости: `pip install -r requirements.txt`
2. Получите токен бота у [@BotFather](https://t.me/BotFather)
3. Установите переменную окружения: `export TELEGRAM_BOT_TOKEN="ваш_токен"`
4. Запустите бота: `python telegram_bot.py`

Бот поддерживает команды `/start`, `/help`, `/calculate` и рассчитывает выбросы CO₂ для самолёта, поезда, автомобиля и автобуса.

Основная бизнес-логика расчета находится в [co2_calculator.py](cci:7://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/co2_calculator.py:0:0-0:0) и использует только стандартную библиотеку Python.

Файл [example.py](cci:7://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:0:0-0:0) демонстрирует концепцию API-клиентов:

- клиент для сервиса маршрутов ([RouteApiClient](cci:2://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:25:0-70:37));
- клиент для сервиса расчета выбросов ([Co2ApiClient](cci:2://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:92:0-165:9));
- переключаемый режим работы: мок / реальные HTTP-запросы.

Тесты находятся в файлах [test_basic.py](cci:7://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/test_basic.py:0:0-0:0) и [test_full_system.py](cci:7://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/test_full_system.py:0:0-0:0).

---

## Зависимости

Проект использует стандартную библиотеку Python и не требует внешних зависимостей для работы основной логики.

Опционально для разработки и тестирования могут использоваться:

- pytest
- black
- flake8

См. [requirements.txt](cci:7://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/requirements.txt:0:0-0:0) для примечаний.

---

## Запуск базового примера CO₂ (без API)

Пример базового использования калькулятора CO₂ без внешних API (если предусмотрен отдельный интерфейс) см. в [co2_calculator.py](cci:7://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/co2_calculator.py:0:0-0:0) и соответствующих тестах.

---

## Пример интеграции с API ([example.py](cci:7://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:0:0-0:0))

[example.py](cci:7://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:0:0-0:0) демонстрирует сценарий:

1. Выбор двух точек на карте (заглушка [select_points_on_map](cci:1://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:168:0-180:29)).
2. Получение маршрута между точками через [RouteApiClient](cci:2://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:25:0-70:37).
3. Получение оценки выбросов CO₂ по маршруту через [Co2ApiClient](cci:2://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:92:0-165:9).
4. Вывод результатов в консоль.

Клиенты реализованы так, чтобы:

- в режиме по умолчанию работать как моки (без реальных HTTP-запросов);
- при необходимости переключаться на реальные HTTP-запросы через `urllib`, используя переменные окружения.

---

## Переменные окружения для API

[example.py](cci:7://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:0:0-0:0) читает конфигурацию API из переменных окружения.

### Режим работы HTTP

- `USE_REAL_HTTP`  
  - не задано или значение отлично от `"1"` — включен мок-режим:
    - HTTP-запросы не отправляются;
    - параметры запроса выводятся в консоль;
    - ответ генерируется локально в коде;
  - `"1"` — выполняются реальные HTTP-запросы через стандартную библиотеку (`urllib`).

### Клиент маршрутов ([RouteApiClient](cci:2://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:25:0-70:37))

- `ROUTE_API_BASE_URL`  
  - базовый URL сервиса маршрутов;  
  - значение по умолчанию:  
    `https://api.routes.local/v1`
- `ROUTE_API_KEY`  
  - опциональный ключ доступа;  
  - если установлен, добавляется заголовок:  
    `Authorization: Bearer <ключ>`

### Клиент расчета CO₂ ([Co2ApiClient](cci:2://file:///Users/sofya.mezentseva/PycharmProjects/counterCO2/example.py:92:0-165:9))

- `CO2_API_BASE_URL`  
  - базовый URL сервиса расчета выбросов;  
  - значение по умолчанию:  
    `https://api.co2.local/v1`
- `CO2_API_KEY`  
  - опциональный ключ доступа;  
  - если установлен, добавляется заголовок:  
    `Authorization: Bearer <ключ>`

---

## Примеры запуска

### 1. Мок-режим (по умолчанию, без сетевых запросов)

```bash
python example.py
В этом режиме:

USE_REAL_HTTP не установлен;
HTTP-запросы не выполняются;
в консоль выводятся параметры «запросов» и результаты, рассчитанные локально.
2. Мок-режим с пользовательскими базовыми URL
bash
export ROUTE_API_BASE_URL="https://api.my-routes.com/v1"
export CO2_API_BASE_URL="https://api.my-co2.com/v1"

python example.py
Используются указанные URL, но режим остается моковым (запросы не ходят в сеть).

3. Реальные HTTP-запросы
bash
export USE_REAL_HTTP=1

export ROUTE_API_BASE_URL="https://real-routes.example.com/v1"
export ROUTE_API_KEY="REAL_ROUTES_KEY"

export CO2_API_BASE_URL="https://real-co2.example.com/v1"
export CO2_API_KEY="REAL_CO2_KEY"

python example.py
В этом режиме:

клиенты формируют HTTP-запросы методом POST с JSON-телом;
выполняется запрос через urllib.request.urlopen;
ответ ожидается в формате JSON и парсится через json.loads;
при ошибках уровня HTTP (4xx/5xx) выбрасывается RuntimeError с кодом и текстом ошибки сервера.
Поведение при ошибках
Ошибки HTTP (например, 400, 401, 500) приводят к выбрасыванию RuntimeError с описанием вида:
RouteApiClient HTTP error: <код> <reason> или
Co2ApiClient HTTP error: <код> <reason>.
При пустом теле ответа в режиме реальных HTTP-клиенты возвращают пустой словарь {}.