# Telegram-бот для расчета выбросов CO₂

Telegram-бот, который рассчитывает выбросы CO₂ для разных видов транспорта между городами.

## Структура проекта

```
counterCO2/
├── api/                    # API модули
│   ├── co2_calculator.py   # Логика расчета CO₂
│   └── transport_logic.py  # Логика доступности транспорта
├── bot/                    # Telegram-бот (переименован из telegram для избежания конфликтов)
│   └── telegram_bot.py     # Основной файл бота
├── db/                     # Модули базы данных
│   ├── cities_database.py  # База данных координат городов
│   ├── distance_service.py # Сервис расчета расстояний
│   └── emission_calculator.py # Обертка для расчета выбросов
├── utils/                  # Утилитарные модули
│   └── visualizer.py       # Функции генерации графиков
└── requirements.txt        # Зависимости Python
```

## Запуск бота

```bash
python3 -m bot.telegram_bot
```

