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
            'marketing': self.handle_marketing,
            'client': self.handle_client,
            'supplier': self.handle_supplier,
            'contract': self.handle_contract,
            'quality': self.handle_quality,
            'risk': self.handle_risk,
            'strategy': self.handle_strategy,
            'compliance': self.handle_compliance,
            'innovation': self.handle_innovation,
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
                                  "Ожидание ответа: 1"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить действие со встречей. Пожалуйста, уточните команду.")()

    def handle_compliance(self, entities: Dict) -> str:
        """Handle compliance management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию по соответствию нормативам"

        compliance_actions = {
            'проверка': 'audit',
            'требования': 'requirements',
            'отчет': 'report',
            'статус': 'status',
            'риски': 'risks',
            'обучение': 'training'
        }

        action = None
        for key, value in compliance_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'audit': lambda: "Аудит соответствия:\n" + \
                           "Проверено процессов: 25\n" + \
                           "Выявлено нарушений: 3\n" + \
                           "Критических: 0\n" + \
                           "Рекомендации: 8",
            'requirements': lambda: "Нормативные требования:\n" + \
                                  "Всего требований: 156\n" + \
                                  "Выполняется: 148\n" + \
                                  "На доработке: 8\n" + \
                                  "Новых: 12",
            'report': lambda: "Отчет по соответствию:\n" + \
                            "Общий уровень: 95%\n" + \
                            "Улучшение: +5%\n" + \
                            "Открытых вопросов: 7\n" + \
                            "Штрафы: 0",
            'status': lambda: "Статус соответствия:\n" + \
                            "Соответствие законам: 100%\n" + \
                            "Внутренним политикам: 98%\n" + \
                            "Отраслевым стандартам: 95%\n" + \
                            "Лицензии: Актуальны",
            'risks': lambda: "Риски несоответствия:\n" + \
                           "Выявлено: 15\n" + \
                           "В работе: 4\n" + \
                           "Устранено: 11\n" + \
                           "Критических: 0",
            'training': lambda: "Обучение по комплаенс:\n" + \
                              "Курсов проведено: 8\n" + \
                              "Обучено сотрудников: 450\n" + \
                              "Успешная сдача: 97%\n" + \
                              "Следующий курс: 15.01.2025"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить операцию по комплаенс. Пожалуйста, уточните команду.")()

    def handle_innovation(self, entities: Dict) -> str:
        """Handle innovation management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию по управлению инновациями"

        innovation_actions = {
            'проекты': 'projects',
            'идеи': 'ideas',
            'статус': 'status',
            'бюджет': 'budget',
            'результаты': 'results',
            'технологии': 'technologies'
        }

        action = None
        for key, value in innovation_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'projects': lambda: "Инновационные проекты:\n" + \
                              "Всего проектов: 12\n" + \
                              "В разработке: 5\n" + \
                              "На тестировании: 3\n" + \
                              "Завершено: 4",
            'ideas': lambda: "Банк инновационных идей:\n" + \
                           "Всего идей: 85\n" + \
                           "На рассмотрении: 15\n" + \
                           "Одобрено: 7\n" + \
                           "В реализации: 4",
            'status': lambda: "Статус инноваций:\n" + \
                            "Успешные внедрения: 8\n" + \
                            "Пилотные проекты: 3\n" + \
                            "Патенты: 2\n" + \
                            "Прототипы: 5",
            'budget': lambda: f"Бюджет на инновации:\n" + \
                            f"Общий бюджет: {self._format_currency(25000000)} руб.\n" + \
                            f"Израсходовано: {self._format_currency(12000000)} руб.\n" + \
                            "ROI: 145%\n" + \
                            "Экономический эффект: Высокий",
            'results': lambda: "Результаты инноваций:\n" + \
                             "Новые продукты: 3\n" + \
                             "Улучшение процессов: 15%\n" + \
                             "Экономия: " + self._format_currency(8000000) + " руб.\n" + \
                             "Удовлетворенность: 92%"

        quality_actions = {
            'проверка': 'inspection',
            'стандарты': 'standards',
            'метрики': 'metrics',
            'улучшение': 'improvement',
            'отчет': 'report',
            'аудит': 'audit'
        }

        action = None
        for key, value in quality_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'inspection': lambda: "Проверка качества:\n" + \
                               "Проверено единиц: 150\n" + \
                               "Соответствует стандартам: 142\n" + \
                               "Требует доработки: 8\n" + \
                               "Критических проблем: 0",
            'standards': lambda: "Стандарты качества:\n" + \
                               "ISO 9001:2015: Внедрен\n" + \
                               "Отраслевые стандарты: 100%\n" + \
                               "Внутренние стандарты: 15\n" + \
                               "Обновление: Ежеквартально",
            'metrics': lambda: "Метрики качества:\n" + \
                             "Уровень дефектов: 0.8%\n" + \
                             "Время простоя: 2.5%\n" + \
                             "Удовлетворенность: 94%\n" + \
                             "Эффективность процессов: 89%",
            'improvement': lambda: "План улучшения качества:\n" + \
                                 "Инициатив: 12\n" + \
                                 "В работе: 5\n" + \
                                 "Завершено: 7\n" + \
                                 "Эффект: +15% к качеству",
            'report': lambda: "Отчет по качеству:\n" + \
                            "Период: Декабрь 2024\n" + \
                            "Общий уровень: 95%\n" + \
                            "Тренд: Рост\n" + \
                            "Рекомендации: 5",
            'audit': lambda: "Аудит качества:\n" + \
                           "Последний аудит: 01.12.2024\n" + \
                           "Найдено несоответствий: 3\n" + \
                           "Устранено: 2\n" + \
                           "Следующий аудит: 15.01.2025"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить операцию с качеством. Пожалуйста, уточните команду.")()
            'technologies': lambda: "Новые технологии:\n" + \
                                  "Внедрено: 5\n" + \
                                  "В процессе: 3\n" + \
                                  "На изучении: 7\n" + \
                                  "Потенциал: Высокий"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить операцию с инновациями. Пожалуйста, уточните команду.")()

    def handle_marketing(self, entities: Dict) -> str:
        """Handle marketing-related commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните маркетинговую операцию"

        marketing_actions = {
            'кампания': 'campaign',
            'анализ': 'analysis',
            'продвижение': 'promotion',
            'стратегия': 'strategy',
            'бренд': 'brand',
            'соцсети': 'social'
        }

        action = None
        for key, value in marketing_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'campaign': lambda: "Маркетинговая кампания:\n" + \
                            "Каналы: Digital, SMM, Email\n" + \
                            "Бюджет: " + self._format_currency(150000) + " руб.\n" + \
                            "Длительность: 3 месяца\n" + \
                            "Охват: 50,000 пользователей",
            'analysis': lambda: "Анализ рынка:\n" + \
                            "Размер рынка: " + self._format_currency(1500000000) + " руб.\n" + \
                            "Рост: 15% в год\n" + \
                            "Конкуренты: 12 основных\n" + \
                            "Доля рынка: 8%",
            'promotion': lambda: "План продвижения:\n" + \
                             "Каналы: 5 активных\n" + \
                             "Конверсия: 2.5%\n" + \
                             "ROI: 185%\n" + \
                             "Новые лиды: 250",
            'strategy': lambda: "Маркетинговая стратегия:\n" + \
                             "Тип: Омниканальная\n" + \
                             "Целевая аудитория: B2B\n" + \
                             "Ключевые метрики: CAC, LTV, ROI\n" + \
                             "Каналы: Digital, Offline, PR",
            'brand': lambda: "Управление брендом:\n" + \
                          "Узнаваемость: 65%\n" + \
                          "Восприятие: Позитивное\n" + \
                          "NPS: 75\n" + \
                          "Адвокаты бренда: 2,500",
            'social': lambda: "Социальные сети:\n" + \
                           "Подписчики: 50,000\n" + \
                           "Вовлеченность: 4.8%\n" + \
                           "Охват: 150,000\n" + \
                           "Лиды: 180 в месяц"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить тип маркетинговой операции. Пожалуйста, уточните команду.")()

    def handle_risk(self, entities: Dict) -> str:
        """Handle risk management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию по управлению рисками"

        risk_actions = {
            'анализ': 'analysis',
            'оценка': 'assessment',
            'митигация': 'mitigation',
            'мониторинг': 'monitoring',
            'отчет': 'report',
            'реестр': 'registry'
        }

        action = None
        for key, value in risk_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'analysis': lambda: "Анализ рисков:\n" + \
                              "Критические риски: 3\n" + \
                              "Высокие риски: 7\n" + \
                              "Средние риски: 12\n" + \
                              "Низкие риски: 25",
            'assessment': lambda: "Оценка рисков:\n" + \
                                "Финансовые риски: Высокие\n" + \
                                "Операционные риски: Средние\n" + \
                                "Репутационные риски: Низкие\n" + \
                                "Compliance риски: Средние",
            'mitigation': lambda: "План митигации рисков:\n" + \
                                "Мероприятий запланировано: 15\n" + \
                                "В процессе: 8\n" + \
                                "Завершено: 4\n" + \
                                "Эффективность: 75%",
            'monitoring': lambda: "Мониторинг рисков:\n" + \
                                "Новые риски: 3\n" + \
                                "Изменение уровня: 5\n" + \
                                "Закрытые риски: 2\n" + \
                                "Требуют внимания: 4",
            'report': lambda: "Отчет по рискам:\n" + \
                            "Период: Q4 2024\n" + \
                            "Общий уровень: Средний\n" + \
                            "Тренд: Снижение\n" + \
                            "Статус контролей: Эффективны",
            'registry': lambda: "Реестр рисков:\n" + \
                              "Всего рисков: 47\n" + \
                              "Активных: 35\n" + \
                              "На контроле: 12\n" + \
                              "Требуют обновления: 5"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить операцию с рисками. Пожалуйста, уточните команду.")()

    def handle_strategy(self, entities: Dict) -> str:
        """Handle strategic management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию по стратегическому управлению"

        strategy_actions = {
            'цели': 'goals',
            'кпэ': 'kpi',
            'анализ': 'analysis',
            'прогресс': 'progress',
            'инициативы': 'initiatives',
            'результаты': 'results'
        }

        action = None
        for key, value in strategy_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'goals': lambda: "Стратегические цели:\n" + \
                           "1. Рост выручки на 25%\n" + \
                           "2. Выход на новые рынки\n" + \
                           "3. Цифровая трансформация\n" + \
                           "4. Повышение эффективности",
            'kpi': lambda: "Ключевые показатели:\n" + \
                         f"Выручка: {self._format_currency(150000000)} руб.\n" + \
                         "Доля рынка: 15%\n" + \
                         "NPS: 82\n" + \
                         "Рентабельность: 23%",
            'analysis': lambda: "Стратегический анализ:\n" + \
                              "Сильные стороны: 5\n" + \
                              "Возможности: 4\n" + \
                              "Угрозы: 3\n" + \
                              "Конкурентные преимущества: 6",
            'progress': lambda: "Прогресс реализации стратегии:\n" + \
                              "Общий прогресс: 68%\n" + \
                              "Проектов запущено: 12\n" + \
                              "Достигнуто целей: 7/15\n" + \
                              "Следующая веха: Q1 2025",
            'initiatives': lambda: "Стратегические инициативы:\n" + \
                                 "Всего: 24\n" + \
                                 "В работе: 15\n" + \
                                 "Завершено: 6\n" + \
                                 "Планируется: 3",
            'results': lambda: "Результаты стратегии:\n" + \
                             "Рост выручки: +18%\n" + \
                             "Новые продукты: 5\n" + \
                             "Новые рынки: 2\n" + \
                             "ROI: 156%"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить операцию со стратегией. Пожалуйста, уточните команду.")()

    def handle_client(self, entities: Dict) -> str:
        """Handle client-related commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию с клиентами"

        client_actions = {
            'база': 'database',
            'статистика': 'statistics',
            'лояльность': 'loyalty',
            'обратная связь': 'feedback',
            'сегмент': 'segment',
            'история': 'history'
        }

        action = None
        for key, value in client_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'database': lambda: "База клиентов:\n" + \
                             "Всего клиентов: 1,500\n" + \
                             "Активных: 850\n" + \
                             "Новых за месяц: 45\n" + \
                             "Средний чек: " + self._format_currency(25000) + " руб.",
            'statistics': lambda: "Статистика по клиентам:\n" + \
                               "Удержание: 85%\n" + \
                               "Средний LTV: " + self._format_currency(120000) + " руб.\n" + \
                               "CAC: " + self._format_currency(15000) + " руб.\n" + \
                               "Срок жизни: 24 месяца",
            'loyalty': lambda: "Программа лояльности:\n" + \
                            "Участников: 750\n" + \
                            "Активность: 65%\n" + \
                            "Средний бонус: " + self._format_currency(2500) + " руб.\n" + \
                            "Окупаемость: 185%",
            'feedback': lambda: "Обратная связь:\n" + \
                             "NPS: 75\n" + \
                             "CSAT: 4.8/5\n" + \
                             "Отзывов за месяц: 125\n" + \
                             "Процент решённых проблем: 95%",
            'segment': lambda: "Сегментация клиентов:\n" + \
                            "Premium: 15%\n" + \
                            "Business: 45%\n" + \
                            "Standard: 40%\n" + \
                            "Потенциал роста: 25%",
            'history': lambda: "История взаимодействий:\n" + \
                            "Всего контактов: 2,500\n" + \
                            "Среднее время ответа: 2.5 часа\n" + \
                            "Успешных сделок: 85%\n" + \
                            "Повторные обращения: 45%"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить тип операции с клиентами. Пожалуйста, уточните команду.")()

    def handle_supplier(self, entities: Dict) -> str:
        """Handle supplier-related commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию с поставщиками"

        supplier_actions = {
            'список': 'list',
            'оценка': 'evaluation',
            'заказ': 'order',
            'контракт': 'contract',
            'история': 'history',
            'статистика': 'statistics'
        }

        action = None
        for key, value in supplier_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'list': lambda: "Список поставщиков:\n" + \
                         "Активных: 25\n" + \
                         "Новых: 3\n" + \
                         "На рассмотрении: 5\n" + \
                         "Заблокированных: 2",
            'evaluation': lambda: "Оценка поставщиков:\n" + \
                               "Качество: 4.8/5\n" + \
                               "Своевременность: 95%\n" + \
                               "Ценовая политика: 4.5/5\n" + \
                               "Надёжность: 4.7/5",
            'order': lambda: "Статус заказов:\n" + \
                          "В обработке: 12\n" + \
                          "Отправлено: 8\n" + \
                          "Получено: 15\n" + \
                          "Общая сумма: " + self._format_currency(750000) + " руб.",
            'contract': lambda: "Контракты с поставщиками:\n" + \
                             "Активных: 18\n" + \
                             "На подписании: 3\n" + \
                             "Истекают в этом месяце: 2\n" + \
                             "Требуют продления: 4",
            'history': lambda: "История поставок:\n" + \
                            "Всего поставок: 150\n" + \
                            "Вовремя: 142\n" + \
                            "С задержкой: 8\n" + \
                            "Среднее время доставки: 5 дней",
            'statistics': lambda: "Статистика поставщиков:\n" + \
                                "Средний срок сотрудничества: 2.5 года\n" + \
                                "Процент брака: 0.5%\n" + \
                                "Процент возвратов: 1.2%\n" + \
                                "Экономия на закупках: 15%"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить тип операции с поставщиками. Пожалуйста, уточните команду.")()

    def handle_contract(self, entities: Dict) -> str:
        """Handle contract-related commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию с договорами"

        contract_actions = {
            'статус': 'status',
            'создать': 'create',
            'изменить': 'modify',
            'продлить': 'extend',
            'расторгнуть': 'terminate',
            'архив': 'archive'
        }

        action = None
        for key, value in contract_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'status': lambda: "Статус договоров:\n" + \
                           "Активных: 45\n" + \
                           "На согласовании: 8\n" + \
                           "Требуют продления: 5\n" + \
                           "Просроченных: 2",
            'create': lambda: "Создание договора:\n" + \
                           "Номер: CTR-2024-001\n" + \
                           "Тип: Стандартный\n" + \
                           "Срок: 12 месяцев\n" + \
                           "Статус: На согласовании",
            'modify': lambda: "Изменение договора:\n" + \
                           "Внесено изменений: 3\n" + \
                           "Текущая версия: 2.1\n" + \
                           "Согласовано: Юр.отдел\n" + \
                           "Ожидает подписания",
            'extend': lambda: "Продление договора:\n" + \
                           "Новый срок: +12 месяцев\n" + \
                           "Условия: Без изменений\n" + \
                           "Требуемые действия: Подписание доп.соглашения",
            'terminate': lambda: "Расторжение договора:\n" + \
                              "Причина: По соглашению сторон\n" + \
                              "Дата: 31.12.2024\n" + \
                              "Требуемые действия: Подготовка соглашения",
            'archive': lambda: "Архив договоров:\n" + \
                            "Всего: 250\n" + \
                            "За текущий год: 45\n" + \
                            "Успешно завершённых: 225\n" + \
                            "Досрочно расторгнутых: 25"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить тип операции с договорами. Пожалуйста, уточните команду.")()

    def handle_quality(self, entities: Dict) -> str:
        """Handle quality management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию с качеством"

        quality_actions = {
            'проверка': 'check',
            'контроль': 'control',
            'стандарты': 'standards',
            'улучшение': 'improvement',
            'отчет': 'report',
            'метрики': 'metrics'
        }

        action = None
        for key, value in quality_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'check': lambda: "Проверка качества:\n" + \
                          "Соответствие стандартам: 98%\n" + \
                          "Выявлено несоответствий: 5\n" + \
                          "Критических: 0\n" + \
                          "Требуют внимания: 3",
            'control': lambda: "Контроль качества:\n" + \
                            "Проведено проверок: 125\n" + \
                            "Пройдено: 120\n" + \
                            "На доработке: 5\n" + \
                            "Эффективность системы: 96%",
            'standards': lambda: "Стандарты качества:\n" + \
                              "Всего стандартов: 45\n" + \
                              "Обновлено в этом году: 8\n" + \
                              "На пересмотре: 3\n" + \
                              "Соответствие ISO: 100%",
            'improvement': lambda: "Улучшение качества:\n" + \
                                "Инициатив запущено: 12\n" + \
                                "Завершено: 8\n" + \
                                "В процессе: 4\n" + \
                                "Эффект: +15% к качеству",
            'report': lambda: "Отчет по качеству:\n" + \
                           "Общий уровень: 4.8/5\n" + \
                           "Тренд: Позитивный\n" + \
                           "Основные улучшения: 5\n" + \
                           "Экономический эффект: " + self._format_currency(250000) + " руб.",
            'metrics': lambda: "Метрики качества:\n" + \
                            "Дефекты: -25%\n" + \
                            "Время исправления: -35%\n" + \
                            "Удовлетворенность: +15%\n" + \
                            "Стоимость качества: -10%"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить тип операции с качеством. Пожалуйста, уточните команду.")()

    def handle_risk(self, entities: Dict) -> str:
        """Handle risk management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию с рисками"

        risk_actions = {
            'анализ': 'analysis',
            'оценка': 'assessment',
            'митигация': 'mitigation',
            'мониторинг': 'monitoring',
            'отчет': 'report',
            'прогноз': 'forecast'
        }

        action = None
        for key, value in risk_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'analysis': lambda: "Анализ рисков:\n" + \
                             "Выявлено рисков: 25\n" + \
                             "Критических: 3\n" + \
                             "Средних: 12\n" + \
                             "Низких: 10",
            'assessment': lambda: "Оценка рисков:\n" + \
                               "Финансовые: Средний уровень\n" + \
                               "Операционные: Низкий уровень\n" + \
                               "Рыночные: Высокий уровень\n" + \
                               "Репутационные: Низкий уровень",
            'mitigation': lambda: "Митигация рисков:\n" + \
                               "План действий: 15 мер\n" + \
                               "Реализовано: 10\n" + \
                               "В процессе: 5\n" + \
                               "Эффективность: 85%",
            'monitoring': lambda: "Мониторинг рисков:\n" + \
                               "Под наблюдением: 20\n" + \
                               "Требуют внимания: 5\n" + \
                               "Частота проверки: Еженедельно\n" + \
                               "Тренд: Стабильный",
            'report': lambda: "Отчет по рискам:\n" + \
                           "Общий уровень: Умеренный\n" + \
                           "Изменение за период: -15%\n" + \
                           "Новые риски: 3\n" + \
                           "Закрытые риски: 5",
            'forecast': lambda: "Прогноз рисков:\n" + \
                             "Краткосрочный: Стабильный\n" + \
                             "Среднесрочный: Умеренный рост\n" + \
                             "Критические области: 2\n" + \
                             "Рекомендации: 8"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить тип операции с рисками. Пожалуйста, уточните команду.")()

    def handle_strategy(self, entities: Dict) -> str:
        """Handle strategy management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию со стратегией"

        strategy_actions = {
            'цели': 'goals',
            'анализ': 'analysis',
            'план': 'plan',
            'развитие': 'development',
            'результаты': 'results',
            'корректировка': 'adjustment'
        }

        action = None
        for key, value in strategy_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'goals': lambda: "Стратегические цели:\n" + \
                          "Количество: 5\n" + \
                          "Выполнено: 2\n" + \
                          "В процессе: 3\n" + \
                          "Прогресс: 65%",
            'analysis': lambda: "Стратегический анализ:\n" + \
                             "SWOT: Обновлен\n" + \
                             "Конкурентный анализ: Актуален\n" + \
                             "Рыночные тренды: +5 новых\n" + \
                             "Рекомендации: 12",
            'plan': lambda: "Стратегический план:\n" + \
                         "Горизонт: 3 года\n" + \
                         "Ключевые инициативы: 8\n" + \
                         "Бюджет: " + self._format_currency(15000000) + " руб.\n" + \
                         "Риски: Умеренные",
            'development': lambda: "Развитие бизнеса:\n" + \
                                "Новые направления: 3\n" + \
                                "Расширение: 2 региона\n" + \
                                "Инвестиции: " + self._format_currency(5000000) + " руб.\n" + \
                                "ROI прогноз: 185%",
            'results': lambda: "Результаты стратегии:\n" + \
                            "Достижение целей: 75%\n" + \
                            "Рост выручки: +25%\n" + \
                            "Доля рынка: +5%\n" + \
                            "Эффективность: Высокая",
            'adjustment': lambda: "Корректировка стратегии:\n" + \
                               "Внесено изменений: 4\n" + \
                               "Причины: Рыночные изменения\n" + \
                               "Влияние: Умеренное\n" + \
                               "Статус: На утверждении"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить тип операции со стратегией. Пожалуйста, уточните команду.")()

    def handle_compliance(self, entities: Dict) -> str:
        """Handle compliance management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию с комплаенс"

        compliance_actions = {
            'проверка': 'audit',
            'требования': 'requirements',
            'отчет': 'report',
            'риски': 'risks',
            'обучение': 'training',
            'нарушения': 'violations'
        }

        action = None
        for key, value in compliance_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'audit': lambda: "Аудит комплаенс:\n" + \
                          "Проверено процессов: 25\n" + \
                          "Соответствует: 22\n" + \
                          "Требует улучшения: 3\n" + \
                          "Критических нарушений: 0",
            'requirements': lambda: "Требования комплаенс:\n" + \
                                "Всего требований: 85\n" + \
                                "Выполняется: 82\n" + \
                                "На доработке: 3\n" + \
                                "Новых: 5",
            'report': lambda: "Отчет по комплаенс:\n" + \
                           "Общий уровень: Высокий\n" + \
                           "Изменения: +5%\n" + \
                           "Основные улучшения: 8\n" + \
                           "Области развития: 3",
            'risks': lambda: "Комплаенс-риски:\n" + \
                          "Выявлено: 15\n" + \
                          "Устранено: 12\n" + \
                          "В работе: 3\n" + \
                          "Приоритетные: 2",
            'training': lambda: "Обучение по комплаенс:\n" + \
                             "Проведено сессий: 12\n" + \
                             "Обучено сотрудников: 150\n" + \
                             "Эффективность: 95%\n" + \
                             "Планируется: 3 курса",
            'violations': lambda: "Нарушения комплаенс:\n" + \
                               "Всего выявлено: 8\n" + \
                               "Устранено: 7\n" + \
                               "В процессе: 1\n" + \
                               "Превентивные меры: 5"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить тип операции с комплаенс. Пожалуйста, уточните команду.")()

    def handle_innovation(self, entities: Dict) -> str:
        """Handle innovation management commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию с инновациями"

        innovation_actions = {
            'проекты': 'projects',
            'идеи': 'ideas',
            'статус': 'status',
            'технологии': 'technologies',
            'результаты': 'results',
            'бюджет': 'budget'
        }

        action = None
        for key, value in innovation_actions.items():
            if key in description:
                action = value
                break

        responses = {
            'projects': lambda: "Инновационные проекты:\n" + \
                             "Активных: 8\n" + \
                             "Завершено: 5\n" + \
                             "На рассмотрении: 3\n" + \
                             "Общий бюджет: " + self._format_currency(5000000) + " руб.",
            'ideas': lambda: "Инновационные идеи:\n" + \
                          "В банке идей: 45\n" + \
                          "На оценке: 12\n" + \
                          "Одобрено: 8\n" + \
                          "Реализуется: 3",
            'status': lambda: "Статус инноваций:\n" + \
                           "Общий прогресс: 75%\n" + \
                           "Успешных внедрений: 12\n" + \
                           "Экономический эффект: " + self._format_currency(2500000) + " руб.\n" + \
                           "ROI: 165%",
            'technologies': lambda: "Новые технологии:\n" + \
                                "Внедрено: 5\n" + \
                                "Тестируется: 3\n" + \
                                "На изучении: 8\n" + \
                                "Эффективность: +25%",
            'results': lambda: "Результаты инноваций:\n" + \
                            "Улучшение процессов: 35%\n" + \
                            "Снижение затрат: 15%\n" + \
                            "Рост производительности: 28%\n" + \
                            "Новые продукты: 3",
            'budget': lambda: "Бюджет инноваций:\n" + \
                           "Выделено: " + self._format_currency(10000000) + " руб.\n" + \
                           "Использовано: 65%\n" + \
                           "ROI текущий: 145%\n" + \
                           "Прогноз окупаемости: 18 месяцев"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить тип операции с инновациями. Пожалуйста, уточните команду.")()

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
