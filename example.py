#!/usr/bin/env python3

"""Демonstration entrypoint kept for backward compatibility.

Основной сценарий интеграции с API находится в модуле `api_demo_main`.
Этот файл оставлен для пользователей, которые запускают `example.py`
напрямую. Вся бизнес-логика вынесена в отдельные модули.
"""

from api_demo_main import main


if __name__ == "__main__":
    main()
