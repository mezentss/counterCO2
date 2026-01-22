# 🤖 Интеграция с Telegram API

## 📋 Обзор архитектуры

### 🏗️ **Структура интеграции:**

```
Telegram Bot API ←→ python-telegram-bot ←→ Наше приложение
      ↓                    ↓
   Webhook              Long Polling
```

## 🔧 **Ключевые компоненты интеграции:**

### 1. **python-telegram-bot библиотека**
```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
```

### 2. **Application класс**
```python
application = Application.builder().token(token).build()
```
- Основной класс для управления ботом
- Обрабатывает все входящие сообщения
- Управляет жизненным циклом бота

### 3. **Обработчики (Handlers)**

#### **CommandHandler** - для текстовых команд
```python
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help_command))
```

#### **CallbackQueryHandler** - для кнопок
```python
application.add_handler(CallbackQueryHandler(button_callback))
```
- Обрабатывает нажатия на inline кнопки
- Получает `callback_data` из кнопок

#### **MessageHandler** - для текстовых сообщений
```python
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
```

## 🔄 **Поток обработки сообщений:**

### **1. Пользователь нажимает кнопку:**
```
Пользователь → Telegram → Bot API → python-telegram-bot → button_callback()
```

#### **button_callback() функция:**
```python
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Закрывает анимацию загрузки
    
    action = query.data  # 'calculate', 'route_best', 'compare'
    
    if action == 'calculate':
        user_data[user_id] = {'action': 'calculate', 'step': 1}
        await query.edit_message_text("Введите город отправления:")
```

### **2. Пользователь вводит текст:**
```
Пользователь → Telegram → Bot API → python-telegram-bot → handle_message()
```

#### **handle_message() функция:**
```python
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    
    # Проверяем состояние пользователя
    if user_id not in user_data:
        await update.message.reply_text("Выберите действие на кнопках:")
        return
    
    # Определяем текущее действие
    action = user_data[user_id]['action']
    step = user_data[user_id]['step']
    
    if action == 'calculate':
        await handle_calculate_input(update, user_id, message_text, step)
```

## 📊 **Управление состоянием:**

### **user_data словарь:**
```python
user_data: Dict[int, Dict] = {}

# Пример структуры:
user_data = {
    12345: {  # ID пользователя Telegram
        'action': 'calculate',     # Текущее действие
        'step': 2,               # Текущий шаг
        'city_from': 'Москва',     # Введенные данные
        'city_to': 'СПб'
    }
}
```

### **Пошаговый ввод:**
```python
# Шаг 1: Запрос города отправления
user_data[user_id] = {'action': 'calculate', 'step': 1}
await update.message.reply_text("Введите город отправления:")

# Шаг 2: Запрос города назначения  
user_data[user_id]['city_from'] = message_text
user_data[user_id]['step'] = 2
await update.message.reply_text("Введите город назначения:")

# Шаг 3: Выполнение расчета
user_data[user_id]['city_to'] = message_text
await perform_calculate(update, user_id)
del user_data[user_id]  # Очистка состояния
```

## 🎨 **Inline клавиатуры:**

### **Создание кнопок:**
```python
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Рассчитать выбросы CO₂", callback_data='calculate')],
        [InlineKeyboardButton("🌱 Найти экологичный маршрут", callback_data='route_best')],
        [InlineKeyboardButton("📈 Сравнить маршруты", callback_data='compare')]
    ]
    return InlineKeyboardMarkup(keyboard)
```

### **callback_data:**
- `'calculate'` - запустить расчет выбросов
- `'route_best'` - найти лучший маршрут
- `'compare'` - сравнить два маршрута

## 📤 **Отправка сообщений:**

### **Текстовые сообщения:**
```python
await update.message.reply_text("Привет! 👋", reply_markup=get_main_keyboard())
```

### **Фото с графиками:**
```python
# Генерируем график
chart_bytes = create_transport_comparison(data)

# Отправляем с подписью
await update.message.reply_photo(
    photo=chart_bytes, 
    caption="Результаты расчета", 
    reply_markup=get_main_keyboard()
)
```

### **Редактирование сообщений:**
```python
# Для кнопок - редактируем текущее сообщение
await query.edit_message_text("Введите город отправления:")
```

## 🔄 **Жизненный цикл бота:**

### **Запуск:**
```python
def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)
```

### **Long Polling:**
- Бот постоянно опрашивает Telegram API
- Получает новые сообщения каждые несколько секунд
- Автоматически обрабатывает все типы обновлений

## 🛡️ **Обработка ошибок:**

### **Telegram API ошибки:**
```python
try:
    await query.edit_message_text(text)
except Exception as e:
    # Если редактирование не удалось, отправляем новое сообщение
    await query.message.reply_text(text)
```

### **Ошибки расчетов:**
```python
try:
    distance_km = get_distance(city_from, city_to)
except ValueError as e:
    await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    return
```

## 📈 **Масштабирование и производительность:**

### **Асинхронность:**
- Все функции `async def`
- Параллельная обработка пользователей
- Эффективное использование ресурсов

### **Очистка состояния:**
```python
# После выполнения операции
del user_data[user_id]  # Освобождаем память
```

## 🔐 **Безопасность:**

### **Токен бота:**
```python
token = os.getenv('TELEGRAM_BOT_TOKEN')  # Из переменных окружения
if not token:
    raise ValueError("Необходимо установить TELEGRAM_BOT_TOKEN")
```

### **Фильтрация сообщений:**
```python
filters.TEXT & ~filters.COMMAND  # Только текст, не команды
filters.COMMAND                # Только команды
```

## 🎯 **Ключевые преимущества архитектуры:**

1. **Интерактивность** - кнопки вместо команд
2. **Состояние** - отслеживание прогресса каждого пользователя
3. **Асинхронность** - одновременная работа с множеством пользователей
4. **Отказоустойчивость** - обработка всех ошибок
5. **Масштабируемость** - легкое добавление новых функций

## 📝 **Самые важные функции:**

### **1. button_callback()**
- **Назначение:** Обработка нажатий на inline кнопки
- **Важность:** Основной способ взаимодействия с ботом
- **Логика:** Определяет действие, сохраняет состояние, запрашивает ввод

### **2. handle_message()**
- **Назначение:** Обработка текстовых сообщений пользователей
- **Важность:** Управляет пошаговым вводом данных
- **Логика:** Проверяет состояние, перенаправляет в нужный обработчик

### **3. perform_*() функции**
- **Назначение:** Выполнение основных операций (расчет, поиск, сравнение)
- **Важность:** Основная бизнес-логика приложения
- **Логика:** Интеграция с модулями расчетов, генерация графиков

### **4. get_main_keyboard()**
- **Назначение:** Создание интерфейса пользователя
- **Важность:** Определяет пользовательский опыт
- **Логика:** Генерирует inline кнопки с callback_data

Эта архитектура обеспечивает надежную, масштабируемую и удобную интеграцию с Telegram API! 🚀
