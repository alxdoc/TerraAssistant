import logging
from typing import Dict
from models import Command, db

logger = logging.getLogger(__name__)

class CommandProcessor:
    def _format_currency(self, amount: float) -> str:
        """Format currency amount with thousand separators"""
        return f"{amount:,.2f}".replace(",", " ")

    def __init__(self):
        self.response_templates = {
            'greeting': [
                "Здравствуйте! Чем могу помочь?",
                "Приветствую! Готов помочь вам.",
                "Добрый день! Как я могу быть полезен?"
            ],
            'unknown': [
                "Извините, я не понял команду. Пожалуйста, повторите.",
                "Не могу распознать команду. Попробуйте сформулировать иначе.",
            ],
            'error': [
                "Произошла ошибка: {details}",
                "Не удалось выполнить команду: {details}"
            ]
        }
        
        # Инициализация обработчиков команд
        self.command_handlers = {
            'greeting': self.handle_greeting,
            'task_creation': self.handle_task_creation,
            'document_analysis': self.handle_document_analysis,
            'search': self.handle_search,
            'calendar': self.handle_calendar,
            'contact': self.handle_contact,
            'reminder': self.handle_reminder,
            'finance': self.handle_finance,
            'project': self.handle_project,
            'sales': self.handle_sales,
            'inventory': self.handle_inventory,
            'analytics': self.handle_analytics,
            'employee': self.handle_employee,
            'meeting': self.handle_meeting,
            'unknown': self.handle_unknown_command
        }

    def process_command(self, command_type: str, entities: Dict) -> str:
        """Process command based on its type"""
        if not command_type:
            logger.warning("Empty command type received")
            return self.format_error("Тип команды не может быть пустым")
            
        try:
            logger.debug(f"Processing command type: {command_type} with entities: {entities}")
            
            # Получаем обработчик команды
            handler = self.command_handlers.get(command_type)
            if not handler:
                logger.warning(f"Unknown command type: {command_type}")
                return self.command_handlers['unknown'](entities)
                
            # Выполняем команду
            result = handler(entities)
            
            # Сохраняем команду в базу данных
            try:
                self.save_command(command_type, result)
            except Exception as db_error:
                logger.error(f"Error saving command to database: {str(db_error)}")
                # Продолжаем выполнение даже при ошибке сохранения
                
            logger.info(f"Command processed successfully: {result}")
            return result
            
        except Exception as e:
            error_msg = f"Error processing command {command_type}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.format_error(error_msg)

    def handle_greeting(self, entities: Dict) -> str:
        """Handle greeting command"""
        import random
        return random.choice(self.response_templates['greeting'])

    def handle_unknown_command(self, entities: Dict) -> str:
        """Handle unknown command"""
        import random
        return random.choice(self.response_templates['unknown'])

    def handle_task_creation(self, entities: Dict) -> str:
        """Handle task creation command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите описание задачи"

        # Расширенная логика создания задачи
        priority_keywords = {
            'срочно': 'high',
            'важно': 'high',
            'критично': 'high',
            'средний': 'medium',
            'обычный': 'medium',
            'низкий': 'low',
            'потом': 'low'
        }

        # Определяем приоритет задачи
        priority = 'medium'
        for keyword, value in priority_keywords.items():
            if keyword in description.lower():
                priority = value
                break

        logger.info(f"Creating task with priority {priority}: {description}")
        return f"Создана задача ({priority} приоритет): {description}"

    def handle_document_analysis(self, entities: Dict) -> str:
        """Handle document analysis command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите документ для анализа"

        # Расширенная логика анализа документов
        doc_types = {
            'договор': 'contract',
            'счет': 'invoice',
            'акт': 'act',
            'отчет': 'report',
            'справка': 'certificate'
        }

        doc_type = 'unknown'
        for key, value in doc_types.items():
            if key in description.lower():
                doc_type = value
                break

        logger.info(f"Analyzing document type {doc_type}: {description}")
        return f"Анализ документа ({doc_type}): {description}"

    def handle_search(self, entities: Dict) -> str:
        """Handle search command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите, что нужно найти"

        # Расширенная логика поиска
        search_categories = {
            'документ': 'documents',
            'файл': 'files',
            'контакт': 'contacts',
            'задача': 'tasks',
            'проект': 'projects',
            'встреча': 'meetings'
        }

        category = 'all'
        for key, value in search_categories.items():
            if key in description.lower():
                category = value
                break

        logger.info(f"Searching in category {category}: {description}")
        return f"Поиск в категории {category}: {description}"

    def handle_calendar(self, entities: Dict) -> str:
        """Handle calendar command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните действие с календарем"

        # Расширенная логика работы с календарем
        calendar_actions = {
            'добавить': 'add',
            'создать': 'add',
            'запланировать': 'add',
            'показать': 'show',
            'найти': 'find',
            'удалить': 'delete',
            'перенести': 'move'
        }

        action = 'show'
        for key, value in calendar_actions.items():
            if key in description.lower():
                action = value
                break

        logger.info(f"Calendar operation {action}: {description}")
        return f"Календарь ({action}): {description}"

    def handle_contact(self, entities: Dict) -> str:
        """Handle contact command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, уточните действие с контактом"

        # Расширенная логика работы с контактами
        contact_actions = {
            'добавить': 'add',
            'создать': 'add',
            'найти': 'find',
            'показать': 'show',
            'обновить': 'update',
            'удалить': 'delete'
        }

        action = 'show'
        for key, value in contact_actions.items():
            if key in description.lower():
                action = value
                break

        logger.info(f"Contact operation {action}: {description}")
        return f"Контакт ({action}): {description}"

    def handle_reminder(self, entities: Dict) -> str:
        """Handle reminder command"""
        description = entities.get('description', '')
        if not description:
            return "Пожалуйста, укажите текст напоминания"

        # Расширенная логика работы с напоминаниями
        reminder_types = {
            'встреча': 'meeting',
            'звонок': 'call',
            'задача': 'task',
            'дедлайн': 'deadline',
            'событие': 'event'
        }

        reminder_type = 'general'
        for key, value in reminder_types.items():
            if key in description.lower():
                reminder_type = value
                break

        logger.info(f"Setting reminder type {reminder_type}: {description}")
        return f"Установлено напоминание ({reminder_type}): {description}"

    def handle_finance(self, entities: Dict) -> str:
        """Handle finance-related commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните финансовую операцию"

        # Расширенная логика работы с финансами
        operation_types = {
            'баланс': 'balance',
            'остаток': 'balance',
            'счет': 'balance',
            'расход': 'expense',
            'трата': 'expense',
            'списание': 'expense',
            'доход': 'income',
            'поступление': 'income',
            'прибыль': 'income',
            'отчет': 'report',
            'сводка': 'report',
            'статистика': 'report',
            'выставить счет': 'invoice',
            'счет-фактура': 'invoice',
            'инвойс': 'invoice'
        }

        operation_type = None
        for key, value in operation_types.items():
            if key in description:
                operation_type = value
                break

        logger.info(f"Finance operation type {operation_type}: {description}")

        responses = {
            'balance': lambda: f"Текущий баланс счета: {self._format_currency(100000)} руб.",
            'expense': lambda: f"Расход успешно записан. Остаток на счете: {self._format_currency(95000)} руб.",
            'income': lambda: f"Доход успешно записан. Новый баланс: {self._format_currency(105000)} руб.",
            'report': lambda: "Финансовый отчет за текущий период:\n" + \
                            f"Доходы: {self._format_currency(150000)} руб.\n" + \
                            f"Расходы: {self._format_currency(80000)} руб.\n" + \
                            f"Прибыль: {self._format_currency(70000)} руб.",
            'invoice': lambda: "Счет успешно создан и отправлен на указанный email.",
        }

        return responses.get(operation_type or 'unknown', lambda: "Не удалось определить тип финансовой операции. Пожалуйста, уточните команду.")()

    def handle_project(self, entities: Dict) -> str:
        """Handle project management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните действие с проектом"

        # Расширенная логика работы с проектами
        project_actions = {
            'создать': 'create',
            'новый': 'create',
            'начать': 'create',
            'статус': 'status',
            'состояние': 'status',
            'обновить': 'update',
            'изменить': 'update',
            'завершить': 'complete',
            'закрыть': 'complete'
        }

        action = None
        for key, value in project_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'create': lambda: "Создан новый проект. ID: PRJ-2024-001, Команда: 5 человек",
            'status': lambda: "Статус проекта PRJ-2024-001:\n" + \
                            "Прогресс: 75%\n" + \
                            "Дедлайн: 20.12.2024\n" + \
                            "Риски: Низкие\n" + \
                            "Бюджет: В рамках",
            'update': lambda: "Проект обновлен. Добавлены новые задачи и ресурсы.",
            'complete': lambda: "Проект успешно завершен.\n" + \
                              "Длительность: 45 дней\n" + \
                              "Выполнено задач: 34/34\n" + \
                              "Отчет отправлен руководителю.",
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить действие с проектом. Пожалуйста, уточните команду.")()

    def handle_sales(self, entities: Dict) -> str:
        """Handle sales-related commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните информацию о продаже"

        # Расширенная логика работы с продажами
        sales_actions = {
            'новая': 'new_sale',
            'создать': 'new_sale',
            'оформить': 'new_sale',
            'статус': 'status',
            'состояние': 'status',
            'отчет': 'report',
            'статистика': 'report',
            'план': 'plan',
            'прогноз': 'forecast'
        }

        action = None
        for key, value in sales_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'new_sale': lambda: "Новая продажа оформлена:\n" + \
                              f"Сумма: {self._format_currency(250000)} руб.\n" + \
                              "Номер заказа: ORD-2024-001\n" + \
                              "Менеджер: Иванов И.И.",
            'status': lambda: "Статус продаж:\n" + \
                            "Выполнено: 85%\n" + \
                            "В работе: 10%\n" + \
                            "Отменено: 5%\n" + \
                            f"Общая сумма: {self._format_currency(1500000)} руб.",
            'report': lambda: f"Отчет по продажам:\n" + \
                            f"Общая сумма: {self._format_currency(1500000)} руб.\n" + \
                            "Количество сделок: 45\n" + \
                            "Средний чек: +12%\n" + \
                            "Конверсия: 8.5%",
            'plan': lambda: "План продаж на месяц:\n" + \
                          f"Цель: {self._format_currency(2000000)} руб.\n" + \
                          "Новых клиентов: 20\n" + \
                          "Сделок: 50",
            'forecast': lambda: "Прогноз продаж:\n" + \
                              "Рост: +15%\n" + \
                              "Новые рынки: 2\n" + \
                              "Потенциальные клиенты: 35",
        }

        return responses.get(action, lambda: "Не удалось определить действие с продажами. Пожалуйста, уточните команду.")()

    def handle_inventory(self, entities: Dict) -> str:
        """Handle inventory management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию со складом"

        # Расширенная логика работы со складом
        inventory_actions = {
            'остаток': 'check',
            'наличие': 'check',
            'поставка': 'delivery',
            'приход': 'delivery',
            'отгрузка': 'shipment',
            'отправка': 'shipment',
            'инвентаризация': 'inventory',
            'ревизия': 'inventory'
        }

        action = None
        for key, value in inventory_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'check': lambda: "Текущие остатки на складе:\n" + \
                           "Товар А: 150 шт.\n" + \
                           "Товар Б: 200 шт.\n" + \
                           "Товар В: 75 шт.\n" + \
                           "Общая стоимость: " + self._format_currency(500000) + " руб.",
            'delivery': lambda: "Поставка оформлена:\n" + \
                              "Дата прибытия: 15.12.2024\n" + \
                              "Количество позиций: 12\n" + \
                              f"Сумма: {self._format_currency(150000)} руб.",
            'shipment': lambda: "Отгрузка запланирована:\n" + \
                              "Номер накладной: WB-2024-001\n" + \
                              "Дата отгрузки: 12.12.2024\n" + \
                              "Статус: Подготовка",
            'inventory': lambda: "Инвентаризация:\n" + \
                               "Последняя: 01.12.2024\n" + \
                               "Расхождения: 0.5%\n" + \
                               "Статус: Завершена",
        }

        return responses.get(action, lambda: "Не удалось определить операцию со складом. Пожалуйста, уточните команду.")()

    def handle_analytics(self, entities: Dict) -> str:
        """Handle analytics and reporting commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните тип аналитики"

        # Расширенная логика работы с аналитикой
        analytics_types = {
            'продажи': 'sales',
            'выручка': 'sales',
            'эффективность': 'performance',
            'производительность': 'performance',
            'прогноз': 'forecast',
            'тренд': 'forecast',
            'сравнение': 'comparison',
            'динамика': 'dynamics'
        }

        analysis_type = None
        for key, value in analytics_types.items():
            if key in description:
                analysis_type = value
                break

        responses = {
            'sales': lambda: f"Анализ продаж:\n" + \
                           f"Оборот: {self._format_currency(2500000)} руб.\n" + \
                           "Рост: +15%\n" + \
                           "Новые клиенты: +25%\n" + \
                           "Повторные продажи: 45%",
            'performance': lambda: "Показатели эффективности:\n" + \
                                 "Конверсия: 8.5%\n" + \
                                 "Средний чек: +12%\n" + \
                                 "Возврат инвестиций: 125%\n" + \
                                 "NPS: 78",
            'forecast': lambda: "Прогноз на следующий квартал:\n" + \
                              "Рост продаж: +20%\n" + \
                              "Новых клиентов: +35\n" + \
                              "Расширение рынка: 2 региона",
            'comparison': lambda: "Сравнительный анализ:\n" + \
                                "План/Факт: 105%\n" + \
                                "Год к году: +25%\n" + \
                                "Доля рынка: +2.5%",
            'dynamics': lambda: "Динамика показателей:\n" + \
                              "Темп роста: 15% в месяц\n" + \
                              "Сезонность: Низкая\n" + \
                              "Тренд: Восходящий",
        }

        return responses.get(analysis_type or 'unknown', lambda: "Не удалось определить тип аналитики. Пожалуйста, уточните запрос.")()

    def handle_employee(self, entities: Dict) -> str:
        """Handle employee management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните действие с данными сотрудника"

        # Расширенная логика работы с сотрудниками
        employee_actions = {
            'график': 'schedule',
            'расписание': 'schedule',
            'отпуск': 'vacation',
            'выходной': 'vacation',
            'зарплата': 'salary',
            'оклад': 'salary',
            'статус': 'info',
            'информация': 'info',
            'оценка': 'performance',
            'развитие': 'development'
        }

        action = None
        for key, value in employee_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'schedule': lambda: "График работы сотрудника на неделю:\n" + \
                              "Пн-Пт: 9:00-18:00\n" + \
                              "Сб-Вс: выходные\n" + \
                              "Всего часов: 40",
            'vacation': lambda: "Информация об отпуске:\n" + \
                              "Доступно дней: 28\n" + \
                              "Использовано: 14\n" + \
                              "Следующий отпуск: 15.01.2024",
            'salary': lambda: f"Информация о заработной плате:\n" + \
                            f"Оклад: {self._format_currency(80000)} руб.\n" + \
                            f"Премия: {self._format_currency(15000)} руб.\n" + \
                            f"Бонусы: {self._format_currency(10000)} руб.\n" + \
                            f"Итого: {self._format_currency(105000)} руб.",
            'info': lambda: "Информация о сотруднике:\n" + \
                          "Должность: Менеджер\n" + \
                          "Отдел: Продажи\n" + \
                          "Стаж: 2 года\n" + \
                          "Проекты: 5",
            'performance': lambda: "Оценка эффективности:\n" + \
                                 "KPI: 95%\n" + \
                                 "Выполнение плана: 110%\n" + \
                                 "Качество работы: Высокое",
            'development': lambda: "План развития:\n" + \
                                 "Обучение: 2 курса\n" + \
                                 "Навыки: +3 новых\n" + \
                                 "Сертификации: 1",
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить действие с данными сотрудника. Пожалуйста, уточните команду.")()

    def handle_meeting(self, entities: Dict) -> str:
        """Handle meeting organization commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните детали встречи"

        # Расширенная логика работы с встречами
        meeting_actions = {
            'создать': 'create',
            'организовать': 'create',
            'запланировать': 'create',
            'статус': 'info',
            'информация': 'info',
            'отменить': 'cancel',
            'перенести': 'reschedule',
            'участники': 'participants'
        }

        action = None
        for key, value in meeting_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'create': lambda: "Встреча запланирована:\n" + \
                            "Дата: 15.12.2024\n" + \
                            "Время: 15:00\n" + \
                            "Участники: 5 человек\n" + \
                            "Приглашения отправлены",
            'info': lambda: "Информация о встрече:\n" + \
                          "Тема: Обсуждение проекта\n" + \
                          "Участники: 5 человек\n" + \
                          "Время: 15:00\n" + \
                          "Длительность: 1 час",
            'cancel': lambda: "Встреча отменена:\n" + \
                            "Участники уведомлены\n" + \
                            "Причина: По запросу организатора",
            'reschedule': lambda: "Встреча перенесена:\n" + \
                                "Новая дата: 16.12.2024\n" + \
                                "Время: 14:00\n" + \
                                "Участники уведомлены",
            'participants': lambda: "Участники встречи:\n" + \
                                  "Всего: 5 человек\n" + \
                                  "Подтвердили: 4\n" + \
                                  "Ожидание ответа: 1",
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить действие со встречей. Пожалуйста, уточните команду.")()

    def format_error(self, details: str) -> str:
        """Format error message"""
        import random
        return random.choice(self.response_templates['error']).format(details=details)

    def save_command(self, command_type: str, result: str) -> None:
        """Save executed command to database"""
        try:
            command = Command(
                text=result,
                command_type=command_type,
                status='completed',
                result=result
            )
            db.session.add(command)
            db.session.commit()
            logger.debug("Command successfully saved to database")
        except Exception as e:
            logger.error(f"Error saving command: {str(e)}", exc_info=True)

# Create global command processor instance
command_processor = CommandProcessor()

def process_command(command_type: str, entities: Dict) -> str:
    """Global function for processing commands"""
    result = command_processor.process_command(command_type, entities)
    command_processor.save_command(command_type, result)
    return result
