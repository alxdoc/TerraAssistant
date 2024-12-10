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
                'покажи информацию', 'найди данные'
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
        
        # Определяем тип команды по ключевым словам
        command_type = 'unknown'
        entities = {}
        
        # Сначала проверяем на приветствие
        greetings = ['привет', 'здравствуй', 'добрый', 'хай', 'hello']
        if any(text.startswith(greeting) for greeting in greetings):
            command_type = 'greeting'
            entities['greeting'] = True
            dialog_context.update_context(command_type)
            return command_type, entities
        
        # Затем проверяем остальные паттерны
        max_similarity = 0
        for intent, patterns in dialog_context.command_patterns.items():
            for pattern in patterns:
                # Проверяем, содержится ли паттерн в тексте
                if pattern in text:
                    command_type = intent
                    # Извлекаем оставшуюся часть текста как описание
                    description = text.replace(pattern, '').strip()
                    if description:
                        entities['description'] = description
                    dialog_context.update_context(command_type)
                    return command_type, entities
                
        logger.debug(f"Определен тип команды: {command_type}")
        logger.debug(f"Извлечены сущности: {entities}")
        
        return command_type, entities
        
    except Exception as e:
        logger.error(f"Ошибка при анализе текста: {str(e)}")
        return 'unknown', {}