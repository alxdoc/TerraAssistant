import logging
from typing import Dict
import re

logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self):
        self.context = {}
        
    def _format_currency(self, amount: float) -> str:
        """Format currency amount with thousand separators"""
        return f"{amount:,.0f}"
        
    def handle_innovation(self, entities: Dict) -> str:
        """Handle innovation-related commands"""
        description = entities.get('description', '').lower()
        if not description:
            return "Пожалуйста, уточните операцию с инновациями"

        innovation_actions = {
            'проект': 'projects',
            'идеи': 'ideas',
            'статус': 'status',
            'бюджет': 'budget',
            'технологии': 'technologies',
            'результаты': 'results'
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
                              "Удовлетворенность: 92%",
            'technologies': lambda: "Используемые технологии:\n" + \
                                  "AI/ML: 3 проекта\n" + \
                                  "Блокчейн: 1 проект\n" + \
                                  "Роботизация: 2 проекта\n" + \
                                  "Big Data: 4 проекта"
        }

        return responses.get(action or 'unknown', lambda: "Не удалось определить операцию с инновациями. Пожалуйста, уточните команду.")()

    def process_command(self, command_type: str, entities: Dict) -> str:
        """Process the command based on its type"""
        logger.debug(f"Processing command of type: {command_type} with entities: {entities}")
        
        # Обработка приветствия
        if command_type == 'greeting':
            return "Здравствуйте! Я - ваш бизнес-ассистент ТЕРРА. Чем могу помочь?"
            
        # Маппинг типов команд на обработчики
        handlers = {
            'innovation': self.handle_innovation,
            'marketing': self.handle_marketing,
            'client': self.handle_client,
            'supplier': self.handle_supplier,
            'contract': self.handle_contract,
            'quality': self.handle_quality,
            'risk': self.handle_risk,
            'strategy': self.handle_strategy,
            'task_creation': lambda x: "Создаю новую задачу: " + x.get('description', 'без описания'),
            'document_analysis': lambda x: "Анализирую документ: " + x.get('description', 'не указан'),
            'search': lambda x: "Ищу информацию по запросу: " + x.get('description', 'не указан'),
            'calendar': lambda x: "Работаю с календарем: " + x.get('description', 'нет деталей'),
            'contact': lambda x: "Работаю с контактами: " + x.get('description', 'нет деталей'),
            'reminder': lambda x: "Устанавливаю напоминание: " + x.get('description', 'без описания'),
            'finance': lambda x: "Работаю с финансами: " + x.get('description', 'нет деталей'),
            'project': lambda x: "Работаю с проектом: " + x.get('description', 'нет деталей'),
            'sales': lambda x: "Работаю с продажами: " + x.get('description', 'нет деталей'),
            'inventory': lambda x: "Работаю со складом: " + x.get('description', 'нет деталей'),
            'analytics': lambda x: "Анализирую данные: " + x.get('description', 'нет деталей'),
            'employee': lambda x: "Работаю с данными сотрудников: " + x.get('description', 'нет деталей'),
            'meeting': lambda x: "Работаю с встречами: " + x.get('description', 'нет деталей')
        }
        
        try:
            # Получаем обработчик для данного типа команды
            handler = handlers.get(command_type)
            
            if handler:
                logger.info(f"Found handler for command type: {command_type}")
                return handler(entities)
            else:
                logger.warning(f"Unknown command type: {command_type}")
                return "Извините, я не распознал команду. Пожалуйста, попробуйте переформулировать."
                
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return "Произошла ошибка при обработке команды. Пожалуйста, попробуйте еще раз."


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

# Create a singleton instance
command_processor = CommandProcessor()

def process_command(command_type: str, entities: Dict) -> str:
    """Global function to process commands"""
    return command_processor.process_command(command_type, entities)