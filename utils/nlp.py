import logging
import re
from typing import Dict, Tuple

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DialogContext:
    def __init__(self):
        self.current_topic = None
        self.command_patterns = {
            'task_creation': [
                'создать задачу', 'новая задача', 'добавить заявку',
                'запланировать', 'поставить задачу', 'назначить задание'
            ],
            'document_analysis': [
                'проверить документ', 'анализ документа', 'проверка договора',
                'изучить документ', 'просмотреть контракт'
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
            'greeting': [
                'привет', 'здравствуй', 'добрый день', 'доброе утро',
                'добрый вечер', 'приветствую'
            ]
        }

    def get_context(self):
        """Возвращает текущий контекст диалога"""
        return {
            'topic': self.current_topic,
            'entities': {},
            'last_command_type': getattr(self, 'last_command_type', None)
        }

    def update_context(self, command_type: str):
        """Обновляет контекст диалога"""
        self.last_command_type = command_type
        if command_type != 'greeting':
            self.current_topic = command_type

def analyze_text(text: str, dialog_context: DialogContext) -> Tuple[str, Dict]:
    """Анализирует текст и возвращает намерение и сущности"""
    try:
        logger.debug(f"Анализ текста: {text}")
        text = text.lower().strip()
        
        # Определяем тип команды и сущности
        command_type = 'unknown'
        entities = {}
        
        # Очищаем текст от ключевого слова "терра"
        text = text.replace('терра', '').replace('terra', '').strip()
        
        # Проверяем на приветствие
        greetings = ['привет', 'здравствуй', 'добрый', 'хай', 'hello']
        if any(text.startswith(greeting) for greeting in greetings):
            command_type = 'greeting'
            entities['greeting'] = True
            dialog_context.update_context(command_type)
            logger.info(f"Распознано приветствие: {text}")
            return command_type, entities
        
        # Проверяем остальные паттерны команд
        for intent, patterns in dialog_context.command_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    command_type = intent
                    # Извлекаем оставшуюся часть текста как описание
                    description = text.replace(pattern, '').strip()
                    if description:
                        entities['description'] = description
                    dialog_context.update_context(command_type)
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