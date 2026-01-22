#!/usr/bin/env python3
"""
Telegram bot for CO2 emission calculations between cities.
"""

import os
import logging
from typing import Dict, List, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

from db.distance_service import get_distance
from db.emission_calculator import calculate_emissions, TransportUnavailableError
from utils.visualizer import create_transport_comparison, create_comparison_pie_chart, create_best_route_visualization

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TRANSPORT_NAMES = {
    'plane': 'Самолёт',
    'train': 'Поезд',
    'car': 'Автомобиль',
    'bus': 'Автобус'
}

# Словарь для хранения состояния пользователей
user_data: Dict[int, Dict] = {}


def get_main_keyboard():
    """Создает главную клавиатуру с кнопками команд."""
    keyboard = [
        [InlineKeyboardButton("📊 Рассчитать выбросы CO₂", callback_data='calculate')],
        [InlineKeyboardButton("🌱 Найти экологичный маршрут", callback_data='route_best')],
        [InlineKeyboardButton("📈 Сравнить маршруты", callback_data='compare')]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    welcome_message = (
        "Привет! 👋\n\n"
        "Я бот для расчёта выбросов CO₂ при поездке между двумя городами.\n\n"
        "Выберите действие на кнопках ниже:"
    )
    await update.message.reply_text(welcome_message, reply_markup=get_main_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, show_keyboard: bool = True) -> None:
    """Обработчик команды /help."""
    help_message = (
        "Справка по командам бота:\n\n"
        "📊 Рассчитать выбросы CO₂ - расчёт для всех видов транспорта\n"
        "🌱 Найти экологичный маршрут - найти самый экологичный вариант\n"
        "📈 Сравнить маршруты - сравнить два маршрута с графиками\n\n"
        "Доступные виды транспорта:\n"
        "✈️ Самолёт, 🚂 Поезд, 🚗 Автомобиль, 🚌 Автобус\n\n"
        "Выберите действие на кнопках ниже:"
    )
    if show_keyboard:
        await update.message.reply_text(help_message, reply_markup=get_main_keyboard())
    else:
        await update.message.reply_text(help_message)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    action = query.data
    
    # Для остальных действий редактируем сообщение
    if action == 'calculate':
        user_data[user_id] = {'action': 'calculate', 'step': 1}
        try:
            await query.edit_message_text(
                "📊 Расчёт выбросов CO₂\n\n"
                "Введите город отправления:"
            )
        except Exception:
            await query.message.reply_text(
                "📊 Расчёт выбросов CO₂\n\n"
                "Введите город отправления:"
            )
    elif action == 'route_best':
        user_data[user_id] = {'action': 'route_best', 'step': 1}
        try:
            await query.edit_message_text(
                "🌱 Поиск экологичного маршрута\n\n"
                "Введите город отправления:"
            )
        except Exception:
            await query.message.reply_text(
                "🌱 Поиск экологичного маршрута\n\n"
                "Введите город отправления:"
            )
    elif action == 'compare':
        user_data[user_id] = {'action': 'compare', 'step': 1}
        try:
            await query.edit_message_text(
                "📈 Сравнение маршрутов\n\n"
                "Введите город отправления для первого маршрута:"
            )
        except Exception:
            await query.message.reply_text(
                "📈 Сравнение маршрутов\n\n"
                "Введите город отправления для первого маршрута:"
            )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений от пользователя."""
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    
    if user_id not in user_data:
        await update.message.reply_text(
            "Пожалуйста, выберите действие на кнопках:",
            reply_markup=get_main_keyboard()
        )
        return
    
    user_action = user_data[user_id]
    action = user_action['action']
    step = user_action['step']
    
    if action == 'calculate':
        await handle_calculate_input(update, user_id, message_text, step)
    elif action == 'route_best':
        await handle_route_best_input(update, user_id, message_text, step)
    elif action == 'compare':
        await handle_compare_input(update, user_id, message_text, step)


async def handle_calculate_input(update: Update, user_id: int, message_text: str, step: int) -> None:
    """Обработка ввода для команды calculate."""
    if step == 1:
        user_data[user_id]['city_from'] = message_text
        user_data[user_id]['step'] = 2
        await update.message.reply_text(f"Город отправления: {message_text}\n\nВведите город назначения:")
    elif step == 2:
        user_data[user_id]['city_to'] = message_text
        await perform_calculate(update, user_id)


async def handle_route_best_input(update: Update, user_id: int, message_text: str, step: int) -> None:
    """Обработка ввода для команды route_best."""
    if step == 1:
        user_data[user_id]['city_from'] = message_text
        user_data[user_id]['step'] = 2
        await update.message.reply_text(f"Город отправления: {message_text}\n\nВведите город назначения:")
    elif step == 2:
        user_data[user_id]['city_to'] = message_text
        await perform_route_best(update, user_id)


async def handle_compare_input(update: Update, user_id: int, message_text: str, step: int) -> None:
    """Обработка ввода для команды compare."""
    if step == 1:
        user_data[user_id]['city1_from'] = message_text
        user_data[user_id]['step'] = 2
        await update.message.reply_text(f"Первый маршрут, город отправления: {message_text}\n\nВведите город назначения для первого маршрута:")
    elif step == 2:
        user_data[user_id]['city1_to'] = message_text
        user_data[user_id]['step'] = 3
        await update.message.reply_text(f"Первый маршрут: {user_data[user_id]['city1_from']} → {message_text}\n\nВведите город отправления для второго маршрута:")
    elif step == 3:
        user_data[user_id]['city2_from'] = message_text
        user_data[user_id]['step'] = 4
        await update.message.reply_text(f"Второй маршрут, город отправления: {message_text}\n\nВведите город назначения для второго маршрута:")
    elif step == 4:
        user_data[user_id]['city2_to'] = message_text
        await perform_compare(update, user_id)


async def perform_calculate(update: Update, user_id: int) -> None:
    """Выполнение расчета выбросов CO2."""
    try:
        city_from = user_data[user_id]['city_from']
        city_to = user_data[user_id]['city_to']
        
        await update.message.reply_text("🔄 Выполняю расчёт...")
        
        distance_km = get_distance(city_from, city_to)
        
        results = []
        transport_types = ['plane', 'train', 'car', 'bus']
        
        for transport_type in transport_types:
            name = TRANSPORT_NAMES.get(transport_type, transport_type)
            
            try:
                emissions = calculate_emissions(
                    transport_type, 
                    distance_km,
                    city_from,
                    city_to
                )
                results.append(f"{name}: {emissions:.2f} кг CO₂")
            except TransportUnavailableError:
                results.append(f"{name}: недоступен для данного маршрута")
            except Exception as e:
                logger.error(f"Error calculating for {transport_type}: {e}")
                results.append(f"{name}: ошибка расчёта")
        
        result_message = (
            f"📊 Результаты расчёта выбросов CO₂\n\n"
            f"📍 Маршрут: {city_from} → {city_to}\n"
            f"📏 Расстояние: {distance_km:.1f} км\n\n"
            f"Выбросы CO₂ по видам транспорта:\n\n"
        )
        result_message += "\n".join(results)
        
        del user_data[user_id]
        await update.message.reply_text(result_message, reply_markup=get_main_keyboard())
        
    except ValueError as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    except Exception as e:
        logger.error(f"Error in calculate: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при расчёте. Попробуйте ещё раз.")


async def perform_route_best(update: Update, user_id: int) -> None:
    """Поиск самого экологичного маршрута."""
    try:
        city_from = user_data[user_id]['city_from']
        city_to = user_data[user_id]['city_to']
        
        await update.message.reply_text("🔄 Ищу самый экологичный маршрут...")
        
        distance_km = get_distance(city_from, city_to)
        
        transport_data = []
        transport_types = ['plane', 'train', 'car', 'bus']
        
        for transport_type in transport_types:
            name = TRANSPORT_NAMES.get(transport_type, transport_type)
            
            try:
                emissions = calculate_emissions(
                    transport_type, 
                    distance_km,
                    city_from,
                    city_to
                )
                transport_data.append({
                    'type': transport_type,
                    'name': name,
                    'emissions': emissions
                })
            except TransportUnavailableError:
                continue
            except Exception:
                continue
        
        if not transport_data:
            await update.message.reply_text("❌ Нет доступных видов транспорта для данного маршрута")
            return
        
        best_transport = min(transport_data, key=lambda x: x['emissions'])
        worst_transport = max(transport_data, key=lambda x: x['emissions'])
        
        savings_percent = ((worst_transport['emissions'] - best_transport['emissions']) / 
                          worst_transport['emissions']) * 100
        
        viz_data = {
            'transport': [item['type'] for item in transport_data],
            'emissions': [item['emissions'] for item in transport_data]
        }
        
        chart_bytes = create_best_route_visualization(best_transport['type'], viz_data)
        
        result_message = (
            f"🌱 Самый экологичный маршрут: {city_from} → {city_to}\n\n"
            f"✅ Лучший вид транспорта: {best_transport['name']}\n"
            f"💨 Выбросы CO₂: {best_transport['emissions']:.2f} кг\n"
            f"💰 Экономия: {savings_percent:.1f}% относительно худшего варианта\n"
            f"📏 Расстояние: {distance_km:.1f} км"
        )
        
        del user_data[user_id]
        await update.message.reply_photo(photo=chart_bytes, caption=result_message, reply_markup=get_main_keyboard())
        
    except ValueError as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    except Exception as e:
        logger.error(f"Error in route_best: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при поиске маршрута. Попробуйте ещё раз.")


async def perform_compare(update: Update, user_id: int) -> None:
    """Сравнение двух маршрутов."""
    try:
        city1_from = user_data[user_id]['city1_from']
        city1_to = user_data[user_id]['city1_to']
        city2_from = user_data[user_id]['city2_from']
        city2_to = user_data[user_id]['city2_to']
        
        await update.message.reply_text("🔄 Сравниваю маршруты...")
        
        # Calculate for route 1
        distance1_km = get_distance(city1_from, city1_to)
        route1_data = {'transport': [], 'emissions': []}
        
        for transport_type in ['plane', 'train', 'car', 'bus']:
            try:
                emissions = calculate_emissions(transport_type, distance1_km, city1_from, city1_to)
                route1_data['transport'].append(transport_type)
                route1_data['emissions'].append(emissions)
            except:
                continue
        
        # Calculate for route 2
        distance2_km = get_distance(city2_from, city2_to)
        route2_data = {'transport': [], 'emissions': []}
        
        for transport_type in ['plane', 'train', 'car', 'bus']:
            try:
                emissions = calculate_emissions(transport_type, distance2_km, city2_from, city2_to)
                route2_data['transport'].append(transport_type)
                route2_data['emissions'].append(emissions)
            except:
                continue
        
        if not route1_data['transport'] or not route2_data['transport']:
            await update.message.reply_text("❌ Не удалось рассчитать выбросы для одного из маршрутов")
            return
        
        # Find best transport for each route
        best_route1_idx = route1_data['emissions'].index(min(route1_data['emissions']))
        best_route2_idx = route2_data['emissions'].index(min(route2_data['emissions']))
        
        # Create comparison chart data
        comparison_data = {
            'transport': [],
            'emissions': []
        }
        
        # Add best transports to comparison
        comparison_data['transport'].append(f"Маршрут 1: {TRANSPORT_NAMES.get(route1_data['transport'][best_route1_idx], route1_data['transport'][best_route1_idx])}")
        comparison_data['emissions'].append(route1_data['emissions'][best_route1_idx])
        
        comparison_data['transport'].append(f"Маршрут 2: {TRANSPORT_NAMES.get(route2_data['transport'][best_route2_idx], route2_data['transport'][best_route2_idx])}")
        comparison_data['emissions'].append(route2_data['emissions'][best_route2_idx])
        
        # Generate comparison chart
        chart_bytes = create_transport_comparison(comparison_data)
        
        total1 = sum(route1_data['emissions'])
        total2 = sum(route2_data['emissions'])
        
        result_message = (
            f"📈 Сравнение маршрутов:\n\n"
            f"🛣️ Маршрут 1: {city1_from} → {city1_to}\n"
            f"📏 Расстояние: {distance1_km:.1f} км\n"
            f"✅ Лучший транспорт: {TRANSPORT_NAMES.get(route1_data['transport'][best_route1_idx])}\n"
            f"💨 Минимальные выбросы: {route1_data['emissions'][best_route1_idx]:.2f} кг CO₂\n\n"
            f"🛣️ Маршрут 2: {city2_from} → {city2_to}\n"
            f"📏 Расстояние: {distance2_km:.1f} км\n"
            f"✅ Лучший транспорт: {TRANSPORT_NAMES.get(route2_data['transport'][best_route2_idx])}\n"
            f"💨 Минимальные выбросы: {route2_data['emissions'][best_route2_idx]:.2f} кг CO₂\n\n"
        )
        
        if total1 < total2:
            result_message += f"🌱 Маршрут 1 экологичнее на {((total2-total1)/total2)*100:.1f}%"
        elif total2 < total1:
            result_message += f"🌱 Маршрут 2 экологичнее на {((total1-total2)/total1)*100:.1f}%"
        else:
            result_message += "⚖️ Маршруты имеют равные выбросы CO₂"
        
        del user_data[user_id]
        await update.message.reply_photo(photo=chart_bytes, caption=result_message, reply_markup=get_main_keyboard())
        
    except ValueError as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    except Exception as e:
        logger.error(f"Error in compare: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при сравнении. Попробуйте ещё раз.")


def main() -> None:
    """Запуск бота."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError(
            "Необходимо установить переменную окружения TELEGRAM_BOT_TOKEN. "
            "Получите токен у @BotFather в Telegram"
        )
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
