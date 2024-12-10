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
            'entities': {}
        }

def analyze_text(text: str, dialog_context: DialogContext) -> Tuple[str, Dict]:
    """Анализирует текст и возвращает намерение и сущности"""
    try:
        logger.debug(f"Анализ текста: {text}")
        text = text.lower().strip()
        
        # Определяем тип команды по ключевым словам
        command_type = 'unknown'
        entities = {}
        
        for intent, patterns in dialog_context.command_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    command_type = intent
                    # Извлекаем оставшуюся часть текста как описание
                    description = text.replace(pattern, '').strip()
                    if description:
                        entities['description'] = description
                    break
            if command_type != 'unknown':
                break
                
        logger.debug(f"Определен тип команды: {command_type}")
        logger.debug(f"Извлечены сущности: {entities}")
        
        return command_type, entities
        
    except Exception as e:
        logger.error(f"Ошибка при анализе текста: {str(e)}")
        return 'unknown', {}