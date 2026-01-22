#!/usr/bin/env python3
"""
Telegram-бот для расчёта выбросов CO2 между двумя городами.
"""

import os
import logging
from typing import Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

from distance_service import get_distance
from emission_calculator import calculate_emissions, TransportUnavailableError

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
WAITING_FOR_CITY_FROM, WAITING_FOR_CITY_TO = range(2)

# Словарь для хранения данных пользователей
user_data: Dict[int, Dict] = {}

# Эмодзи для видов транспорта
TRANSPORT_EMOJIS = {
    'plane': '✈️',
    'train': '🚂',
    'car': '🚗',
    'bus': '🚌'
}

# Русские названия видов транспорта
TRANSPORT_NAMES = {
    'plane': 'Самолёт',
    'train': 'Поезд',
    'car': 'Автомобиль',
    'bus': 'Автобус'
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    welcome_message = (
        "Привет! 👋\n\n"
        "Я бот для расчёта выбросов CO2 при поездке между двумя городами.\n\n"
        "Доступные виды транспорта:\n"
        "✈️ Самолёт\n"
        "🚂 Поезд\n"
        "🚗 Автомобиль\n"
        "🚌 Автобус\n\n"
        "Для начала расчёта нажмите /calculate"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    help_message = (
        "Бот рассчитывает выбросы CO2 для поездки между двумя городами.\n\n"
        "Доступные виды транспорта:\n"
        "✈️ Самолёт\n"
        "🚂 Поезд\n"
        "🚗 Автомобиль\n"
        "🚌 Автобус\n\n"
        "Для начала расчёта нажмите /calculate"
    )
    await update.message.reply_text(help_message)


async def calculate_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса расчёта - запрос города отправления."""
    user_id = update.effective_user.id
    user_data[user_id] = {}
    
    await update.message.reply_text(
        "Введите город отправления:"
    )
    return WAITING_FOR_CITY_FROM


async def receive_city_from(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение города отправления и запрос города назначения."""
    user_id = update.effective_user.id
    city_from = update.message.text.strip()
    
    user_data[user_id]['city_from'] = city_from
    
    await update.message.reply_text(
        f"Город отправления: {city_from}\n\n"
        "Введите город назначения:"
    )
    return WAITING_FOR_CITY_TO


async def receive_city_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение города назначения и выполнение расчёта."""
    user_id = update.effective_user.id
    city_to = update.message.text.strip()
    city_from = user_data[user_id].get('city_from')
    
    if not city_from:
        await update.message.reply_text(
            "Ошибка: не найден город отправления. Начните заново с /calculate"
        )
        return ConversationHandler.END
    
    user_data[user_id]['city_to'] = city_to
    
    # Выполняем расчёт
    try:
        await update.message.reply_text("Выполняю расчёт...")
        
        # Получаем расстояние
        try:
            distance_km = get_distance(city_from, city_to)
        except ValueError as e:
            await update.message.reply_text(f"Ошибка: {str(e)}")
            return ConversationHandler.END
        
        # Рассчитываем выбросы для каждого вида транспорта
        results = []
        transport_types = ['plane', 'train', 'car', 'bus']
        
        for transport_type in transport_types:
            emoji = TRANSPORT_EMOJIS.get(transport_type, '')
            name = TRANSPORT_NAMES.get(transport_type, transport_type)
            
            try:
                emissions = calculate_emissions(
                    transport_type, 
                    distance_km,
                    city_from,
                    city_to
                )
                results.append(
                    f"{emoji} {name}: {emissions:.2f} кг CO₂"
                )
            except TransportUnavailableError:
                results.append(
                    f"{emoji} {name}: добраться данным видом транспорта невозможно."
                )
            except Exception as e:
                logger.error(f"Ошибка при расчёте для {transport_type}: {e}")
                results.append(
                    f"{emoji} {name}: добраться данным видом транспорта невозможно."
                )
        
        # Формируем итоговое сообщение
        result_message = (
            f"📊 Результаты расчёта выбросов CO₂\n\n"
            f"📍 Маршрут: {city_from} → {city_to}\n"
            f"📏 Расстояние: {distance_km:.1f} км\n\n"
            f"Выбросы CO₂ по видам транспорта:\n\n"
        )
        result_message += "\n".join(results)
        
        await update.message.reply_text(result_message)
        
    except Exception as e:
        logger.error(f"Ошибка при расчёте: {e}", exc_info=True)
        await update.message.reply_text(
            f"Произошла ошибка при расчёте: {str(e)}\n"
            "Попробуйте ещё раз с командой /calculate"
        )
    
    # Очищаем данные пользователя
    if user_id in user_data:
        del user_data[user_id]
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена текущей операции."""
    user_id = update.effective_user.id
    if user_id in user_data:
        del user_data[user_id]
    
    await update.message.reply_text(
        "Операция отменена. Для начала нового расчёта используйте /calculate"
    )
    return ConversationHandler.END


def main() -> None:
    """Запуск бота."""
    # Получаем токен из переменной окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError(
            "Необходимо установить переменную окружения TELEGRAM_BOT_TOKEN. "
            "Получите токен у @BotFather в Telegram"
        )
    
    # Создаём приложение
    application = Application.builder().token(token).build()
    
    # Создаём ConversationHandler для процесса расчёта
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('calculate', calculate_start)],
        states={
            WAITING_FOR_CITY_FROM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_city_from),
                CommandHandler('cancel', cancel),
            ],
            WAITING_FOR_CITY_TO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_city_to),
                CommandHandler('cancel', cancel),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(conv_handler)
    
    # Запускаем бота
    logger.info("Бот запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
