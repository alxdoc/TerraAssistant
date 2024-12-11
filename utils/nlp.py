import logging
import re
from typing import Dict, Tuple, Optional

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DialogContext:
    def __init__(self):
        self.current_topic: Optional[str] = None
        self.last_command_type: Optional[str] = None
        self.command_patterns = {
            'task_creation': [
                'создать задачу', 'новая задача', 'добавить заявку',
                'запланировать', 'поставить задачу', 'назначить задание',
                'добавить поручение', 'создать поручение', 'новое поручение',
                'создай задачу', 'поставь задачу', 'заведи задачу',
                'сделай задачу', 'внеси задачу', 'добавь задачу'
            ],
            'marketing': [
                'маркетинг', 'рекламная кампания', 'продвижение',
                'анализ рынка', 'целевая аудитория', 'бренд',
                'социальные сети', 'маркетинговый план'
            ],
            'client': [
                'клиентская база', 'клиенты', 'работа с клиентами',
                'обслуживание клиентов', 'лояльность клиентов',
                'обратная связь', 'клиентский опыт'
            ],
            'supplier': [
                'поставщики', 'управление поставками', 'закупки',
                'оценка поставщиков', 'договор поставки', 'логистика',
                'цепочка поставок'
            ],
            'contract': [
                'договор', 'контракт', 'соглашение', 'условия договора',
                'подписание договора', 'расторжение договора',
                'дополнительное соглашение'
            ],
            'quality': [
                'качество', 'контроль качества', 'управление качеством',
                'стандарты качества', 'улучшение качества', 'оценка качества',
                'система качества'
            ],
            'document_analysis': [
                'проверить документ', 'анализ документа', 'проверка договора',
                'изучить документ', 'просмотреть контракт', 'проанализировать соглашение'
            ],
            'search': [
                'найти', 'поиск', 'искать', 'где находится',
                'покажи информацию', 'найди данные', 'поищи'
            ],
            'calendar': [
                'календарь', 'расписание', 'встреча',
                'запланировать встречу', 'добавить в календарь'
            ],
            'contact': [
                'контакт', 'добавить контакт', 'найти контакт',
                'информация о человеке', 'данные сотрудника', 'телефон'
            ],
            'reminder': [
                'напомнить', 'установить напоминание',
                'поставить будильник', 'не забыть', 'запомнить'
            ],
            'finance': [
                'финансы', 'баланс', 'бюджет', 'расходы', 'доходы',
                'платеж', 'счет', 'транзакция', 'оплата', 'выставить счет'
            ],
            'project': [
                'проект', 'создать проект', 'статус проекта', 'обновить проект',
                'завершить проект', 'команда проекта', 'план проекта'
            ],
            'sales': [
                'продажи', 'новая сделка', 'клиент', 'заказ', 
                'оформить продажу', 'воронка продаж', 'выставить счет',
                'статус сделки', 'потенциальный клиент'
            ],
            'inventory': [
                'склад', 'товары', 'остатки', 'проверить наличие',
                'заказать товар', 'инвентаризация', 'поставка',
                'приход товара', 'отгрузка'
            ],
            'analytics': [
                'аналитика', 'анализ данных', 'тренды', 'прогноз',
                'показатели', 'метрики', 'эффективность', 'отчет по продажам',
                'статистика', 'динамика продаж'
            ],
            'employee': [
                'сотрудник', 'персонал', 'штат', 'отпуск',
                'график работы', 'зарплата', 'оценка работы',
                'повышение', 'обучение', 'компетенции'
            ],
            'meeting': [
                'совещание', 'организовать встречу', 'запланировать звонок',
                'конференция', 'презентация', 'брифинг', 'переговоры'
            ],
            'greeting': [
                'привет', 'здравствуй', 'добрый день', 'доброе утро',
                'добрый вечер', 'приветствую'
            ]
        }

    def get_context(self) -> Dict:
        """Возвращает текущий контекст диалога"""
        return {
            'topic': self.current_topic,
            'entities': {},
            'last_command_type': self.last_command_type
        }

    def update_context(self, command_type: str) -> None:
        """Обновляет контекст диалога"""
        self.last_command_type = command_type
        if command_type != 'greeting':
            self.current_topic = command_type

    def analyze_text(self, text: str) -> Tuple[str, Dict]:
        """Анализирует текст и возвращает намерение и сущности"""
        try:
            logger.debug(f"Анализ текста: {text}")
            text = text.lower().strip()
            
            # Определяем тип команды и сущности
            command_type = 'unknown'
            entities: Dict = {}
            
            # Очищаем текст от ключевого слова "терра"
            text = text.replace('терра', '').replace('terra', '').strip()
            
            # Проверяем на приветствие
            greetings = ['привет', 'здравствуй', 'добрый', 'хай', 'hello']
            if any(text.startswith(greeting) for greeting in greetings):
                command_type = 'greeting'
                entities['greeting'] = True
                self.update_context(command_type)
                logger.info(f"Распознано приветствие: {text}")
                return command_type, entities
            
            # Проверяем на создание задачи первым делом
            task_patterns = self.command_patterns.get('task_creation', [])
            for pattern in task_patterns:
                if pattern.lower() in text:
                    command_type = 'task_creation'
                    # Извлекаем оставшуюся часть текста как описание
                    description = text.replace(pattern.lower(), '').strip()
                    if description:
                        entities['description'] = description
                    self.update_context(command_type)
                    logger.info(f"Распознана команда создания задачи: {text}")
                    logger.debug(f"Извлечено описание: {description}")
                    return command_type, entities
            
            # Проверяем остальные приоритетные типы команд
            priority_types = ['meeting', 'reminder']
            for priority_type in priority_types:
                patterns = self.command_patterns.get(priority_type, [])
                for pattern in patterns:
                    if pattern.lower() in text:
                        command_type = priority_type
                        # Извлекаем оставшуюся часть текста как описание
                        description = text.replace(pattern.lower(), '').strip()
                        if description:
                            entities['description'] = description
                        self.update_context(command_type)
                        logger.info(f"Распознана приоритетная команда типа {priority_type}: {text}")
                        logger.debug(f"Извлечено описание: {description}")
                        return command_type, entities
            
            # Затем проверяем остальные типы команд
            for intent, patterns in self.command_patterns.items():
                if intent not in priority_types:
                    for pattern in patterns:
                        if pattern.lower() in text:
                            command_type = intent
                            description = text.replace(pattern.lower(), '').strip()
                            if description:
                                entities['description'] = description
                            self.update_context(command_type)
                            logger.info(f"Распознана команда типа {intent}: {text}")
                            logger.debug(f"Извлечено описание: {description}")
                            return command_type, entities
            
            # Если команда не распознана, сохраняем текст как описание
            if text:
                entities['description'] = text
                logger.warning(f"Команда не распознана, сохранён текст: {text}")
            
            return command_type, entities
            
        except Exception as e:
            logger.error(f"Ошибка при анализе текста: {str(e)}", exc_info=True)
            return 'unknown', {'error': str(e)}
