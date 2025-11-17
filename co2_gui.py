#!/usr/bin/env python3
"""
Графический интерфейс для CO2 калькулятора.
Позволяет пользователю выбирать города с автодополнением и получать расчет выбросов CO2.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional, List

from cities_database import search_cities, get_city_info
from transport_logic import TransportAvailability
from co2_calculator import CO2Calculator


class AutocompleteEntry(tk.Frame):
    """
    Виджет поля ввода с автодополнением для выбора городов.
    """
    
    def __init__(self, parent, placeholder="Введите название города...", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.placeholder = placeholder
        self.selected_city = None
        self.suggestions = []
        
        # Создаем основные элементы
        self._create_widgets()
        self._bind_events()
    
    def _create_widgets(self):
        """Создание виджетов."""
        # Поле ввода
        self.entry = tk.Entry(self, font=('Arial', 12), width=40)
        self.entry.pack(fill='x', padx=5, pady=2)
        
        # Список предложений
        self.suggestions_frame = tk.Frame(self)
        self.suggestions_listbox = tk.Listbox(
            self.suggestions_frame, 
            height=6, 
            font=('Arial', 10),
            selectmode='single'
        )
        
        # Скроллбар для списка
        scrollbar = tk.Scrollbar(self.suggestions_frame, orient='vertical')
        self.suggestions_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.suggestions_listbox.yview)
        
        self.suggestions_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Изначально список скрыт
        self._hide_suggestions()
        
        # Placeholder
        self._show_placeholder()
    
    def _bind_events(self):
        """Привязка событий."""
        self.entry.bind('<KeyRelease>', self._on_key_release)
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<Return>', self._on_enter)
        
        self.suggestions_listbox.bind('<Double-Button-1>', self._on_suggestion_select)
        self.suggestions_listbox.bind('<Return>', self._on_suggestion_select)
    
    def _show_placeholder(self):
        """Показать placeholder текст."""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg='gray')
    
    def _hide_placeholder(self):
        """Скрыть placeholder текст."""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg='black')
    
    def _on_focus_in(self, event):
        """Обработка получения фокуса."""
        self._hide_placeholder()
    
    def _on_focus_out(self, event):
        """Обработка потери фокуса."""
        # Задержка для обработки выбора из списка
        self.after(100, self._delayed_focus_out)
    
    def _delayed_focus_out(self):
        """Отложенная обработка потери фокуса."""
        if not self.entry.get():
            self._show_placeholder()
        self._hide_suggestions()
    
    def _on_key_release(self, event):
        """Обработка ввода текста."""
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Tab'):
            return
        
        query = self.entry.get()
        
        # Игнорируем placeholder
        if query == self.placeholder:
            return
        
        if len(query) >= 2:
            self._update_suggestions(query)
        else:
            self._hide_suggestions()
            self.selected_city = None
    
    def _on_enter(self, event):
        """Обработка нажатия Enter."""
        if self.suggestions_listbox.winfo_viewable():
            selection = self.suggestions_listbox.curselection()
            if selection:
                self._select_suggestion(selection[0])
            else:
                # Выбираем первый вариант, если есть
                if self.suggestions:
                    self._select_suggestion(0)
        self._hide_suggestions()
    
    def _update_suggestions(self, query):
        """Обновление списка предложений."""
        self.suggestions = search_cities(query, limit=8)
        
        if self.suggestions:
            self._show_suggestions()
            
            # Очищаем и заполняем список
            self.suggestions_listbox.delete(0, tk.END)
            for city in self.suggestions:
                self.suggestions_listbox.insert(tk.END, city['display_name'])
        else:
            self._hide_suggestions()
    
    def _show_suggestions(self):
        """Показать список предложений."""
        if not self.suggestions_frame.winfo_viewable():
            self.suggestions_frame.pack(fill='x', padx=5, pady=(0, 5))
    
    def _hide_suggestions(self):
        """Скрыть список предложений."""
        if self.suggestions_frame.winfo_viewable():
            self.suggestions_frame.pack_forget()
    
    def _on_suggestion_select(self, event):
        """Обработка выбора предложения."""
        selection = self.suggestions_listbox.curselection()
        if selection:
            self._select_suggestion(selection[0])
    
    def _select_suggestion(self, index):
        """Выбор предложения по индексу."""
        if 0 <= index < len(self.suggestions):
            city = self.suggestions[index]
            self.selected_city = city
            
            # Обновляем текст в поле ввода
            self.entry.delete(0, tk.END)
            self.entry.insert(0, city['name'])
            self.entry.config(fg='black')
            
            self._hide_suggestions()
    
    def get_selected_city(self):
        """Получить выбранный город."""
        return self.selected_city
    
    def clear(self):
        """Очистить поле ввода."""
        self.entry.delete(0, tk.END)
        self.selected_city = None
        self._hide_suggestions()
        self._show_placeholder()


class CO2CalculatorGUI:
    """
    Основное GUI приложение для расчета выбросов CO2.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CO2 Калькулятор - Расчет выбросов при путешествиях")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Инициализация компонентов
        self.transport_logic = TransportAvailability()
        self.calculator = CO2Calculator()
        
        # Переменные
        self.api_key_var = tk.StringVar()
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """Создание всех виджетов интерфейса."""
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="🌍 CO2 Калькулятор", 
            font=('Arial', 18, 'bold'),
            fg='#2E8B57'
        )
        title_label.pack(pady=10)
        
        # Описание
        desc_label = tk.Label(
            self.root,
            text="Рассчитайте выбросы CO2 для путешествий между городами",
            font=('Arial', 11),
            fg='gray'
        )
        desc_label.pack(pady=(0, 20))
        
        # Фрейм для ввода городов
        cities_frame = tk.LabelFrame(self.root, text="Выбор маршрута", font=('Arial', 12, 'bold'))
        cities_frame.pack(fill='x', padx=20, pady=10)
        
        # Город отправления
        tk.Label(cities_frame, text="Откуда:", font=('Arial', 11)).pack(anchor='w', padx=10, pady=(10, 5))
        self.from_city_entry = AutocompleteEntry(cities_frame, "Введите город отправления...")
        self.from_city_entry.pack(fill='x', padx=10, pady=(0, 10))
        
        # Город назначения
        tk.Label(cities_frame, text="Куда:", font=('Arial', 11)).pack(anchor='w', padx=10, pady=(10, 5))
        self.to_city_entry = AutocompleteEntry(cities_frame, "Введите город назначения...")
        self.to_city_entry.pack(fill='x', padx=10, pady=(0, 10))
        
        # Фрейм для API ключа
        api_frame = tk.LabelFrame(self.root, text="Настройки API (опционально)", font=('Arial', 12))
        api_frame.pack(fill='x', padx=20, pady=10)
        
        api_info = tk.Label(
            api_frame,
            text="API ключ OpenRouteService для точных маршрутов (получить на openrouteservice.org)",
            font=('Arial', 9),
            fg='gray'
        )
        api_info.pack(anchor='w', padx=10, pady=(5, 0))
        
        api_entry_frame = tk.Frame(api_frame)
        api_entry_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(api_entry_frame, text="API ключ:", font=('Arial', 10)).pack(side='left')
        api_entry = tk.Entry(api_entry_frame, textvariable=self.api_key_var, font=('Arial', 10), show='*')
        api_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        # Кнопка расчета
        calc_button = tk.Button(
            self.root,
            text="🔍 Найти маршруты и рассчитать CO2",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            command=self._calculate_routes,
            cursor='hand2'
        )
        calc_button.pack(pady=20)
        
        # Фрейм для результатов
        self.results_frame = tk.LabelFrame(self.root, text="Результаты расчета", font=('Arial', 12, 'bold'))
        self.results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Изначально показываем инструкцию
        self._show_instructions()
    
    def _setup_layout(self):
        """Настройка компоновки интерфейса."""
        # Центрируем окно на экране
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _show_instructions(self):
        """Показать инструкции по использованию."""
        instructions = tk.Label(
            self.results_frame,
            text="""📋 Инструкция по использованию:

1. Введите город отправления в первое поле
2. При вводе появятся варианты городов - выберите нужный
3. Введите город назначения во второе поле
4. При желании укажите API ключ для более точных расчетов
5. Нажмите кнопку "Найти маршруты и рассчитать CO2"
6. Получите список доступных видов транспорта с расчетом выбросов

🌱 Выбирайте более экологичные виды транспорта!""",
            font=('Arial', 11),
            justify='left',
            fg='#555'
        )
        instructions.pack(padx=20, pady=20)
    
    def _clear_results(self):
        """Очистить область результатов."""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
    
    def _calculate_routes(self):
        """Основная функция расчета маршрутов."""
        # Получаем выбранные города
        from_city = self.from_city_entry.get_selected_city()
        to_city = self.to_city_entry.get_selected_city()
        
        # Проверяем, что города выбраны
        if not from_city:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите город отправления из списка предложений")
            return
        
        if not to_city:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите город назначения из списка предложений")
            return
        
        if from_city['name'] == to_city['name']:
            messagebox.showerror("Ошибка", "Города отправления и назначения не могут быть одинаковыми")
            return
        
        # Обновляем API ключ если указан
        api_key = self.api_key_var.get().strip()
        if api_key:
            self.transport_logic.calculator.ors_api_key = api_key
        
        # Показываем индикатор загрузки
        self._show_loading()
        
        # Запускаем расчет в отдельном потоке
        thread = threading.Thread(
            target=self._perform_calculation,
            args=(from_city, to_city)
        )
        thread.daemon = True
        thread.start()
    
    def _show_loading(self):
        """Показать индикатор загрузки."""
        self._clear_results()
        
        loading_label = tk.Label(
            self.results_frame,
            text="⏳ Выполняется расчет маршрутов...",
            font=('Arial', 12),
            fg='#FF8C00'
        )
        loading_label.pack(pady=50)
    
    def _perform_calculation(self, from_city: dict, to_city: dict):
        """Выполнить расчет в отдельном потоке."""
        try:
            # Получаем доступные виды транспорта
            transports = self.transport_logic.get_available_transports(from_city, to_city)
            
            # Обновляем интерфейс в основном потоке
            self.root.after(0, self._show_results, from_city, to_city, transports)
            
        except Exception as e:
            error_msg = f"Ошибка при расчете: {str(e)}"
            self.root.after(0, self._show_error, error_msg)
    
    def _show_error(self, error_msg: str):
        """Показать ошибку."""
        self._clear_results()
        
        error_label = tk.Label(
            self.results_frame,
            text=f"❌ {error_msg}",
            font=('Arial', 11),
            fg='red'
        )
        error_label.pack(pady=20)
    
    def _show_results(self, from_city: dict, to_city: dict, transports: List[dict]):
        """Показать результаты расчета."""
        self._clear_results()
        
        # Заголовок с маршрутом
        route_label = tk.Label(
            self.results_frame,
            text=f"🗺️ Маршрут: {from_city['name']} → {to_city['name']}",
            font=('Arial', 14, 'bold'),
            fg='#2E8B57'
        )
        route_label.pack(pady=(10, 20))
        
        if not transports:
            no_routes_label = tk.Label(
                self.results_frame,
                text="😔 К сожалению, не найдено доступных маршрутов для данного направления",
                font=('Arial', 11),
                fg='#FF6B6B'
            )
            no_routes_label.pack(pady=20)
            return
        
        # Создаем скроллируемую область для результатов
        canvas = tk.Canvas(self.results_frame)
        scrollbar = tk.Scrollbar(self.results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Отображаем каждый вид транспорта
        for i, transport in enumerate(transports):
            self._create_transport_card(scrollable_frame, transport, i, transports)
        
        # Размещаем скроллируемую область
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Добавляем сравнительную информацию
        self._add_comparison_info(scrollable_frame, transports)
    
    def _create_transport_card(self, parent, transport: dict, index: int, all_transports: List[dict]):
        """Создать карточку для вида транспорта."""
        # Определяем цвет рамки в зависимости от экологичности
        if index == 0:  # Самый экологичный
            border_color = '#4CAF50'  # Зеленый
            bg_color = '#F1F8E9'
        elif transport['co2_emissions_kg'] <= all_transports[0]['co2_emissions_kg'] * 2:
            border_color = '#FF9800'  # Оранжевый
            bg_color = '#FFF3E0'
        else:
            border_color = '#F44336'  # Красный
            bg_color = '#FFEBEE'
        
        # Основная рамка
        card_frame = tk.Frame(parent, relief='solid', borderwidth=2, bg=bg_color)
        card_frame.pack(fill='x', padx=10, pady=5)
        
        # Заголовок с иконкой
        icons = {'Автомобиль': '🚗', 'Автобус': '🚌', 'Поезд': '🚆', 'Самолет': '✈️'}
        icon = icons.get(transport['name'], '🚶')
        
        header_frame = tk.Frame(card_frame, bg=bg_color)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        title_label = tk.Label(
            header_frame,
            text=f"{icon} {transport['name']}",
            font=('Arial', 13, 'bold'),
            bg=bg_color,
            fg=border_color
        )
        title_label.pack(side='left')
        
        # Значок экологичности
        if index == 0:
            eco_label = tk.Label(
                header_frame,
                text="🌱 Самый экологичный",
                font=('Arial', 10, 'bold'),
                bg=bg_color,
                fg='#4CAF50'
            )
            eco_label.pack(side='right')
        
        # Основная информация
        info_frame = tk.Frame(card_frame, bg=bg_color)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        # CO2 выбросы (главная метрика)
        co2_label = tk.Label(
            info_frame,
            text=f"💨 Выбросы CO2: {transport['co2_emissions_kg']} кг",
            font=('Arial', 12, 'bold'),
            bg=bg_color,
            fg='#D32F2F'
        )
        co2_label.pack(anchor='w')
        
        # Дополнительная информация
        details = [
            f"📏 Расстояние: {transport['distance_km']} км",
            f"⏱️ Время в пути: {transport['estimated_time']}",
            f"💰 Стоимость: {transport['cost_category']}",
            f"📊 Коэффициент: {transport['co2_coefficient']} кг/км"
        ]
        
        for detail in details:
            detail_label = tk.Label(
                info_frame,
                text=detail,
                font=('Arial', 10),
                bg=bg_color,
                fg='#555'
            )
            detail_label.pack(anchor='w')
        
        # Примечание о доступности
        if transport.get('availability_reason'):
            reason_label = tk.Label(
                info_frame,
                text=f"ℹ️ {transport['availability_reason']}",
                font=('Arial', 9),
                bg=bg_color,
                fg='#666',
                wraplength=600
            )
            reason_label.pack(anchor='w', pady=(5, 0))
        
        # Отступ снизу
        tk.Label(card_frame, text="", bg=bg_color, height=1).pack()
    
    def _add_comparison_info(self, parent, transports: List[dict]):
        """Добавить сравнительную информацию."""
        if len(transports) < 2:
            return
        
        # Разделитель
        separator = tk.Frame(parent, height=2, bg='#DDD')
        separator.pack(fill='x', padx=10, pady=20)
        
        # Заголовок сравнения
        comparison_label = tk.Label(
            parent,
            text="📊 Сравнение экологичности",
            font=('Arial', 12, 'bold'),
            fg='#2E8B57'
        )
        comparison_label.pack(pady=(10, 15))
        
        # Самый и наименее экологичный
        best = transports[0]
        worst = transports[-1]
        
        if best['co2_emissions_kg'] != worst['co2_emissions_kg']:
            difference = worst['co2_emissions_kg'] - best['co2_emissions_kg']
            percentage = (difference / worst['co2_emissions_kg']) * 100
            
            comparison_text = (
                f"🌱 Выбирая {best['name']} вместо {worst['name']}, "
                f"вы сэкономите {difference:.1f} кг CO2 ({percentage:.0f}%)"
            )
            
            comparison_info = tk.Label(
                parent,
                text=comparison_text,
                font=('Arial', 11),
                fg='#4CAF50',
                wraplength=600,
                justify='center'
            )
            comparison_info.pack(pady=(0, 15))
        
        # Общая информация
        total_distance = transports[0]['distance_km']
        info_text = (
            f"Общее расстояние маршрута: {total_distance} км\n"
            f"Найдено {len(transports)} доступных способов передвижения"
        )
        
        info_label = tk.Label(
            parent,
            text=info_text,
            font=('Arial', 10),
            fg='#666',
            justify='center'
        )
        info_label.pack(pady=(0, 20))
    
    def run(self):
        """Запуск приложения."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()


def main():
    """Главная функция запуска приложения."""
    try:
        app = CO2CalculatorGUI()
        app.run()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        messagebox.showerror("Критическая ошибка", f"Не удалось запустить приложение:\n{e}")


if __name__ == "__main__":
    main()
